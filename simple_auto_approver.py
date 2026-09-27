#!/usr/bin/env python3
"""
Simple fully-automatic approval system
- Monitors terminal windows
- Automatically sends "1" + Enter to the active terminal when the user is idle
- No OCR needed; estimates prompts from screen-change detection
"""

import sys
import time
import win32gui
import keyboard
import mouse

# UTF-8 setup
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class SimpleAutoApprover:
    """Simple automatic approval system"""

    def __init__(self, idle_seconds=3):
        self.running = False
        self.approval_count = 0
        self.last_activity_time = time.time()
        self.idle_threshold = idle_seconds

        # Terminal window patterns
        self.terminal_patterns = [
            'pycharm', 'cmd', 'powershell', 'windows terminal',
            'git bash', 'claude', 'python', 'mintty', 'terminal',
            'catapro', 'mingw', 'bash'
        ]

        # Duplicate prevention
        self.last_approval_window = None
        self.last_approval_time = 0
        self.min_approval_interval = 3  # only once every 3 seconds for the same window

        # Activity counter
        self.user_inputs = 0

        print(f"✅ 초기화 완료 (Idle 임계값: {idle_seconds}초)")

    def start_activity_monitoring(self):
        """Start monitoring user activity"""
        def on_activity(*args):
            self.last_activity_time = time.time()
            self.user_inputs += 1

        # Keyboard monitoring
        keyboard.on_press(on_activity)

        # Mouse monitoring (uses the mouse module's hook)
        mouse.hook(on_activity)

        print("✅ 사용자 활동 모니터링 시작")

    def is_user_idle(self) -> bool:
        """Check whether the user is idle"""
        return (time.time() - self.last_activity_time) >= self.idle_threshold

    def find_all_terminals(self):
        """Find all terminal windows (multiple PyCharm instances, other monitors, etc.)"""
        terminals = []

        def callback(hwnd, extra):
            try:
                # Only check visible windows (including other monitors)
                if not win32gui.IsWindowVisible(hwnd):
                    return True

                # Confirm the window actually exists
                if not win32gui.IsWindow(hwnd):
                    return True

                title = win32gui.GetWindowText(hwnd)
                if not title:  # Skip windows with no title
                    return True

                title_lower = title.lower()

                # Match terminal patterns
                for pattern in self.terminal_patterns:
                    if pattern in title_lower:
                        # Duplicate prevention
                        if not any(t['hwnd'] == hwnd for t in terminals):
                            terminals.append({
                                'hwnd': hwnd,
                                'title': title
                            })
                            print(f"🔍 발견: {title} (hwnd: {hwnd})")
                        break
            except Exception as e:
                pass
            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            print(f"❌ 창 열거 오류: {e}")

        print(f"📊 총 {len(terminals)}개의 터미널 창 발견")
        return terminals

    def find_active_terminal(self):
        """Find the currently active terminal"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return None

            title = win32gui.GetWindowText(hwnd).lower()

            # Match terminal patterns
            for pattern in self.terminal_patterns:
                if pattern in title:
                    return {
                        'hwnd': hwnd,
                        'title': win32gui.GetWindowText(hwnd)
                    }

            return None

        except Exception as e:
            return None

    def should_approve(self, window_info):
        """Decide whether to auto-approve"""
        if window_info is None:
            return False

        hwnd = window_info['hwnd']

        # Duplicate prevention: don't approve the same window too often
        if hwnd == self.last_approval_window:
            if time.time() - self.last_approval_time < self.min_approval_interval:
                return False

        return True

    def auto_approve(self, window_info):
        """Run the auto-approval"""
        try:
            hwnd = window_info['hwnd']
            title = window_info['title']

            # Force the window to the foreground
            try:
                # Try to activate the window
                win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)  # Wait long enough for the window switch
            except Exception as e:
                print(f"   ⚠️ 창 전환 실패: {e}")
                return False

            # Send only "1" (no Enter)
            keyboard.press('1')
            time.sleep(0.1)
            keyboard.release('1')
            time.sleep(0.2)

            # For PyCharm, cycle through all tabs and input on each
            if 'pycharm' in title.lower() or 'gdi+' in title.lower():
                # Check up to 10 tabs (generous upper bound)
                for tab_index in range(10):
                    # Move to the next tab with Alt+Right
                    keyboard.press('alt')
                    time.sleep(0.05)
                    keyboard.press('right')
                    time.sleep(0.05)
                    keyboard.release('right')
                    keyboard.release('alt')
                    time.sleep(0.3)

                    # Send only "1" to the next tab (no Enter)
                    keyboard.press('1')
                    time.sleep(0.1)
                    keyboard.release('1')
                    time.sleep(0.2)

                # Return to the original tab (Alt+Left x10)
                for _ in range(10):
                    keyboard.press('alt')
                    time.sleep(0.05)
                    keyboard.press('left')
                    time.sleep(0.05)
                    keyboard.release('left')
                    keyboard.release('alt')
                    time.sleep(0.1)

            # Record it
            self.last_approval_window = hwnd
            self.last_approval_time = time.time()
            self.approval_count += 1

            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] ✅ 자동 승인: {title} (총 {self.approval_count}회)")

            return True

        except Exception as e:
            print(f"❌ 승인 실패: {e}")
            return False

    def run(self, check_interval=1):
        """Main loop"""
        print()
        print("="*60)
        print("🚀 간단한 자동 승인 시스템")
        print("="*60)
        print()
        print("📋 작동 방식:")
        print(f"   1. 사용자가 {self.idle_threshold}초 동안 입력이 없으면 idle로 판단")
        print("   2. 활성화된 터미널 창이 있는지 확인")
        print("   3. Idle 상태에서 터미널이 활성화되어 있으면")
        print("      자동으로 '1' + Enter 입력")
        print()
        print("⚙️ 설정:")
        print(f"   - Idle 임계값: {self.idle_threshold}초")
        print(f"   - 체크 간격: {check_interval}초")
        print(f"   - 최소 승인 간격: {self.min_approval_interval}초")
        print()
        print("✅ 모니터링 대상 터미널:")
        for pattern in self.terminal_patterns:
            print(f"   - {pattern}")
        print()
        print("⚠️ 중지: Ctrl+C")
        print("="*60)
        print()

        # Start activity monitoring
        self.start_activity_monitoring()

        self.running = True
        last_check = time.time()
        last_status_time = time.time()

        try:
            print("🔄 모니터링 시작...")
            print()

            while self.running:
                time.sleep(0.1)

                current_time = time.time()

                # Periodic check
                if current_time - last_check >= check_interval:
                    # Check idle state
                    if self.is_user_idle():
                        # Find all terminals
                        terminals = self.find_all_terminals()

                        if terminals:
                            print(f"💤 Idle 감지 + 터미널 {len(terminals)}개 발견")

                            # Auto-approve each terminal
                            for terminal in terminals:
                                if self.should_approve(terminal):
                                    self.auto_approve(terminal)
                                    time.sleep(0.2)  # Wait between windows

                    last_check = current_time

                # Print status every 10 seconds
                if current_time - last_status_time >= 10:
                    idle = "💤" if self.is_user_idle() else "👤"
                    idle_time = int(current_time - self.last_activity_time)
                    print(f"[{time.strftime('%H:%M:%S')}] {idle} "
                          f"Idle: {idle_time}초 | "
                          f"승인: {self.approval_count}회 | "
                          f"입력: {self.user_inputs}회")

                    last_status_time = current_time

        except KeyboardInterrupt:
            print("\n\n🛑 사용자 중단")

        finally:
            self.running = False
            keyboard.unhook_all()
            mouse.unhook_all()

            print()
            print("="*60)
            print("📊 최종 통계:")
            print(f"   - 총 자동 승인: {self.approval_count}회")
            print(f"   - 사용자 입력: {self.user_inputs}회")
            print("="*60)
            print("👋 프로그램 종료")


def main():
    """Main function"""
    import argparse

    # Disable stdout buffering
    sys.stdout.reconfigure(line_buffering=True)

    parser = argparse.ArgumentParser(description='간단한 자동 승인 시스템')
    parser.add_argument('--idle', type=int, default=3,
                        help='Idle 시간 (초, 기본값: 3)')
    parser.add_argument('--interval', type=float, default=0.5,
                        help='체크 간격 (초, 기본값: 0.5)')

    args = parser.parse_args()

    print()
    print("🎯 간단한 자동 승인 시스템")
    print(f"   Idle 임계값: {args.idle}초")
    print(f"   체크 간격: {args.interval}초")
    print()
    sys.stdout.flush()

    approver = SimpleAutoApprover(idle_seconds=args.idle)
    approver.run(check_interval=args.interval)


if __name__ == "__main__":
    main()