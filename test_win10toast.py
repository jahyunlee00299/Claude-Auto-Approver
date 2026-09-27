"""
win10toast notification test - verify the actual popup
"""
from win10toast import ToastNotifier
import time

def test_win10toast():
    """Windows notification test using win10toast"""
    print("win10toast 알림 테스트를 시작합니다...")

    toaster = ToastNotifier()

    try:
        print("알림을 표시합니다... (5초간 표시)")
        print("우측 하단을 확인하세요!")

        # Show notification (for 5 seconds)
        toaster.show_toast(
            "Claude Auto Approver 테스트",
            "이 알림이 우측 하단에 보이나요?",
            duration=5,
            threaded=False  # run synchronously (wait until the notification disappears)
        )

        print("알림이 표시되었습니다!")
        print("우측 하단에 팝업이 보였나요?")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_win10toast()
    input("\n아무 키나 누르면 종료...")
