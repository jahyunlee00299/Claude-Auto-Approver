"""
Winotify Notification Service Implementation (SRP: Single Responsibility)
Only handles displaying Windows toast notifications
"""

import os
import time
from typing import Optional

from ...interfaces import INotificationService, NotificationData

# Winotify import
try:
    from winotify import Notification, audio
    WINOTIFY_AVAILABLE = True
except ImportError:
    WINOTIFY_AVAILABLE = False


class WinotifyNotificationService(INotificationService):
    """
    Windows toast notification service using winotify
    Implements INotificationService interface (DIP)
    """

    def __init__(
        self,
        app_name: str = "Claude Auto Approver",
        icon_path: Optional[str] = None,
        duration: str = "short"
    ):
        """
        Initialize notification service

        Args:
            app_name: Application name shown in notifications
            icon_path: Path to notification icon (optional)
            duration: Notification duration ("short" = 5s, "long" = 25s)
        """
        self._app_name = app_name
        self._icon_path = icon_path
        self._duration = duration

    def show(self, notification: NotificationData) -> bool:
        """
        Display a Windows toast notification

        Args:
            notification: NotificationData object with notification details

        Returns:
            True if notification was displayed successfully
        """
        if not WINOTIFY_AVAILABLE:
            print(f"[INFO] Notification (winotify not available): {notification.title}")
            return False

        try:
            # Build detailed message
            timestamp = notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')

            if notification.window_info:
                message = f"Window: {notification.window_info}\nTime: {timestamp}\n\n{notification.message}"
            else:
                message = f"Time: {timestamp}\n\n{notification.message}"

            # Create notification
            toast = Notification(
                app_id=self._app_name,
                title=notification.title,
                msg=message,
                duration=self._duration
            )

            # Set icon
            icon_path = notification.icon_path or self._icon_path
            if icon_path and os.path.exists(icon_path):
                try:
                    toast.icon = icon_path
                except Exception:
                    pass

            # Set sound
            toast.set_audio(audio.SMS, loop=False)

            # Show notification
            toast.show()

            # Give Windows time to process
            time.sleep(0.5)

            return True

        except Exception as e:
            print(f"[WARNING] Notification error: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if winotify is available

        Returns:
            True if notifications can be displayed
        """
        return WINOTIFY_AVAILABLE


class ConsoleNotificationService(INotificationService):
    """
    Fallback notification service that prints to console
    Useful for testing or when winotify is not available
    """

    def show(self, notification: NotificationData) -> bool:
        """
        Display notification as console output

        Args:
            notification: NotificationData object

        Returns:
            Always returns True
        """
        timestamp = notification.timestamp.strftime('%H:%M:%S')
        print(f"\n[NOTIFICATION] {timestamp}")
        print(f"  Title: {notification.title}")
        print(f"  Message: {notification.message}")
        if notification.window_info:
            print(f"  Window: {notification.window_info}")
        if notification.response_key:
            print(f"  Key: {notification.response_key}")
        print()
        return True

    def is_available(self) -> bool:
        """Console is always available"""
        return True
