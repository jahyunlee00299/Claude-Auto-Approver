"""
Configuration settings for Claude Auto Approver
SOLID: Single source of truth for all configuration values
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ApprovalPatterns:
    """Approval pattern configuration"""

    # Question patterns (asking for permission)
    question_patterns: List[str] = field(default_factory=lambda: [
        'do you want',
        'would you like',
        'would you',
    ])

    # Action patterns (what's being asked)
    action_patterns: List[str] = field(default_factory=lambda: [
        'to proceed',
        'proceed',
        'to approve',
        'approve',
        'to create',
        'create',
        'to allow',
        'allow',
        'select',
        'choose',
    ])

    # Specific patterns (exact matches)
    specific_patterns: List[str] = field(default_factory=lambda: [
        'select an option',
        'choose an option',
        "yes, and don't ask again",
        'yes, and remember',
        'yes, allow all edits',
        'approve this action',
        'allow this action',
        'grant permission',
        'proceed with',
        'continue with',
        'select one of the following',
        'choose one of the following',
        'no, and tell claude',
        'tell claude what to do differently',
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
