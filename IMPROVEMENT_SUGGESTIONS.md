# 탭 네비게이션 개선 방안

## 1. 직접 숫자 입력 방식 (가장 간단하고 확실)
```python
# 현재: Alt+Right/Left로 탐색 후 Enter
# 개선: '2' 키를 직접 입력

win32api.keybd_event(ord('2'), 0, 0, 0)
time.sleep(0.05)
win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)
```

**장점**:
- OCR 불필요
- 가장 빠르고 확실
- "2. Yes, and don't ask again"을 직접 선택

**단점**:
- 옵션 순서가 바뀌면 문제 발생 가능

## 2. Down 키 사용
```python
# Alt+Right/Left 대신 Down 키로 이동
VK_DOWN = 0x28

for i in range(5):
    win32api.keybd_event(VK_DOWN, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

    # OCR로 "don't ask again" 확인
    new_img = self.capture_window(hwnd)
    new_text = self.extract_text_from_image(new_img)

    if "don't ask again" in new_text.lower():
        # Enter로 선택
        win32api.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        break
```

## 3. 타이밍 증가
```python
# 현재: time.sleep(0.2)
# 개선: time.sleep(0.5)

# 각 키 입력 후 충분한 대기 시간 확보
time.sleep(0.5)  # 화면 업데이트 대기
```

## 4. OCR 정확도 향상
```python
def extract_text_from_image(self, img):
    """이미지 전처리로 OCR 정확도 향상"""
    try:
        # 그레이스케일 변환
        img = img.convert('L')

        # 대비 증가
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # OCR 수행 (PSM 모드 지정)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, lang='eng', config=custom_config)

        return text
    except Exception:
        return ""
```

## 5. 더 정확한 화면 변화 감지
```python
def detect_screen_change(self, text1, text2):
    """텍스트 길이와 특징으로 변화 감지"""
    # 길이 차이가 10% 이상이면 변화로 인정
    if abs(len(text1) - len(text2)) > len(text1) * 0.1:
        return True

    # 특정 키워드 변화 확인
    keywords1 = set(text1.lower().split())
    keywords2 = set(text2.lower().split())

    # 차집합이 20% 이상이면 변화로 인정
    diff = len(keywords1.symmetric_difference(keywords2))
    total = len(keywords1.union(keywords2))

    return diff / total > 0.2 if total > 0 else False
```

## 6. 시도 횟수 증가 및 안전장치
```python
MAX_ATTEMPTS = 10  # 5에서 10으로 증가
MAX_TOTAL_TIME = 30  # 30초 제한

start_time = time.time()

for i in range(MAX_ATTEMPTS):
    # 시간 제한 체크
    if time.time() - start_time > MAX_TOTAL_TIME:
        print(f"[TIMEOUT] Navigation timeout after {MAX_TOTAL_TIME}s")
        break

    # 네비게이션 로직...
```

## 7. 하이브리드 접근법 (추천)
```python
def smart_navigate(self, hwnd):
    """하이브리드 접근: 먼저 '2' 시도, 실패하면 탐색"""

    # 1단계: '2' 직접 입력 시도
    print("[INFO] Trying direct '2' input...")
    win32api.keybd_event(ord('2'), 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

    # 화면 캡처하여 확인
    img = self.capture_window(hwnd)
    text = self.extract_text_from_image(img)

    # 성공 확인 (대화상자가 사라졌는지)
    if not self.check_approval_pattern(text):
        print("[SUCCESS] Direct input worked!")
        return True

    # 2단계: 실패하면 Down 키로 탐색
    print("[INFO] Direct input failed, trying Down key navigation...")
    VK_DOWN = 0x28
    VK_RETURN = 0x0D

    for i in range(5):
        win32api.keybd_event(VK_DOWN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)  # 충분한 대기

        img = self.capture_window(hwnd)
        text = self.extract_text_from_image(img)

        if "don't ask again" in text.lower():
            print(f"[SUCCESS] Found target after {i+1} Down presses")
            win32api.keybd_event(VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True

    # 3단계: Alt+Right/Left 탐색 (현재 방식)
    print("[INFO] Trying Alt+Right/Left navigation...")
    # ... 기존 코드

    return False
```

## 추천 구현 순서

1. **즉시 개선 (빠른 테스트)**:
   - 직접 '2' 입력 시도
   - 타이밍을 0.2초 → 0.5초로 증가

2. **중기 개선**:
   - Down 키 사용 추가
   - 하이브리드 접근법 구현

3. **장기 개선**:
   - OCR 전처리 추가
   - 화면 변화 감지 알고리즘 개선
   - 시도 횟수 증가 및 타임아웃 추가

## 설정 파일 추가
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
