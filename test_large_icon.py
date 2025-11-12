"""
큰 아이콘과 개선된 알림 테스트
"""
import sys
import os
import time

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_auto_approver import show_notification_popup

def test_large_icon():
    """큰 아이콘 알림 테스트"""
    print("=" * 60)
    print("큰 아이콘 알림 테스트")
    print("=" * 60)

    # 아이콘 파일 확인
    icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    if os.path.exists(icon_path):
        from PIL import Image
        img = Image.open(icon_path)
        print(f"[OK] 아이콘 크기: {img.size}")
    else:
        print(f"[ERROR] 아이콘 파일 없음")

    print("\n알림 테스트:")
    print("-" * 40)

    # 테스트 1: PowerShell
    print("\n1. PowerShell 승인")
    show_notification_popup(
        title="자동 승인 완료",
        message="'Y' 키가 전송되었습니다",
        window_info="PowerShell - Administrator",
        duration=5
    )
    time.sleep(2)

    # 테스트 2: Git Bash
    print("\n2. Git Bash 승인")
    show_notification_popup(
        title="자동 승인 완료",
        message="'2' 키가 전송되었습니다",
        window_info="Git Bash",
        duration=5
    )

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("\n특징:")
    print("- 256x256 크기의 큰 아이콘")
    print("- 중복 제거된 깔끔한 메시지")
    print("- 윈도우 정보와 시간 표시")
    print("=" * 60)

if __name__ == "__main__":
    test_large_icon()