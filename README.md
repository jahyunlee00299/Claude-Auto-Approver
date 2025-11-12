# 🤖 Claude Auto Approver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

OCR 기반 지능형 승인 시스템 - PyCharm, CMD, PowerShell 등 모든 창에서 나타나는 Claude Code 승인 프롬프트를 자동으로 감지하고 처리합니다.

## ✨ 주요 기능

### 🧠 듀얼 모드 모니터링
- **패시브 OCR 모드**: 현재 활성화된 창을 OCR로 실시간 모니터링
- **액티브 사이클링 모드**: 사용자가 idle일 때 자동으로 탭/창을 순회하며 승인 요청 탐지

### 🎯 지능형 감지
- **OCR 기반 텍스트 분석**: Tesseract OCR로 승인 프롬프트 정확하게 감지
- **키 프로브 방식**: "1" + Backspace로 빠른 승인 감지 (기본값)
- **스마트 패턴 매칭**: "Would you like to proceed?", "Do you want to approve?" 등 다양한 패턴 인식

### 🛡️ 안전한 필터링
- **시스템 창 제외**: Windows 알림 센터, 작업 표시줄, 시스템 UI 자동 제외
- **중복 승인 방지**: 같은 창에 한 번만 승인 (프로그램 재시작 전까지)
- **크기 검증**: 최소 크기 미달 창 자동 제외

### 💬 통합 알림 시스템
- **Windows 알림**: 승인 완료 시 winotify로 알림 표시
- **상세 로깅**: 승인 시각, 창 정보, 감지 방법 등 상세 기록
- **커스텀 아이콘**: approval_icon.png로 알림 아이콘 커스터마이징

### 🖥️ 다중 모니터 지원
- **모든 모니터**: 좌우, 상하 배치된 모든 모니터의 창 모니터링
- **최소화된 창 복원**: 필요시 자동으로 창 복원 후 승인

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

#### MODE 1: 패시브 OCR 모니터링 (항상 활성)
1. 현재 포커스된 창을 지속적으로 모니터링
2. OCR로 텍스트 추출 및 승인 패턴 확인
3. 승인 요청 감지 시 즉시 자동 승인

#### MODE 2: 액티브 탭 사이클링 (Idle 시)
1. **사용자 Idle 감지**: 10초간 입력 없음
2. **창/탭 순회**: 최대 5개 창 × 10개 탭 자동 순회
3. **키 프로브 감지**: 각 탭마다 "1" + Backspace 입력
   - 승인 창이면: "1"이 승인으로 처리됨
   - 일반 에디터면: "1" 입력 후 Backspace로 취소
4. **사용자 활동 재개 시**: 즉시 패시브 모드로 복귀

### 예시 출력

```
==============================================================
OCR Auto Approver
==============================================================

=== DUAL MODE MONITORING ===

MODE 1 - Passive OCR (Always Active):
  - Monitors current window with OCR
  - Detects approval dialogs and auto-responds

MODE 2 - Active Cycling (When Idle):
  - Starts after 10s of inactivity
  - Cycles through windows/tabs
  - Presses '1' + Backspace on each tab

Press Ctrl+C to stop

[INFO] Scanning for target windows...
[OK] Found 8 target windows:
  1. Python 3.11 (cmd.exe) - ocr_auto_approver.py (800x600)
  2. MINGW64:/c/Users/<user>/PycharmProjects (1200x800)
  3. PyCharm 2024.1 - Claude-Auto-Approver (1920x1080)
  ...

[STATUS] Passive monitoring active | Idle: 5.2s | Approvals: 0 | Checks: 125

======================================================================
[2025-01-14 12:34:56] APPROVAL REQUEST DETECTED (OCR Passive)
======================================================================
Window Title: MINGW64:/c/Users/<user>/PycharmProjects/Claude-Auto-Approver
Action: Sending '2'
======================================================================

[INFO] Executing approval sequence for: MINGW64:/c/Users/<user>...
[INFO] Sending key: '2'
[SUCCESS] Approval completed at 12:34:56
[INFO] Total approvals so far: 1
[INFO] Window added to approved list (won't auto-approve again)
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
# Tab cycling settings (138-148번 줄)
self.enable_tab_cycling = True          # 탭 사이클링 활성화/비활성화
self.idle_time_threshold = 10           # Idle 판단 시간 (초)
self.tab_cycle_interval = 0.05          # 탭당 체류 시간 (초)
self.max_tabs_to_cycle = 10            # 창당 최대 탭 수
self.max_windows_to_cycle = 5          # 최대 순회 창 수
self.use_key_probe = True              # 키 프로브 방식 사용 (False면 OCR)
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
# 176-187번 줄
self.exclude_keywords = [
    'claude auto approver',
    'chrome',
    'google chrome',
    'your_app_name',  # 여기에 추가
]
```

