#!/usr/bin/env python3
"""
Test script to check if auto-approver is detecting this window
"""
import time
import win32gui

def main():
    # Get this window's handle
    current_window = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(current_window)

    print("=" * 70)
    print("WINDOW DETECTION TEST")
    print("=" * 70)
    print(f"\nCurrent window title: {window_title}")
    print(f"Current window handle: {current_window}")

    # Check if this is the MINGW terminal where Claude is running
    if 'MINGW' in window_title.upper() or 'BASH' in window_title.upper():
        print("\n✓ This appears to be a MINGW/Bash terminal")
        print("  The auto-approver should be monitoring this window")
    else:
        print("\n✗ This does not appear to be the expected terminal type")

    print("\n" + "=" * 70)
    print("TEST: Creating an approval dialog simulation")
    print("=" * 70)
    print("\nThis message simulates an approval request:")
    print("\n  Do you want to proceed?")
    print("  ❯ 1. Yes")
    print("    2. No")
    print("\nIf the auto-approver is working, it should detect this pattern")
    print("and automatically press '2' within a few seconds.")
    print("\nWaiting 10 seconds to see if auto-approval happens...")

    for i in range(10, 0, -1):
        print(f"  {i} seconds remaining...")
        time.sleep(1)

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nDid the auto-approver detect and respond to the approval dialog?")
    print("Check if you received a notification or saw automatic input.")
    print("\nIf not, the OCR might not be recognizing the text properly.")

if __name__ == "__main__":
    main()
