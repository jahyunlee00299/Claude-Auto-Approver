"""
winotify의 이미지/아이콘 지원 테스트
"""
from winotify import Notification, audio
import time

def test_winotify_icon():
    """winotify 아이콘 기능 테스트"""
    print("winotify 아이콘 기능 테스트...")

    # 알림 생성
    toast = Notification(
        app_id="Claude Auto Approver",
        title="아이콘 테스트",
        msg="이 알림에 아이콘이 표시되어야 합니다",
        duration="long"
    )

    # 아이콘 설정 시도 (다양한 방법)
    print("\n사용 가능한 메서드:")
    methods = dir(toast)
    for method in methods:
        if 'icon' in method.lower() or 'image' in method.lower():
            print(f"  - {method}")

    # 알림 표시
    toast.set_audio(audio.Default, loop=False)
    toast.show()

    print("\n알림이 표시되었습니다!")

if __name__ == "__main__":
    test_winotify_icon()