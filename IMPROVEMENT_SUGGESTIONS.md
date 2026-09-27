# Tab Navigation Improvement Proposals

## 1. Direct Numeric Key Input (Simplest and Most Reliable)
```python
# Current: navigate with Alt+Right/Left, then Enter
# Improved: type the '2' key directly

win32api.keybd_event(ord('2'), 0, 0, 0)
time.sleep(0.05)
win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)
```

**Pros**:
- No OCR needed
- Fastest and most reliable
- Selects "2. Yes, and don't ask again" directly

**Cons**:
- Can break if the option order changes

## 2. Using the Down Key
```python
# Move with the Down key instead of Alt+Right/Left
VK_DOWN = 0x28

for i in range(5):
    win32api.keybd_event(VK_DOWN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

    # Confirm "don't ask again" via OCR
    new_img = self.capture_window(hwnd)
    new_text = self.extract_text_from_image(new_img)

    if "don't ask again" in new_text.lower():
        # Confirm with Enter
        win32api.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        break
```

## 3. Increased Timing
```python
# Current: time.sleep(0.2)
# Improved: time.sleep(0.5)

# Ensure enough wait time after each key press
time.sleep(0.5)  # wait for screen update
```

## 4. Improved OCR Accuracy
```python
def extract_text_from_image(self, img):
    """Preprocess the image to improve OCR accuracy"""
    try:
        # Convert to grayscale
        img = img.convert('L')

        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Run OCR (with a specific PSM mode)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, lang='eng', config=custom_config)

        return text
    except Exception:
        return ""
```

## 5. More Accurate Screen Change Detection
```python
def detect_screen_change(self, text1, text2):
    """Detect changes using text length and characteristic differences"""
    # Treat as changed if the length difference exceeds 10%
    if abs(len(text1) - len(text2)) > len(text1) * 0.1:
        return True

    # Check for keyword changes
    keywords1 = set(text1.lower().split())
    keywords2 = set(text2.lower().split())

    # Treat as changed if the symmetric difference exceeds 20%
    diff = len(keywords1.symmetric_difference(keywords2))
    total = len(keywords1.union(keywords2))

    return diff / total > 0.2 if total > 0 else False
```

## 6. Increased Attempt Count and Safeguards
```python
MAX_ATTEMPTS = 10  # increased from 5
MAX_TOTAL_TIME = 30  # 30-second limit

start_time = time.time()

for i in range(MAX_ATTEMPTS):
    # Check the time limit
    if time.time() - start_time > MAX_TOTAL_TIME:
        print(f"[TIMEOUT] Navigation timeout after {MAX_TOTAL_TIME}s")
        break

    # Navigation logic...
```

## 7. Hybrid Approach (Recommended)
```python
def smart_navigate(self, hwnd):
    """Hybrid approach: try '2' first, then fall back to navigation"""

    # Step 1: try direct '2' input
    print("[INFO] Trying direct '2' input...")
    win32api.keybd_event(ord('2'), 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

    # Capture the screen to check
    img = self.capture_window(hwnd)
    text = self.extract_text_from_image(img)

    # Confirm success (whether the dialog disappeared)
    if not self.check_approval_pattern(text):
        print("[SUCCESS] Direct input worked!")
        return True

    # Step 2: fall back to Down-key navigation
    print("[INFO] Direct input failed, trying Down key navigation...")
    VK_DOWN = 0x28
    VK_RETURN = 0x0D

    for i in range(5):
        win32api.keybd_event(VK_DOWN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)  # wait long enough

        img = self.capture_window(hwnd)
        text = self.extract_text_from_image(img)

        if "don't ask again" in text.lower():
            print(f"[SUCCESS] Found target after {i+1} Down presses")
            win32api.keybd_event(VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True

    # Step 3: fall back to Alt+Right/Left navigation (current approach)
    print("[INFO] Trying Alt+Right/Left navigation...")
    # ... existing code

    return False
```

## Recommended Implementation Order

1. **Immediate improvements (quick to test)**:
   - Try direct '2' input
   - Increase timing from 0.2s to 0.5s

2. **Medium-term improvements**:
   - Add Down-key usage
   - Implement the hybrid approach

3. **Long-term improvements**:
   - Add OCR preprocessing
   - Improve the screen-change detection algorithm
   - Increase attempt count and add a timeout

## Adding a Configuration File
```json
{
  "navigation": {
    "method": "hybrid",  // "direct", "down", "alt_arrows", "hybrid"
    "direct_key": "2",
    "max_attempts": 10,
    "step_delay": 0.5,
    "timeout_seconds": 30
  }
}
```
