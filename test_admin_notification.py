#!/usr/bin/env python3
"""
Test notification with admin check
"""
import ctypes
import sys
import os
from winotify import Notification

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with admin privileges"""
    if is_admin():
        return True
    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            __file__,
            None,
            1
        )
        return False

def test_notification():
    """Test notification"""
    print("Testing notification...")

    toast = Notification(
        app_id="Claude Auto Approver",
        title="Admin Test Notification",
        msg="If you see this, notifications are working!",
        duration="long"
    )
    toast.show()

    print("Notification sent!")
    print("\nCheck Windows Action Center (Win+N)")

def main():
    print("=" * 60)
    print("Admin Notification Test")
    print("=" * 60)
    print()

    if is_admin():
        print("[OK] Running as Administrator")
    else:
        print("[INFO] Not running as Administrator")
        print("Testing notification anyway...")

    test_notification()

if __name__ == "__main__":
    main()