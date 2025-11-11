#!/usr/bin/env python3
"""
Approval Notifier - 승인 요청 감지 시 알림만 표시 (자동 입력 없음)
백그라운드에서 실행되며 승인 프롬프트 감지 시 Windows 알림 표시
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

# UTF-8 설정 (이미 설정되어 있지 않은 경우에만)
if sys.platform == 'win32':
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except:
            pass  # 이미 설정되어 있거나 변경할 수 없음


class ApprovalNotifier:
    """승인 요청 감지 및 알림"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.notification_count = 0

        # 승인 패턴
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

        # 대상 창 패턴
        self.terminal_patterns = [
            'MINGW', 'bash', 'Claude', 'Terminal', 'cmd',
            'PowerShell', 'PyCharm', 'VSCode', 'Code', 'Python',
            'catapro', 'Console', 'Shell'
        ]

        # 중복 방지 - 창별로 추적
        self.last_notification_per_window = {}  # {hwnd: last_time}
        self.min_notification_interval = 10  # 같은 창에서 10초에 한 번만 알림

        # 마지막으로 감지한 텍스트 (같은 내용 반복 방지)
        self.last_detected_text = ""
        self.last_detected_time = 0

        print("✅ Approval Notifier 초기화 완료")

    def find_terminal_windows(self):
        """모든 터미널/IDE 창 찾기"""
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
        """현재 콘솔 화면 버퍼 읽기"""
        try:
            console_handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
            csbi = console_handle.GetConsoleScreenBufferInfo()
            cursor_pos = csbi['CursorPosition']

            # 최근 20줄 읽기
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
        """다른 프로세스의 콘솔 버퍼 읽기 - 현재는 비활성화 (stdout 문제)"""
        # FreeConsole()이 현재 프로그램의 stdout을 닫아버리는 문제로 비활성화
        # GUI 창 감지로 대체
        return None

    def check_approval_pattern(self, text):
        """승인 패턴 확인"""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.approval_patterns:
            if pattern.lower() in text_lower:
                return True
        return False

    def should_notify(self, window_id, text=""):
        """알림을 보내야 하는지 확인 (중복 방지)"""
        current_time = time.time()

        # 1. 같은 창에서 너무 자주 알림 방지
        if window_id in self.last_notification_per_window:
            last_time = self.last_notification_per_window[window_id]
            if current_time - last_time < self.min_notification_interval:
                return False

        # 2. 같은 텍스트 내용 반복 방지
        if text and text == self.last_detected_text:
            if current_time - self.last_detected_time < self.min_notification_interval:
                return False

        return True

    def show_notification(self, window_title="", source_type="", window_id=None, text=""):
        """Windows 알림 표시"""
        # 중복 체크
        if not self.should_notify(window_id or window_title, text):
            return

        try:
            # 창 제목 단순화 (너무 긴 경우)
            if len(window_title) > 50:
                display_title = window_title[:47] + "..."
            else:
                display_title = window_title

            # 소스 타입 표시
            source_label = ""
            if source_type == "console":
                source_label = "📟 터미널"
            elif source_type == "gui":
                source_label = "🖥️ GUI 창"
            else:
                source_label = "📋 창"

            # Windows 알림 생성
            toast = Notification(
                app_id="Claude Auto Approver",
                title="🔔 승인 요청",
                msg=f"{source_label}: {display_title}\n\nClaude Code가 승인을 기다리고 있습니다.",
                duration="long",
                icon=""
            )

            # 소리 설정
            toast.set_audio(audio.Default, loop=False)

            # 알림 표시
            toast.show()

            # 추가로 시스템 비프음
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            # 중복 방지 정보 업데이트
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
            # 알림 실패해도 소리는 재생
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass

    def check_window_for_approval(self):
        """모든 창에서 승인 프롬프트 확인 - 터미널 및 콘솔 창 포함"""
        def callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                title_lower = title.lower()

                # 제외할 창 (일반 에디터, README 등)
                exclude_keywords = ['readme', '.md', '.txt', '.py', 'editor']
                if any(exc in title_lower for exc in exclude_keywords):
                    return True

                # 터미널 패턴에 해당하는 창 찾기
                is_terminal = any(pattern.lower() in title_lower for pattern in self.terminal_patterns)

                # 승인 대화상자 키워드
                approval_keywords = ['question', 'approval', 'proceed?', 'permission', 'authorize']
                has_approval_keyword = any(keyword in title_lower for keyword in approval_keywords)

                # 터미널 창이거나 승인 키워드가 있는 창
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
        """메인 모니터링 루프"""
        print("\n🔍 백그라운드 모니터링 시작...")
        print("   - 모든 터미널/PyCharm 콘솔 모니터링")
        print("   - GUI 창 제목 모니터링")
        print("   - 승인 요청 감지 시 Windows 알림 표시")
        print("   - 자동 입력 없음 (알림만)")
        print()

        while self.running:
            try:
                detected = False

                # 1. 현재 콘솔 화면 읽기
                screen_text = self.read_console_screen_buffer()
                if screen_text and self.check_approval_pattern(screen_text):
                    print(f"\n📋 [현재 콘솔] 승인 요청 패턴 감지!")
                    self.show_notification("현재 콘솔", "console", window_id="current_console", text=screen_text)
                    detected = True

                # 2. 활성 창(foreground) 확인
                if not detected:
                    try:
                        fg_hwnd = win32gui.GetForegroundWindow()
                        fg_title = win32gui.GetWindowText(fg_hwnd)
                        fg_title_lower = fg_title.lower()

                        # 활성 창이 터미널인지 확인
                        is_terminal = any(pattern.lower() in fg_title_lower for pattern in self.terminal_patterns)

                        # 제외 키워드 확인
                        exclude_keywords = ['readme', '.md', '.txt', '.py', 'editor']
                        is_excluded = any(exc in fg_title_lower for exc in exclude_keywords)

                        # 터미널이고 제외 대상이 아니면 감지
                        if is_terminal and not is_excluded and fg_title:
                            print(f"\n📋 [활성 터미널] 창 감지! ({fg_title})")
                            self.show_notification(fg_title, "terminal", window_id=fg_hwnd, text=fg_title)
                            detected = True
                    except:
                        pass

                # 3. 모든 터미널/콘솔 창 확인 (백업)
                if not detected:
                    approval_windows = self.check_window_for_approval()
                    if approval_windows:
                        hwnd = approval_windows[0]['hwnd']
                        window_title = approval_windows[0]['title']

                        # 제외 키워드 다시 확인
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
        """모니터링 시작"""
        if self.running:
            print("⚠️ 이미 실행 중입니다")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ 백그라운드 모니터링 시작됨")

    def stop(self):
        """모니터링 중지"""
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

        # 메인 스레드 대기
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
