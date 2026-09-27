#!/usr/bin/env python3
"""
Terminal Output Monitor
Monitors terminal output and automatically sends '1' when an approval-request pattern is detected
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
    """Terminal output monitoring and auto-approval"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0

        # Approval-request patterns (patterns to find in terminal output)
        self.approval_patterns = [
            # Claude Code style patterns
            ['1.', 'Yes'],
            ['1.', 'Approve'],
            ['1.', '승인'],
            ['1.', 'OK'],
            ['1.', 'Continue'],
            ['(1)', 'Yes'],
            ['[1]', 'Yes'],
            # Generic selection-prompt patterns
            'Select option (1',
            'Choose (1)',
            '1) Yes',
            '1: Yes',
        ]

        # Target terminal window patterns
        self.terminal_patterns = ['MINGW', 'bash', 'Claude', 'Terminal', 'cmd', 'PowerShell']

        # Duplicate prevention
        self.last_input_time = 0
        self.min_input_interval = 2  # only send input once every 2 seconds

    def find_terminal_windows(self):
        """Find all terminal windows"""
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
        """Read the current console screen buffer (Windows)"""
        try:
            # Get the standard output handle
            console_handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)

            # Get console screen buffer info
            csbi = console_handle.GetConsoleScreenBufferInfo()

            # Current cursor position
            cursor_pos = csbi['CursorPosition']

            # Only read the last few lines (recent 20 lines)
            lines_to_read = min(20, cursor_pos.Y + 1)
            start_y = max(0, cursor_pos.Y - lines_to_read + 1)

            # Read text from the screen buffer
            buffer_text = []
            for y in range(start_y, cursor_pos.Y + 1):
                try:
                    # Read line by line
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
        """Check text for an approval pattern"""
        if not text:
            return False

        text_lower = text.lower()

        for pattern in self.approval_patterns:
            if isinstance(pattern, list):
                # Check that every element is present
                if all(p.lower() in text_lower for p in pattern):
                    return True
            else:
                # Single pattern
                if pattern.lower() in text_lower:
                    return True

        return False

    def send_input_to_terminal(self, terminal):
        """Send '1' to the terminal"""
        try:
            hwnd = terminal['hwnd']
            title = terminal['title']

            print(f"\n📤 '{title}'에 '1' 입력 중...")

            # Activate the window
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

            time.sleep(0.2)

            # Send '1'
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
        """Main monitoring loop"""
        print("\n🔍 터미널 출력 모니터링 시작...")

        while self.running:
            try:
                # Duplicate prevention
                if time.time() - self.last_input_time < self.min_input_interval:
                    time.sleep(0.5)
                    continue

                # Read the current console screen
                screen_text = self.read_console_screen_buffer()

                # Check for an approval pattern
                if self.check_approval_pattern(screen_text):
                    print("\n📋 승인 요청 패턴 감지!")
                    print(f"   감지된 텍스트:\n{screen_text[-200:]}")  # last 200 chars only

                    # Find terminal windows
                    terminals = self.find_terminal_windows()

                    if terminals:
                        # Send input to the first terminal
                        self.send_input_to_terminal(terminals[0])
                    else:
                        print("   ⚠️ 대상 터미널을 찾을 수 없습니다")

                time.sleep(0.5)

            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(1)

        print("\n🛑 모니터링 종료")

    def start(self):
        """Start monitoring"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ Terminal Monitor 시작됨")

    def stop(self):
        """Stop monitoring"""
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

        # Wait on the main thread
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
