#!/usr/bin/env python3
"""
Auto Yes - automatically detects the approval dialog and sends '1' + Enter to another Git Bash window
"""

import sys
import time
import threading
import win32gui
import win32con
import win32api
import win32console

# UTF-8 setup
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


class AutoYesApprover:
    """Automatically detects the approval dialog and sends '1' to another window"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0

        # Window patterns to detect (approval dialog)
        self.approval_patterns = [
            'Question', '질문', 'Confirm', '확인',
            'Approval', '승인', 'Permission', 'Allow'
        ]

        # Target Git Bash window patterns
        self.target_patterns = [
            'MINGW', 'bash', 'Claude', 'Terminal'
        ]

        # Duplicate-prevention
        self.last_handled_window = None
        self.last_handled_time = 0

    def find_approval_window(self):
        """Find the approval dialog"""
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
        """Find the target Git Bash window"""
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

        # If multiple windows exist, return the first one
        return windows[0] if windows else None

    def send_approval(self, target_window):
        """Send only '1' to the target window (no Enter)"""
        try:
            hwnd = target_window['hwnd']
            title = target_window['title']

            print(f"\n📤 '{title}'로 전환하여 '1' 입력 중...")

            # Activate the window
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass  # Ignore the error and continue

            time.sleep(0.2)

            # Send only '1' (no Enter!)
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
        """Main monitoring loop"""
        print("\n🔍 모니터링 시작...")

        while self.running:
            try:
                # Find the approval dialog
                approval_window = self.find_approval_window()

                if approval_window:
                    # Duplicate-prevention: handle the same window at most once every 3s
                    hwnd = approval_window['hwnd']
                    if hwnd == self.last_handled_window:
                        if time.time() - self.last_handled_time < 3:
                            time.sleep(0.5)
                            continue

                    print(f"\n📋 승인 대화상자 감지: '{approval_window['title']}'")

                    # Find the target Git Bash window
                    target_window = self.find_target_bash_window()

                    if target_window:
                        # Send the approval
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
        """Start monitoring"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ Auto Yes Approver 시작됨")

    def stop(self):
        """Stop monitoring"""
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

        # Wait on the main thread
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
