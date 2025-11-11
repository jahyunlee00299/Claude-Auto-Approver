#!/usr/bin/env python3
"""
Screen OCR Monitor
화면 캡처 + OCR로 다른 터미널의 출력을 읽어 자동 승인
"""
import sys
import time
import threading
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import pytesseract
import io
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Tesseract 경로 설정 (필요시 수정)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class ScreenOCRMonitor:
    """화면 OCR 기반 터미널 모니터링"""

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
        ]

        # 터미널 패턴
        self.terminal_patterns = ['MINGW', 'bash', 'Claude', 'Terminal']

        # 중복 방지
        self.last_input_time = 0
        self.min_input_interval = 3

        # 현재 창
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

    def find_target_terminals(self):
        """대상 터미널 창 찾기"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and hwnd != self.current_hwnd:
                    if any(p in title for p in self.terminal_patterns):
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

        except Exception as e:
            print(f"   ⚠️ 캡처 실패: {e}")
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

        except Exception as e:
            print(f"   ⚠️ OCR 실패: {e}")
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
        """터미널에 '1' 입력"""
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

            # '1' 입력
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.last_input_time = time.time()

            print(f"   ✅ '1' 입력 완료! (총 {self.approval_count}회)")

            # 원래 창으로 복귀
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
        print("\n🔍 화면 OCR 모니터링 시작...")

        while self.running:
            try:
                # 중복 방지
                if time.time() - self.last_input_time < self.min_input_interval:
                    time.sleep(1)
                    continue

                # 대상 터미널 찾기
                terminals = self.find_target_terminals()

                if not terminals:
                    time.sleep(2)
                    continue

                # 각 터미널 확인
                for terminal in terminals:
                    # 화면 캡처
                    img = self.capture_window(terminal['hwnd'])
                    if not img:
                        continue

                    # OCR로 텍스트 추출
                    text = self.extract_text_from_image(img)

                    # 승인 패턴 확인
                    if self.check_approval_pattern(text):
                        print(f"\n📋 승인 요청 감지! (창: {terminal['title']})")
                        print(f"   추출된 텍스트: {text[:100]}...")
                        self.send_input_to_terminal(terminal)
                        break

                time.sleep(2)  # OCR은 느리므로 2초 간격

            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(2)

        print("\n🛑 모니터링 종료")

    def start(self):
        """모니터링 시작"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ Screen OCR Monitor 시작됨")

    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)


def main():
    print("=" * 70)
    print("🤖 Screen OCR Monitor")
    print("=" * 70)
    print()
    print("작동 방식:")
    print("  1. 다른 터미널 창을 찾습니다")
    print("  2. 화면을 캡처하여 OCR로 텍스트를 읽습니다")
    print("  3. '1. Yes' 등의 승인 패턴을 감지합니다")
    print("  4. 패턴 발견 시 해당 창에 '1'을 입력합니다 (Enter 없음)")
    print()
    print("⚠️ 주의:")
    print("  - Tesseract OCR이 설치되어 있어야 합니다")
    print("  - OCR 처리로 인해 약간의 지연이 있을 수 있습니다")
    print()
    print("종료: Ctrl+C")
    print("=" * 70)

    # win32console import
    global win32console
    import win32console

    monitor = ScreenOCRMonitor()

    try:
        # 대상 터미널 확인
        terminals = monitor.find_target_terminals()
        if terminals:
            print("\n📋 모니터링 대상 터미널:")
            for i, term in enumerate(terminals, 1):
                print(f"   {i}. {term['title']}")
        else:
            print("\n⚠️ 대상 터미널을 찾을 수 없습니다")

        monitor.start()

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
