"""
Keyboard Executor Implementation (SRP: Single Responsibility)
Only handles sending keyboard inputs to windows
"""

import time
from typing import Optional

from ...interfaces import IApprovalExecutor
from ...interfaces.approval_executor import ExecutionResult

# Windows API imports
try:
    import win32gui
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class KeyboardExecutor(IApprovalExecutor):
    """
    Keyboard-based approval executor using Windows API
    Implements IApprovalExecutor interface (DIP)
    """

    def __init__(
        self,
        activation_delay: float = 0.3,
        key_delay: float = 0.05
    ):
        """
        Initialize keyboard executor

        Args:
            activation_delay: Delay after window activation (seconds)
            key_delay: Delay between key down and key up (seconds)
        """
        if not WIN32_AVAILABLE:
            raise RuntimeError("win32api is not available. This executor requires Windows.")

        self._activation_delay = activation_delay
        self._key_delay = key_delay

    def send_key(self, hwnd: int, key: str) -> ExecutionResult:
        """
        Send key input to specified window (assumes window is already active)

        Args:
            hwnd: Window handle (for verification)
            key: Key to send (e.g., '1', '2')

        Returns:
            ExecutionResult with success status
        """
        try:
            # Verify window still exists
            if not win32gui.IsWindow(hwnd):
                return ExecutionResult(
                    success=False,
                    key_sent=key,
                    error_message="Window no longer exists"
                )

            # Send key
            self._send_key_event(key)

            return ExecutionResult(success=True, key_sent=key)

        except Exception as e:
            return ExecutionResult(
                success=False,
                key_sent=key,
                error_message=str(e)
            )

    def activate_and_send(self, hwnd: int, key: str) -> ExecutionResult:
        """
        Activate window and send key input

        Args:
            hwnd: Window handle
            key: Key to send

        Returns:
            ExecutionResult with success status
        """
        try:
            # Verify window exists
            if not win32gui.IsWindow(hwnd):
                return ExecutionResult(
                    success=False,
                    key_sent=key,
                    error_message="Window no longer exists"
                )

            # Activate window
            if not self._activate_window(hwnd):
                return ExecutionResult(
                    success=False,
                    key_sent=key,
                    error_message="Failed to activate window"
                )

            # Wait for activation
            time.sleep(self._activation_delay)

            # Send key
            self._send_key_event(key)

            return ExecutionResult(success=True, key_sent=key)

        except Exception as e:
            return ExecutionResult(
                success=False,
                key_sent=key,
                error_message=str(e)
            )

    def _activate_window(self, hwnd: int) -> bool:
        """
        Activate a window (bring to foreground)

        Args:
            hwnd: Window handle

        Returns:
            True if activation successful
        """
        try:
            # Try direct SetForegroundWindow
            try:
                win32gui.SetForegroundWindow(hwnd)
                return True
            except Exception:
                pass

            # Alternative: simulate Alt key to allow SetForegroundWindow
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32gui.SetForegroundWindow(hwnd)

            return True

        except Exception:
            return False

    def _send_key_event(self, key: str) -> None:
        """
        Send a single key event

        Args:
            key: Key character to send
        """
        # Get key code
        key_code = ord(key.upper()) if len(key) == 1 else self._get_special_key(key)

        # Key down
        win32api.keybd_event(key_code, 0, 0, 0)
        time.sleep(self._key_delay)

        # Key up
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

    def _get_special_key(self, key_name: str) -> int:
        """
        Get key code for special keys

        Args:
            key_name: Name of special key (e.g., 'enter', 'tab')

        Returns:
            Windows virtual key code
        """
        special_keys = {
            'enter': win32con.VK_RETURN,
            'return': win32con.VK_RETURN,
            'tab': win32con.VK_TAB,
            'escape': win32con.VK_ESCAPE,
            'esc': win32con.VK_ESCAPE,
            'space': win32con.VK_SPACE,
            'up': win32con.VK_UP,
            'down': win32con.VK_DOWN,
            'left': win32con.VK_LEFT,
            'right': win32con.VK_RIGHT,
        }
        return special_keys.get(key_name.lower(), ord(key_name[0].upper()))
