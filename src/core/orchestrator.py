"""
Approval Orchestrator (SRP: Single Responsibility)
Coordinates all services to detect and approve dialogs
Only handles orchestration logic - does not implement any service functionality
"""

import time
import threading
from typing import Optional, Dict
from datetime import datetime

from .interfaces import (
    IWindowService,
    IOCRService,
    IPatternDetector,
    IApprovalExecutor,
    INotificationService,
    ITrayService,
    WindowInfo,
    NotificationData,
)


class ApprovalOrchestrator:
    """
    Main orchestrator that coordinates all services
    All dependencies are injected through constructor (DIP)
    """

    def __init__(
        self,
        window_service: IWindowService,
        ocr_service: IOCRService,
        pattern_detector: IPatternDetector,
        approval_executor: IApprovalExecutor,
        notification_service: INotificationService,
        tray_service: Optional[ITrayService] = None,
        scan_interval: float = 10.0,
        cooldown_seconds: float = 20.0
    ):
        """
        Initialize orchestrator with all required services

        Args:
            window_service: Service for window operations (DIP: interface dependency)
            ocr_service: Service for OCR operations (DIP: interface dependency)
            pattern_detector: Service for pattern detection (DIP: interface dependency)
            approval_executor: Service for approval execution (DIP: interface dependency)
            notification_service: Service for notifications (DIP: interface dependency)
            tray_service: Optional tray service (DIP: interface dependency)
            scan_interval: Seconds between scans
            cooldown_seconds: Seconds before re-approving same window
        """
        # Injected dependencies (DIP: all are interfaces)
        self._window_service = window_service
        self._ocr_service = ocr_service
        self._pattern_detector = pattern_detector
        self._approval_executor = approval_executor
        self._notification_service = notification_service
        self._tray_service = tray_service

        # Configuration
        self._scan_interval = scan_interval
        self._cooldown_seconds = cooldown_seconds

        # State
        self._running = False
        self._paused = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._approval_count = 0
        self._approved_windows: Dict[int, float] = {}  # hwnd -> last_approval_timestamp
        self._pending_notifications = []

        # Setup tray callbacks if available
        if self._tray_service:
            self._tray_service.set_pause_callback(self._on_pause)
            self._tray_service.set_resume_callback(self._on_resume)
            self._tray_service.set_exit_callback(self._on_exit)

    def start(self) -> None:
        """Start the monitoring process"""
        if self._running:
            print("[WARNING] Already running")
            return

        self._running = True

        # Start tray icon if available
        if self._tray_service and self._tray_service.is_available():
            self._tray_service.start()

        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        print("[OK] Orchestrator started")

    def stop(self) -> None:
        """Stop the monitoring process"""
        self._running = False

        if self._monitor_thread:
            self._monitor_thread.join(timeout=3)

        if self._tray_service:
            self._tray_service.stop()

        print("[INFO] Orchestrator stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        self._print_startup_info()

        last_status_time = time.time()
        check_count = 0

        while self._running:
            try:
                # Check if paused
                if self._paused:
                    time.sleep(1)
                    continue

                # Periodic status update
                current_time = time.time()
                if current_time - last_status_time >= 30:
                    print(f"[STATUS] Active monitoring | Approvals: {self._approval_count} | Checks: {check_count}")
                    last_status_time = current_time
                    self._update_tray_status()

                # Get all target windows
                windows = self._window_service.find_visible_windows()

                # Process each window
                for window in windows:
                    check_count += 1
                    self._process_window(window)

                # Show pending notifications
                self._show_pending_notifications()

                # Wait for next scan
                time.sleep(self._scan_interval)

            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                time.sleep(3)

        print("[INFO] Monitoring stopped")

    def _process_window(self, window: WindowInfo) -> None:
        """
        Process a single window for approval detection

        Args:
            window: WindowInfo object to process
        """
        try:
            # Check cooldown
            if not self._should_approve(window.hwnd):
                return

            # Capture window
            image = self._window_service.capture_window(window.hwnd)
            if image is None:
                return

            # Extract text via OCR
            text = self._ocr_service.extract_text(image, fast_mode=True)
            if not text:
                return

            # Debug: potential approval dialog
            if self._has_approval_keywords(text):
                self._print_potential_dialog(window, text)

            # Detect approval pattern
            result = self._pattern_detector.detect(text)
            if not result.is_approval:
                return

            # Log detection
            self._print_detection(window, result, text)

            # Execute approval
            exec_result = self._approval_executor.activate_and_send(
                window.hwnd,
                result.recommended_key
            )

            if exec_result.success:
                self._approval_count += 1
                self._approved_windows[window.hwnd] = time.time()
                self._update_tray_status()

                # Queue notification
                self._queue_notification(window, result.recommended_key, text)

                print(f"[SUCCESS] Approval completed - option '{result.recommended_key}' selected")
                print(f"[INFO] Total approvals: {self._approval_count}")
            else:
                print(f"[ERROR] Approval failed: {exec_result.error_message}")

        except Exception as e:
            pass  # Silent fail for individual windows

    def _should_approve(self, hwnd: int) -> bool:
        """
        Check if window should be approved (cooldown check)

        Args:
            hwnd: Window handle

        Returns:
            True if window can be approved
        """
        if hwnd not in self._approved_windows:
            return True

        time_since = time.time() - self._approved_windows[hwnd]
        return time_since >= self._cooldown_seconds

    def _has_approval_keywords(self, text: str) -> bool:
        """Check if text has potential approval keywords"""
        text_lower = text.lower()
        keywords = ['do you want', 'would you', 'proceed', 'select', 'choose']
        return any(kw in text_lower for kw in keywords)

    def _queue_notification(self, window: WindowInfo, key: str, text: str) -> None:
        """Queue a notification for later display"""
        # Prepare text preview
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text_preview = '\n'.join(lines[:8])
        if len(text_preview) > 400:
            text_preview = text_preview[:400] + '...'

        safe_title = window.title[:60]

        self._pending_notifications.append(NotificationData(
            title="Auto Approval Complete",
            message=f"Window: {safe_title}\n{text_preview}" if text_preview else f"Window: {safe_title}",
            window_info=safe_title,
            response_key=key
        ))

    def _show_pending_notifications(self) -> None:
        """Show all pending notifications"""
        if not self._pending_notifications:
            return

        print(f"\n[INFO] Showing {len(self._pending_notifications)} queued notification(s)...")

        for notification in self._pending_notifications:
            try:
                self._notification_service.show(notification)
                print(f"[SUCCESS] Notification shown for: {notification.window_info}")
            except Exception as e:
                print(f"[WARNING] Failed to show notification: {e}")

        self._pending_notifications.clear()

    def _update_tray_status(self) -> None:
        """Update tray icon status"""
        if self._tray_service:
            self._tray_service.update_approval_count(self._approval_count)

    def _on_pause(self) -> None:
        """Handle pause callback from tray"""
        self._paused = True

    def _on_resume(self) -> None:
        """Handle resume callback from tray"""
        self._paused = False

    def _on_exit(self) -> None:
        """Handle exit callback from tray"""
        self._running = False

    def _print_startup_info(self) -> None:
        """Print startup information"""
        print("\n" + "=" * 60)
        print("OCR Auto Approver (SOLID Architecture)")
        print("=" * 60)
        print("\n=== ACTIVE OCR MONITORING ===")
        print("\nMode: Active OCR (All Windows)")
        print("  - Scans ALL visible windows with OCR")
        print("  - Detects approval dialogs automatically")
        print("  - Auto-responds when pattern detected")
        print("\nPress Ctrl+C to stop\n")

        # Show initial windows
        windows = self._window_service.find_visible_windows()
        print(f"[OK] Found {len(windows)} target windows:")
        for i, win in enumerate(windows[:10], 1):
            safe_title = win.title[:50]
            print(f"  {i}. {safe_title} ({win.width}x{win.height})")
        if len(windows) > 10:
            print(f"  ... and {len(windows) - 10} more")
        print()

    def _print_potential_dialog(self, window: WindowInfo, text: str) -> None:
        """Print debug info for potential dialog"""
        print(f"\n[DEBUG] Potential approval dialog detected!")
        print(f"[DEBUG] OCR Text Length: {len(text)}")
        print(f"[DEBUG] OCR Text (first 10 non-empty lines):")
        line_count = 0
        for line in text.split('\n'):
            if line.strip():
                print(f"  {line.strip()[:80]}")
                line_count += 1
                if line_count >= 10:
                    break

    def _print_detection(self, window: WindowInfo, result, text: str) -> None:
        """Print detection information"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        safe_title = window.title[:60]

        print(f"\n{'=' * 70}")
        print(f"[{timestamp}] APPROVAL REQUEST DETECTED")
        print(f"{'=' * 70}")
        print(f"Window Title: {safe_title}")
        print(f"Pattern: {result.matched_pattern}")
        print(f"Action: Sending '{result.recommended_key}'")
        print(f"\n=== Detected Text (first 15 lines) ===")

        line_count = 0
        for line in text.split('\n'):
            if line.strip():
                print(f"  {line.strip()[:100]}")
                line_count += 1
                if line_count >= 15:
                    break

        print(f"{'=' * 70}\n")

    @property
    def approval_count(self) -> int:
        """Get total approval count"""
        return self._approval_count

    @property
    def is_running(self) -> bool:
        """Check if orchestrator is running"""
        return self._running

    @property
    def is_paused(self) -> bool:
        """Check if orchestrator is paused"""
        return self._paused
