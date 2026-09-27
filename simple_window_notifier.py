#!/usr/bin/env python3
"""
Simple Window Notifier - works without Tesseract
Shows a notification when the active window is a specific project/terminal
"""
import time
import win32gui
import winsound
from winotify import Notification, audio

class SimpleWindowNotifier:
    def __init__(self):
        self.running = False
        self.notification_count = 0

        # Window patterns to monitor (project names, etc.)
        self.watch_patterns = [
            'catapro',  # PyCharm project
            'Claude',   # Claude terminal
            'bash',     # Git Bash
            'Terminal', # terminal
            'MINGW',    # MinGW
        ]

        # Patterns to exclude
        self.exclude_patterns = [
            'readme', '.md', '.txt', '.py', 'editor',
            'chrome', 'firefox', 'browser'
        ]

        # Duplicate prevention
        self.last_notification_per_window = {}
        self.min_notification_interval = 20  # notify at most once every 20 seconds

        print("[OK] Simple Window Notifier initialized")

    def get_foreground_window(self):
        """Get info about the foreground window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return hwnd, title
        except:
            return None, None

    def should_monitor(self, title):
        """Check whether this window should be monitored"""
        if not title:
            return False

        title_lower = title.lower()

        # Check exclude patterns
        for exclude in self.exclude_patterns:
            if exclude in title_lower:
                return False

        # Check watch patterns
        for pattern in self.watch_patterns:
            if pattern.lower() in title_lower:
                return True

        return False

    def should_notify(self, hwnd):
        """Check whether a notification should be sent"""
        current_time = time.time()

        if hwnd in self.last_notification_per_window:
            last_time = self.last_notification_per_window[hwnd]
            if current_time - last_time < self.min_notification_interval:
                return False

        return True

    def show_notification(self, window_title):
        """Show a notification"""
        try:
            # Simplify the window title
            if len(window_title) > 50:
                display_title = window_title[:47] + "..."
            else:
                display_title = window_title

            # Windows notification
            toast = Notification(
                app_id="Claude Auto Approver",
                title="Approval May Be Needed",
                msg=f"Active window: {display_title}\n\nCheck if Claude Code is waiting for approval.",
                duration="long"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()

            # System beep
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            self.notification_count += 1
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] Notification sent: {display_title}")

        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass

    def run(self):
        """Main loop"""
        print("\n" + "="*60)
        print("Simple Window Notifier")
        print("="*60)
        print("\nMonitoring active window...")
        print("Will notify when you're in a monitored window")
        print("(catapro, Claude terminals, etc.)")
        print(f"\nNotification interval: {self.min_notification_interval} seconds")
        print("\nPress Ctrl+C to stop\n")

        self.running = True

        try:
            while self.running:
                # Check the active window
                hwnd, title = self.get_foreground_window()

                if hwnd and title and self.should_monitor(title):
                    # Check whether a notification is needed
                    if self.should_notify(hwnd):
                        try:
                            # Print safely (ignore encoding errors)
                            safe_title = title.encode('ascii', 'ignore').decode('ascii')
                            print(f"\n[DETECTED] Monitored window: {safe_title}")
                        except:
                            print("\n[DETECTED] Monitored window (title contains special chars)")
                        self.show_notification(title)
                        self.last_notification_per_window[hwnd] = time.time()

                time.sleep(2)  # check every 2 seconds

        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user")
        finally:
            self.running = False
            print(f"\n[STATS] Total notifications: {self.notification_count}")
            print("[INFO] Stopped")


if __name__ == "__main__":
    notifier = SimpleWindowNotifier()
    notifier.run()
