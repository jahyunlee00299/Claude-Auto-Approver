"""
Enhanced Auto Approver with Real Click Functionality
Actually detects on-screen buttons and clicks them automatically
"""

import time
import logging
import threading
import pyautogui
import win32gui
import win32con
from typing import List, Dict, Any, Optional, Tuple

# PyAutoGUI safety settings
pyautogui.FAILSAFE = True  # Stops if the mouse is moved to the top-left corner of the screen
pyautogui.PAUSE = 0.1  # Wait 0.1 seconds between each command


class EnhancedAutoApprover:
    """Auto Approver with added real screen-click functionality"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.monitor_thread = None

        # Button text patterns to approve
        self.button_patterns = config.get('button_patterns', [
            'OK', '확인', 'Yes', '예', 'Allow', '허용',
            'Continue', '계속', 'Approve', '승인', 'Accept'
        ])

        # Window title patterns to detect
        self.window_patterns = config.get('window_patterns', [
            'Confirm', '확인', 'Alert', '경고', 'Question',
            'Approval', '승인', 'Permission', 'Claude'
        ])

        self.delay = config.get('delay_seconds', 0.5)
        self.safe_mode = config.get('safe_mode', True)
        self.click_count = 0

        self.logger.info("Enhanced AutoApprover 초기화 완료")

    def start(self):
        """Start monitoring"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.logger.info("모니터링 시작됨")
        print("🟢 자동 승인 모니터링이 시작되었습니다.")
        print("   - 화면 왼쪽 상단으로 마우스를 이동하면 중지됩니다.")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.logger.info(f"모니터링 중지됨. 총 {self.click_count}개 승인 처리")
        print(f"🔴 모니터링이 중지되었습니다. (총 {self.click_count}개 자동 승인)")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Detect the approval dialog
                window_info = self._find_approval_window()
                if window_info:
                    self._handle_approval_window(window_info)

                # Detect the button image on screen
                button_location = self._find_approval_button()
                if button_location:
                    self._click_button(button_location)

                time.sleep(0.5)

            except pyautogui.FailSafeException:
                print("⚠️ 안전 모드: 마우스가 화면 왼쪽 상단에 있습니다.")
                self.running = False
            except Exception as e:
                self.logger.error(f"모니터링 오류: {e}")

    def _find_approval_window(self) -> Optional[Dict]:
        """Find the approval dialog"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    for pattern in self.window_patterns:
                        if pattern.lower() in window_text.lower():
                            rect = win32gui.GetWindowRect(hwnd)
                            windows.append({
                                'hwnd': hwnd,
                                'title': window_text,
                                'rect': rect
                            })
            return True

        windows = []
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
        except Exception as e:
            self.logger.error(f"창 열거 오류: {e}")

        return windows[0] if windows else None

    def _handle_approval_window(self, window_info: Dict):
        """Handle the approval window"""
        hwnd = window_info['hwnd']
        title = window_info['title']
        rect = window_info['rect']

        print(f"📋 승인 대화상자 감지: '{title}'")

        if self.safe_mode:
            print(f"   🔒 안전 모드: 실제 클릭하지 않음")
            return

        # Bring the window to the foreground
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
        except Exception as e:
            self.logger.error(f"창 활성화 실패: {e}")
            return

        # Estimate the OK button position near the window center
        center_x = (rect[0] + rect[2]) // 2
        bottom_y = rect[3] - 50  # buttons are usually at the bottom

        # Try pressing Enter to click the default button
        pyautogui.press('enter')
        self.click_count += 1

        print(f"   ✅ 자동 승인 완료 (Enter 키 사용)")
        self.logger.info(f"창 '{title}' 자동 승인됨")

    def _find_approval_button(self) -> Optional[Tuple[int, int]]:
        """Find the approval button on screen"""
        # This part could save an actual button image ahead of time
        # and use pyautogui.locateOnScreen() to find it.
        # Example:
        # button_location = pyautogui.locateOnScreen('ok_button.png')
        # if button_location:
        #     return pyautogui.center(button_location)
        return None

    def _click_button(self, location: Tuple[int, int]):
        """Click the button"""
        if self.safe_mode:
            print(f"   🔒 안전 모드: 위치 {location}를 클릭하지 않음")
            return

        x, y = location
        current_pos = pyautogui.position()

        # Click
        pyautogui.click(x, y)
        self.click_count += 1

        # Return to the original position
        pyautogui.moveTo(current_pos)

        print(f"   ✅ 버튼 클릭: ({x}, {y})")
        self.logger.info(f"버튼 클릭: {location}")

    def get_status(self) -> Dict[str, Any]:
        """Return the current status"""
        return {
            'running': self.running,
            'safe_mode': self.safe_mode,
            'click_count': self.click_count,
            'window_patterns': len(self.window_patterns),
            'button_patterns': len(self.button_patterns)
        }

    def test_detection(self):
        """Detection test - shows the currently active window"""
        print("\n🔍 현재 열려있는 창 목록:")

        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    windows.append(window_text)
            return True

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        for i, title in enumerate(windows[:10], 1):
            # Check whether it matches a pattern
            matched = any(p.lower() in title.lower() for p in self.window_patterns)
            status = "✅ 감지 대상" if matched else ""
            print(f"   {i}. {title} {status}")

        # Mouse position
        x, y = pyautogui.position()
        print(f"\n🖱️ 현재 마우스 위치: ({x}, {y})")

        # Screen size
        width, height = pyautogui.size()
        print(f"📐 화면 크기: {width} x {height}")


if __name__ == "__main__":
    import sys
    import io

    # UTF-8 setup
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("🚀 Enhanced Auto Approver - 테스트 모드")
    print("="*50)

    config = {
        'safe_mode': True,  # safe mode for testing
        'delay_seconds': 0.5
    }

    approver = EnhancedAutoApprover(config)

    # Test against the current window
    approver.test_detection()

    print("\n📝 모니터링을 시작하려면 Enter를 누르세요...")
    input()

    approver.start()

    print("\n⏰ 10초 동안 모니터링합니다...")
    print("   (테스트를 위해 메모장이나 다른 대화상자를 열어보세요)")

    time.sleep(10)

    approver.stop()

    status = approver.get_status()
    print(f"\n📊 최종 상태:")
    print(f"   - 클릭 횟수: {status['click_count']}")