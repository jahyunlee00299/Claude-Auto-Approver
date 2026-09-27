"""
Auto Approver Core Module
Handles automatic approval of prompts and dialogs
"""

import time
import logging
import threading
import pyautogui
import win32gui
import win32con
from typing import List, Dict, Any, Optional, Tuple


class AutoApprover:
    """Main class for automatic approval functionality"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AutoApprover

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.monitor_thread = None
        self.patterns = config.get('patterns', [])
        self.delay = config.get('delay_seconds', 1)
        self.safe_mode = config.get('safe_mode', True)

        # Approval dialog detection patterns - only detects real approval windows like AskUserQuestion
        self.window_patterns = config.get('window_patterns', [
            'Question', '질문', 'Approval', '승인', 'Permission', '허용',
            'Allow', 'Authorize', 'Grant', 'Accept'
        ])

        # Window patterns to exclude (regular editor or app windows)
        self.exclude_patterns = config.get('exclude_patterns', [
            'Visual Studio', 'PyCharm', 'Code', 'Notepad', 'Chrome',
            'Firefox', 'Explorer', 'README', 'md', 'txt', 'py'
        ])

        # Button text patterns
        self.button_patterns = config.get('button_patterns', [
            'OK', '확인', 'Yes', '예', 'Allow', '허용',
            'Continue', '계속', 'Approve', '승인', 'Accept', '동의'
        ])

        self.approval_count = 0

        # PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

        self.logger.info("AutoApprover initialized")

    def start(self):
        """Start the auto approval monitoring"""
        if self.running:
            self.logger.warning("AutoApprover is already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.logger.info("AutoApprover started")

    def stop(self):
        """Stop the auto approval monitoring"""
        if not self.running:
            self.logger.warning("AutoApprover is not running")
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.logger.info("AutoApprover stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        self.logger.debug("Monitor loop started")

        while self.running:
            try:
                # Check for approval prompts
                if self._check_for_prompts():
                    self._handle_approval()

                # Sleep for a short interval
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}", exc_info=True)

        self.logger.debug("Monitor loop ended")

    def _check_for_prompts(self) -> bool:
        """
        Check if there are any approval prompts

        Returns:
            True if prompt found, False otherwise
        """
        # Find the approval dialog
        window_info = self._find_approval_window()
        if window_info:
            self.current_window = window_info
            return True
        return False

    def _find_approval_window(self) -> Optional[Dict]:
        """Find an approval dialog"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    # Check exclude patterns
                    for exclude in self.exclude_patterns:
                        if exclude.lower() in window_text.lower():
                            return True

                    # Check approval window patterns
                    for pattern in self.window_patterns:
                        if pattern.lower() in window_text.lower():
                            try:
                                rect = win32gui.GetWindowRect(hwnd)
                                windows.append({
                                    'hwnd': hwnd,
                                    'title': window_text,
                                    'rect': rect
                                })
                            except Exception as e:
                                self.logger.debug(f"Error getting window rect: {e}")
            return True

        windows = []
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
        except Exception as e:
            self.logger.error(f"Error enumerating windows: {e}")

        return windows[0] if windows else None

    def _handle_approval(self):
        """Handle the approval action"""
        if not hasattr(self, 'current_window') or not self.current_window:
            return

        hwnd = self.current_window['hwnd']
        title = self.current_window['title']

        print(f"\n📋 승인 대화상자 감지: '{title}'")
        self.logger.info(f"Detected approval window: '{title}'")

        if self.safe_mode:
            print(f"   🔒 안전 모드: 실제 클릭하지 않음")
            self.logger.info("Safe mode: Would approve prompt")
            return

        try:
            # Bring the window to the foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(self.delay)

            # Wrap in try-except to guard against a fail-safe error
            try:
                # Try pressing Enter to click the default button
                pyautogui.press('enter')
                self.approval_count += 1
                print(f"   ✅ 자동 승인 완료 (Enter 키 사용)")
                self.logger.info(f"Auto-approved window: '{title}'")

            except pyautogui.FailSafeException:
                # If the fail-safe triggers, send Enter using win32api instead
                import win32api
                import win32con
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                self.approval_count += 1
                print(f"   ✅ 자동 승인 완료 (win32api 사용)")
                self.logger.info(f"Auto-approved window using win32api: '{title}'")

        except Exception as e:
            self.logger.error(f"Error handling approval: {e}")
            print(f"   ❌ 자동 승인 실패: {e}")

    def detect_pattern(self, text: str) -> bool:
        """
        Check if text matches any configured patterns

        Args:
            text: Text to check

        Returns:
            True if pattern matched, False otherwise
        """
        text_lower = text.lower()
        for pattern in self.patterns:
            if pattern.lower() in text_lower:
                self.logger.debug(f"Pattern matched: {pattern}")
                return True
        return False

    def add_pattern(self, pattern: str):
        """
        Add a new pattern to detect

        Args:
            pattern: Pattern string to add
        """
        if pattern not in self.patterns:
            self.patterns.append(pattern)
            self.logger.info(f"Added pattern: {pattern}")

    def remove_pattern(self, pattern: str):
        """
        Remove a pattern from detection

        Args:
            pattern: Pattern string to remove
        """
        if pattern in self.patterns:
            self.patterns.remove(pattern)
            self.logger.info(f"Removed pattern: {pattern}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the approver

        Returns:
            Dictionary with status information
        """
        return {
            'running': self.running,
            'safe_mode': self.safe_mode,
            'delay_seconds': self.delay,
            'pattern_count': len(self.patterns),
            'approval_count': self.approval_count
        }