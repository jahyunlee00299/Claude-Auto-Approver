# 📖 Claude Auto Approver 사용 가이드

## 🎯 프로그램 개요

**ocr_auto_approver.py** - OCR 기반 지능형 자동 승인 시스템

### 주요 기능
- 🔍 **Active OCR 모니터링**: 모든 창을 3초마다 스캔하여 승인 요청 자동 감지
- 🎯 **지능형 옵션 선택**: 옵션 개수에 따라 최적의 선택 (3개→2번, 2개→1번)
- 🛡️ **스마트 필터링**: Chrome, PowerPoint, 시스템 창 자동 제외
- 💬 **통합 알림**: SMS 사운드와 함께 상세한 Windows 알림
- ⏱️ **시간 기반 재승인**: 10초 쿨다운으로 같은 창 재승인 가능
- 🖥️ **다중 모니터**: 모든 모니터의 창 동시 모니터링

---

## 🚀 빠른 시작

### 1. 사전 요구사항

#### Tesseract OCR 설치 (필수)
```bash
# Windows
# https://github.com/UB-Mannheim/tesseract/wiki 에서 설치
# 기본 경로: C:\Program Files\Tesseract-OCR\tesseract.exe
```

설치 확인:
```bash
tesseract --version
```

다른 경로에 설치했다면 `ocr_auto_approver.py` 23번 줄 수정:
```python
pytesseract.pytesseract.tesseract_cmd = r'당신의\경로\tesseract.exe'
```

#### Python 패키지 설치
```bash
# 저장소 클론
git clone https://github.com/jahyunlee00299/Claude-Auto-Approver.git
cd Claude-Auto-Approver

# 의존성 설치
pip install -r requirements.txt
```

**필수 패키지:**
- `pytesseract` - OCR 텍스트 추출
- `Pillow` - 이미지 처리
- `pywin32` - Windows API 접근
- `winotify` - Windows 알림

### 2. 기본 실행

```bash
python ocr_auto_approver.py
```

### 3. 실행 화면

```
============================================================
OCR Auto Approver
============================================================

=== ACTIVE OCR MONITORING ===

Mode: Active OCR (All Windows)
  - Scans ALL visible windows with OCR
  - Detects approval dialogs automatically
  - Auto-responds when pattern detected
  - Excludes: Chrome, PowerPoint, HWP, System windows

Press Ctrl+C to stop

[INFO] Scanning for target windows...
[OK] Found 8 target windows:
  1. MINGW64:/c/Users/Jahyun/PycharmProjects (1936x1064)
  2. PyCharm 2024.1 - Claude-Auto-Approver (1920x1080)
  ...

[STATUS] Active monitoring | Approvals: 0 | Checks: 33
```

---

## 📋 작동 방식

### Active OCR 모니터링 프로세스

```
┌─────────────────────────────────────────────────────────┐
│ 1. 전체 창 열거                                          │
│    → 모든 가시적인 창 목록 가져오기                      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 필터링                                                │
│    → 시스템 창, 제외 키워드 포함 창 제외                │
│    → Chrome, PowerPoint, HWP, NVIDIA Overlay 등          │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 스크린샷 캡처                                         │
│    → 각 창의 화면을 BitBlt로 캡처                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 4. OCR 텍스트 추출                                       │
│    → Tesseract OCR로 텍스트 추출                         │
│    → 하단 영역 우선 스캔 (승인 대화상자 위치)           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 5. 패턴 매칭                                             │
│    → 승인 패턴 확인 (22개 패턴)                          │
│    → 옵션 번호 확인 (1., 2. 필수)                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 6. 자동 승인                                             │
│    → 옵션 개수 판단 (2개 vs 3개)                         │
│    → 적절한 키 전송 ('1' 또는 '2')                       │
│    → Windows 알림 표시                                   │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 7. 쿨다운                                                │
│    → 같은 창은 10초 후 재승인 가능                       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 8. 반복                                                  │
│    → 3초 대기 후 1번부터 반복                            │
└─────────────────────────────────────────────────────────┘
```

### 승인 로직

