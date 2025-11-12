"""
향상된 알림 시스템 테스트
"""
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_auto_approver import show_notification_popup

def test_enhanced_notification():
    """향상된 알림 시스템 테스트"""
    print("향상된 알림 시스템 테스트를 시작합니다...")
    print("-" * 50)

    # 테스트 1: 윈도우 정보가 있는 경우
    print("\n[테스트 1] 윈도우 정보 포함 알림")
    show_notification_popup(
        title="자동 승인 완료",
        message="'Y' 키가 전송되었습니다",
        window_info="PowerShell - Administrator: Claude Code",
        duration=3
    )

    print("\n[테스트 2] 윈도우 정보 없는 알림")
    show_notification_popup(
        title="자동 승인 완료",
        message="승인 처리가 완료되었습니다",
        duration=3
    )

    print("\n[테스트 3] 다양한 윈도우 타입")
    show_notification_popup(
        title="자동 승인 완료",
        message="'2' 키가 전송되었습니다",
        window_info="MINGW64:/c/Users/Jahyun/Projects - Git Bash",
        duration=3
    )

    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("\n참고:")
    print("- logo.png 파일이 있으면 알림에 로고가 표시됩니다")
    print("- 각 알림에는 처리 시간과 윈도우 정보가 포함됩니다")
    print("- 알림은 Windows Action Center에 기록됩니다")

if __name__ == "__main__":
    test_enhanced_notification()