#!/usr/bin/env python3
"""Check Windows notification settings"""
import winreg
import subprocess

def check_notification_settings():
    """Check if Windows notifications are enabled"""
    print("="*60)
    print("Windows Notification Settings Check")
    print("="*60)
    print()

    # Check if Focus Assist is on
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)

        try:
            value, _ = winreg.QueryValueEx(key, "NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK")
            print(f"[INFO] Toasts above lock screen: {bool(value)}")
        except:
            print("[INFO] Toast above lock setting not found")

        winreg.CloseKey(key)
    except Exception as e:
        print(f"[WARNING] Could not read notification settings: {e}")

    # Check system notification state
    print("\n[INFO] Opening Windows Notification Settings...")
    print("[ACTION] Please check the following:")
    print("  1. 'Notifications' should be ON")
    print("  2. Look for 'Python' or 'Claude Auto Approver' in the app list")
    print("  3. Make sure app notifications are enabled")
    print("\n[INFO] Press Enter after checking settings...")

    # Open notification settings
    try:
        subprocess.Popen(['explorer', 'ms-settings:notifications'])
        print("[OK] Notification settings opened")
    except Exception as e:
        print(f"[ERROR] Could not open settings: {e}")

if __name__ == "__main__":
    check_notification_settings()
    input()