#### 옵션 인식 방식
- **첫 단어만 추출**: "1. Yes, proceed once" → "yes"
- **화살표 처리**: "❯ 1. Yes" → "1." 위치 찾기 → "yes"
- **유연한 형식**: 특수문자, 공백 앞에 있어도 인식

**인식 가능한 형식:**
```
✅ 1. Yes
✅ ❯ 1. Yes (화살표)
✅   1. Yes (공백)
✅ } 1. Yes (중괄호)
✅ * 1. Yes (기호)
```

#### 옵션 개수 기반 선택
- **2개 옵션** (1, 2만 존재):
  ```
  ❯ 1. Yes                       ← 선택 ✓
    2. Tell Claude what to do differently
  ```
  → **Option 1 선택** (더 안전한 일회성 승인)

- **3개 옵션** (1, 2, 3 모두 존재):
  ```
  1. Yes, proceed once
  2. Yes, and don't ask again    ← 선택 ✓
  3. No, and tell Claude what to do differently
  ```
  → **Option 2 선택** (재질문 방지)

---

## 📋 감지 패턴

### 승인 패턴 - 질문 + 동작 조합 방식

프로그램은 **유연한 조합 매칭**으로 다양한 패턴을 인식합니다:

#### 질문 패턴
```
✓ "do you want"
✓ "would you like"
✓ "would you"
```

#### 동작 패턴
```
✓ "to proceed" / "proceed"
✓ "to approve" / "approve"
✓ "to create" / "create"
✓ "to allow" / "allow"
✓ "select"
✓ "choose"
```

#### 특정 패턴 (정확히 일치)
```
✓ "select an option"
✓ "choose an option"
✓ "yes, and don't ask again"
✓ "yes, and remember"
✓ "yes, allow all edits"
✓ "approve this action"
✓ "allow this action"
✓ "grant permission"
✓ "proceed with"
✓ "continue with"
✓ "select one of the following"
✓ "choose one of the following"
✓ "no, and tell claude"
✓ "tell claude what to do differently"
```

### 매칭 방식

1. **질문 + 동작 조합**: "do you want" + "to proceed" → ✅
2. **특정 패턴 일치**: "select an option" → ✅
3. **Fallback**: 질문 또는 동작만 있어도 → ✅

**인식 가능한 예시:**
```
✅ "Do you want to proceed?"
✅ "Do you want to continue?" (조합 매칭)
✅ "Would you like to approve?"
✅ "Would you like to create?"
✅ "Select an option"
✅ "Choose one"
```

### 필수 조건

다음 조건을 **모두** 만족해야 승인 실행:

1. ✅ 위 패턴 중 하나 이상 포함
2. ✅ 줄에 **"1." 또는 "1)" 포함** (줄 시작 아니어도 OK)
3. ✅ 줄에 **"2." 또는 "2)" 포함** (줄 시작 아니어도 OK)

**예시 - 감지됨:**
```
Do you want to proceed?
1. Yes, proceed once
2. Yes, and don't ask again
```

```
Do you want to proceed?
❯ 1. Yes                         ← 화살표 있어도 OK
  2. Tell Claude what to do differently
```

**예시 - 감지 안 됨:**
```
Some random text with 1. and 2.  # 승인 패턴 없음
```

---

## ⚙️ 설정 및 커스터마이징

### 1. 쿨다운 시간 조정

`ocr_auto_approver.py` 203번 줄:
```python
self.re_approval_cooldown = 10  # 같은 창 재승인 대기 시간 (초)
```

**사용 사례:**
- `= 5`: 더 빠른 재승인 (공격적)
- `= 30`: 느린 재승인 (보수적)
- `= 0`: 즉시 재승인 (주의!)

### 2. 스캔 주기 조정

`ocr_auto_approver.py` 776번 줄:
```python
time.sleep(3)  # 스캔 주기 (초)
```

**사용 사례:**
- `= 1`: 빠른 감지, 높은 CPU 사용
- `= 5`: 느린 감지, 낮은 CPU 사용
- `= 3`: **권장 (기본값)**

### 3. OCR 모드 설정

`ocr_auto_approver.py` 731번 줄:
```python
text = self.extract_text_from_image(img, fast_mode=False)
```

