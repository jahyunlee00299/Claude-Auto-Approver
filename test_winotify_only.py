#!/usr/bin/env python3
"""
Test ONLY Winotify for Windows notifications
"""
import time
import winsound
from winotify import Notification, audio

def show_winotify_advanced(title, message, count=1):
    """Show Windows notification with all winotify features"""
    try:
        timestamp = time.strftime('%H:%M:%S')

        # Create notification with all details
        toast = Notification(
            app_id="Claude Auto Approver",
            title=f"[{count}] {title} - {timestamp}",
            msg=message,
            duration="long",  # long duration
            icon=""  # No custom icon for now
        )

        # Add attribution text
        toast.attribution = "Claude Auto Approver"

        # Set audio (different sounds for different counts)
        if count <= 2:
            toast.set_audio(audio.Default, loop=False)
        elif count <= 4:
            toast.set_audio(audio.IM, loop=False)
        else:
            toast.set_audio(audio.Mail, loop=False)

        # Add actions (buttons)
        toast.add_actions(label="OK", launch="")
        toast.add_actions(label="View Details", launch="")

        # Show the notification
        toast.show()

        # Also play system sound
        try:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        print(f"[SUCCESS] Winotify notification #{count} sent!")
        print(f"          Title: [{count}] {title}")
        print(f"          Sound: {'Default' if count <= 2 else 'IM' if count <= 4 else 'Mail'}")
        return True

    except Exception as e:
        print(f"[ERROR] Winotify failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_winotify():
    """Test basic winotify without any extras"""
    print("\n" + "="*60)
    print("BASIC WINOTIFY TEST")
    print("="*60)

    try:
        toast = Notification(
            app_id="Claude Auto Approver",
            title="Simple Test",
            msg="If you see this, winotify works!",
            duration="long"
        )
        toast.show()
        print("[SUCCESS] Basic notification sent!")
        return True
    except Exception as e:
        print(f"[FAIL] Basic notification failed: {e}")
        return False

def test_advanced_winotify():
    """Test advanced winotify features"""
    print("\n" + "="*60)
    print("ADVANCED WINOTIFY TEST")
    print("="*60)

    notifications = [
        ("Auto Approval", "PowerShell window detected and approved"),
        ("Auto Approval", "Python console detected and approved"),
        ("Auto Approval", "Command Prompt detected and approved"),
        ("Auto Approval", "Git Bash detected and approved"),
        ("Auto Approval", "VS Code detected and approved"),
    ]

    success_count = 0

    for i, (title, message) in enumerate(notifications, 1):
        print(f"\n[Advanced Test {i}/5]")

        if show_winotify_advanced(title, message, i):
            success_count += 1

        if i < len(notifications):
            time.sleep(2)

    return success_count

def check_windows_settings():
    """Check and display Windows notification settings"""
    print("\n" + "="*60)
    print("WINDOWS NOTIFICATION SETTINGS CHECK")
    print("="*60)

    import subprocess

    # Try to open notification settings
    print("\nOpening Windows Notification Settings...")
    try:
        subprocess.Popen(['start', 'ms-settings:notifications'], shell=True)
        print("[OK] Settings opened. Please check:")
        print("     1. 'Get notifications from apps and other senders' is ON")
        print("     2. Python.exe is in the app list and allowed")
        print("     3. Focus Assist is OFF")
    except:
        print("[INFO] Could not open settings automatically")

    print("\nManual check instructions:")
    print("1. Press Win+I to open Settings")
    print("2. Go to System > Notifications & actions")
    print("3. Make sure notifications are ON")
    print("4. Check Python in the app list")
    print("5. Turn OFF Focus Assist (Win+N)")

def main():
    print("\n" + "="*70)
    print(" WINOTIFY-ONLY NOTIFICATION TEST")
    print("="*70)
    print("\nThis test will ONLY use winotify (no message boxes)")
    print("Testing in 3 steps...")
    time.sleep(2)

    # Step 1: Basic test
    basic_success = test_basic_winotify()
    time.sleep(2)

    if not basic_success:
        print("\n[WARNING] Basic winotify failed!")
        print("Checking Windows settings...")
        check_windows_settings()
        print("\nTrying advanced test anyway...")
        time.sleep(3)

    # Step 2: Advanced test
    success_count = test_advanced_winotify()

    # Step 3: Results
    print("\n" + "="*70)
    print(" TEST RESULTS")
    print("="*70)
    print(f"\nBasic Test: {'PASSED' if basic_success else 'FAILED'}")
    print(f"Advanced Test: {success_count}/5 notifications sent")

    if success_count == 0 and not basic_success:
        print("\n[CRITICAL] No notifications were displayed!")
        print("\nTROUBLESHOOTING:")
        check_windows_settings()

        print("\nALTERNATIVE SOLUTIONS:")
        print("1. Run as Administrator")
        print("2. Reinstall winotify: pip uninstall winotify && pip install winotify")
        print("3. Try running from a different Python environment")
        print("4. Check if Windows 10/11 is up to date")
    else:
        print("\n[SUCCESS] Winotify is working!")
        print(f"Check Windows Action Center for {success_count} notifications")
        print("They should appear as 'Claude Auto Approver'")

    print("="*70)

if __name__ == "__main__":
    main()