#!/usr/bin/env python3
"""
Debug winotify - check Windows notification settings
"""
import subprocess
import time

print("="*70)
print("WINOTIFY DEBUG TEST")
print("="*70)

# Step 1: Check winotify installation
print("\n[STEP 1] Checking winotify installation...")
try:
    from winotify import Notification, audio
    print("[OK] winotify is installed")
except ImportError:
    print("[ERROR] winotify is NOT installed")
    print("Run: pip install winotify")
    exit(1)

# Step 2: Check Windows notification settings
print("\n[STEP 2] Opening Windows Notification Settings...")
print("Please check if notifications are enabled for Python!")
try:
    subprocess.Popen(['powershell', '-Command', "Start-Process 'ms-settings:notifications'"])
    print("[INFO] Windows Settings opened - check 'Notifications' section")
    time.sleep(3)
except:
    print("[WARNING] Could not open settings automatically")

# Step 3: Send test notification with different methods
print("\n[STEP 3] Sending test notifications...")

# Method 1: Basic notification
print("\n[Method 1] Basic notification...")
try:
    toast1 = Notification(
        app_id="Python Test",
        title="METHOD 1: Basic Test",
        msg="If you see this, Method 1 works!",
        duration="long"
    )
    toast1.show()
    print("[OK] Method 1 notification sent")
    time.sleep(2)
except Exception as e:
    print(f"[ERROR] Method 1 failed: {e}")

# Method 2: With sound
print("\n[Method 2] With SMS sound...")
try:
    toast2 = Notification(
        app_id="Python Test",
        title="METHOD 2: With Sound",
        msg="If you hear a sound and see this, Method 2 works!",
        duration="long"
    )
    toast2.set_audio(audio.SMS, loop=False)
    toast2.show()
    print("[OK] Method 2 notification sent (with sound)")
    time.sleep(2)
except Exception as e:
    print(f"[ERROR] Method 2 failed: {e}")

# Method 3: Different app ID
print("\n[Method 3] Different app ID...")
try:
    toast3 = Notification(
        app_id="Microsoft.WindowsTerminal_8wekyb3d8bbwe!App",  # Windows Terminal app ID
        title="METHOD 3: Terminal App ID",
        msg="Using Windows Terminal app ID - do you see this?",
        duration="long"
    )
    toast3.set_audio(audio.SMS, loop=False)
    toast3.show()
    print("[OK] Method 3 notification sent (Windows Terminal app ID)")
    time.sleep(2)
except Exception as e:
    print(f"[ERROR] Method 3 failed: {e}")

# Method 4: PowerShell app ID
print("\n[Method 4] PowerShell app ID...")
try:
    toast4 = Notification(
        app_id="{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe",
        title="METHOD 4: PowerShell ID",
        msg="Using PowerShell app ID - do you see this?",
        duration="long"
    )
    toast4.set_audio(audio.SMS, loop=False)
    toast4.show()
    print("[OK] Method 4 notification sent (PowerShell app ID)")
    time.sleep(2)
except Exception as e:
    print(f"[ERROR] Method 4 failed: {e}")

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("If you didn't see ANY notifications above:")
print("1. Check Windows Settings > System > Notifications")
print("2. Make sure 'Focus assist' is OFF")
print("3. Make sure notifications from Python/PowerShell are allowed")
print("4. Check Windows Action Center (bottom right, notification icon)")
print("\nIf you saw at least ONE notification, tell me which method worked!")
print("="*70)

input("\nPress Enter to exit...")
