#!/usr/bin/env python3
"""
Test Windows notifications using windows-toasts library
"""
import time
import asyncio
from windows_toasts import WindowsToaster, Toast, ToastDisplayImage

async def show_toast_async(title, message, count=1):
    """Show Windows toast notification asynchronously"""
    toaster = WindowsToaster('Claude Auto Approver')

    # Create toast
    toast = Toast()
    toast.text_fields = [title, message, f'Approval #{count}']

    # Show toast
    await toaster.show_toast(toast)
    print(f"[SUCCESS] Toast #{count} displayed: {title}")

def show_toast_notification(title, message, count=1):
    """Wrapper to show toast notification"""
    try:
        # Run async function
        asyncio.run(show_toast_async(title, message, count))
        return True
    except Exception as e:
        print(f"[ERROR] Failed to show toast: {e}")
        return False

def main():
    print("=" * 60)
    print("Windows-Toasts Library Test")
    print("=" * 60)
    print()

    notifications = [
        ("Auto Approval 1", "PowerShell window detected"),
        ("Auto Approval 2", "Python console detected"),
        ("Auto Approval 3", "Command Prompt detected"),
        ("Auto Approval 4", "Git Bash detected"),
        ("Auto Approval 5", "VS Code detected"),
    ]

    for i, (title, message) in enumerate(notifications, 1):
        timestamp = time.strftime('%H:%M:%S')
        full_title = f"[{i}] {title} - {timestamp}"

        print(f"\n[Test {i}/5]")
        print(f"  Title: {full_title}")
        print(f"  Message: {message}")

        success = show_toast_notification(full_title, message, i)

        if not success:
            print("  [FAIL] Could not show notification")

        if i < len(notifications):
            print("  Waiting 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("Test Complete!")
    print()
    print("Check Windows notification area for 5 toasts")
    print("All should be from 'Claude Auto Approver'")
    print("=" * 60)

if __name__ == "__main__":
    main()