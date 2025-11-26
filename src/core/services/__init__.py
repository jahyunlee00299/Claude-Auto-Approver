"""
Services module - Concrete implementations of interfaces
"""

from .window import Win32WindowService, WindowFilter
from .ocr import TesseractOCRService, ImagePreprocessor
from .detection import CompositePatternDetector
from .execution import KeyboardExecutor
from .notification import WinotifyNotificationService
from .tray import PystrayTrayService

__all__ = [
    'Win32WindowService', 'WindowFilter',
    'TesseractOCRService', 'ImagePreprocessor',
    'CompositePatternDetector',
    'KeyboardExecutor',
    'WinotifyNotificationService',
    'PystrayTrayService',
]
