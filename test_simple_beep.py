#!/usr/bin/env python3
"""Test simple beep and message box as fallback"""
import winsound
import time

def test_beep():
    """Test beep sound"""
    print("Testing beep sound...")
    winsound.Beep(1000, 500)  # 1000Hz for 500ms
    print("Beep sent!")

def test_messagebox():
    """Test Windows message box"""
    import ctypes
    print("\nTesting message box...")

    # MB_OK | MB_ICONINFORMATION | MB_TOPMOST
    result = ctypes.windll.user32.MessageBoxW(
        0,
        "This is a test notification from Claude Auto Approver.\n\nIf you see this popup, basic Windows notifications work!",
        "Claude Auto Approver - Test",
        0x00000040 | 0x00040000  # MB_ICONINFORMATION | MB_TOPMOST
    )

    print(f"Message box result: {result}")

if __name__ == "__main__":
    print("="*60)
    print("Simple Notification Test")
    print("="*60)
    print()

    test_beep()
    time.sleep(1)
    test_messagebox()

    print("\n[SUCCESS] Tests complete!")
