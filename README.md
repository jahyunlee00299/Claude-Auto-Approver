# 🤖 Claude Auto Approver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

OCR 기반 지능형 승인 시스템 - PyCharm, CMD, PowerShell 등 모든 창에서 나타나는 Claude Code 승인 프롬프트를 자동으로 감지하고 처리합니다.

## ✨ 주요 기능

### 🔍 Active OCR 모니터링
- **전체 창 스캔**: 모든 가시적인 창을 3초마다 OCR로 스캔하여 승인 요청 감지
- **백그라운드 모니터링**: 현재 포커스와 무관하게 모든 창 모니터링
- **다중 모니터 지원**: 모든 모니터의 창을 동시에 모니터링

### 🎯 지능형 감지
- **OCR 기반 텍스트 분석**: Tesseract OCR로 승인 프롬프트 정확하게 감지
- **스마트 패턴 매칭**: "Would you like to proceed?", "Do you want to approve?" 등 22개 이상의 패턴 인식
- **옵션 번호 검증**: 반드시 "1."/"1)"과 "2."/"2)" 형식의 옵션 번호가 있어야 감지

### 🛡️ 안전한 필터링
- **시스템 창 제외**: Windows 알림 센터, 작업 표시줄, 시스템 UI 자동 제외
- **프로그램 필터링**: Chrome, PowerPoint, HWP, Excel, NVIDIA Overlay 등 자동 제외
- **시간 기반 재승인**: 같은 창은 10초 쿨다운 후 재승인 가능
- **크기 검증**: 최소 크기 미달 창 자동 제외

### 💬 통합 알림 시스템
- **Windows 알림**: 승인 완료 시 winotify로 알림 표시 (SMS 사운드)
- **상세 정보**: 감지된 텍스트 미리보기, 선택한 옵션, 창 정보 포함
- **상세 로깅**: 승인 시각, 창 정보, OCR 텍스트 등 상세 기록
- **커스텀 아이콘**: approval_icon.png로 알림 아이콘 커스터마이징

### 🎮 지능형 옵션 선택
- **3개 옵션**: Option 2 선택 (일반적으로 "Yes, and don't ask again")
- **2개 옵션**: Option 1 선택 (더 안전한 일회성 승인)

## 🚀 빠른 시작

### 사전 요구사항

#### 1. Tesseract OCR 설치 (필수)

```bash
# Windows
# https://github.com/UB-Mannheim/tesseract/wiki 에서 설치 프로그램 다운로드
# 기본 설치 경로: C:\Program Files\Tesseract-OCR\tesseract.exe
```

설치 후 경로 확인:
- 기본 경로: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- 다른 경로에 설치했다면 `ocr_auto_approver.py`의 23번 줄 수정:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'당신의\경로\tesseract.exe'
  ```

#### 2. Python 패키지 설치

```bash
# 저장소 클론
git clone https://github.com/jahyunlee00299/Claude-Auto-Approver.git
cd Claude-Auto-Approver

# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용법

```bash
# 메인 프로그램 실행
python ocr_auto_approver.py
```

### 작동 방식

#### Active OCR 모니터링
1. **전체 창 열거**: 모든 가시적인 창 목록을 가져옴
2. **필터링**: 시스템 창, 제외 키워드가 포함된 창 제외
3. **스크린샷 캡처**: 각 창의 화면을 캡처
4. **OCR 텍스트 추출**: Tesseract로 텍스트 추출
5. **패턴 매칭**: 승인 패턴 및 옵션 번호(1., 2.) 확인
6. **자동 승인**:
   - 옵션 개수 판단 (2개 vs 3개)
   - 적절한 키('1' 또는 '2') 전송
   - Windows 알림 표시
7. **쿨다운**: 같은 창은 10초 후 재승인 가능
8. **반복**: 3초마다 전체 프로세스 반복

### 예시 출력

