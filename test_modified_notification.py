"""
Test for the modified notification function in ocr_auto_approver.py
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_auto_approver import show_notification_popup

def test_notification():
    """Test for the modified notification system"""
    print("수정된 알림 시스템 테스트를 시작합니다...")

    # Show the notification
    show_notification_popup(
        title="테스트 알림",
        message="winotify만 사용하는 수정된 알림 시스템입니다."
    )

    print("테스트 완료!")

if __name__ == "__main__":
    test_notification()