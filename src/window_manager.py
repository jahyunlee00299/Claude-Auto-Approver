"""
Window Manager for window operations
SOLID: Single Responsibility - Only handles window-related operations
"""
import time
from typing import List, Optional
from dataclasses import dataclass
from PIL import Image

import win32gui
import win32ui
import win32con
import win32api
import win32console

from .config import WindowFilters


@dataclass
class WindowInfo:
    """Information about a window"""
    hwnd: int
    title: str
    class_name: str
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    @property
    def safe_title(self) -> str:
        """ASCII-safe title for console output"""
        try:
            return self.title.encode('ascii', 'ignore').decode('ascii')
        except:
            return "Window with special characters"


class WindowManager:
    """Manages window operations: finding, filtering, capturing, activating"""

    def __init__(self, filters: WindowFilters):
        self.filters = filters
        self._current_hwnd: Optional[int] = None

        try:
            self._current_hwnd = win32console.GetConsoleWindow()
        except:
            pass

    @property
    def current_hwnd(self) -> Optional[int]:
        """Get current console window handle"""
        return self._current_hwnd

    def is_system_window(self, hwnd: int) -> bool:
        """Check if window is a system window"""
        try:
            class_name = win32gui.GetClassName(hwnd)

            # Check system window classes
            if class_name in self.filters.system_classes:
                return True

            # Additional checks for system-related windows
            class_lower = class_name.lower()
            system_keywords = ['notification', 'toast', 'windows.ui', 'xaml', 'dwm']
            if any(kw in class_lower for kw in system_keywords):
                return True

            # Check window styles
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if style & win32con.WS_EX_TOOLWINDOW:
                return True
            if style & win32con.WS_EX_NOACTIVATE:
                return True

            # Check for hidden system windows
            try:
                left, top, _, _ = win32gui.GetWindowRect(hwnd)
                if left == -32000 and top == -32000:
                    return True
            except:
                pass

            return False

        except:
            return False

    def is_excluded(self, title: str) -> bool:
        """Check if window title matches exclusion keywords"""
        title_lower = title.lower()
        return any(exc in title_lower for exc in self.filters.exclude_keywords)

    def find_target_windows(self, verbose: bool = False) -> List[WindowInfo]:
        """
        Find all visible windows that should be monitored

        Args:
            verbose: If True, print detailed debug information

        Returns:
            List of WindowInfo objects
        """
        windows: List[WindowInfo] = []

        def callback(hwnd, _):
            if not (win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd)):
                return True

            title = win32gui.GetWindowText(hwnd)
            if not title:
                return True

            # Filter system windows
            if self.is_system_window(hwnd):
                if verbose:
                    print(f"[FILTER] System window: {title[:40]}")
                return True

            # Filter excluded keywords
            if self.is_excluded(title):
                if verbose:
                    print(f"[FILTER] Excluded: {title[:40]}")
                return True

            # Check window size
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top

                if width < self.filters.min_width or height < self.filters.min_height:
                    if verbose:
                        print(f"[FILTER] Too small ({width}x{height}): {title[:40]}")
                    return True

                try:
                    class_name = win32gui.GetClassName(hwnd)
                except:
                    class_name = "Unknown"

                windows.append(WindowInfo(
                    hwnd=hwnd,
                    title=title,
                    class_name=class_name,
                    left=left,
                    top=top,
                    right=right,
                    bottom=bottom
                ))

                if verbose:
                    print(f"[TARGET] {title[:40]} ({width}x{height})")

            except:
                pass

            return True

        try:
            win32gui.EnumWindows(callback, None)
        except:
            pass

        return windows

    def activate_window(self, hwnd: int) -> bool:
        """
        Activate a window (bring to foreground)

        Args:
            hwnd: Window handle

        Returns:
            True if successful, False otherwise
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
            except:
                # Alternative: simulate Alt key
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
                win32gui.SetForegroundWindow(hwnd)

            time.sleep(0.2)

            # Verify
            return win32gui.GetForegroundWindow() == hwnd

        except Exception as e:
            print(f"[DEBUG] Failed to activate window: {e}")
            return False

    def capture_window(self, hwnd: int) -> Optional[Image.Image]:
        """
        Capture window screenshot

        Args:
            hwnd: Window handle

        Returns:
            PIL Image object or None on failure
        """
        try:
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

            # Copy screen
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

            # Convert to PIL Image
            bmp_info = bitmap.GetInfo()
            bmp_bits = bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_bits, 'raw', 'BGRX', 0, 1
            )

            # Cleanup
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            return img

        except:
            return None

    def return_to_current_window(self) -> None:
        """Return focus to the original console window"""
        if self._current_hwnd:
            time.sleep(0.2)
            try:
                win32gui.SetForegroundWindow(self._current_hwnd)
                time.sleep(0.3)
            except:
                pass
