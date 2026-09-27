#!/usr/bin/env python3
"""
Approval Notifier - shows a notification only when an approval request is detected (no auto-input)
Runs in the background and shows a Windows notification when an approval prompt is detected
"""
import sys
import time
import threading
import win32gui
import win32console
import win32con
import win32process
import winsound
import ctypes
import io
from winotify import Notification, audio

# UTF-8 setup (only if not already set)
if sys.platform == 'win32':
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except:
            pass  # Already set, or cannot be changed


class ApprovalNotifier:
    """Detects approval requests and shows notifications"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.notification_count = 0

        # Approval patterns
        self.approval_patterns = [
            'Do you want to proceed?',
            '1. Yes',
            '2. Yes, and don\'t ask again',
            '3. No, and tell Claude',
            '1. Approve',
            '1. OK',
            '1) Yes',
            '1: Yes',
            'option (1-',
            'Select (1)',
        ]

        # Target window patterns
        self.terminal_patterns = [
            'MINGW', 'bash', 'Claude', 'Terminal', 'cmd',
            'PowerShell', 'PyCharm', 'VSCode', 'Code', 'Python',
            'catapro', 'Console', 'Shell'
        ]

        # Duplicate-prevention - tracked per window
        self.last_notification_per_window = {}  # {hwnd: last_time}
        self.min_notification_interval = 10  # notify at most once every 10s per window

        # Last detected text (to avoid repeating the same content)
        self.last_detected_text = ""
        self.last_detected_time = 0

        print("✅ Approval Notifier 초기화 완료")

    def find_terminal_windows(self):
        """Find all terminal/IDE windows"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and any(p in title for p in self.terminal_patterns):
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        windows.append({'hwnd': hwnd, 'title': title, 'pid': pid})
                    except:
                        windows.append({'hwnd': hwnd, 'title': title, 'pid': None})
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def read_console_screen_buffer(self):
        """Read the current console screen buffer"""
        try:
            console_handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
            csbi = console_handle.GetConsoleScreenBufferInfo()
            cursor_pos = csbi['CursorPosition']

            # Read the last 20 lines
            lines_to_read = min(20, cursor_pos.Y + 1)
            start_y = max(0, cursor_pos.Y - lines_to_read + 1)

            buffer_text = []
            for y in range(start_y, cursor_pos.Y + 1):
                try:
                    coord = win32console.PyCOORDType(0, y)
                    size = csbi['Size'].X
                    text = console_handle.ReadConsoleOutputCharacter(size, coord)
                    buffer_text.append(text.strip())
                except:
                    pass

            return '\n'.join(buffer_text)
        except Exception:
            return ""

    def read_other_console_buffer(self, pid):
        """Read another process's console buffer - currently disabled (stdout issue)"""
        # Disabled because FreeConsole() closes the current program's stdout
        # Replaced with GUI window detection instead
        return None

    def check_approval_pattern(self, text):
        """Check the approval pattern"""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.approval_patterns:
            if pattern.lower() in text_lower:
                return True
        return False

    def should_notify(self, window_id, text=""):
        """Check whether a notification should be sent (duplicate-prevention)"""
        current_time = time.time()

        # 1. Prevent notifying too often for the same window
        if window_id in self.last_notification_per_window:
            last_time = self.last_notification_per_window[window_id]
            if current_time - last_time < self.min_notification_interval:
                return False

        # 2. Prevent repeating the same text content
        if text and text == self.last_detected_text:
            if current_time - self.last_detected_time < self.min_notification_interval:
                return False

        return True

    def show_notification(self, window_title="", source_type="", window_id=None, text=""):
        """Show a Windows notification"""
        # Duplicate check
        if not self.should_notify(window_id or window_title, text):
            return

        try:
            # Simplify the window title (if too long)
            if len(window_title) > 50:
                display_title = window_title[:47] + "..."
            else:
                display_title = window_title

            # Source type label
            source_label = ""
            if source_type == "console":
                source_label = "📟 터미널"
            elif source_type == "gui":
                source_label = "🖥️ GUI 창"
            else:
                source_label = "📋 창"

            # Create the Windows notification
            toast = Notification(
                app_id="Claude Auto Approver",
                title="🔔 승인 요청",
                msg=f"{source_label}: {display_title}\n\nClaude Code가 승인을 기다리고 있습니다.",
                duration="long",
                icon=""
            )

            # Set the sound
            toast.set_audio(audio.Default, loop=False)

            # Show the notification
            toast.show()

            # Also play a system beep
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            # Update duplicate-prevention info
            current_time = time.time()
            if window_id:
                self.last_notification_per_window[window_id] = current_time
            if text:
                self.last_detected_text = text
                self.last_detected_time = current_time

            self.notification_count += 1
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] 🔔 알림: {source_label} - {display_title}")

        except Exception as e:
            print(f"⚠️ 알림 표시 실패: {e}")
            # Still play the sound even if the notification fails
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass

    def check_window_for_approval(self):
        """Check all windows for an approval prompt - includes terminal and console windows"""
        def callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                title_lower = title.lower()

                # Windows to exclude (regular editors, README, etc.)
                exclude_keywords = ['readme', '.md', '.txt', '.py', 'editor']
                if any(exc in title_lower for exc in exclude_keywords):
                    return True

                # Find windows matching the terminal patterns
                is_terminal = any(pattern.lower() in title_lower for pattern in self.terminal_patterns)

                # Approval dialog keywords
                approval_keywords = ['question', 'approval', 'proceed?', 'permission', 'authorize']
                has_approval_keyword = any(keyword in title_lower for keyword in approval_keywords)

                # A terminal window, or one with an approval keyword
                if is_terminal or has_approval_keyword:
                    result.append({'hwnd': hwnd, 'title': title})
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def monitor_loop(self):
        """Main monitoring loop"""
        print("\n🔍 백그라운드 모니터링 시작...")
        print("   - 모든 터미널/PyCharm 콘솔 모니터링")
        print("   - GUI 창 제목 모니터링")
        print("   - 승인 요청 감지 시 Windows 알림 표시")
        print("   - 자동 입력 없음 (알림만)")
        print()

        while self.running:
            try:
                detected = False

                # 1. Read the current console screen
                screen_text = self.read_console_screen_buffer()
                if screen_text and self.check_approval_pattern(screen_text):
                    print(f"\n📋 [현재 콘솔] 승인 요청 패턴 감지!")
                    self.show_notification("현재 콘솔", "console", window_id="current_console", text=screen_text)
                    detected = True

                # 2. Check the foreground window
                if not detected:
                    try:
                        fg_hwnd = win32gui.GetForegroundWindow()
                        fg_title = win32gui.GetWindowText(fg_hwnd)
                        fg_title_lower = fg_title.lower()

                        # Check whether the foreground window is a terminal
                        is_terminal = any(pattern.lower() in fg_title_lower for pattern in self.terminal_patterns)

                        # Check the exclusion keywords
                        exclude_keywords = ['readme', '.md', '.txt', '.py', 'editor']
                        is_excluded = any(exc in fg_title_lower for exc in exclude_keywords)

                        # Detect if it's a terminal and not excluded
                        if is_terminal and not is_excluded and fg_title:
                            print(f"\n📋 [활성 터미널] 창 감지! ({fg_title})")
                            self.show_notification(fg_title, "terminal", window_id=fg_hwnd, text=fg_title)
                            detected = True
                    except:
                        pass

                # 3. Check all terminal/console windows (fallback)
                if not detected:
                    approval_windows = self.check_window_for_approval()
                    if approval_windows:
                        hwnd = approval_windows[0]['hwnd']
                        window_title = approval_windows[0]['title']

                        # Re-check the exclusion keywords
                        exclude_keywords = ['readme', '.md', '.txt', '.py', 'editor']
                        if not any(exc in window_title.lower() for exc in exclude_keywords):
                            print(f"\n📋 [터미널] 승인 가능 창 감지! ({window_title})")
                            self.show_notification(window_title, "terminal", window_id=hwnd, text=window_title)
                            detected = True

                time.sleep(1)

            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(2)

        print("\n🛑 모니터링 종료")

    def start(self):
        """Start monitoring"""
        if self.running:
            print("⚠️ 이미 실행 중입니다")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ 백그라운드 모니터링 시작됨")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("⏹️ 모니터링 중지됨")


def main():
    print("=" * 70)
    print("🔔 Claude Code Approval Notifier")
    print("=" * 70)
    print()
    print("기능:")
    print("  ✅ 백그라운드에서 승인 요청 모니터링")
    print("  ✅ 승인 프롬프트 감지 시 Windows 알림 표시")
    print("  ✅ 소리 알림 포함")
    print("  ⚠️ 자동 입력 없음 (알림만)")
    print()
    print("감지 패턴:")
    print("  - 'Do you want to proceed?'")
    print("  - '1. Yes' / '2. Yes, and don't ask again'")
    print("  - 'option (1-' 형태의 선택 프롬프트")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)
    print()

    notifier = ApprovalNotifier()

    try:
        notifier.start()

        # Wait on the main thread
        print("💤 백그라운드 실행 중... (최소화해도 계속 동작)")
        while notifier.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Ctrl+C로 중단")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        notifier.stop()
        print(f"\n📊 총 {notifier.notification_count}회 알림 표시")
        print("🏁 프로그램 종료")


if __name__ == "__main__":
    main()
