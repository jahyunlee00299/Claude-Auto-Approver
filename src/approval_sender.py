"""
Approval Sender for key input handling
SOLID: Single Responsibility - Only handles sending approval keys and cooldown management
"""
import time
from typing import Dict, Optional
from dataclasses import dataclass

import win32api
import win32con
import win32gui

from .config import MonitoringSettings


@dataclass
class ApprovalResult:
    """Result of sending approval"""
    success: bool
    response_key: str
    timestamp: str
    error: Optional[str] = None


class ApprovalSender:
    """Handles sending approval keys to windows and managing cooldowns"""

    def __init__(self, settings: MonitoringSettings):
        self.settings = settings
        self.approval_count: int = 0
        self._approved_windows: Dict[int, float] = {}  # hwnd -> timestamp

    @property
    def total_approvals(self) -> int:
        """Get total number of approvals sent"""
        return self.approval_count

    def should_approve(self, hwnd: int) -> bool:
        """
        Check if window should be approved (cooldown check)

        Args:
            hwnd: Window handle

        Returns:
            True if approval is allowed, False if in cooldown
        """
        if hwnd not in self._approved_windows:
            return True

        last_approval_time = self._approved_windows[hwnd]
        time_since_approval = time.time() - last_approval_time

        return time_since_approval >= self.settings.re_approval_cooldown

    def get_cooldown_remaining(self, hwnd: int) -> int:
        """
        Get remaining cooldown time for a window

        Args:
            hwnd: Window handle

        Returns:
            Remaining seconds, or 0 if not in cooldown
        """
        if hwnd not in self._approved_windows:
            return 0

        last_approval_time = self._approved_windows[hwnd]
        time_since_approval = time.time() - last_approval_time
        remaining = self.settings.re_approval_cooldown - time_since_approval

        return max(0, int(remaining))

    def send_approval(self, hwnd: int, response_key: str) -> ApprovalResult:
        """
        Send approval key to window

        Args:
            hwnd: Window handle
            response_key: Key to send ('1' or '2')

        Returns:
            ApprovalResult with success status
        """
        timestamp = time.strftime('%H:%M:%S')

        try:
            # Activate window
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

            time.sleep(0.3)

            # Send key
            key_code = ord(response_key)
            win32api.keybd_event(key_code, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

            # Update tracking
            self.approval_count += 1
            self._approved_windows[hwnd] = time.time()

            return ApprovalResult(
                success=True,
                response_key=response_key,
                timestamp=timestamp
            )

        except Exception as e:
            return ApprovalResult(
                success=False,
                response_key=response_key,
                timestamp=timestamp,
                error=str(e)
            )

    def clear_cooldown(self, hwnd: int) -> None:
        """
        Clear cooldown for a specific window

        Args:
            hwnd: Window handle
        """
        if hwnd in self._approved_windows:
            del self._approved_windows[hwnd]

    def clear_all_cooldowns(self) -> None:
        """Clear all cooldowns"""
        self._approved_windows.clear()

    def get_approved_windows(self) -> Dict[int, float]:
        """Get dictionary of approved windows and their timestamps"""
        return self._approved_windows.copy()
