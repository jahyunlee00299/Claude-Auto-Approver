#!/usr/bin/env python3
"""
Cross Terminal Monitor
Monitors another terminal window's output and auto-inputs '1' on an approval request
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
    """Monitors other terminal windows and auto-approves"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0
        self.current_hwnd = None

        # Approval request patterns
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

        # Target terminal window patterns (windows running Claude Code)
        self.target_patterns = ['MINGW', 'bash', 'Claude', 'Terminal']

        # Duplicate prevention
        self.last_input_time = 0
        self.min_input_interval = 3  # At most once every 3 seconds

        # Store current window
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

    def find_target_terminals(self):
        """Find target terminal windows (excluding the current one)"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # Not the current window, and matches a terminal pattern
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
        """Try reading the window's text via the Windows API"""
        try:
            # Try to get text via SendMessage
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
                return buffer.value
        except:
            pass
        return ""

    def get_console_screen_buffer_from_hwnd(self, hwnd):
        """Read the console screen buffer of a specific window"""
        try:
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # Directly accessing another process's console buffer is complex,
            # so screen capture + OCR or another method is needed
            # For now, only the window title is checked
            return ""
        except:
            return ""

    def check_approval_pattern(self, text):
        """Check text for an approval pattern"""
        if not text:
            return False

        text_lower = text.lower()

        for pattern in self.approval_patterns:
            if pattern.lower() in text_lower:
                return True

        return False

    def send_input_to_terminal(self, terminal):
        """Send '1' to the terminal (no Enter)"""
        try:
            hwnd = terminal['hwnd']
            title = terminal['title']

            print(f"\n📤 '{title}'에 '1' 입력 중...")

            # Activate window
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

            time.sleep(0.3)

            # Send '1' only (no Enter!)
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.last_input_time = time.time()

            print(f"   ✅ '1' 입력 완료! (Enter 없음) (총 {self.approval_count}회)")

            # Return to the original window
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
        """Main monitoring loop"""
        print("\n🔍 다른 터미널 창 모니터링 시작...")
        print("   (창 제목에서 승인 요청 패턴 감지)")

        while self.running:
            try:
                # Duplicate prevention
                if time.time() - self.last_input_time < self.min_input_interval:
                    time.sleep(0.5)
                    continue

                # Find target terminals
                terminals = self.find_target_terminals()

                if not terminals:
                    time.sleep(1)
                    continue

                # Check each terminal
                for terminal in terminals:
                    hwnd = terminal['hwnd']
                    title = terminal['title']

                    # Try reading window text
                    window_text = self.read_window_text_via_api(hwnd)

                    # Also check the pattern in the title (some apps show info there)
                    combined_text = title + " " + window_text

                    # Check approval pattern
                    if self.check_approval_pattern(combined_text):
                        print(f"\n📋 승인 요청 패턴 감지! (창: {title})")
                        self.send_input_to_terminal(terminal)
                        break  # Handle only one

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

        print("✅ Cross Terminal Monitor 시작됨")

    def stop(self):
        """Stop monitoring"""
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

    # Import win32process
    global win32process
    import win32process

    monitor = CrossTerminalMonitor()

    try:
        monitor.start()

        # Show the list of target terminals
        print("\n📋 모니터링 대상 터미널 목록:")
        terminals = monitor.find_target_terminals()
        if terminals:
            for i, term in enumerate(terminals, 1):
                print(f"   {i}. {term['title']}")
        else:
            print("   ⚠️ 대상 터미널을 찾을 수 없습니다")
            print("   → MINGW, bash, Claude, Terminal 등의 창을 열어주세요")

        # Wait on main thread
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
