#!/usr/bin/env python3
"""
Terminal Output Monitor
터미널 출력을 모니터링하여 승인 요청 패턴 감지 시 자동으로 '1' 입력
"""
import sys
import time
import threading
import win32gui
import win32con
import win32api
import win32console
import io
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class TerminalMonitor:
    """터미널 출력 모니터링 및 자동 승인"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0

        # 승인 요청 패턴들 (터미널 출력에서 찾을 패턴)
        self.approval_patterns = [
            # Claude Code 스타일 패턴
            ['1.', 'Yes'],
            ['1.', 'Approve'],
            ['1.', '승인'],
            ['1.', 'OK'],
            ['1.', 'Continue'],
            ['(1)', 'Yes'],
            ['[1]', 'Yes'],
            # 일반적인 선택 패턴
            'Select option (1',
            'Choose (1)',
            '1) Yes',
            '1: Yes',
        ]

        # 대상 터미널 창 패턴
        self.terminal_patterns = ['MINGW', 'bash', 'Claude', 'Terminal', 'cmd', 'PowerShell']

        # 중복 방지
        self.last_input_time = 0
        self.min_input_interval = 2  # 2초에 한 번만 입력

    def find_terminal_windows(self):
        """모든 터미널 창 찾기"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and any(p in title for p in self.terminal_patterns):
                    windows.append({'hwnd': hwnd, 'title': title})
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def read_console_screen_buffer(self):
        """현재 콘솔 화면 버퍼 읽기 (Windows)"""
        try:
            # 표준 출력 핸들 가져오기
            console_handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)

            # 콘솔 화면 버퍼 정보 가져오기
            csbi = console_handle.GetConsoleScreenBufferInfo()

            # 현재 커서 위치
            cursor_pos = csbi['CursorPosition']

            # 마지막 몇 줄만 읽기 (최근 20줄)
            lines_to_read = min(20, cursor_pos.Y + 1)
            start_y = max(0, cursor_pos.Y - lines_to_read + 1)

            # 화면 버퍼에서 텍스트 읽기
            buffer_text = []
            for y in range(start_y, cursor_pos.Y + 1):
                try:
                    # 한 줄씩 읽기
                    coord = win32console.PyCOORDType(0, y)
                    size = csbi['Size'].X
                    text = console_handle.ReadConsoleOutputCharacter(size, coord)
                    buffer_text.append(text.strip())
                except:
                    pass

            return '\n'.join(buffer_text)
        except Exception as e:
            return ""

    def check_approval_pattern(self, text):
        """텍스트에서 승인 패턴 확인"""
        if not text:
            return False

        text_lower = text.lower()

        for pattern in self.approval_patterns:
            if isinstance(pattern, list):
                # 모든 요소가 포함되어 있는지 확인
                if all(p.lower() in text_lower for p in pattern):
                    return True
            else:
                # 단일 패턴
                if pattern.lower() in text_lower:
                    return True

        return False

    def send_input_to_terminal(self, terminal):
        """터미널에 '1' 입력"""
        try:
            hwnd = terminal['hwnd']
            title = terminal['title']

            print(f"\n📤 '{title}'에 '1' 입력 중...")

            # 창 활성화
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

            time.sleep(0.2)

            # '1' 입력
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.last_input_time = time.time()

            print(f"   ✅ '1' 입력 완료! (총 {self.approval_count}회)")
            return True

        except Exception as e:
            print(f"   ❌ 입력 실패: {e}")
            return False

    def monitor_loop(self):
        """메인 모니터링 루프"""
        print("\n🔍 터미널 출력 모니터링 시작...")

        while self.running:
            try:
                # 중복 방지
                if time.time() - self.last_input_time < self.min_input_interval:
                    time.sleep(0.5)
                    continue

                # 현재 콘솔 화면 읽기
                screen_text = self.read_console_screen_buffer()

                # 승인 패턴 확인
                if self.check_approval_pattern(screen_text):
                    print("\n📋 승인 요청 패턴 감지!")
                    print(f"   감지된 텍스트:\n{screen_text[-200:]}")  # 마지막 200자만

                    # 터미널 창 찾기
                    terminals = self.find_terminal_windows()

                    if terminals:
                        # 첫 번째 터미널에 입력
                        self.send_input_to_terminal(terminals[0])
                    else:
                        print("   ⚠️ 대상 터미널을 찾을 수 없습니다")

                time.sleep(0.5)

            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(1)

        print("\n🛑 모니터링 종료")

    def start(self):
        """모니터링 시작"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ Terminal Monitor 시작됨")

    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)


def main():
    print("=" * 70)
    print("🤖 Terminal Output Monitor")
    print("=" * 70)
    print()
    print("작동 방식:")
    print("  1. 터미널 출력을 실시간으로 모니터링합니다")
    print("  2. 승인 요청 패턴을 감지합니다 (예: '1. Yes', '1) Approve' 등)")
    print("  3. 패턴 감지 시 자동으로 '1'을 입력합니다")
    print()
    print("감지 패턴:")
    print("  - '1. Yes' 형태의 선택지")
    print("  - 'Select option (1-' 형태의 프롬프트")
    print("  - '1) Yes' 또는 '1: Yes' 형태")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)

    monitor = TerminalMonitor()

    try:
        monitor.start()

        # 메인 스레드 대기
        while monitor.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Ctrl+C로 중단되었습니다")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        monitor.stop()
        print(f"\n📊 총 {monitor.approval_count}회 자동 입력")
        print("🏁 프로그램 종료")


if __name__ == "__main__":
    main()
