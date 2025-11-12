"""
win10toast 간단 테스트
"""
from win10toast import ToastNotifier
import time

print("win10toast 테스트 시작...")

toaster = ToastNotifier()

print("알림 표시 중... (우측 하단 확인!)")

# 알림 표시 (5초간)
toaster.show_toast(
    "Test Notification",
    "우측 하단에서 올라오는 알림이 보이나요?",
    duration=5,
    threaded=True
)

print("알림이 표시되었습니다!")
print("5초간 대기 중...")
time.sleep(6)

print("테스트 완료!")
