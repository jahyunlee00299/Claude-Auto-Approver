#!/usr/bin/env python3
"""
Simple test to send key '1' to foreground window
"""
import time
import win32gui
import win32api
import win32con

def send_key_to_foreground(key='1', delay=0.05):
    """Send a key to the current foreground window"""
    try:
        # Get current foreground window
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)

        print(f"[INFO] Current foreground window: {title}")
        print(f"[INFO] Window handle: {hwnd}")
        print(f"[INFO] Will send key '{key}' in 3 seconds...")
        print("[INFO] Switch to your target window now!")

        time.sleep(3)

        # Get foreground window again (in case it changed)
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)

        print(f"\n[ACTION] Sending key '{key}' to: {title}")

        # Method 1: Using keybd_event
        print(f"[DEBUG] Sending key down...")
        win32api.keybd_event(ord(key), 0, 0, 0)

        time.sleep(delay)

        print(f"[DEBUG] Sending key up...")
        win32api.keybd_event(ord(key), 0, win32con.KEYEVENTF_KEYUP, 0)

        print(f"\n[SUCCESS] Key '{key}' sent successfully!")
        print(f"[INFO] Check if '{key}' was received by the window")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to send key: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_repeated_keys():
    """Send key '1' multiple times for testing"""
    print("\n" + "="*70)
    print("Testing repeated key presses")
    print("="*70)
    print("[INFO] Will send '1' three times with 1 second interval")
    print("[INFO] Switch to your test window (e.g., notepad) in 3 seconds...")
    print()

    time.sleep(3)

    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    print(f"[INFO] Target window: {title}\n")

    for i in range(1, 4):
        print(f"[{i}/3] Sending '1'...")
        win32api.keybd_event(ord('1'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)

    print("\n[SUCCESS] Sent '1' three times")
    print("[INFO] You should see '111' in the target window")

def main():
    print("="*70)
    print("Key Press Test - Direct keyboard input test")
    print("="*70)
    print("\nTest options:")
    print("1. Send single key '1' to foreground window")
    print("2. Send '1' three times (for visual confirmation)")
    print()

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == '1':
        send_key_to_foreground('1')
    elif choice == '2':
        test_repeated_keys()
    else:
        print("[ERROR] Invalid choice")
        return

    print("\n" + "="*70)
    print("Test completed")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Test cancelled")
    except EOFError:
        # Run default test if no input (non-interactive mode)
        print("\n[INFO] Running default test (repeated keys)")
        test_repeated_keys()
