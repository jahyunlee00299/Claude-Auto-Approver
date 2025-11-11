#!/usr/bin/env python3
"""
Debug OCR - Test if OCR can read the approval dialog
"""
import win32gui
import win32ui
import win32con
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def find_question_window():
    """Find Question window"""
    result = []

    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'question' in title.lower():
                windows.append({'hwnd': hwnd, 'title': title})
        return True

    win32gui.EnumWindows(callback, result)
    return result[0] if result else None

def capture_window(hwnd):
    """Capture window screenshot"""
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return img
    except Exception as e:
        print(f"Error capturing: {e}")
        return None

print("="*70)
print("OCR Debug Tool")
print("="*70)
print("\nSearching for Question window...")

window = find_question_window()

if not window:
    print("ERROR: No Question window found!")
    print("Please run: python test_approval_dialog.py")
else:
    print(f"Found window: {window['title']}")
    print(f"Capturing screenshot...")

    img = capture_window(window['hwnd'])

    if img:
        print(f"Screenshot captured: {img.size}")
        print(f"\nRunning OCR...")

        text = pytesseract.image_to_string(img, lang='eng')

        print(f"\n{'='*70}")
        print("OCR RESULT:")
        print(f"{'='*70}")
        print(text)
        print(f"{'='*70}")

        print(f"\nText length: {len(text)} characters")

        # Check patterns
        patterns = ['proceed', 'Yes', 'Approve', 'option', 'Select', 'ask again', 'tell Claude']
        print(f"\nPattern matching:")
        for pattern in patterns:
            if pattern.lower() in text.lower():
                print(f"  ✓ Found: '{pattern}'")
            else:
                print(f"  ✗ Not found: '{pattern}'")

        # Save screenshot
        img.save('debug_screenshot.png')
        print(f"\nScreenshot saved to: debug_screenshot.png")
    else:
        print("ERROR: Failed to capture screenshot")
