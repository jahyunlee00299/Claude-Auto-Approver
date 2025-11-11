#!/usr/bin/env python3
"""
Claude Code Auto Approver
Git Bash 창에서 '1'을 누르면 자동으로 Claude Code의 승인 대화상자를 처리
"""

import sys
import time
import threading
import win32gui
import win32con
import win32api
import win32console
import msvcrt
from pathlib import Path

# UTF-8 설정
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.auto_approver import AutoApprover
from src.utils.config import load_config


class ClaudeCodeApprover:
    """Claude Code 승인을 처리하는 메인 클래스"""

    def __init__(self):
        self.running = False
        self.approver = None
        self.monitor_thread = None
        self.claude_window = None

        # 설정 로드
        config = load_config()
        config['safe_mode'] = False
        config['delay_seconds'] = 0.2

        # Claude Code 창 패턴
        self.claude_patterns = [
            'MINGW64', 'bash', 'Claude', 'Code', 'Terminal'
        ]

    def find_claude_window(self):
        """Claude Code가 실행 중인 Git Bash 창 찾기"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    # Git Bash나 Terminal 창 찾기
                    if any(pattern.lower() in window_text.lower()
                           for pattern in self.claude_patterns):
                        # 현재 창이 아닌 다른 창 찾기
                        try:
                            current_window = win32console.GetConsoleWindow()
                            if hwnd != current_window:
                                windows.append({
                                    'hwnd': hwnd,
                                    'title': window_text
                                })
                        except:
                            windows.append({
                                'hwnd': hwnd,
                                'title': window_text
                            })
            return True

        windows = []
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
        except Exception as e:
            print(f"❌ 창 검색 오류: {e}")

        return windows

    def send_approval_to_claude(self, target_window):
        """Claude 창으로 이동하여 '1' + Enter 입력"""
        try:
            hwnd = target_window['hwnd']
            title = target_window['title']

            print(f"\n📤 승인 전송 중: '{title}'")

            # 창을 전면으로 가져오기
            try:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.3)
            except Exception as e:
                print(f"   ⚠️ 창 전환 경고 (무시 가능): {e}")
                time.sleep(0.3)

            # '1' 입력만 (Enter 없음)
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            print(f"   ✅ '1' 전송 완료! (Enter 없음)")
            return True

        except Exception as e:
            print(f"   ❌ 입력 전송 실패: {e}")
            return False

    def monitor_keyboard(self):
        """키보드 입력 모니터링 - '1' 키 감지"""
        print("\n⌨️  키보드 모니터링 시작...")
        print("   → 이 창에서 '1'을 누르면 Claude 창으로 이동하여 자동 승인합니다")

        while self.running:
            # 키 입력 대기 (논블로킹)
            if msvcrt.kbhit():
                key = msvcrt.getch()

                # '1' 키 감지
                if key == b'1':
                    print("\n🔑 '1' 키 감지!")

                    # Claude 창 찾기
                    claude_windows = self.find_claude_window()

                    if not claude_windows:
                        print("   ⚠️ Claude Code 창을 찾을 수 없습니다")
                        continue

                    # 여러 창이 있으면 선택
                    if len(claude_windows) > 1:
                        print(f"\n   📋 {len(claude_windows)}개의 터미널 창 발견:")
                        for i, win in enumerate(claude_windows, 1):
                            print(f"      {i}. {win['title']}")
                        print(f"\n   → 첫 번째 창으로 전송합니다: {claude_windows[0]['title']}")

                    # 승인 전송
                    self.send_approval_to_claude(claude_windows[0])

                elif key == b'q' or key == b'Q':
                    print("\n👋 종료 요청...")
                    self.running = False
                    break

            time.sleep(0.1)

    def start(self):
        """승인 시스템 시작"""
        if self.running:
            print("⚠️ 이미 실행 중입니다")
            return

        self.running = True

        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(target=self.monitor_keyboard)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ Claude Code Auto Approver 시작됨")

    def stop(self):
        """승인 시스템 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("🛑 Claude Code Auto Approver 중지됨")


def main():
    print("=" * 70)
    print("🤖 Claude Code Auto Approver")
    print("=" * 70)
    print()
    print("이 프로그램은 다음과 같이 작동합니다:")
    print("  1. 이 창에서 '1'을 누릅니다 (Enter 치지 않음)")
    print("  2. 자동으로 Claude Code 창을 찾아 이동합니다")
    print("  3. '1'만 자동으로 입력합니다 (Enter 없음)")
    print()
    print("종료하려면 'q'를 누르세요")
    print("=" * 70)

    approver = ClaudeCodeApprover()

    try:
        approver.start()

        # 메인 스레드는 대기
        while approver.running:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n⚠️ Ctrl+C로 중단되었습니다")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        approver.stop()
        print("\n🏁 프로그램 종료")


if __name__ == "__main__":
    main()
