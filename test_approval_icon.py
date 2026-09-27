"""
Notification test using approval_icon.png
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_auto_approver import show_notification_popup

def test_approval_icon():
    """Test a notification that includes the approval icon"""
    print("승인 아이콘 알림 테스트를 시작합니다...")
    print("-" * 50)

    # Check for the icon file
    icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    if os.path.exists(icon_path):
        print(f"[OK] 승인 아이콘 파일 확인: {icon_path}")
    else:
        print(f"[ERROR] 승인 아이콘 파일이 없습니다: {icon_path}")

    print("\n[테스트 1] PowerShell 승인")
    show_notification_popup(
        title="자동 승인 완료",
        message="'Y' 키가 전송되었습니다",
        window_info="PowerShell - Administrator: Claude Code",
        duration=3
    )

    print("\n[테스트 2] Git Bash 승인")
    show_notification_popup(
        title="자동 승인 완료",
        message="'2' 키가 전송되었습니다",
        window_info="MINGW64:/c/Users/<user>/Projects - Git Bash",
        duration=3
    )

    print("\n[테스트 3] 일반 다이얼로그 승인")
    show_notification_popup(
        title="자동 승인 완료",
        message="승인 처리가 완료되었습니다",
        window_info="Question - Application Dialog",
        duration=3
    )

    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("\n알림 특징:")
    print("- 귀여운 캐릭터 아이콘 (approval_icon.png)")
    print("- 처리된 윈도우 정보 표시")
    print("- 정확한 처리 시간 기록")
    print("- Windows Action Center에 기록")

if __name__ == "__main__":
    test_approval_icon()