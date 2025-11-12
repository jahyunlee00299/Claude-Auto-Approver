"""
winotify 알림 테스트 프로그램
"""
from winotify import Notification, audio
import time

def test_winotify():
    """winotify 알림 테스트"""
    print("winotify 알림 테스트를 시작합니다...")

    try:
        # 타임스탬프 추가
        timestamp = time.strftime('%H:%M:%S')

        # 알림 생성
        toast = Notification(
            app_id="Claude Auto Approver",
            title=f"테스트 알림 [{timestamp}]",
            msg=f"알림이 정상적으로 작동합니다!\n시간: {timestamp}"
        )

        # 무음 설정
        toast.set_audio(audio.Silent, loop=False)

        # 알림 표시
        print("알림을 표시합니다...")
        toast.show()
        print("알림이 표시되었습니다!")

        # 알림이 표시되도록 대기
        time.sleep(2)

        print("테스트 완료!")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_winotify()
