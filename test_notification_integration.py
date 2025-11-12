#!/usr/bin/env python3
"""
알림 기능 통합 테스트
"""
import time
from ocr_auto_approver import show_notification_popup

print("="*70)
print("Notification Integration Test")
print("="*70)
print()

print("[TEST 1] Testing notification function...")
try:
    show_notification_popup(
        "Auto Approval Complete",
        "'2' key was sent",
        window_info="Claude Code - Question",
        duration=3
    )
    print("[OK] Notification function called successfully")
except Exception as e:
    print(f"[ERROR] Notification failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("Check your Windows notification center for the notification!")
print("Waiting 5 seconds...")
time.sleep(5)

print()
print("[TEST 2] Testing with different message...")
try:
    show_notification_popup(
        "Test Notification",
        "This is a test message",
        window_info="Test Window",
        duration=3
    )
    print("[OK] Second notification sent")
except Exception as e:
    print(f"[ERROR] Second notification failed: {e}")

print()
print("="*70)
print("Test complete. Check Windows notification center!")
print("="*70)
