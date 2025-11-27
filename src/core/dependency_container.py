"""
Dependency Container (DIP: Dependency Inversion Principle)
Creates and wires all dependencies together
Concrete implementations are only referenced here
"""

from typing import Optional

from .orchestrator import ApprovalOrchestrator
from .interfaces import TrayConfig

# Service implementations
from .services.window import Win32WindowService, WindowFilter
from .services.ocr import TesseractOCRService, ImagePreprocessor
from .services.detection import (
    CompositePatternDetector,
    QuestionPattern,
    ActionPattern,
    SpecificPattern,
    OptionPattern,
)
from .services.execution import KeyboardExecutor
from .services.notification import WinotifyNotificationService
from .services.tray import PystrayTrayService

# Config
from ..config import Settings


class DependencyContainer:
    """
    Dependency Injection Container
    Creates all services and wires them together

    This is the only place where concrete implementations are referenced
    All other code depends only on interfaces (DIP)
    """

    @staticmethod
    def create_orchestrator(
        settings: Optional[Settings] = None,
        use_tray: bool = True
    ) -> ApprovalOrchestrator:
        """
        Create fully configured ApprovalOrchestrator

        Args:
            settings: Settings instance or None for defaults
            use_tray: Whether to enable tray icon

        Returns:
            Configured ApprovalOrchestrator instance
        """
        # Load settings
        config = settings or Settings.load()

        # Create Window Service
        window_filter = WindowFilter(
            exclude_keywords=config.exclude_keywords,
            min_width=config.min_window_width,
            min_height=config.min_window_height
        )
        window_service = Win32WindowService(window_filter=window_filter)

        # Create OCR Service
        preprocessor = ImagePreprocessor()
        ocr_service = TesseractOCRService(
            tesseract_path=config.tesseract_path,
            preprocessor=preprocessor,
            language=config.ocr_language
        )

        # Create Pattern Detector
        patterns = [
            QuestionPattern(keywords=config.question_patterns),
            ActionPattern(keywords=config.action_patterns),
            SpecificPattern(keywords=config.specific_patterns),
            OptionPattern(),
        ]
        pattern_detector = CompositePatternDetector(patterns=patterns)

        # Create Executor
        approval_executor = KeyboardExecutor(
            activation_delay=config.activation_delay,
            key_delay=config.key_delay
        )

        # Create Notification Service
        notification_service = WinotifyNotificationService(
            app_name=config.app_name,
            icon_path=config.icon_path
        )

        # Create Tray Service (optional)
        tray_service = None
        if use_tray:
            tray_config = TrayConfig(
                app_name=config.app_name,
                icon_path=config.icon_path,
                tooltip=config.app_name
            )
            tray_service = PystrayTrayService(config=tray_config)

        # Create and return Orchestrator
        return ApprovalOrchestrator(
            window_service=window_service,
            ocr_service=ocr_service,
            pattern_detector=pattern_detector,
            approval_executor=approval_executor,
            notification_service=notification_service,
            tray_service=tray_service,
            scan_interval=config.scan_interval,
            cooldown_seconds=config.cooldown_seconds
        )

    @staticmethod
    def create_minimal_orchestrator() -> ApprovalOrchestrator:
        """
        Create minimal orchestrator without tray (for testing)

        Returns:
            ApprovalOrchestrator with minimal configuration
        """
        return DependencyContainer.create_orchestrator(use_tray=False)
