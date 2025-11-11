#!/usr/bin/env python3
import sys
import win32gui
import win32ui
import win32con
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print("Getting foreground window...")
hwnd = win32gui.GetForegroundWindow()
title = win32gui.GetWindowText(hwnd)
try:
    print(f"Window: {title}")
except:
    print("Window: (title contains special chars)")

print("Capturing window...")
left, top, right, bottom = win32gui.GetWindowRect(hwnd)
width = right - left
height = bottom - top
print(f"Size: {width}x{height}")

hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()

saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
saveDC.SelectObject(saveBitMap)
saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)
img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

# Try full image first, then bottom half
print("Running OCR on full image...")
text = pytesseract.image_to_string(img, lang='eng')

if len(text) < 50:  # If too little text, try bottom half
    print("Not enough text, trying bottom half...")
    bottom_region = img.crop((0, int(height * 0.5), width, height))
    text = pytesseract.image_to_string(bottom_region, lang='eng')

# Save to file
with open('ocr_result.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"OCR completed. Text length: {len(text)} chars")
print("Saved to ocr_result.txt")

# Check patterns
patterns = ['Do you want to proceed?', '1. Yes', '2. Yes, and don\'t ask again', '3. No, and tell Claude']
found_patterns = []
for pattern in patterns:
    if pattern.lower() in text.lower():
        found_patterns.append(pattern)

if found_patterns:
    print(f"FOUND {len(found_patterns)} patterns!")
    for p in found_patterns:
        print(f"  - {p}")
else:
    print("No approval patterns found")

# Cleanup
win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)

print("Done!")
