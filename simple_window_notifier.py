#!/usr/bin/env python3
"""
Simple Window Notifier - Tesseract 없이 작동
활성 창이 특정 프로젝트/터미널일 때 알림 표시
"""
import time
import win32gui
import winsound
from winotify import Notification, audio

class SimpleWindowNotifier:
    def __init__(self):
        self.running = False
        self.notification_count = 0

        # 모니터링할 창 패턴 (프로젝트 이름 등)
        self.watch_patterns = [
            'catapro',  # PyCharm 프로젝트
            'Claude',   # Claude 터미널
            'bash',     # Git Bash
            'Terminal', # 터미널
            'MINGW',    # MinGW
        ]

        # 제외할 패턴
        self.exclude_patterns = [
            'readme', '.md', '.txt', '.py', 'editor',
            'chrome', 'firefox', 'browser'
        ]

        # 중복 방지
        self.last_notification_per_window = {}
        self.min_notification_interval = 20  # 20초에 한 번만 알림

        print("[OK] Simple Window Notifier initialized")

    def get_foreground_window(self):
        """활성 창 정보 가져오기"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return hwnd, title
        except:
            return None, None

    def should_monitor(self, title):
        """이 창을 모니터링해야 하는지 확인"""
        if not title:
            return False

        title_lower = title.lower()

        # 제외 패턴 확인
        for exclude in self.exclude_patterns:
            if exclude in title_lower:
                return False

        # 감시 패턴 확인
        for pattern in self.watch_patterns:
            if pattern.lower() in title_lower:
                return True

        return False

    def should_notify(self, hwnd):
        """알림을 보내야 하는지 확인"""
        current_time = time.time()

        if hwnd in self.last_notification_per_window:
            last_time = self.last_notification_per_window[hwnd]
            if current_time - last_time < self.min_notification_interval:
                return False

        return True

    def show_notification(self, window_title):
        """알림 표시"""
        try:
            # 창 제목 단순화
            if len(window_title) > 50:
                display_title = window_title[:47] + "..."
            else:
                display_title = window_title

            # Windows 알림
            toast = Notification(
                app_id="Claude Auto Approver",
                title="Approval May Be Needed",
                msg=f"Active window: {display_title}\n\nCheck if Claude Code is waiting for approval.",
                duration="long"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()

            # 시스템 비프음
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
        """메인 루프"""
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
                # 활성 창 확인
                hwnd, title = self.get_foreground_window()

                if hwnd and title and self.should_monitor(title):
                    # 알림 필요 여부 확인
                    if self.should_notify(hwnd):
                        try:
                            # 안전하게 출력 (인코딩 오류 무시)
                            safe_title = title.encode('ascii', 'ignore').decode('ascii')
                            print(f"\n[DETECTED] Monitored window: {safe_title}")
                        except:
                            print("\n[DETECTED] Monitored window (title contains special chars)")
                        self.show_notification(title)
                        self.last_notification_per_window[hwnd] = time.time()

                time.sleep(2)  # 2초마다 확인

        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user")
        finally:
            self.running = False
            print(f"\n[STATS] Total notifications: {self.notification_count}")
            print("[INFO] Stopped")


if __name__ == "__main__":
    notifier = SimpleWindowNotifier()
    notifier.run()
