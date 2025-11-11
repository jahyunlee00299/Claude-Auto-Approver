#!/usr/bin/env python3
"""
OCR-based Approval Notifier
화면 OCR로 다른 터미널의 승인 요청을 감지하고 알림 표시
"""
import sys
import time
import threading
import win32gui
import win32ui
import win32con
import win32console
import winsound
from PIL import Image
import pytesseract
import io
from winotify import Notification, audio

# No UTF-8 configuration - use ASCII only for output to avoid encoding issues

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRNotifier:
    """OCR-based approval detection and notification"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.notification_count = 0
        self.current_hwnd = None

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

        # Exclude keywords
        self.exclude_keywords = ['readme', '.md', '.txt', '.py', 'editor']

        # Duplicate prevention - track per window
        self.last_notification_per_window = {}
        self.min_notification_interval = 15  # Notify once per 15 seconds per window

        # Current window
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

        print("[OK] OCR Notifier initialized")

    def find_target_windows(self):
        """모니터링 대상 창 찾기 - 모든 보이는 창 (현재 창 포함)"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # 현재 창도 포함
                    # 제외 키워드 확인
                    title_lower = title.lower()
                    is_excluded = any(exc in title_lower for exc in self.exclude_keywords)

                    if not is_excluded:
                        windows.append({'hwnd': hwnd, 'title': title})
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def capture_window(self, hwnd):
        """창 스크린샷 캡처"""
        try:
            # 창 크기 가져오기
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            # 최소 크기 확인
            if width < 100 or height < 100:
                return None

            # 디바이스 컨텍스트
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # 비트맵 생성
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # 화면 복사
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            # PIL Image로 변환
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            # 정리
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            return img

        except Exception:
            return None

    def extract_text_from_image(self, img):
        """이미지에서 텍스트 추출 (OCR)"""
        try:
            # 이미지 하단 일부만 (최근 출력 부분)
            width, height = img.size
            # 하단 30% 영역만 크롭
            bottom_region = img.crop((0, int(height * 0.7), width, height))

            # OCR 수행
            text = pytesseract.image_to_string(bottom_region, lang='eng')
            return text

        except Exception:
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

    def should_notify(self, hwnd):
        """알림을 보내야 하는지 확인 (중복 방지)"""
        current_time = time.time()

        # 같은 창에서 너무 자주 알림 방지
        if hwnd in self.last_notification_per_window:
            last_time = self.last_notification_per_window[hwnd]
            if current_time - last_time < self.min_notification_interval:
                return False

        return True

    def show_notification(self, window_title):
        """Windows 알림 표시"""
        try:
            # 창 제목 단순화
            if len(window_title) > 50:
                display_title = window_title[:47] + "..."
            else:
                display_title = window_title

            # Windows 알림 생성
            toast = Notification(
                app_id="Claude Auto Approver",
                title="Approval Request",
                msg=f"Claude Code is waiting for approval in:\n{display_title}",
                duration="long"
            )

            # 소리 설정
            toast.set_audio(audio.Default, loop=False)

            # 알림 표시
            toast.show()

            # 추가로 시스템 비프음
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            self.notification_count += 1
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] Notification sent: {display_title}")

        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")
            # 알림 실패해도 소리는 재생
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass

    def monitor_loop(self):
        """메인 모니터링 루프"""
        print("\n" + "="*60)
        print("OCR-based Approval Notifier")
        print("="*60)
        print("\nMonitoring all windows via screen OCR...")
        print(f"Notification interval: {self.min_notification_interval} seconds")
        print("\nPress Ctrl+C to stop\n")

        while self.running:
            try:
                # 대상 창 찾기
                windows = self.find_target_windows()

                # 각 창 확인 (최대 5개까지만)
                for window in windows[:5]:
                    hwnd = window['hwnd']
                    title = window['title']

                    # 화면 캡처
                    img = self.capture_window(hwnd)
                    if not img:
                        continue

                    # OCR로 텍스트 추출
                    text = self.extract_text_from_image(img)

                    # 승인 패턴 확인
                    if self.check_approval_pattern(text):
                        # 중복 체크
                        if self.should_notify(hwnd):
                            print(f"\n[DETECTED] Approval request in: {title}")
                            self.show_notification(title)
                            self.last_notification_per_window[hwnd] = time.time()

                time.sleep(3)  # OCR은 느리므로 3초 간격

            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                time.sleep(3)

        print("\n[INFO] Monitoring stopped")

    def start(self):
        """모니터링 시작"""
        if self.running:
            print("[WARNING] Already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("[OK] OCR Notifier started")

    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        print("[INFO] Monitoring stopped")


def main():
    print("=" * 70)
    print("OCR-based Claude Approval Notifier")
    print("=" * 70)
    print()
    print("Features:")
    print("  - Monitors all visible windows via screen OCR")
    print("  - Detects approval prompts from Claude Code")
    print("  - Shows Windows notifications")
    print("  - NO automatic input (notification only)")
    print()
    print("Requirements:")
    print("  - Tesseract OCR must be installed")
    print("  - May have slight delay due to OCR processing")
    print()
    print("Exit: Ctrl+C")
    print("=" * 70)
    print()

    notifier = OCRNotifier()

    try:
        # 대상 창 확인
        windows = notifier.find_target_windows()
        if windows:
            print(f"\nFound {len(windows)} windows to monitor")
        else:
            print("\n[WARNING] No windows found to monitor")

        notifier.start()

        # 메인 스레드 대기
        while notifier.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        notifier.stop()
        print(f"\n[STATS] Total notifications: {notifier.notification_count}")
        print("[INFO] Program terminated")


if __name__ == "__main__":
    main()
