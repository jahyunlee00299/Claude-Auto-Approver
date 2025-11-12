#!/usr/bin/env python3
"""
Final test of the improved notification system
"""
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the notification function from ocr_auto_approver
from ocr_auto_approver import show_notification_popup

def main():
    print("=" * 60)
    print("Claude Auto Approver - Final Notification Test")
    print("=" * 60)
    print()
    print("Testing the improved notification system...")
    print()

    # Test notifications
    test_cases = [
        ("Auto Approval #1", "PowerShell window detected"),
        ("Auto Approval #2", "Python console detected"),
        ("Auto Approval #3", "Command Prompt detected"),
    ]

    for i, (title, message) in enumerate(test_cases, 1):
        print(f"[Test {i}/3] {title}")
        print(f"  Message: {message}")

        # Call the actual notification function
        show_notification_popup(title, message)

        if i < len(test_cases):
            print("  Waiting 2 seconds...")
            time.sleep(2)
        print()

    print("=" * 60)
    print("Test Complete!")
    print()
    print("Check Windows Action Center for notifications")
    print("All notifications should show:")
    print("  - 'Claude Auto Approver' attribution at bottom")
    print("  - Timestamp in the title")
    print("  - Notification sound")
    print("=" * 60)

if __name__ == "__main__":
    main()