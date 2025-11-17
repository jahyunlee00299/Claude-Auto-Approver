#!/usr/bin/env python3
"""Detailed toast notification test with multiple methods"""
import time
import os
import sys

def test_winotify_verbose():
    """Test winotify with verbose output"""
    print("\n" + "="*60)
    print("TEST 1: winotify with detailed logging")
    print("="*60)

    try:
        from winotify import Notification, audio

        print("[1] Creating notification object...")
        toast = Notification(
            app_id="Claude Auto Approver",
            title="TEST - Winotify",
            msg="Test notification #1\n\nCurrent time: " + time.strftime('%H:%M:%S'),
            duration="long"  # Try 'long' instead of 'short'
        )

        print("[2] Setting audio...")
        toast.set_audio(audio.Default, loop=False)

        print("[3] Adding icon...")
        icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
        if os.path.exists(icon_path):
            toast.icon = icon_path
            print(f"    Icon set: {icon_path}")

        print("[4] Showing notification...")
        toast.show()

        print("[SUCCESS] winotify notification sent!")
        print("         Check bottom-right corner of screen")
        time.sleep(2)
        return True

    except Exception as e:
        print(f"[FAILED] winotify error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_win10toast():
    """Test using win10toast library"""
    print("\n" + "="*60)
    print("TEST 2: win10toast library")
    print("="*60)

    try:
        print("[INFO] Checking if win10toast is installed...")
        from win10toast import ToastNotifier

        print("[1] Creating ToastNotifier...")
        toaster = ToastNotifier()

        print("[2] Showing notification...")
        icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")

        toaster.show_toast(
            "Claude Auto Approver - TEST 2",
            "Test notification using win10toast\n\nTime: " + time.strftime('%H:%M:%S'),
            icon_path=icon_path if os.path.exists(icon_path) else None,
            duration=5,
            threaded=False
        )

        print("[SUCCESS] win10toast notification sent!")
        return True

    except ImportError:
        print("[INFO] win10toast not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "win10toast"],
                      capture_output=True)
        print("[INFO] Installed. Please run this script again.")
        return False
    except Exception as e:
        print(f"[FAILED] win10toast error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_windows_toasts():
    """Test using windows-toasts library (newer)"""
    print("\n" + "="*60)
    print("TEST 3: windows-toasts library")
    print("="*60)

    try:
        print("[INFO] Checking if windows-toasts is installed...")
        from windows_toasts import Toast, WindowsToaster

        print("[1] Creating WindowsToaster...")
        toaster = WindowsToaster('Claude Auto Approver')

        print("[2] Creating toast...")
        newToast = Toast()
        newToast.text_fields = [
            'Claude Auto Approver - TEST 3',
            'Test notification using windows-toasts\n\nTime: ' + time.strftime('%H:%M:%S')
        ]

        print("[3] Showing notification...")
        toaster.show_toast(newToast)

        print("[SUCCESS] windows-toasts notification sent!")
        time.sleep(2)
        return True

    except ImportError:
        print("[INFO] windows-toasts not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "windows-toasts"],
                      capture_output=True)
        print("[INFO] Installed. Please run this script again.")
        return False
    except Exception as e:
        print(f"[FAILED] windows-toasts error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plyer():
    """Test using plyer library (cross-platform)"""
    print("\n" + "="*60)
    print("TEST 4: plyer library")
    print("="*60)

    try:
        print("[INFO] Checking if plyer is installed...")
        from plyer import notification

        print("[1] Showing notification...")
        notification.notify(
            title='Claude Auto Approver - TEST 4',
            message='Test notification using plyer\n\nTime: ' + time.strftime('%H:%M:%S'),
            app_name='Claude Auto Approver',
            timeout=10
        )

        print("[SUCCESS] plyer notification sent!")
        time.sleep(2)
        return True

    except ImportError:
        print("[INFO] plyer not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "plyer"],
                      capture_output=True)
        print("[INFO] Installed. Please run this script again.")
        return False
    except Exception as e:
        print(f"[FAILED] plyer error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_focus_assist():
    """Check Windows Focus Assist status"""
    print("\n" + "="*60)
    print("Checking Windows Focus Assist Status")
    print("="*60)

    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\Cache\DefaultAccount"
        )

        print("[INFO] Checking Focus Assist registry keys...")
        # This is complex to parse, so just inform user
        print("[INFO] Focus Assist settings exist in registry")

        winreg.CloseKey(key)

    except Exception as e:
        print(f"[INFO] Could not check Focus Assist: {e}")

    print("\n[ACTION] Manual check required:")
    print("  1. Press Win+A to open Action Center")
    print("  2. Click 'Focus assist' button")
    print("  3. Make sure it's set to 'Off' or 'Priority only'")
    print("  4. If it's 'Alarms only', notifications won't show!")

if __name__ == "__main__":
    print("="*60)
    print("COMPREHENSIVE TOAST NOTIFICATION TEST")
    print("="*60)
    print("\nThis will test multiple notification libraries.")
    print("Watch the bottom-right corner of your screen!\n")

    results = []

    # Test each method
    results.append(("winotify", test_winotify_verbose()))
    time.sleep(3)

    results.append(("win10toast", test_win10toast()))
    time.sleep(3)

    results.append(("windows-toasts", test_windows_toasts()))
    time.sleep(3)

    results.append(("plyer", test_plyer()))
    time.sleep(3)

    # Check Focus Assist
    check_focus_assist()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{name:20} {status}")

    print("\n[INFO] If NO notifications appeared, check:")
    print("  1. Windows Settings > System > Notifications")
    print("  2. Focus Assist is OFF (Win+A)")
    print("  3. 'Show notification banners' is ON")
    print("  4. Python.exe has notification permissions")
