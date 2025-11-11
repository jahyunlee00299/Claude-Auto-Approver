#!/usr/bin/env python3
"""
Console Buffer Monitor
Windows API를 사용하여 다른 터미널의 콘솔 버퍼를 직접 읽어 자동 승인
"""
import sys
import time
import threading
import win32gui
import win32con
import win32api
import win32process
import win32console
import ctypes
from ctypes import wintypes
import io

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ConsoleBufferMonitor:
    """Windows 콘솔 버퍼 직접 읽기"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0
        self.current_hwnd = None

        # 승인 패턴
        self.approval_patterns = [
            '1. Yes',
            '1. Approve',
            '1. OK',
            '1) Yes',
            '1: Yes',
            'option (1-',
            'Select (1)',
        ]

        # 터미널 패턴
        self.terminal_patterns = ['MINGW', 'bash', 'Claude', 'Terminal', 'cmd']

        # 중복 방지
        self.last_input_time = 0
        self.min_input_interval = 2

        # 현재 창
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

    def find_target_terminals(self):
        """대상 터미널 창 찾기"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and hwnd != self.current_hwnd:
                    if any(p in title for p in self.terminal_patterns):
                        # 프로세스 ID 가져오기
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'pid': pid
                        })
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def attach_console(self, pid):
        """다른 프로세스의 콘솔에 연결"""
        try:
            # 현재 콘솔에서 분리
            kernel32 = ctypes.windll.kernel32
            kernel32.FreeConsole()
            time.sleep(0.1)

            # 대상 프로세스 콘솔에 연결
            if kernel32.AttachConsole(pid):
                return True

            return False
        except Exception as e:
            print(f"   ⚠️ 콘솔 연결 실패: {e}")
            return False

    def detach_and_restore_console(self):
        """콘솔 분리 및 원래 콘솔로 복귀"""
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.FreeConsole()
            time.sleep(0.1)

            # 원래 콘솔에 재연결 (없으면 새로 할당)
            kernel32.AllocConsole()
        except:
            pass

    def read_console_buffer(self):
        """현재 연결된 콘솔 버퍼 읽기"""
        try:
            # 표준 출력 핸들 가져오기
            console_handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)

            # 콘솔 화면 버퍼 정보
            csbi = console_handle.GetConsoleScreenBufferInfo()

            # 현재 화면 크기
            window = csbi['Window']
            width = window.Right - window.Left + 1
            height = window.Bottom - window.Top + 1

            # 마지막 20줄만 읽기
            lines_to_read = min(20, height)
            start_y = max(0, window.Bottom - lines_to_read + 1)

            buffer_text = []
            for y in range(start_y, window.Bottom + 1):
                try:
                    coord = win32console.PyCOORDType(window.Left, y)
                    text = console_handle.ReadConsoleOutputCharacter(width, coord)
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

            time.sleep(0.3)

            # '1' 입력
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.last_input_time = time.time()

            print(f"   ✅ '1' 입력 완료! (총 {self.approval_count}회)")

            # 원래 창으로 복귀
            if self.current_hwnd:
                time.sleep(0.2)
                try:
                    win32gui.SetForegroundWindow(self.current_hwnd)
                except:
                    pass

            return True

        except Exception as e:
            print(f"   ❌ 입력 실패: {e}")
            return False

    def monitor_loop(self):
        """메인 모니터링 루프"""
        print("\n🔍 콘솔 버퍼 모니터링 시작...")

        while self.running:
            try:
                # 중복 방지
                if time.time() - self.last_input_time < self.min_input_interval:
                    time.sleep(0.5)
                    continue

                # 대상 터미널 찾기
                terminals = self.find_target_terminals()

                if not terminals:
                    time.sleep(1)
                    continue

                # 각 터미널 확인
                for terminal in terminals:
                    pid = terminal['pid']

                    # 콘솔에 연결 시도
                    if self.attach_console(pid):
                        # 콘솔 버퍼 읽기
                        text = self.read_console_buffer()

                        # 콘솔 분리 및 복원
                        self.detach_and_restore_console()

                        # 승인 패턴 확인
                        if text and self.check_approval_pattern(text):
                            print(f"\n📋 승인 요청 감지! (창: {terminal['title']})")
                            print(f"   텍스트: {text[:150]}...")
                            self.send_input_to_terminal(terminal)
                            break
                    else:
                        # 연결 실패 시 콘솔 복원
                        self.detach_and_restore_console()

                time.sleep(1)

            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                # 오류 시 콘솔 복원 시도
                try:
                    self.detach_and_restore_console()
                except:
                    pass
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

        print("✅ Console Buffer Monitor 시작됨")

    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)


def main():
    print("=" * 70)
    print("🤖 Console Buffer Monitor")
    print("=" * 70)
    print()
    print("작동 방식:")
    print("  1. 다른 터미널 창의 프로세스를 찾습니다")
    print("  2. Windows API로 콘솔 버퍼에 직접 연결합니다")
    print("  3. 콘솔 화면 내용을 직접 읽습니다")
    print("  4. '1. Yes' 등의 승인 패턴 감지 시 '1'을 입력합니다")
    print()
    print("⚠️ 주의:")
    print("  - 다른 프로세스의 콘솔에 연결하므로 권한이 필요할 수 있습니다")
    print("  - 모니터링 중 이 창의 출력이 일시적으로 중단될 수 있습니다")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)

    monitor = ConsoleBufferMonitor()

    try:
        # 대상 터미널 확인
        terminals = monitor.find_target_terminals()
        if terminals:
            print("\n📋 모니터링 대상 터미널:")
            for i, term in enumerate(terminals, 1):
                print(f"   {i}. {term['title']} (PID: {term['pid']})")
        else:
            print("\n⚠️ 대상 터미널을 찾을 수 없습니다")

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