**fast_mode 옵션:**
- `False`: **정확한 OCR** (권장, 기본값)
  - PSM 모드 자동 선택
  - 전체 이미지 스캔
  - 처리 시간: ~0.5-0.8초/창

- `True`: **빠른 OCR**
  - PSM 6 (단일 블록)
  - 이미지 크기 축소 (800x600)
  - 하단 40%만 스캔
  - 처리 시간: ~0.2-0.4초/창
  - **정확도 감소 주의!**

### 4. 제외 키워드 추가

`ocr_auto_approver.py` 171-185번 줄:
```python
self.exclude_keywords = [
    'auto approval complete',  # 알림 팝업
    'chrome',
    'google chrome',
    'nvidia geforce',
    'powerpoint',
    'ppt',
    'microsoft powerpoint',
    'hwp',
    '.hwp',
    'your_custom_keyword',  # 여기에 추가
]
```

**사용 사례:**
```python
self.exclude_keywords = [
    # 기존 키워드...
    'slack',           # Slack 앱 제외
    'discord',         # Discord 제외
    'notepad++',       # Notepad++ 제외
    'my_app',          # 커스텀 앱 제외
]
```

### 5. 커스텀 아이콘 설정

프로젝트 루트에 `approval_icon.png` 배치:
```bash
# 권장 크기: 256x256 픽셀
# 형식: PNG
cp your_icon.png approval_icon.png
```

알림에 커스텀 아이콘이 표시됩니다.

---

## 🔍 디버깅 및 로그 해석

### 정상 작동 로그

```
[STATUS] Active monitoring | Approvals: 0 | Checks: 33
```
- `Approvals`: 누적 승인 횟수
- `Checks`: OCR 스캔 횟수 (모든 창 × 반복 횟수)

### 잠재적 승인 감지

```
[DEBUG] Potential approval dialog detected!
[DEBUG] OCR Text Length: 450
[DEBUG] OCR Text (first 10 non-empty lines):
  Do you want to proceed?
  1. Yes, proceed once
  2. Yes, and don't ask again
```
→ 승인 키워드는 있지만 옵션 번호 검증 진행 중

### 옵션 감지 상태

```
[DEBUG] Option detection: has_option_1=True, has_option_2=True
```
- `True, True`: ✅ 옵션 번호 정상 감지
- `False, *`: ❌ Option 1 없음
- `*, False`: ❌ Option 2 없음

### 승인 실행

```
======================================================================
[2025-01-14 12:34:56] APPROVAL REQUEST DETECTED (Active Scan)
======================================================================
Window Title: MINGW64:/c/Users/Jahyun/PycharmProjects
Action: Sending '1'
Detected Text Preview: Do you want to proceed?
1. Yes, proceed once
2. Yes, and don't ask again
======================================================================

[INFO] Executing approval sequence for: MINGW64:/c/Users/Jahyun...
[INFO] Sending key: '1'
[SUCCESS] Approval completed at 12:34:56
[INFO] Total approvals so far: 1
[INFO] Window added to cooldown list (10s before next approval)
```

---

## 🔧 문제 해결

### Q1: 승인이 감지되지 않아요

**원인 및 해결:**

