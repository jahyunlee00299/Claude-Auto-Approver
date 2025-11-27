"""
Window Filter (SRP: Single Responsibility)
Only handles window filtering logic - excluded keywords, system windows, etc.
"""

from typing import List, Set
from dataclasses import dataclass, field


@dataclass
class WindowFilter:
    """
    Window filtering configuration and logic
    Separates filtering concerns from window enumeration (SRP)
    """

    # Keywords to exclude from window titles
    exclude_keywords: List[str] = field(default_factory=lambda: [
        'auto approval complete',
        'chrome',
        'google chrome',
        'nvidia geforce',
        'program manager',
        'microsoft text input',
        'settings',
        '설정',
        'powerpoint',
        'ppt',
        'microsoft powerpoint',
        'hwp',
        '.hwp',
        'hancom',
        'hanword',
        '한글',
        '한컴',
        'excel',
        'microsoft excel',
        '.xlsx',
        '.xls',
    ])

    # System window class names to exclude
    system_classes: Set[str] = field(default_factory=lambda: {
        'Windows.UI.Core.CoreWindow',
        'Shell_TrayWnd',
        'NotifyIconOverflowWindow',
        'Windows.UI.Input.InputSite.WindowClass',
        'ApplicationFrameWindow',
        'Windows.Internal.Shell.TabProxyWindow',
        'ImmersiveLauncher',
        'MultitaskingViewFrame',
        'ForegroundStaging',
        'Dwm',
    })

    # Minimum window dimensions
    min_width: int = 100
    min_height: int = 20

    def should_exclude_by_title(self, title: str) -> bool:
        """
        Check if window should be excluded based on title

        Args:
            title: Window title

        Returns:
            True if window should be excluded
        """
        if not title:
            return True

        title_lower = title.lower()
        return any(kw in title_lower for kw in self.exclude_keywords)

    def should_exclude_by_class(self, class_name: str) -> bool:
        """
        Check if window should be excluded based on class name

        Args:
            class_name: Window class name

        Returns:
            True if window should be excluded
        """
        if not class_name:
            return False

        # Check exact match in system classes
        if class_name in self.system_classes:
            return True

        # Check partial matches for common system window patterns
        class_lower = class_name.lower()
        system_patterns = ['notification', 'toast', 'windows.ui', 'xaml', 'dwm']
        return any(pattern in class_lower for pattern in system_patterns)

    def should_exclude_by_size(self, width: int, height: int) -> bool:
        """
        Check if window should be excluded based on size

        Args:
            width: Window width
            height: Window height

        Returns:
            True if window is too small
        """
        return width < self.min_width or height < self.min_height

    def should_exclude_by_position(self, left: int, top: int) -> bool:
        """
        Check if window should be excluded based on position
        Hidden system windows are often at -32000, -32000

        Args:
            left: Window left position
            top: Window top position

        Returns:
            True if window appears to be hidden
        """
        return left == -32000 and top == -32000

    def add_exclude_keyword(self, keyword: str) -> None:
        """Add a keyword to exclude list"""
        if keyword.lower() not in [k.lower() for k in self.exclude_keywords]:
            self.exclude_keywords.append(keyword.lower())

    def remove_exclude_keyword(self, keyword: str) -> bool:
        """Remove a keyword from exclude list"""
        keyword_lower = keyword.lower()
        for i, k in enumerate(self.exclude_keywords):
            if k.lower() == keyword_lower:
                self.exclude_keywords.pop(i)
                return True
        return False
