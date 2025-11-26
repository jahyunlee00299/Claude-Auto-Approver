"""
Window Service Interface (ISP: Interface Segregation Principle)
Defines contract for window management operations only
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple
from PIL import Image


@dataclass
class WindowInfo:
    """Window information data transfer object"""
    hwnd: int
    title: str
    class_name: str
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)

    @property
    def width(self) -> int:
        return self.rect[2] - self.rect[0]

    @property
    def height(self) -> int:
        return self.rect[3] - self.rect[1]

    def __repr__(self) -> str:
        safe_title = self.title[:40] if self.title else "Unknown"
        return f"WindowInfo(hwnd={self.hwnd}, title='{safe_title}', size={self.width}x{self.height})"


class IWindowService(ABC):
    """
    Window Service Interface (SRP: Single Responsibility)
    Only handles window enumeration, filtering, and capture
    """

    @abstractmethod
    def find_visible_windows(self) -> List[WindowInfo]:
        """
        Find all visible windows that match filtering criteria

        Returns:
            List of WindowInfo objects for visible windows
        """
        pass

    @abstractmethod
    def activate_window(self, hwnd: int) -> bool:
        """
        Bring window to foreground and activate it

        Args:
            hwnd: Window handle

        Returns:
            True if activation successful, False otherwise
        """
        pass

    @abstractmethod
    def capture_window(self, hwnd: int) -> Optional[Image.Image]:
        """
        Capture screenshot of specified window

        Args:
            hwnd: Window handle

        Returns:
            PIL Image object or None if capture failed
        """
        pass

    @abstractmethod
    def is_window_valid(self, hwnd: int) -> bool:
        """
        Check if window handle is still valid

        Args:
            hwnd: Window handle

        Returns:
            True if window exists and is valid
        """
        pass