## 🎯 감지 패턴

### 승인 패턴 (자동 감지되는 문장)

프로그램은 다음과 같은 승인 요청 패턴을 자동으로 인식합니다 (150-174번 줄):

```
- "Would you like to proceed"
- "Do you want to proceed"
- "Would you like to approve"
- "Do you want to approve"
- "Do you want to create"
- "Select an option"
- "Choose an option"
- "Yes, and don't ask again"
- "Yes, and remember"
- "Approve this action"
- "Allow this action"
- "Grant permission"
- "Proceed with"
- "Continue with"
```

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

프로그램은 승인 옵션을 지능적으로 선택합니다 (481-516번 줄):

- **Option 2가 "No"를 포함** → Option 1 선택
- **Option 3이 "No, and tell Claude"** → Option 2 선택 (allow all)
- **기본값**: Option 2 선택 ("Yes, and don't ask again")

## 🔍 문제 해결

### Q: 승인이 감지되지 않아요

**A:** 다음을 확인하세요:
1. Tesseract OCR이 올바르게 설치되었는지 확인
   ```bash
   tesseract --version
   ```
2. 창 제목이 `exclude_keywords`에 포함되어 있지 않은지 확인
3. OCR 텍스트 추출이 제대로 되고 있는지 로그 확인
4. `use_key_probe = False`로 설정하고 OCR 모드로 시도

### Q: 잘못된 창에서 승인이 실행돼요

**A:** 다음을 시도하세요:
1. `exclude_keywords`에 해당 프로그램 키워드 추가
2. `idle_time_threshold` 값을 늘려서 더 긴 Idle 시간 요구
3. `enable_tab_cycling = False`로 설정해서 액티브 모드 비활성화

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

### Q: 중복으로 승인되는 것 같아요

**A:** 프로그램은 중복 승인 방지 메커니즘이 내장되어 있습니다 (204번 줄):
- 각 창은 프로그램 실행 중 **한 번만** 승인됩니다
- 재승인이 필요하면 프로그램을 재시작하세요

## 📁 프로젝트 구조

```
Claude-Auto-Approver/
├── ocr_auto_approver.py        # 메인 OCR 자동 승인 프로그램
├── approval_icon.png           # 알림 아이콘 (선택)
├── requirements.txt            # Python 의존성
├── IMPROVEMENTS.md            # 개선 사항 문서
├── README.md                  # 이 파일
└── test_*.py                  # 각종 테스트 스크립트
```

## 🧪 테스트

프로젝트에는 다양한 테스트 파일들이 포함되어 있습니다:

```bash
# 창 감지 테스트
python check_pycharm_titles.py

# 알림 테스트
python test_approval_notification.py

# 패턴 인식 테스트
python test_pattern_recognition.py

# Claude 창 감지 테스트
python detect_claude_window.py
```

## 📊 성능 및 최적화

### 패시브 모드
- **체크 주기**: 2초
- **OCR 처리 시간**: 창당 약 0.5-1초
- **CPU 사용률**: 평균 5-10%

### 액티브 모드
- **탭 전환 속도**: 50ms (조정 가능)
- **창당 처리 시간**: 약 0.5-1초
- **최대 순회 시간**: 약 5-10초 (5창 × 10탭 기준)

### 메모리 사용량
- **기본**: ~50-100MB
- **OCR 처리 중**: ~100-150MB

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

## 📈 개선 사항 (v2.0)

### 향상된 필터링 시스템
- **시스템 창 필터링**: 알림 센터, 작업 표시줄 등 시스템 UI 자동 제외
- **창 크기 검증**: 최소 100x20 픽셀 이상의 창만 모니터링
- **중복 방지**: 같은 창에 한 번만 자동 승인 (재시작 전까지)

### 듀얼 모드 아키텍처
- **패시브 + 액티브 모드**: 두 가지 감지 방식을 동시에 운용
- **키 프로브 방식**: OCR보다 빠른 "1" + Backspace 감지
- **스마트 Idle 감지**: 사용자 활동 패턴 학습

### 개선된 패턴 매칭
- **문장 기반 감지**: 22개 이상의 승인 패턴 인식
- **지능형 응답 선택**: 옵션 내용 분석 후 적절한 응답 선택
- **컨텍스트 인식**: Claude 관련 키워드로 정확도 향상

자세한 내용은 [IMPROVEMENTS.md](IMPROVEMENTS.md)를 참조하세요.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=jahyunlee00299/Claude-Auto-Approver&type=Date)](https://star-history.com/#jahyunlee00299/Claude-Auto-Approver&Date)

---

**⭐ If you find this project useful, please consider giving it a star! ⭐**
