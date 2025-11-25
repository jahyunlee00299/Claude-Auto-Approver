"""
Configuration settings for Claude Auto Approver
SOLID: Single source of truth for all configuration values
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ApprovalPatterns:
    """Approval pattern configuration - Strict Claude Code detection"""

    # Required question pattern
    question_pattern: str = 'do you want to proceed'

    # Required option patterns (option number + "yes")
    option_1_pattern: str = '1. yes'
    option_2_pattern: str = '2. yes'

    # Optional: detect 3-option dialog
    option_3_pattern: str = '3. no'

    # Alternative patterns for OCR errors
    option_1_alternatives: List[str] = field(default_factory=lambda: [
        '1. yes',
        '1) yes',
        '1.yes',
        '> 1. yes',
        '1, yes',
    ])

    option_2_alternatives: List[str] = field(default_factory=lambda: [
        '2. yes',
        '2) yes',
        '2.yes',
        '2, yes',
    ])

    option_3_alternatives: List[str] = field(default_factory=lambda: [
        '3. no',
        '3) no',
        '3.no',
        '3, no',
    ])


@dataclass
class WindowFilters:
    """Window filtering configuration"""

    # Keywords to exclude from monitoring
    exclude_keywords: List[str] = field(default_factory=lambda: [
        'auto approval complete',
        'chrome',
        'google chrome',
        'nvidia geforce',
        'program manager',
        'microsoft text input',
        'settings',
        'powerpoint',
        'ppt',
        'microsoft powerpoint',
        'hwp',
        '.hwp',
        'hancom',
        'hanword',
        'excel',
        'microsoft excel',
        '.xlsx',
        '.xls',
    ])

    # System window class names to exclude
    system_classes: List[str] = field(default_factory=lambda: [
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
    ])

    # Minimum window dimensions
    min_width: int = 100
    min_height: int = 20


@dataclass
class MonitoringSettings:
    """Monitoring behavior configuration"""

    # Cooldown before same window can be approved again (seconds)
    re_approval_cooldown: int = 20

    # Scan interval (seconds)
    scan_interval: int = 10

    # Status update interval (seconds)
    status_interval: int = 30


@dataclass
class OCRSettings:
    """OCR configuration"""

    # Tesseract executable path
    tesseract_path: str = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # OCR language
    language: str = 'eng'

    # Minimum image width for scaling
    min_scale_width: int = 1200

    # Contrast enhancement factor
    contrast_factor: float = 2.0


@dataclass
class Config:
    """Main configuration container"""

    patterns: ApprovalPatterns = field(default_factory=ApprovalPatterns)
    filters: WindowFilters = field(default_factory=WindowFilters)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    ocr: OCRSettings = field(default_factory=OCRSettings)

    @classmethod
    def default(cls) -> 'Config':
        """Create default configuration"""
        return cls()
