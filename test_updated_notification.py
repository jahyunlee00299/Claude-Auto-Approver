#!/usr/bin/env python3
"""
Test the updated notification system
"""
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the notification function
from ocr_auto_approver import show_notification_popup

def main():
    print("=" * 60)
    print("Updated Notification System Test")
    print("=" * 60)
    print()
    print("This will show notifications using:")
    print("  1. Direct message box (popup window)")
    print("  2. Windows notification (if message box fails)")
    print("  3. PowerShell (if both fail)")
    print()

    # Test notifications
    test_cases = [
        ("Auto Approval #1", "PowerShell window detected"),
        ("Auto Approval #2", "Python console detected"),
        ("Auto Approval #3", "Command Prompt detected"),
        ("Auto Approval #4", "Git Bash detected"),
        ("Auto Approval #5", "VS Code detected"),
    ]

    for i, (title, message) in enumerate(test_cases, 1):
        print(f"\n[Test {i}/5] {title}")
        print(f"  Message: {message}")

        # Call the updated notification function
        show_notification_popup(title, message)

        if i < len(test_cases):
            print("  Waiting 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("Test Complete!")
    print()
    print("You should have seen:")
    print("  - 5 message box popups OR")
    print("  - 5 Windows notifications OR")
    print("  - A combination of both")
    print()
    print("At least ONE method should have worked!")
    print("=" * 60)

if __name__ == "__main__":
    main()