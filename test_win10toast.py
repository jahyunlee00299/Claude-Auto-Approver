"""
win10toast 알림 테스트 - 실제 팝업 확인
"""
from win10toast import ToastNotifier
import time

def test_win10toast():
    """win10toast로 윈도우 알림 테스트"""
    print("win10toast 알림 테스트를 시작합니다...")

    toaster = ToastNotifier()

    try:
        print("알림을 표시합니다... (5초간 표시)")
        print("우측 하단을 확인하세요!")

        # 알림 표시 (5초간)
        toaster.show_toast(
            "Claude Auto Approver 테스트",
            "이 알림이 우측 하단에 보이나요?",
            duration=5,
            threaded=False  # 동기적으로 실행 (알림이 사라질 때까지 대기)
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
