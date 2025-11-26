"""
Win32 Window Service Implementation (SRP: Single Responsibility)
Handles window enumeration, activation, and capture using Windows API
"""

import time
from typing import List, Optional
from PIL import Image

from ...interfaces import IWindowService, WindowInfo
from .window_filter import WindowFilter

# Windows API imports - lazy loaded for cross-platform compatibility
try:
    import win32gui
    import win32ui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class Win32WindowService(IWindowService):
    """
    Windows API based window service implementation
    Implements IWindowService interface (DIP: depends on abstraction)
    """

    def __init__(self, window_filter: Optional[WindowFilter] = None):
        """
        Initialize Win32 Window Service

        Args:
            window_filter: WindowFilter instance for filtering logic (DIP: dependency injection)
        """
        if not WIN32_AVAILABLE:
            raise RuntimeError("win32gui is not available. This service requires Windows.")

        self._filter = window_filter or WindowFilter()
        self._current_hwnd: Optional[int] = None

        # Try to get current console window
        try:
            import win32console
            self._current_hwnd = win32console.GetConsoleWindow()
        except Exception:
            pass

    def find_visible_windows(self) -> List[WindowInfo]:
        """
        Find all visible windows that pass filtering criteria

        Returns:
            List of WindowInfo for visible, non-excluded windows
        """
        windows: List[WindowInfo] = []

        def enum_callback(hwnd, result_list):
            try:
                # Check if window is visible or minimized (can restore)
                if not (win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd)):
                    return True

                title = win32gui.GetWindowText(hwnd)
                if not title:
                    return True

                # Get window class name
                try:
                    class_name = win32gui.GetClassName(hwnd)
                except Exception:
                    class_name = "Unknown"

                # Apply filters
                if self._filter.should_exclude_by_class(class_name):
                    return True

                if self._filter.should_exclude_by_title(title):
                    return True

                # Check window style - exclude tool windows
                try:
                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    if style & win32con.WS_EX_TOOLWINDOW:
                        return True
                    if style & win32con.WS_EX_NOACTIVATE:
                        return True
                except Exception:
                    pass

                # Get window rect
                try:
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    width = right - left
                    height = bottom - top

                    if self._filter.should_exclude_by_position(left, top):
                        return True

                    if self._filter.should_exclude_by_size(width, height):
                        return True

                    result_list.append(WindowInfo(
                        hwnd=hwnd,
                        title=title,
                        class_name=class_name,
                        rect=(left, top, right, bottom)
                    ))

                except Exception:
                    pass

            except Exception:
                pass

            return True

        try:
            win32gui.EnumWindows(enum_callback, windows)
        except Exception:
            pass

        return windows

    def activate_window(self, hwnd: int) -> bool:
        """
        Bring window to foreground and activate it

        Args:
            hwnd: Window handle

        Returns:
            True if window was successfully activated
        """
        try:
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)

            # Show window
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            time.sleep(0.1)

            # Try to set foreground
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                # Alternative: simulate Alt key to allow SetForegroundWindow
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
                win32gui.SetForegroundWindow(hwnd)

            time.sleep(0.2)

            # Verify activation
            return win32gui.GetForegroundWindow() == hwnd

        except Exception:
            return False

    def capture_window(self, hwnd: int) -> Optional[Image.Image]:
        """
        Capture screenshot of specified window

        Args:
            hwnd: Window handle

        Returns:
            PIL Image object or None if capture failed
        """
        try:
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            if width < 100 or height < 100:
                return None

            # Create device contexts
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # Create bitmap
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)

            # Copy screen content
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

            # Convert to PIL Image
            bmp_info = bitmap.GetInfo()
            bmp_bits = bitmap.GetBitmapBits(True)
            image = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_bits, 'raw', 'BGRX', 0, 1
            )

            # Cleanup Windows resources
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            return image

        except Exception:
            return None

    def is_window_valid(self, hwnd: int) -> bool:
        """
        Check if window handle is still valid

        Args:
            hwnd: Window handle

        Returns:
            True if window exists
        """
        try:
            return win32gui.IsWindow(hwnd)
        except Exception:
            return False

    def get_current_hwnd(self) -> Optional[int]:
        """Get the console window handle"""
        return self._current_hwnd

    def return_to_current_window(self) -> bool:
        """Return focus to the original console window"""
        if self._current_hwnd:
            try:
                win32gui.SetForegroundWindow(self._current_hwnd)
                return True
            except Exception:
                pass
        return False