1. **Tesseract OCR 미설치 또는 잘못된 경로**
   ```bash
   tesseract --version  # 설치 확인
   ```
   → 설치 안 됨: [Tesseract 다운로드](https://github.com/UB-Mannheim/tesseract/wiki)

   → 경로 수정: `ocr_auto_approver.py` 23번 줄
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

2. **창 제목이 제외 키워드에 포함**
   ```python
   # 171-185번 줄에서 확인
   self.exclude_keywords = [...]
   ```
   → 제외 키워드 목록에서 제거

3. **OCR 품질 문제**
   - ✅ 창을 더 크게 만들기
   - ✅ 폰트 크기 증가
   - ✅ 고대비 테마 사용
   - ✅ 창을 최상단으로 가져오기

4. **로그 확인**
   ```
   [DEBUG] Potential approval dialog detected!  ← 키워드 감지됨
   [DEBUG] has_option_1=True, has_option_2=True  ← 옵션도 감지됨
   ```
   - 위 메시지가 없으면 OCR이 텍스트를 제대로 읽지 못함
   - 있지만 승인 안 되면 패턴 매칭 실패

### Q2: 잘못된 창에서 승인이 실행돼요

**해결 방법:**

1. **제외 키워드 추가**
   ```python
   self.exclude_keywords = [
       # 기존 키워드...
       'unwanted_app',  # 추가
   ]
   ```

2. **쿨다운 시간 증가**
   ```python
   self.re_approval_cooldown = 30  # 10 → 30초
   ```

3. **스캔 주기 증가**
   ```python
   time.sleep(5)  # 3 → 5초
   ```

### Q3: 재승인이 필요한데 안 돼요

**원인:**
- 10초 쿨다운 기간 중

**해결 방법:**

1. **쿨다운 시간 단축**
   ```python
   self.re_approval_cooldown = 5  # 10 → 5초
   ```

2. **즉시 재승인 (주의!)**
   ```python
   self.re_approval_cooldown = 0  # 쿨다운 없음
   ```

3. **프로그램 재시작**
   ```bash
   Ctrl+C  # 중지
   python ocr_auto_approver.py  # 재시작
   ```

### Q4: 알림이 표시되지 않아요

**해결 방법:**

1. **winotify 설치 확인**
   ```bash
   pip install --upgrade winotify
   ```

2. **Windows 알림 설정 확인**
   - 설정 → 시스템 → 알림
   - Python/PowerShell 알림 활성화 확인

3. **아이콘 파일 확인**
   ```bash
   ls approval_icon.png  # 파일 존재 확인
   ```

### Q5: OCR이 텍스트를 제대로 읽지 못해요

**원인:**
- 폰트가 너무 작음
- 저해상도 화면
- 특수 폰트 사용
- 배경색과 텍스트 색상이 비슷함

**해결 방법:**

1. **창 크기 증가**
   - 터미널 창을 최대화
   - 폰트 크기를 14pt 이상으로

2. **고대비 테마 사용**
   - 흰 배경에 검은 텍스트
   - 또는 검은 배경에 흰 텍스트

3. **OCR 모드 변경**
   ```python
   # Normal mode로 변경
   text = self.extract_text_from_image(img, fast_mode=False)
   ```

4. **테스트 스크립트 실행**
   ```bash
   python test_detection.py
   ```
   → OCR이 어떻게 텍스트를 읽는지 확인

### Q6: CPU 사용량이 너무 높아요

**해결 방법:**

1. **스캔 주기 증가**
   ```python
   time.sleep(5)  # 3 → 5초
   ```

2. **Fast OCR 모드 사용**
   ```python
   text = self.extract_text_from_image(img, fast_mode=True)
   ```

3. **제외 키워드 추가**
   - 불필요한 창 스캔 방지

---

## 🧪 테스트

### 1. OCR 감지 테스트

```bash
python test_detection.py
```

**기능:**
- 모든 창 목록 표시
- 선택한 창의 스크린샷 캡처
- OCR 텍스트 추출 결과 표시
- 승인 패턴 감지 여부 확인

**사용 시나리오:**
- OCR이 제대로 작동하는지 확인
- 어떤 텍스트가 추출되는지 확인
- 승인 패턴이 제대로 감지되는지 확인

### 2. OCR + 키 입력 통합 테스트

```bash
python test_ocr_with_key.py
```

**기능:**
- 창 선택
- OCR 텍스트 추출
- 승인 패턴 확인
- 사용자 확인 후 키 '1' 전송

**사용 시나리오:**
- 전체 프로세스가 제대로 작동하는지 확인
- 키 입력이 실제로 전달되는지 확인

### 3. 키 입력만 테스트

```bash
python test_key_only.py
```

**기능:**
- 키 '1'을 3회 반복 전송
- 메모장 등에서 '111' 확인

**사용 시나리오:**
- 키 입력 메커니즘 자체가 작동하는지 확인
- win32api.keybd_event 함수 테스트

---

## 💡 고급 사용법

### 1. 백그라운드 실행

#### Windows 작업 스케줄러
1. `taskschd.msc` 실행
2. 새 작업 만들기
3. **트리거**: 로그온 시
4. **작업**:
   - 프로그램: `python.exe`
   - 인수: `"C:\path\to\ocr_auto_approver.py"`
5. **설정**: "숨김" 체크

#### Python 백그라운드 실행
```python
# run_approver_background.py
import subprocess
import sys

subprocess.Popen(
    [sys.executable, 'ocr_auto_approver.py'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)
```

실행:
```bash
python run_approver_background.py
```

### 2. 특정 시간대만 실행

`ocr_auto_approver.py`의 `monitor_loop()` 함수 수정:

```python
def monitor_loop(self):
    import datetime

    # ... 기존 코드 ...

    while self.running:
        try:
            # 시간 확인 (오전 9시 ~ 오후 6시만 실행)
            current_hour = datetime.datetime.now().hour
            if not (9 <= current_hour < 18):
                print(f"[INFO] Outside working hours ({current_hour}:00), sleeping...")
                time.sleep(60)  # 1분 대기
                continue

            # ... 기존 모니터링 코드 ...
```

### 3. 로그 파일로 저장

```bash
# 로그를 파일로 리다이렉션
python ocr_auto_approver.py > approver.log 2>&1

# 실시간으로 로그 보기 (별도 터미널)
tail -f approver.log

# Windows에서
Get-Content approver.log -Wait
```

### 4. 여러 인스턴스 실행 (주의!)

다른 설정으로 여러 인스턴스 실행:

```bash
# 인스턴스 1: 빠른 스캔
python ocr_auto_approver.py  # 기본 3초

# 인스턴스 2: 특정 창만 (코드 수정 필요)
# exclude_keywords를 다르게 설정
```

**주의:** CPU 사용량이 배로 증가합니다!

---

## 📊 성능 최적화

### 현재 성능 지표

| 항목 | 값 | 설명 |
|------|-----|------|
| 스캔 주기 | 3초 | 조정 가능 |
| OCR 처리 시간 | 0.3-0.8초/창 | Tesseract 의존 |
| 동시 모니터링 | 10-20개 창 | 시스템에 따라 다름 |
| CPU 사용률 | 10-20% | OCR 처리 중 spike |
| 메모리 사용량 | 80-200MB | OCR 처리 중 증가 |

### 최적화 팁

#### 1. CPU 사용량 감소
```python
# 스캔 주기 증가
time.sleep(5)  # 3 → 5초

# Fast OCR 모드
text = self.extract_text_from_image(img, fast_mode=True)
```

#### 2. 메모리 사용량 감소
```python
# 이미지 크기 축소 (extract_text_from_image 함수 내)
if width > 800 or height > 600:
    ratio = min(800/width, 600/height)
    new_size = (int(width * ratio), int(height * ratio))
    img = img.resize(new_size, Image.LANCZOS)
```

#### 3. 스캔 속도 증가
```python
# 제외 키워드 적극 활용
self.exclude_keywords = [
    # 불필요한 앱들 모두 추가
    'chrome', 'slack', 'discord', 'spotify', ...
]
```

---

## 📞 지원 및 기여

### 문제 보고
GitHub Issues에 보고해주세요:
https://github.com/jahyunlee00299/Claude-Auto-Approver/issues

**Issue 템플릿:**
```
## 문제 설명
[간단한 설명]

## 재현 방법
1. [단계 1]
2. [단계 2]

## 예상 동작
[예상했던 동작]

## 실제 동작
[실제로 일어난 동작]

## 환경
- OS: Windows 10/11
- Python: 3.x
- Tesseract: 5.x

## 로그
[관련 로그 붙여넣기]
```

### 기여하기
Pull Request를 환영합니다!

1. Fork 저장소
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 열기

---

## ⚠️ 주의사항

1. **자동 승인의 위험성**
   - 이 도구는 모든 승인 요청을 자동으로 수락합니다
   - 중요한 작업 전에는 프로그램을 중지하세요 (`Ctrl+C`)

2. **오탐지 가능성**
   - OCR은 100% 정확하지 않습니다
   - 제외 키워드를 적극 활용하세요

3. **시스템 리소스**
   - OCR은 CPU 집약적입니다
   - 배터리 사용 시 주의하세요

4. **개인정보 보호**
   - 화면 캡처가 진행됩니다
   - 민감한 정보가 있는 창은 제외 키워드에 추가하세요

---

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요! ⭐**
