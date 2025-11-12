#!/usr/bin/env python3
"""
Check which windows are currently being monitored
"""
import sys
sys.path.insert(0, '.')

from ocr_auto_approver import OCRAutoApprover

def main():
    print("=" * 70)
    print("Checking Currently Monitored Windows")
    print("=" * 70)
    print()

    # Create approver instance
    approver = OCRAutoApprover()

    # Find target windows
    windows = approver.find_target_windows(verbose=True)

    print()
    print("=" * 70)
    print(f"SUMMARY: Found {len(windows)} windows to monitor")
    print("=" * 70)

    if windows:
        for i, win in enumerate(windows, 1):
            title = win['title']
            hwnd = win['hwnd']
            class_name = win['class']
            left, top, right, bottom = win['pos']
            width = right - left
            height = bottom - top

            # Convert to ASCII-safe string
            try:
                safe_title = title.encode('ascii', 'ignore').decode('ascii')
            except:
                safe_title = "Window with special characters"

            print(f"\n{i}. {safe_title}")
            print(f"   Handle: {hwnd}")
            print(f"   Class:  {class_name}")
            print(f"   Size:   {width}x{height}")
            print(f"   Pos:    ({left}, {top})")
    else:
        print("\nNo windows found to monitor")

    print()

if __name__ == "__main__":
    main()