```
============================================================
OCR Auto Approver
============================================================

=== ACTIVE OCR MONITORING ===

Mode: Active OCR (All Windows)
  - Scans ALL visible windows with OCR
  - Detects approval dialogs automatically
  - Auto-responds when pattern detected
  - Excludes: Chrome, PowerPoint, HWP, Excel, System windows

Press Ctrl+C to stop

[INFO] Scanning for target windows...
[OK] Found 8 target windows:
  1. MINGW64:/c/Users/Jahyun/PycharmProjects (1936x1064)
  2. PyCharm 2024.1 - Claude-Auto-Approver (1920x1080)
  3. Python 3.11 (cmd.exe) - ocr_auto_approver.py (800x600)
  ...

[STATUS] Active monitoring | Approvals: 0 | Checks: 125

[DEBUG] Potential approval dialog detected!
[DEBUG] Option 1: 1. yes, proceed once
[DEBUG] Option 2: 2. yes, and don't ask again
[DEBUG] 2 options detected - selecting option 1

======================================================================
[2025-01-14 12:34:56] APPROVAL REQUEST DETECTED (Active Scan)
======================================================================
Window Title: MINGW64:/c/Users/Jahyun/PycharmProjects/Claude-Auto-Approver
Action: Sending '1'
Detected Text Preview: Do you want to proceed with this action?
1. Yes, proceed once
2. Yes, and don't ask again
======================================================================

[INFO] Executing approval sequence for: MINGW64:/c/Users/Jahyun...
[INFO] Sending key: '1'
[SUCCESS] Approval completed at 12:34:56
[INFO] Total approvals so far: 1
[INFO] Window added to cooldown list (10s before next approval)
```

## 📋 시스템 요구사항

