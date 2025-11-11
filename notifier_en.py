#!/usr/bin/env python3
"""Simple approval notifier - English only version"""
import time
import win32console
import winsound
from winotify import Notification, audio

class ApprovalNotifier:
    def __init__(self):
        self.running = False
        self.last_pattern = ""
        self.last_notification_time = 0
        self.notification_interval = 15  # notify once every 15 seconds

        # Approval patterns
        self.patterns = [
            'Do you want to proceed?',
            '1. Yes',
            '2. Yes, and don\'t ask again',
        ]

        print("[OK] Simple Notifier initialized")

    def read_console(self):
        """Read current console screen"""
        try:
            handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
            csbi = handle.GetConsoleScreenBufferInfo()
            cursor_pos = csbi['CursorPosition']

            # Read last 20 lines
            lines_to_read = min(20, cursor_pos.Y + 1)
            start_y = max(0, cursor_pos.Y - lines_to_read + 1)

            buffer_text = []
            for y in range(start_y, cursor_pos.Y + 1):
                try:
                    coord = win32console.PyCOORDType(0, y)
                    size = csbi['Size'].X
                    text = handle.ReadConsoleOutputCharacter(size, coord)
                    buffer_text.append(text.strip())
                except:
                    pass

            return '\n'.join(buffer_text)
        except:
            return ""

    def check_pattern(self, text):
        """Check if text contains approval pattern"""
        if not text:
            return False
        text_lower = text.lower()
        for pattern in self.patterns:
            if pattern.lower() in text_lower:
                return True
        return False

    def should_notify(self, text):
        """Check if we should send notification"""
        current_time = time.time()

        # Same pattern: notify only once every 15 seconds
        if text == self.last_pattern:
            if current_time - self.last_notification_time < self.notification_interval:
                return False

        return True

    def notify(self, text):
        """Show notification"""
        if not self.should_notify(text):
            return

        try:
            toast = Notification(
                app_id="Claude Auto Approver",
                title="Approval Request",
                msg="Claude Code is waiting for approval in current terminal.",
                duration="long"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()

            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            # Record
            self.last_pattern = text
            self.last_notification_time = time.time()

            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] Notification sent")

        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")

    def run(self):
        """Main loop"""
        print("\n" + "="*60)
        print("Claude Approval Notifier")
        print("="*60)
        print("\nMonitoring current console...")
        print(f"Notification interval: {self.notification_interval} seconds")
        print("\nPress Ctrl+C to stop\n")

        self.running = True

        try:
            while self.running:
                # Read console
                text = self.read_console()

                # Check pattern
                if text and self.check_pattern(text):
                    self.notify(text)

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted")
        finally:
            self.running = False
            print("[INFO] Stopped")


if __name__ == "__main__":
    notifier = ApprovalNotifier()
    notifier.run()
