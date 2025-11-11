#!/usr/bin/env python3
"""
Hybrid Monitor - 콘솔 버퍼 + 화면 캡처 OCR
모든 타입의 터미널/코딩 프로그램 출력 모니터링
"""
import sys
import time
import threading
import win32gui
import win32ui
import win32con
import win32api
import win32process
import win32console
import ctypes
from PIL import Image
import io

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# OCR 시도 (없어도 작동)
try:
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False
    print("⚠️ pytesseract 없음 - OCR 기능 비활성화 (콘솔 전용 모드)")


class HybridMonitor:
    """하이브리드 모니터링 - 콘솔 + 화면 캡처"""

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
            'option (1)',
            'Select (1)',
        ]

        # 대상 창 패턴
        self.target_patterns = [
            'MINGW', 'bash', 'Claude', 'Terminal', 'cmd',
            'PyCharm', 'IntelliJ', 'VSCode', 'Code',
            'Python', 'CataPro'
        ]

        # 중복 방지
        self.last_input_time = 0
        self.min_input_interval = 2

        # 현재 창
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

    def find_all_target_windows(self):
        """모든 대상 창 찾기"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and hwnd != self.current_hwnd:
                    if any(p in title for p in self.target_patterns):
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

    def try_read_console_buffer(self, pid):
        """콘솔 버퍼 읽기 시도 (콘솔 앱만)"""
        try:
            kernel32 = ctypes.windll.kernel32

            # 현재 콘솔 분리
            kernel32.FreeConsole()
            time.sleep(0.05)

            # 대상 콘솔 연결
            if not kernel32.AttachConsole(pid):
                # 연결 실패 - 콘솔 복원
                kernel32.AllocConsole()
                return None

            # 콘솔 버퍼 읽기
            try:
                console_handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
                csbi = console_handle.GetConsoleScreenBufferInfo()

                window = csbi['Window']
                width = window.Right - window.Left + 1

                # 마지막 15줄만
                lines_to_read = min(15, window.Bottom - window.Top + 1)
                start_y = max(0, window.Bottom - lines_to_read + 1)

                buffer_text = []
                for y in range(start_y, window.Bottom + 1):
                    try:
                        coord = win32console.PyCOORDType(window.Left, y)
                        text = console_handle.ReadConsoleOutputCharacter(width, coord)
                        buffer_text.append(text.strip())
                    except:
                        pass

                result = '\n'.join(buffer_text)

                # 콘솔 복원
                kernel32.FreeConsole()
                time.sleep(0.05)
                kernel32.AllocConsole()

                return result

            except Exception as e:
                # 실패 시 콘솔 복원
                kernel32.FreeConsole()
                kernel32.AllocConsole()
                return None

        except:
            return None

    def capture_window_screenshot(self, hwnd):
        """창 스크린샷 캡처"""
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
                return None

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            return img

        except Exception as e:
            return None

    def extract_text_from_image(self, img):
        """OCR로 텍스트 추출"""
        if not OCR_AVAILABLE:
            return ""

        try:
            width, height = img.size
            # 하단 40% 영역만 (최근 출력)
            bottom_region = img.crop((0, int(height * 0.6), width, height))

            text = pytesseract.image_to_string(bottom_region, lang='eng')
            return text

        except Exception as e:
            return ""

    def check_approval_pattern(self, text):
        """승인 패턴 확인"""
        if not text:
            return False

        text_lower = text.lower()

        for pattern in self.approval_patterns:
            if pattern.lower() in text_lower:
                return True

        return False

    def send_input_to_window(self, window):
        """창에 '1' 입력"""
        try:
            hwnd = window['hwnd']
            title = window['title']

            print(f"\n📤 '{title}'에 '1' 입력 중...")

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

            # 원래 창으로
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
        print("\n🔍 하이브리드 모니터링 시작...")
        print("   - 콘솔: 버퍼 직접 읽기")
        if OCR_AVAILABLE:
            print("   - GUI: 화면 캡처 + OCR")
        else:
            print("   - GUI: 비활성화 (pytesseract 없음)")

        while self.running:
            try:
                # 중복 방지
                if time.time() - self.last_input_time < self.min_input_interval:
                    time.sleep(0.5)
                    continue

                # 모든 대상 창 찾기
                windows = self.find_all_target_windows()

                if not windows:
                    time.sleep(1)
                    continue

                # 각 창 확인
                for window in windows:
                    text = None

                    # 1. 먼저 콘솔 버퍼 읽기 시도 (빠름)
                    text = self.try_read_console_buffer(window['pid'])

                    if text:
                        # 콘솔 버퍼 읽기 성공
                        if self.check_approval_pattern(text):
                            print(f"\n📋 [콘솔] 승인 요청 감지! ({window['title']})")
                            self.send_input_to_window(window)
                            break

                    # 2. 콘솔 버퍼 실패 시 화면 캡처 + OCR (느림)
                    elif OCR_AVAILABLE:
                        img = self.capture_window_screenshot(window['hwnd'])
                        if img:
                            text = self.extract_text_from_image(img)
                            if self.check_approval_pattern(text):
                                print(f"\n📋 [OCR] 승인 요청 감지! ({window['title']})")
                                self.send_input_to_window(window)
                                break

                time.sleep(1)

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

        print("✅ Hybrid Monitor 시작됨")

    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)


def main():
    print("=" * 70)
    print("🤖 Hybrid Monitor - 콘솔 + 화면 캡처")
    print("=" * 70)
    print()
    print("특징:")
    print("  ✅ 콘솔 창: Windows API로 버퍼 직접 읽기 (빠름)")
    print("  ✅ GUI 앱: 화면 캡처 + OCR로 읽기 (느림)")
    print("  ✅ PyCharm, VSCode, CataPro 등 모두 지원")
    print()
    print("모니터링 대상:")
    print("  - Git Bash, CMD, PowerShell, Terminal")
    print("  - PyCharm, IntelliJ, VSCode")
    print("  - CataPro 등 코딩 프로그램")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)

    monitor = HybridMonitor()

    try:
        # 대상 창 표시
        windows = monitor.find_all_target_windows()
        if windows:
            print(f"\n📋 발견된 창 ({len(windows)}개):")
            for i, win in enumerate(windows, 1):
                print(f"   {i}. {win['title']} (PID: {win['pid']})")
        else:
            print("\n⚠️ 대상 창을 찾을 수 없습니다")

        monitor.start()

        # 메인 대기
        while monitor.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Ctrl+C로 중단")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        monitor.stop()
        print(f"\n📊 총 {monitor.approval_count}회 자동 입력")
        print("🏁 프로그램 종료")


if __name__ == "__main__":
    main()
