#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 승인 알림 프로그램 - 현재 콘솔만 모니터링
"""
import sys
import io
import time
import win32console
import winsound
from winotify import Notification, audio

# UTF-8 설정
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

class SimpleNotifier:
    def __init__(self):
        self.running = False
        self.last_pattern = ""
        self.last_notification_time = 0
        self.notification_interval = 15  # 15초에 한 번만 알림

        # 승인 패턴
        self.patterns = [
            'Do you want to proceed?',
            '1. Yes',
            '2. Yes, and don\'t ask again',
        ]

        print("✅ Simple Notifier 초기화")

    def read_console(self):
        """현재 콘솔 화면 읽기"""
        try:
            handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
            csbi = handle.GetConsoleScreenBufferInfo()
            cursor_pos = csbi['CursorPosition']

            # 최근 20줄
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
        """승인 패턴 확인"""
        if not text:
            return False
        text_lower = text.lower()
        for pattern in self.patterns:
            if pattern.lower() in text_lower:
                return True
        return False

    def should_notify(self, text):
        """알림을 보내야 하는지 확인"""
        current_time = time.time()

        # 같은 패턴은 15초에 한 번만
        if text == self.last_pattern:
            if current_time - self.last_notification_time < self.notification_interval:
                return False

        return True

    def notify(self, text):
        """알림 표시"""
        if not self.should_notify(text):
            return

        try:
            toast = Notification(
                app_id="Claude Auto Approver",
                title="🔔 승인 요청",
                msg="현재 터미널에서 승인을 기다리고 있습니다.\n\nClaude Code 승인 프롬프트 감지됨",
                duration="long"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()

            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            # 기록
            self.last_pattern = text
            self.last_notification_time = time.time()

            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] 🔔 알림 표시됨")

        except Exception as e:
            print(f"⚠️ 알림 실패: {e}")

    def run(self):
        """메인 루프"""
        print("\n" + "="*60)
        print("🔔 Simple Claude Approval Notifier")
        print("="*60)
        print("\n현재 콘솔 모니터링 중...")
        print(f"알림 간격: {self.notification_interval}초")
        print("\n종료: Ctrl+C\n")

        self.running = True

        try:
            while self.running:
                # 콘솔 읽기
                text = self.read_console()

                # 패턴 확인
                if text and self.check_pattern(text):
                    self.notify(text)

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⚠️ 중단됨")
        finally:
            self.running = False
            print("🏁 종료")


if __name__ == "__main__":
    notifier = SimpleNotifier()
    notifier.run()
