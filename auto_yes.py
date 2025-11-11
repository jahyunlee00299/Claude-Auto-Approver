#!/usr/bin/env python3
"""
Auto Yes - 자동으로 승인 대화상자를 감지하여 다른 Git Bash 창에 '1' + Enter 입력
"""

import sys
import time
import threading
import win32gui
import win32con
import win32api
import win32console

# UTF-8 설정
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


class AutoYesApprover:
    """승인 대화상자를 자동으로 감지하여 다른 창에 '1' 입력"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0

        # 감지할 창 패턴 (승인 대화상자)
        self.approval_patterns = [
            'Question', '질문', 'Confirm', '확인',
            'Approval', '승인', 'Permission', 'Allow'
        ]

        # 대상 Git Bash 창 패턴
        self.target_patterns = [
            'MINGW', 'bash', 'Claude', 'Terminal'
        ]

        # 중복 방지
        self.last_handled_window = None
        self.last_handled_time = 0

    def find_approval_window(self):
        """승인 대화상자 찾기"""
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and any(p.lower() in title.lower() for p in self.approval_patterns):
                    windows.append({'hwnd': hwnd, 'title': title})
            return True

        windows = []
        try:
            win32gui.EnumWindows(enum_callback, windows)
        except:
            pass

        return windows[0] if windows else None

    def find_target_bash_window(self):
        """대상 Git Bash 창 찾기"""
        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and any(p in title for p in self.target_patterns):
                    windows.append({'hwnd': hwnd, 'title': title})
            return True

        windows = []
        try:
            win32gui.EnumWindows(enum_callback, windows)
        except:
            pass

        # 여러 창이 있으면 첫 번째 반환
        return windows[0] if windows else None

    def send_approval(self, target_window):
        """대상 창에 '1'만 전송 (Enter 없음)"""
        try:
            hwnd = target_window['hwnd']
            title = target_window['title']

            print(f"\n📤 '{title}'로 전환하여 '1' 입력 중...")

            # 창 활성화
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass  # 에러 무시하고 계속

            time.sleep(0.2)

            # '1' 입력만 (Enter 없음!)
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            print(f"   ✅ '1' 입력 완료! (Enter 없음) (총 {self.approval_count}회)")
            return True

        except Exception as e:
            print(f"   ❌ 전송 실패: {e}")
            return False

    def monitor_loop(self):
        """메인 모니터링 루프"""
        print("\n🔍 모니터링 시작...")

        while self.running:
            try:
                # 승인 대화상자 찾기
                approval_window = self.find_approval_window()

                if approval_window:
                    # 중복 방지: 같은 창은 3초에 한 번만 처리
                    hwnd = approval_window['hwnd']
                    if hwnd == self.last_handled_window:
                        if time.time() - self.last_handled_time < 3:
                            time.sleep(0.5)
                            continue

                    print(f"\n📋 승인 대화상자 감지: '{approval_window['title']}'")

                    # 대상 Git Bash 창 찾기
                    target_window = self.find_target_bash_window()

                    if target_window:
                        # 승인 전송
                        if self.send_approval(target_window):
                            self.last_handled_window = hwnd
                            self.last_handled_time = time.time()
                    else:
                        print("   ⚠️ 대상 Git Bash 창을 찾을 수 없습니다")

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

        print("✅ Auto Yes Approver 시작됨")

    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)


def main():
    print("=" * 70)
    print("🤖 Auto Yes Approver")
    print("=" * 70)
    print()
    print("작동 방식:")
    print("  1. 승인 대화상자를 자동으로 감지합니다")
    print("  2. Git Bash 창을 찾습니다")
    print("  3. 해당 창으로 이동하여 '1'만 입력합니다 (Enter 없음!)")
    print()
    print("감지 대상:")
    print("  - Question, Confirm, Approval 등의 대화상자")
    print()
    print("입력 대상:")
    print("  - MINGW, bash, Claude, Terminal 창")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)

    approver = AutoYesApprover()

    try:
        approver.start()

        # 메인 스레드 대기
        while approver.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Ctrl+C로 중단되었습니다")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        approver.stop()
        print(f"\n📊 총 {approver.approval_count}회 자동 승인")
        print("🏁 프로그램 종료")


if __name__ == "__main__":
    main()
