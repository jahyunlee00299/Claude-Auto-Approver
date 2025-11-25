"""
Main Approver Orchestrator
SOLID: Single Responsibility - Only coordinates other components
       Dependency Inversion - Depends on abstractions (injected dependencies)
"""
import os
import time
import threading
from typing import Optional

from .config import Config
from .pattern_matcher import PatternMatcher
from .window_manager import WindowManager, WindowInfo
from .ocr_engine import OCREngine
from .approval_sender import ApprovalSender
from .notification_manager import NotificationManager, NotificationData


class Approver:
    """
    Main orchestrator that coordinates all components for auto-approval

    Uses dependency injection for all components, making it easy to:
    - Test with mock components
    - Swap implementations (Open/Closed Principle)
    - Maintain single responsibility per component
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        pattern_matcher: Optional[PatternMatcher] = None,
        window_manager: Optional[WindowManager] = None,
        ocr_engine: Optional[OCREngine] = None,
        approval_sender: Optional[ApprovalSender] = None,
        notification_manager: Optional[NotificationManager] = None,
    ):
        """
        Initialize Approver with optional dependency injection

        Args:
            config: Configuration object (default: Config.default())
            pattern_matcher: Pattern matching component
            window_manager: Window management component
            ocr_engine: OCR engine component
            approval_sender: Approval sending component
            notification_manager: Notification component
        """
        # Use provided config or create default
        self.config = config or Config.default()

        # Initialize components with dependency injection
        self.pattern_matcher = pattern_matcher or PatternMatcher(self.config.patterns)
        self.window_manager = window_manager or WindowManager(self.config.filters)
        self.ocr_engine = ocr_engine or OCREngine(self.config.ocr)
        self.approval_sender = approval_sender or ApprovalSender(self.config.monitoring)
        self.notification_manager = notification_manager or NotificationManager()

        # Set icon path if exists
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "approval_icon.png")
        if os.path.exists(icon_path):
            self.notification_manager.icon_path = icon_path

        # State
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._check_count = 0

    @property
    def running(self) -> bool:
        """Check if monitoring is running"""
        return self._running

    @property
    def approval_count(self) -> int:
        """Get total approval count"""
        return self.approval_sender.total_approvals

    def start(self) -> None:
        """Start monitoring"""
        if self._running:
            print("[WARNING] Already running")
            return

        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

        print("[OK] Approver started")

    def stop(self) -> None:
        """Stop monitoring"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=3)
        print("[INFO] Monitoring stopped")

    def _process_window(self, window: WindowInfo) -> bool:
        """
        Process a single window for approval detection

        Args:
            window: WindowInfo object

        Returns:
            True if approval was sent, False otherwise
        """
        hwnd = window.hwnd
        title = window.title

        # Check cooldown
        if not self.approval_sender.should_approve(hwnd):
            return False

        # Skip system windows
        if self.window_manager.is_system_window(hwnd):
            return False

        # Skip excluded windows
        if self.window_manager.is_excluded(title):
            return False

        # Capture window
        self._check_count += 1
        img = self.window_manager.capture_window(hwnd)
        if not img:
            return False

        # Extract text
        text = self.ocr_engine.extract_text(img, fast_mode=True)
        if not text:
            return False

        # Debug: Check for potential approval
        text_lower = text.lower()
        if 'do you want' in text_lower or 'would you' in text_lower or 'proceed' in text_lower:
            self._print_debug_info(text)

        # Check pattern
        match_result = self.pattern_matcher.check_approval_pattern(text)
        if not match_result.is_match:
            return False

        # Determine response key
        response_key = self.pattern_matcher.determine_response_key(text)

        # Print detection info
        self._print_detection_info(window, response_key, text)

        # Send approval
        result = self.approval_sender.send_approval(hwnd, response_key)

        if result.success:
            print(f"[SUCCESS] Approval completed at {result.timestamp}")
            print(f"[INFO] Total approvals: {self.approval_count}")
            print(f"[INFO] Cooldown: {self.config.monitoring.re_approval_cooldown}s")

            # Return to original window
            self.window_manager.return_to_current_window()

            # Queue notification
            self._queue_approval_notification(window, response_key, text)

            return True
        else:
            print(f"[ERROR] Approval failed: {result.error}")
            return False

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        self._print_startup_banner()

        # Show initial windows
        initial_windows = self.window_manager.find_target_windows()
        print(f"[OK] Found {len(initial_windows)} target windows:")
        for i, win in enumerate(initial_windows[:10], 1):
            print(f"  {i}. {win.safe_title[:50]} ({win.width}x{win.height})")
        if len(initial_windows) > 10:
            print(f"  ... and {len(initial_windows) - 10} more")
        print()

        last_status_time = time.time()

        while self._running:
            try:
                # Periodic status
                current_time = time.time()
                if current_time - last_status_time >= self.config.monitoring.status_interval:
                    print(f"[STATUS] Monitoring | Approvals: {self.approval_count} | Checks: {self._check_count}")
                    last_status_time = current_time

                # Scan windows
                windows = self.window_manager.find_target_windows()
                for window in windows:
                    try:
                        self._process_window(window)
                    except:
                        pass

                # Show pending notifications
                pending = self.notification_manager.get_pending_count()
                if pending > 0:
                    print(f"\n[INFO] Showing {pending} notification(s)...")
                    self.notification_manager.show_pending_notifications()

                # Sleep
                time.sleep(self.config.monitoring.scan_interval)

            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                time.sleep(3)

        print("\n[INFO] Monitoring stopped")

    def _print_startup_banner(self) -> None:
        """Print startup banner"""
        print("\n" + "=" * 60)
        print("OCR Auto Approver")
        print("=" * 60)
        print("\n=== ACTIVE OCR MONITORING ===")
        print("\nMode: Active OCR (All Windows)")
        print("  - Scans ALL visible windows with OCR")
        print("  - Detects approval dialogs automatically")
        print("  - Auto-responds when pattern detected")
        print("  - Excludes: Chrome, PowerPoint, HWP, System windows")
        print("\nPress Ctrl+C to stop\n")

    def _print_debug_info(self, text: str) -> None:
        """Print debug info for potential approval"""
        print(f"\n[DEBUG] Potential approval dialog detected!")
        print(f"[DEBUG] OCR Text Length: {len(text)}")
        print(f"[DEBUG] OCR Text (first 10 non-empty lines):")
        line_count = 0
        for line in text.split('\n'):
            if line.strip():
                safe_line = line.strip()[:80]
                try:
                    safe_line = safe_line.encode('ascii', 'ignore').decode('ascii')
                except:
                    pass
                print(f"  {safe_line}")
                line_count += 1
                if line_count >= 10:
                    break

    def _print_detection_info(self, window: WindowInfo, response_key: str, text: str) -> None:
        """Print detection info"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        print(f"\n{'=' * 70}")
        print(f"[{timestamp}] APPROVAL REQUEST DETECTED (Active Scan)")
        print(f"{'=' * 70}")
        print(f"Window Title: {window.safe_title[:60]}")
        print(f"Action: Sending '{response_key}'")
        print(f"\n=== Detected Text (first 15 lines) ===")

        line_count = 0
        for line in text.split('\n'):
            if line.strip():
                safe_line = line.strip()[:100]
                try:
                    safe_line = safe_line.encode('ascii', 'ignore').decode('ascii')
                except:
                    pass
                print(f"  {safe_line}")
                line_count += 1
                if line_count >= 15:
                    break
        print(f"{'=' * 70}\n")

    def _queue_approval_notification(self, window: WindowInfo, response_key: str, text: str) -> None:
        """Queue notification for approval"""
        window_type = NotificationManager.determine_window_type(window.title)
        text_preview = NotificationManager.create_text_preview(text)

        message = f"Window: {window.safe_title[:40]}"
        if text_preview:
            message += f" | {text_preview[:100]}"

        self.notification_manager.queue_notification(NotificationData(
            title="Auto Approval Complete",
            message=message,
            window_info=window.safe_title[:100],
            window_type=window_type,
            timestamp=time.strftime('%H:%M:%S'),
            response_key=response_key
        ))

    def list_windows(self) -> None:
        """List all target windows"""
        windows = self.window_manager.find_target_windows()
        print(f"\nFound {len(windows)} windows:")
        for i, win in enumerate(windows, 1):
            print(f"  {i}. [{win.hwnd}] {win.safe_title[:50]} (pos: {win.left},{win.top})")
