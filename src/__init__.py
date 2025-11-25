"""
Claude Auto Approver - SOLID Architecture
"""
from .config import Config, ApprovalPatterns, WindowFilters, MonitoringSettings, OCRSettings
from .pattern_matcher import PatternMatcher, MatchResult
from .window_manager import WindowManager, WindowInfo
from .ocr_engine import OCREngine
from .approval_sender import ApprovalSender, ApprovalResult
from .notification_manager import NotificationManager, NotificationData
from .approver import Approver

__all__ = [
    # Config
    'Config',
    'ApprovalPatterns',
    'WindowFilters',
    'MonitoringSettings',
    'OCRSettings',
    # Pattern Matcher
    'PatternMatcher',
    'MatchResult',
    # Window Manager
    'WindowManager',
    'WindowInfo',
    # OCR Engine
    'OCREngine',
    # Approval Sender
    'ApprovalSender',
    'ApprovalResult',
    # Notification Manager
    'NotificationManager',
    'NotificationData',
    # Main Orchestrator
    'Approver',
]
