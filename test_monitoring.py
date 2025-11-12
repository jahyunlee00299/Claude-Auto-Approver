#!/usr/bin/env python3
"""
모니터링 기능 테스트
"""
import sys
import io
import time
import win32gui

# UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import the auto approver
from ocr_auto_approver import OCRAutoApprover

def test_window_capture():
    """테스트: 윈도우 캡처가 잘 되는지 확인"""
    print("="*80)
    print("윈도우 캡처 테스트")
    print("="*80)
    print()

    approver = OCRAutoApprover()

    # Find target windows
    windows = approver.find_target_windows()
    print(f"발견된 타겟 윈도우: {len(windows)}개\n")

    if not windows:
        print("⚠️  타겟 윈도우를 찾지 못했습니다.")
        return

    # Test capture on first 3 windows
    for i, win in enumerate(windows[:3], 1):
        print(f"{i}. 윈도우 테스트: {win['title'][:50]}")
        print(f"   HWND: {win['hwnd']}")
        print(f"   크기: {win['pos'][2]-win['pos'][0]}x{win['pos'][3]-win['pos'][1]}")

        # Try to capture
        try:
            img = approver.capture_window(win['hwnd'])
            if img:
                width, height = img.size
                print(f"   ✓ 캡처 성공: {width}x{height}")

                # Try OCR (fast mode)
                text = approver.extract_text_from_image(img, fast_mode=True)
                text_preview = text[:100].replace('\n', ' ').strip()
                print(f"   ✓ OCR 추출: {len(text)} 문자")
                if text_preview:
                    print(f"   미리보기: {text_preview}...")

                # Check for approval pattern
                has_approval = approver.check_approval_pattern(text)
                print(f"   승인 패턴: {'✓ 발견' if has_approval else '없음'}")
            else:
                print(f"   ✗ 캡처 실패")
        except Exception as e:
            print(f"   ✗ 오류: {e}")

        print()

    print("="*80)

def test_idle_detection():
    """테스트: 유휴 시간 감지"""
    print("="*80)
    print("유휴 시간 감지 테스트")
    print("="*80)
    print()

    approver = OCRAutoApprover()

    print("5초 동안 유휴 시간을 감지합니다...")
    print("(마우스나 키보드를 사용하면 시간이 리셋됩니다)")
    print()

    for i in range(5):
        idle_time = approver.get_idle_time()
        is_idle = approver.is_user_idle()
        print(f"  {i+1}초: 유휴 시간 = {idle_time:.1f}초, 유휴 상태 = {is_idle}")
        time.sleep(1)

    print()
    print("="*80)

def test_foreground_window():
    """테스트: 현재 활성 윈도우 감지"""
    print("="*80)
    print("현재 활성 윈도우 감지 테스트")
    print("="*80)
    print()

    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)

        print(f"현재 활성 윈도우:")
        print(f"  제목: {title}")
        print(f"  HWND: {hwnd}")
        print(f"  클래스: {class_name}")
    except Exception as e:
        print(f"오류: {e}")

    print()
    print("="*80)

if __name__ == "__main__":
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                      모니터링 기능 테스트                                 ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()

    # Run tests
    test_foreground_window()
    print()
    test_window_capture()
    print()
    test_idle_detection()

    print("\n✓ 모든 테스트 완료\n")
