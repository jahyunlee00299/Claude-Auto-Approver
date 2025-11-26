"""
System Tray Service Interface (ISP: Interface Segregation Principle)
Defines contract for system tray icon management
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class TrayConfig:
    """Tray icon configuration"""
    app_name: str = "Claude Auto Approver"
    icon_path: Optional[str] = None
    tooltip: str = "Claude Auto Approver"


class ITrayService(ABC):
    """
    System Tray Service Interface (SRP: Single Responsibility)
    Only handles system tray icon management
    """

    @abstractmethod
    def start(self) -> bool:
        """
        Start the tray icon

        Returns:
            True if tray icon started successfully
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop and remove the tray icon"""
        pass

    @abstractmethod
    def update_tooltip(self, text: str) -> None:
        """
        Update tray icon tooltip text

        Args:
            text: New tooltip text
        """
        pass

    @abstractmethod
    def set_pause_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for pause action"""
        pass

    @abstractmethod
    def set_resume_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for resume action"""
        pass

    @abstractmethod
    def set_exit_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for exit action"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if tray service is available

        Returns:
            True if system tray is supported
        """
        pass
