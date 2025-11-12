"""
수정된 ocr_auto_approver.py의 알림 함수 테스트
"""
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_auto_approver import show_notification_popup

def test_notification():
    """수정된 알림 시스템 테스트"""
    print("수정된 알림 시스템 테스트를 시작합니다...")

    # 알림 표시
    show_notification_popup(
        title="테스트 알림",
        message="winotify만 사용하는 수정된 알림 시스템입니다."
    )

    print("테스트 완료!")

if __name__ == "__main__":
    test_notification()