- **OS**: Windows 10/11
- **Python**: 3.7+
- **필수 소프트웨어**:
  - Tesseract OCR 5.0+ ([다운로드](https://github.com/UB-Mannheim/tesseract/wiki))
- **필수 패키지**:
  - `pytesseract` - OCR 텍스트 추출
  - `Pillow` - 이미지 처리
  - `pywin32` - Windows API 접근
  - `winotify` - Windows 알림

## ⚙️ 설정 및 커스터마이징

### 주요 설정 값 (ocr_auto_approver.py)

```python
# Cooldown settings (203번 줄)
self.re_approval_cooldown = 10          # 같은 창 재승인 대기 시간 (초)

# Monitoring interval (776번 줄)
time.sleep(3)                           # 스캔 주기 (초) - CPU 사용량 조절

# OCR settings (731번 줄)
fast_mode=False                         # True로 설정 시 빠른 OCR (정확도 감소)
```

### 커스텀 아이콘 설정

프로젝트 루트에 `approval_icon.png` 파일을 배치하면 Windows 알림에 표시됩니다:

```bash
# 이미지 크기 권장: 256x256 픽셀
# 형식: PNG
cp your_icon.png approval_icon.png
```

### 제외 키워드 추가

특정 창을 모니터링에서 제외하려면 `ocr_auto_approver.py`의 `exclude_keywords` 리스트에 추가:

```python
# 171-185번 줄
self.exclude_keywords = [
    'auto approval complete',  # 알림 팝업 제외
    'chrome',                  # Chrome 브라우저
    'google chrome',
    'nvidia geforce',          # NVIDIA 오버레이
    'powerpoint',              # PowerPoint
    'ppt',
    'microsoft powerpoint',
    'hwp',                     # 한글 워드프로세서
    '.hwp',
    'excel',                   # Excel
    'microsoft excel',
    '.xlsx',
    '.xls',
    'your_app_name',          # 여기에 추가
]
```

## 🎯 감지 패턴

### 승인 패턴 (자동 감지되는 문장)

프로그램은 **질문 + 동작 조합 방식**으로 유연하게 패턴을 인식합니다 (145-182번 줄):

#### 질문 패턴
```
- "do you want"
- "would you like"
- "would you"
```

#### 동작 패턴
```
- "to proceed" / "proceed"
- "to approve" / "approve"
- "to create" / "create"
- "to allow" / "allow"
- "select"
- "choose"
```

#### 특정 패턴 (정확히 일치)
```
- "select an option"
- "choose an option"
- "yes, and don't ask again"
- "yes, and remember"
- "yes, allow all edits"
- "approve this action"
- "allow this action"
- "grant permission"
- "proceed with"
- "continue with"
- "select one of the following"
- "choose one of the following"
- "no, and tell claude"
- "tell claude what to do differently"
```

**매칭 방식:**
1. **질문 + 동작** 조합 (예: "do you want" + "to proceed")
2. **특정 패턴** 정확히 일치
3. **Fallback**: 질문 또는 동작만 있어도 인식

**인식 예시:**
- ✅ "Do you want to proceed?"
- ✅ "Do you want to continue?" (조합 매칭)
- ✅ "Would you like to approve?"
- ✅ "Select an option"

**중요**: 패턴 매칭은 다음 조건을 **모두** 만족해야 합니다:
- 위 패턴 중 하나 이상 포함
- 줄에 "1." 또는 "1)" 포함
- 줄에 "2." 또는 "2)" 포함
- **화살표(❯) 등 특수문자 앞에 있어도 인식**

### 시스템 창 자동 제외

다음 시스템 창들은 자동으로 필터링됩니다 (189-201번 줄):

```
- Windows.UI.Core.CoreWindow (알림 센터)
- Shell_TrayWnd (작업 표시줄)
- NotifyIconOverflowWindow (시스템 트레이)
- ApplicationFrameWindow (UWP 앱 컨테이너)
- Windows.Internal.Shell.TabProxyWindow
- ImmersiveLauncher (시작 메뉴)
- MultitaskingViewFrame (작업 보기)
- ForegroundStaging (시스템 스테이징 창)
- Dwm (Desktop Window Manager)
```

### 응답 로직

프로그램은 승인 옵션을 지능적으로 선택합니다 (507-559번 줄):

#### 옵션 인식 방식
- **첫 단어만 추출**: "1. Yes, proceed once" → "yes"
- **화살표 처리**: "❯ 1. Yes" → "1." 위치 찾기 → "yes"
- **유연한 형식**: 특수문자, 공백 앞에 있어도 인식

#### 선택 로직
- **3개 옵션 감지** (1, 2, 3 모두 존재) → **Option 2 선택**
  - 일반적으로 "Yes, and don't ask again"
  - 가장 편리한 선택 (재질문 방지)

- **2개 옵션 감지** (1, 2만 존재) → **Option 1 선택**
  - 일반적으로 "Yes, proceed once"
  - 더 안전한 선택 (일회성 승인)

**인식 가능한 형식:**
```
✅ 1. Yes
✅ ❯ 1. Yes (화살표)
✅   1. Yes (공백)
✅ } 1. Yes (중괄호)
✅ * 1. Yes (기호)
```

## 🔍 문제 해결

### Q: 승인이 감지되지 않아요

**A:** 다음을 확인하세요:
1. Tesseract OCR이 올바르게 설치되었는지 확인
   ```bash
   tesseract --version
   ```
2. 창 제목이 `exclude_keywords`에 포함되어 있지 않은지 확인
3. 로그에서 다음 확인:
   - `[DEBUG] Potential approval dialog detected!` - OCR이 키워드 감지
   - `[DEBUG] Option detection: has_option_1=True, has_option_2=True` - 옵션 번호 감지
   - 위 두 조건이 모두 만족되어야 승인 실행
4. OCR 품질 개선:
   - 창을 더 크게 만들기
   - 폰트 크기 증가
   - 고대비 테마 사용

### Q: 잘못된 창에서 승인이 실행돼요

**A:** 다음을 시도하세요:
1. `exclude_keywords`에 해당 프로그램 키워드 추가
2. `re_approval_cooldown` 값을 늘려서 재승인 간격 증가
3. 스캔 주기를 늘리기 (776번 줄의 `time.sleep(3)`을 더 큰 값으로)

### Q: Tesseract 오류가 발생해요

**A:**
```python
# ocr_auto_approver.py 23번 줄 확인
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 설치 경로가 다르면 수정:
pytesseract.pytesseract.tesseract_cmd = r'당신의\설치\경로\tesseract.exe'
```

### Q: 알림이 표시되지 않아요

**A:**
1. Windows 알림 설정 확인: 설정 → 시스템 → 알림
2. winotify 재설치: `pip install --upgrade winotify`
3. approval_icon.png 파일이 프로젝트 루트에 있는지 확인

### Q: 재승인이 필요한데 안 돼요

**A:** 프로그램은 시간 기반 재승인 메커니즘이 있습니다 (201-203번 줄):
- 같은 창은 **10초 쿨다운** 후 재승인 가능
- 더 빠른 재승인이 필요하면 `re_approval_cooldown` 값을 줄이세요
- 즉시 재승인이 필요하면 프로그램을 재시작하세요

## 📁 프로젝트 구조

```
Claude-Auto-Approver/
├── ocr_auto_approver.py        # 메인 OCR 자동 승인 프로그램
├── approval_icon.png           # 알림 아이콘 (선택)
├── requirements.txt            # Python 의존성
├── README.md                  # 이 파일
├── test_detection.py          # OCR 감지 테스트
├── test_ocr_with_key.py       # OCR + 키 입력 통합 테스트
├── test_key_only.py           # 키 입력 기능 테스트
└── test_*.py                  # 기타 테스트 스크립트
```

## 🧪 테스트

프로젝트에는 다양한 테스트 파일들이 포함되어 있습니다:

```bash
# OCR 감지 테스트 (창 캡처 + OCR 텍스트 확인)
python test_detection.py

# OCR + 키 입력 통합 테스트 (전체 프로세스)
python test_ocr_with_key.py

# 키 입력만 테스트 (메모장 등에서 '1' 입력 확인)
python test_key_only.py

# 배경 알림 테스트
python test_bg_notification.py

# 현재 창 확인
python check_current_window.py
```

## 📊 성능 및 최적화

### Active OCR 모니터링
- **스캔 주기**: 3초 (조정 가능)
- **OCR 처리 시간**: 창당 약 0.3-0.8초
- **동시 모니터링**: 평균 10-20개 창
- **CPU 사용률**: 평균 10-20% (OCR 처리 중 spike)

### 메모리 사용량
- **기본**: ~80-120MB
- **OCR 처리 중**: ~150-200MB

### 최적화 팁
1. **스캔 주기 조절**: `time.sleep(3)`을 더 큰 값으로 (CPU 사용량 감소)
2. **Fast OCR 모드**: `extract_text_from_image(img, fast_mode=True)` (정확도 감소)
3. **제외 키워드 추가**: 불필요한 창 모니터링 방지

## 🔧 고급 사용법

### 백그라운드 실행

```bash
# Windows 시작 시 자동 실행하려면 작업 스케줄러 사용
# 1. 작업 스케줄러 실행 (taskschd.msc)
# 2. 새 작업 만들기
# 3. 트리거: 로그온 시
# 4. 작업: python.exe, 인수: "경로\ocr_auto_approver.py"
```

### 특정 시간대만 실행

```python
# ocr_auto_approver.py의 monitor_loop() 함수에 추가
import datetime

# 오전 9시부터 오후 6시까지만 실행
current_hour = datetime.datetime.now().hour
if not (9 <= current_hour < 18):
    time.sleep(60)  # 1분 대기 후 재확인
    continue
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OCR powered by [Tesseract](https://github.com/tesseract-ocr/tesseract)
- Windows notifications by [winotify](https://github.com/versa-syahptr/winotify)
- Built with Python and love ❤️

## 📞 Contact

- GitHub: [@jahyunlee00299](https://github.com/jahyunlee00299)
- Issues: [GitHub Issues](https://github.com/jahyunlee00299/Claude-Auto-Approver/issues)

## ⚠️ 주의사항

- 이 도구는 **승인 프롬프트를 자동으로 수락**합니다
- 중요한 작업 전에는 프로그램을 일시 중지하세요 (Ctrl+C)
- 첫 실행 시 테스트 환경에서 동작을 확인하세요
- 프로덕션 환경에서는 신중하게 사용하세요

## 📈 최근 개선 사항

### v2.7 (2025-01)
- **Excel 제외**: Excel 창은 자동으로 모니터링에서 제외
- **향상된 필터링**: .xlsx, .xls 파일명 패턴도 필터링

### v2.6 (2025-01)
- **화살표 형식 지원**: "❯ 1. Yes" 형식의 Claude Code 대화상자 인식
- **유연한 패턴 매칭**: 질문 + 동작 조합 방식으로 더 많은 패턴 인식
- **첫 단어 추출**: "1. Yes, proceed once" → "yes"만 추출하여 OCR 오류 방지
- **특수문자 처리**: 중괄호, 기호 등 앞에 있어도 옵션 번호 인식

### v2.5 (2025-01)
- **옵션 개수 기반 선택**: 3개 옵션이면 2번, 2개 옵션이면 1번 선택
- **시간 기반 재승인**: 10초 쿨다운으로 같은 창 재승인 가능
- **향상된 디버깅**: OCR 텍스트, 옵션 감지 상태 실시간 로깅
- **알림 개선**: SMS 사운드, 감지된 텍스트 미리보기 추가
- **필터링 강화**: Chrome, PowerPoint, HWP 등 더 많은 프로그램 제외

### v2.0
- **Active OCR 모니터링**: 모든 창을 주기적으로 스캔
- **향상된 필터링**: 시스템 창, 크기 검증, 프로그램별 제외
- **패턴 매칭 강화**: 22개 이상의 승인 패턴 인식
- **다중 모니터 지원**: 모든 모니터의 창 동시 모니터링
- **winotify 알림**: 상세한 Windows 네이티브 알림

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=jahyunlee00299/Claude-Auto-Approver&type=Date)](https://star-history.com/#jahyunlee00299/Claude-Auto-Approver&Date)

---

**⭐ If you find this project useful, please consider giving it a star! ⭐**
