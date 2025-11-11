#!/usr/bin/env python3
"""
Cross Terminal Monitor
다른 터미널 창의 출력을 모니터링하여 승인 요청 시 자동으로 '1' 입력
"""
import sys
import time
import threading
import win32gui
import win32con
import win32api
import win32console
import ctypes
import io
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class CrossTerminalMonitor:
    """다른 터미널 창 모니터링 및 자동 승인"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0
        self.current_hwnd = None

        # 승인 요청 패턴들
        self.approval_patterns = [
            '1. Yes',
            '1. Approve',
            '1. OK',
            '1. Continue',
            '1) Yes',
            '1: Yes',
            '[1] Yes',
            'option (1-',
            'Select (1)',
        ]

        # 대상 터미널 창 패턴 (Claude Code 실행 중인 창)
        self.target_patterns = ['MINGW', 'bash', 'Claude', 'Terminal']

        # 중복 방지
        self.last_input_time = 0
        self.min_input_interval = 3  # 3초에 한 번만 입력

        # 현재 창 저장
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

    def find_target_terminals(self):
        """대상 터미널 창들 찾기 (현재 창 제외)"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # 현재 창이 아니고, 터미널 패턴과 일치하는 경우
                if title and hwnd != self.current_hwnd:
                    if any(p in title for p in self.target_patterns):
                        windows.append({'hwnd': hwnd, 'title': title})
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def read_window_text_via_api(self, hwnd):
        """Windows API를 사용하여 창의 텍스트 읽기 (시도)"""
        try:
            # SendMessage를 사용하여 텍스트 가져오기 시도
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
                return buffer.value
        except:
            pass
        return ""

    def get_console_screen_buffer_from_hwnd(self, hwnd):
        """특정 창의 콘솔 스크린 버퍼 읽기"""
        try:
            # 프로세스 ID 가져오기
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # 다른 프로세스의 콘솔 버퍼에 직접 접근하는 것은 복잡하므로
            # 화면 캡처 + OCR 또는 다른 방법 필요
            # 현재는 창 제목만 확인
            return ""
        except:
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
        """터미널에 '1' 입력 (Enter 없음)"""
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

            # '1' 입력만 (Enter 없음!)
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.last_input_time = time.time()

            print(f"   ✅ '1' 입력 완료! (Enter 없음) (총 {self.approval_count}회)")

            # 원래 창으로 돌아오기
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
        print("\n🔍 다른 터미널 창 모니터링 시작...")
        print("   (창 제목에서 승인 요청 패턴 감지)")

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
                    hwnd = terminal['hwnd']
                    title = terminal['title']

                    # 창 텍스트 읽기 시도
                    window_text = self.read_window_text_via_api(hwnd)

                    # 제목에서도 패턴 확인 (일부 앱은 제목에 정보 표시)
                    combined_text = title + " " + window_text

                    # 승인 패턴 확인
                    if self.check_approval_pattern(combined_text):
                        print(f"\n📋 승인 요청 패턴 감지! (창: {title})")
                        self.send_input_to_terminal(terminal)
                        break  # 하나만 처리

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

        print("✅ Cross Terminal Monitor 시작됨")

    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)


def main():
    print("=" * 70)
    print("🤖 Cross Terminal Monitor")
    print("=" * 70)
    print()
    print("작동 방식:")
    print("  1. 다른 터미널 창들을 실시간으로 모니터링합니다")
    print("  2. 창 제목/내용에서 승인 요청 패턴을 감지합니다")
    print("  3. 패턴 감지 시 해당 창으로 이동하여 '1'을 입력합니다 (Enter 없음)")
    print()
    print("감지 패턴:")
    for i, pattern in enumerate(CrossTerminalMonitor().approval_patterns[:5], 1):
        print(f"  {i}. '{pattern}'")
    print("  ...")
    print()
    print("⚠️ 주의: 이 창이 아닌 다른 터미널 창을 모니터링합니다")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)

    # win32process import 추가
    global win32process
    import win32process

    monitor = CrossTerminalMonitor()

    try:
        monitor.start()

        # 대상 터미널 목록 표시
        print("\n📋 모니터링 대상 터미널 목록:")
        terminals = monitor.find_target_terminals()
        if terminals:
            for i, term in enumerate(terminals, 1):
                print(f"   {i}. {term['title']}")
        else:
            print("   ⚠️ 대상 터미널을 찾을 수 없습니다")
            print("   → MINGW, bash, Claude, Terminal 등의 창을 열어주세요")

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
