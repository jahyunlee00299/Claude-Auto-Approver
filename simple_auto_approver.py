#!/usr/bin/env python3
"""
간단한 완전 자동 승인 시스템
- 터미널 창을 모니터링
- 사용자가 idle 상태일 때 자동으로 활성 터미널에 "1" + Enter 입력
- OCR 불필요, 화면 변화 감지로 프롬프트 추정
"""

import sys
import time
import win32gui
import keyboard
import mouse

# UTF-8 설정
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class SimpleAutoApprover:
    """간단한 자동 승인 시스템"""

    def __init__(self, idle_seconds=3):
        self.running = False
        self.approval_count = 0
        self.last_activity_time = time.time()
        self.idle_threshold = idle_seconds

        # 터미널 창 패턴
        self.terminal_patterns = [
            'pycharm', 'cmd', 'powershell', 'windows terminal',
            'git bash', 'claude', 'python', 'mintty', 'terminal',
            'catapro', 'mingw', 'bash'
        ]

        # 중복 방지
        self.last_approval_window = None
        self.last_approval_time = 0
        self.min_approval_interval = 3  # 같은 창에 3초에 한 번만

        # 활동 카운터
        self.user_inputs = 0

        print(f"✅ 초기화 완료 (Idle 임계값: {idle_seconds}초)")

    def start_activity_monitoring(self):
        """사용자 활동 모니터링 시작"""
        def on_activity(*args):
            self.last_activity_time = time.time()
            self.user_inputs += 1

        # 키보드 모니터링
        keyboard.on_press(on_activity)

        # 마우스 모니터링 (mouse 모듈 hook 사용)
        mouse.hook(on_activity)

        print("✅ 사용자 활동 모니터링 시작")

    def is_user_idle(self) -> bool:
        """사용자 idle 확인"""
        return (time.time() - self.last_activity_time) >= self.idle_threshold

    def find_all_terminals(self):
        """모든 터미널 창 찾기 (여러 PyCharm 등, 다른 모니터 포함)"""
        terminals = []

        def callback(hwnd, extra):
            try:
                # 보이는 창만 체크 (다른 모니터 포함)
                if not win32gui.IsWindowVisible(hwnd):
                    return True

                # 창이 실제로 존재하는지 확인
                if not win32gui.IsWindow(hwnd):
                    return True

                title = win32gui.GetWindowText(hwnd)
                if not title:  # 제목이 없는 창은 제외
                    return True

                title_lower = title.lower()

                # 터미널 패턴 매칭
                for pattern in self.terminal_patterns:
                    if pattern in title_lower:
                        # 중복 방지
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
        """현재 활성화된 터미널 찾기"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return None

            title = win32gui.GetWindowText(hwnd).lower()

            # 터미널 패턴 매칭
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
        """자동 승인 여부 판단"""
        if window_info is None:
            return False

        hwnd = window_info['hwnd']

        # 중복 방지: 같은 창에 너무 자주 승인하지 않음
        if hwnd == self.last_approval_window:
            if time.time() - self.last_approval_time < self.min_approval_interval:
                return False

        return True

    def auto_approve(self, window_info):
        """자동 승인 실행"""
        try:
            hwnd = window_info['hwnd']
            title = window_info['title']

            # 창을 강제로 전면에 가져오기
            try:
                # 창 활성화 시도
                win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)  # 창 전환 충분히 대기
            except Exception as e:
                print(f"   ⚠️ 창 전환 실패: {e}")
                return False

            # "1"만 입력 (Enter 없음)
            keyboard.press('1')
            time.sleep(0.1)
            keyboard.release('1')
            time.sleep(0.2)

            # PyCharm인 경우 모든 탭 순회하며 입력
            if 'pycharm' in title.lower() or 'gdi+' in title.lower():
                # 최대 10개 탭 확인 (충분히 많이)
                for tab_index in range(10):
                    # Alt+Right로 다음 탭으로 이동
                    keyboard.press('alt')
                    time.sleep(0.05)
                    keyboard.press('right')
                    time.sleep(0.05)
                    keyboard.release('right')
                    keyboard.release('alt')
                    time.sleep(0.3)

                    # 다음 탭에 "1"만 입력 (Enter 없음)
                    keyboard.press('1')
                    time.sleep(0.1)
                    keyboard.release('1')
                    time.sleep(0.2)

                # 원래 탭으로 돌아가기 (Alt+Left 10번)
                for _ in range(10):
                    keyboard.press('alt')
                    time.sleep(0.05)
                    keyboard.press('left')
                    time.sleep(0.05)
                    keyboard.release('left')
                    keyboard.release('alt')
                    time.sleep(0.1)

            # 기록
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
        """메인 루프"""
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

        # 활동 모니터링 시작
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

                # 정기 체크
                if current_time - last_check >= check_interval:
                    # Idle 상태 확인
                    if self.is_user_idle():
                        # 모든 터미널 찾기
                        terminals = self.find_all_terminals()

                        if terminals:
                            print(f"💤 Idle 감지 + 터미널 {len(terminals)}개 발견")

                            # 각 터미널에 자동 승인
                            for terminal in terminals:
                                if self.should_approve(terminal):
                                    self.auto_approve(terminal)
                                    time.sleep(0.2)  # 각 창 사이 대기

                    last_check = current_time

                # 10초마다 상태 출력
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
    """메인 함수"""
    import argparse

    # stdout 버퍼링 비활성화
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