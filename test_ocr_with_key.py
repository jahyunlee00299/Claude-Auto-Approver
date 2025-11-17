#!/usr/bin/env python3
"""
Test OCR detection and key press for approval dialogs
"""
import time
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import pytesseract

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def capture_window(hwnd):
    """Capture window screenshot"""
    try:
        # Get window size
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        # Device context
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # Bitmap
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        # Copy screen
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        # Convert to PIL Image
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        # Cleanup
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return img

    except Exception as e:
        print(f"[ERROR] Capture failed: {e}")
        return None

def check_approval_text(text):
    """Check if text contains approval patterns"""
    if not text:
        return False

    text_lower = text.lower()

    # Check for option numbers
    has_option_1 = ('1.' in text or '1)' in text)
    has_option_2 = ('2.' in text or '2)' in text)

    print(f"\n[CHECK] has_option_1: {has_option_1}")
    print(f"[CHECK] has_option_2: {has_option_2}")

    if not (has_option_1 and has_option_2):
        print("[CHECK] Missing option numbers")
        return False

    # Check for approval keywords
    approval_keywords = ['approve', 'proceed', 'allow', 'select', 'choose', 'want to', 'would you', 'do you']
    found_keywords = [kw for kw in approval_keywords if kw in text_lower]

    print(f"[CHECK] Found keywords: {found_keywords}")

    if found_keywords:
        return True

    return False

def send_key(hwnd, key):
    """Send key to window"""
    try:
        print(f"\n[ACTION] Bringing window to foreground...")
        # Try to set foreground
        try:
            win32gui.SetForegroundWindow(hwnd)
        except:
            # Alternative method: simulate Alt key
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32gui.SetForegroundWindow(hwnd)

        time.sleep(0.3)

        # Verify foreground
        current = win32gui.GetForegroundWindow()
        if current != hwnd:
            print(f"[WARNING] Window not in foreground (current: {win32gui.GetWindowText(current)})")
        else:
            print(f"[OK] Window is in foreground")

        # Send key
        print(f"[ACTION] Sending key '{key}'...")
        key_code = ord(key)

        # Key down
        win32api.keybd_event(key_code, 0, 0, 0)
        print(f"[DEBUG] Key down sent")
        time.sleep(0.05)

        # Key up
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        print(f"[DEBUG] Key up sent")

        print(f"[SUCCESS] Key '{key}' sent successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send key: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("OCR Detection and Key Press Test")
    print("=" * 70)
    print("\nThis script will:")
    print("1. List all visible windows")
    print("2. Wait for you to select a window")
    print("3. Capture screenshot and run OCR")
    print("4. If approval pattern detected, send key '1'")
    print("\n" + "=" * 70)

    # Find all windows
    windows = []
    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                results.append((hwnd, title))

    win32gui.EnumWindows(callback, windows)

    # Filter and display
    print("\nAvailable windows:")
    valid_windows = []
    for i, (hwnd, title) in enumerate(windows, 1):
        if title and len(title) > 1:
            safe_title = title.encode('ascii', 'ignore').decode('ascii')
            if safe_title:
                valid_windows.append((hwnd, title))
                if len(valid_windows) <= 20:  # Show first 20
                    print(f"  {len(valid_windows)}. {safe_title[:60]}")

    print(f"\nTotal: {len(valid_windows)} windows")

    # Select window
    print("\n" + "=" * 70)
    try:
        choice = input("Enter window number to test (or 0 to scan current foreground window): ")
        choice = int(choice)

        if choice == 0:
            # Use current foreground window
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            print(f"\n[INFO] Using current foreground window: {title}")
        elif 1 <= choice <= len(valid_windows):
            hwnd, title = valid_windows[choice - 1]
            print(f"\n[INFO] Selected: {title}")
        else:
            print("[ERROR] Invalid choice")
            return
    except ValueError:
        print("[ERROR] Invalid input")
        return

    # Wait before capture
    print("\n[INFO] Waiting 3 seconds before capture...")
    print("[INFO] Make sure the approval dialog is visible!")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    # Capture
    print("\n[ACTION] Capturing window...")
    img = capture_window(hwnd)

    if not img:
        print("[ERROR] Failed to capture window")
        return

    print(f"[OK] Captured image: {img.size[0]}x{img.size[1]}")

    # Save screenshot for debugging
    screenshot_path = "test_screenshot.png"
    img.save(screenshot_path)
    print(f"[OK] Screenshot saved to: {screenshot_path}")

    # OCR
    print("\n[ACTION] Running OCR...")
    text = pytesseract.image_to_string(img, lang='eng')

    print(f"\n[OCR RESULT] Length: {len(text)} characters")
    print("=" * 70)
    print("OCR Text:")
    print("=" * 70)
    print(text)
    print("=" * 70)

    # Check pattern
    print("\n[ACTION] Checking for approval pattern...")
    if check_approval_text(text):
        print("\n[SUCCESS] Approval pattern detected!")

        # Ask if should send key
        response = input("\nSend key '1' to this window? (y/n): ")
        if response.lower() == 'y':
            success = send_key(hwnd, '1')
            if success:
                print("\n[SUCCESS] Test completed successfully!")
            else:
                print("\n[FAILED] Failed to send key")
        else:
            print("\n[INFO] Key press skipped by user")
    else:
        print("\n[RESULT] No approval pattern detected")
        print("[INFO] This window does not appear to have an approval dialog")

    print("\n" + "=" * 70)
    print("Test completed")
    print("=" * 70)

if __name__ == "__main__":
    main()
