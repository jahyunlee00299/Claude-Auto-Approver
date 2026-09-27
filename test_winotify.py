"""
winotify notification test program
"""
from winotify import Notification, audio
import time

def test_winotify():
    """winotify notification test"""
    print("winotify 알림 테스트를 시작합니다...")

    try:
        # Add timestamp
        timestamp = time.strftime('%H:%M:%S')

        # Create notification
        toast = Notification(
            app_id="Claude Auto Approver",
            title=f"테스트 알림 [{timestamp}]",
            msg=f"알림이 정상적으로 작동합니다!\n시간: {timestamp}"
        )

        # Set silent mode
        toast.set_audio(audio.Silent, loop=False)

        # Show notification
        print("알림을 표시합니다...")
        toast.show()
        print("알림이 표시되었습니다!")

        # Wait for the notification to display
        time.sleep(2)

        print("테스트 완료!")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_winotify()
