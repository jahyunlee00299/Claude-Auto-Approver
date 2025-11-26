"""
Interfaces module - Abstract base classes for dependency inversion
All components depend on these abstractions, not concrete implementations
"""

from .window_service import IWindowService, WindowInfo
from .ocr_service import IOCRService
from .pattern_detector import IPatternDetector, IPattern, DetectionResult
from .approval_executor import IApprovalExecutor
from .notification_service import INotificationService, NotificationData
from .tray_service import ITrayService, TrayConfig

__all__ = [
    'IWindowService', 'WindowInfo',
    'IOCRService',
    'IPatternDetector', 'IPattern', 'DetectionResult',
    'IApprovalExecutor',
    'INotificationService', 'NotificationData',
    'ITrayService', 'TrayConfig',
]
