"""
Notification Manager for displaying notifications
SOLID: Single Responsibility - Only handles notification display
"""
import os
import time
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class NotificationData:
    """Data for a notification"""
    title: str
    message: str
    window_info: Optional[str] = None
    window_type: Optional[str] = None
    timestamp: Optional[str] = None
    response_key: Optional[str] = None


class NotificationManager:
    """Manages notification display using winotify"""

    def __init__(self, icon_path: Optional[str] = None):
        self._icon_path = icon_path
        self._pending: List[NotificationData] = []

    @property
    def icon_path(self) -> Optional[str]:
        """Get notification icon path"""
        return self._icon_path

    @icon_path.setter
    def icon_path(self, path: str) -> None:
        """Set notification icon path"""
        if os.path.exists(path):
            self._icon_path = path
        else:
            print(f"[WARNING] Icon path does not exist: {path}")

    def queue_notification(self, data: NotificationData) -> None:
        """
        Add notification to pending queue

        Args:
            data: NotificationData to queue
        """
        self._pending.append(data)

    def get_pending_count(self) -> int:
        """Get number of pending notifications"""
        return len(self._pending)

    def show_notification(self, data: NotificationData) -> bool:
        """
        Show a single notification

        Args:
            data: NotificationData to display

        Returns:
            True if successful, False otherwise
        """
        try:
            from winotify import Notification, audio

            # Build message
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            if data.window_info:
                message = f"Window: {data.window_info}\nTime: {current_time}\n\n{data.message}"
            else:
                message = f"Time: {current_time}\n\n{data.message}"

            # Create notification
            toast = Notification(
                app_id="Claude Auto Approver",
                title=f"{data.title}",
                msg=message,
                duration="short"
            )

            # Add icon if available
            if self._icon_path and os.path.exists(self._icon_path):
                try:
                    toast.icon = self._icon_path
                except:
                    pass

            # Set sound
            toast.set_audio(audio.SMS, loop=False)

            # Show
            toast.show()
            time.sleep(0.5)

            return True

        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")
            return False

    def show_pending_notifications(self) -> int:
        """
        Show all pending notifications

        Returns:
            Number of notifications shown
        """
        if not self._pending:
            return 0

        shown = 0
        for data in self._pending:
            if self.show_notification(data):
                shown += 1
                print(f"[SUCCESS] Notification shown: {data.title}")

        # Clear queue
        self._pending.clear()

        return shown

    def clear_pending(self) -> None:
        """Clear all pending notifications"""
        self._pending.clear()

    @staticmethod
    def determine_window_type(title: str) -> str:
        """
        Determine window type from title

        Args:
            title: Window title

        Returns:
            Window type string
        """
        title_lower = title.lower()

        if 'powershell' in title_lower:
            return "PowerShell"
        elif 'cmd' in title_lower or 'command' in title_lower:
            return "CMD"
        elif 'bash' in title_lower or 'mingw' in title_lower:
            return "Bash/Git"
        elif 'python' in title_lower:
            return "Python"
        elif 'question' in title_lower:
            return "Dialog"
        elif ' - ' in title:
            return title.split(' - ')[-1][:20]
        else:
            return title[:20]

    @staticmethod
    def create_text_preview(text: str, max_lines: int = 8, max_chars: int = 400) -> str:
        """
        Create text preview for notification

        Args:
            text: Full text
            max_lines: Maximum number of lines
            max_chars: Maximum number of characters

        Returns:
            Truncated preview string
        """
        if not text:
            return ''

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        preview = '\n'.join(lines[:max_lines])

        if len(preview) > max_chars:
            preview = preview[:max_chars] + '...'

        return preview
