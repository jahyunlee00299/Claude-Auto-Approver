"""
Notification Service Interface (OCP: Open/Closed Principle)
Defines contract for notification delivery
New notification methods can be added without modifying existing code
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class NotificationData:
    """Notification data transfer object"""
    title: str
    message: str
    window_info: Optional[str] = None
    icon_path: Optional[str] = None
    timestamp: datetime = None
    response_key: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def __repr__(self) -> str:
        return f"NotificationData(title='{self.title[:30]}', timestamp={self.timestamp.strftime('%H:%M:%S')})"


class INotificationService(ABC):
    """
    Notification Service Interface (SRP: Single Responsibility)
    Only handles notification display
    """

    @abstractmethod
    def show(self, notification: NotificationData) -> bool:
        """
        Display a notification to the user

        Args:
            notification: NotificationData object with notification details

        Returns:
            True if notification was displayed successfully
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if notification service is available

        Returns:
            True if notifications can be displayed
        """
        pass
