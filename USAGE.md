# 📖 Claude Auto Approver 사용 가이드

## 🎯 프로그램 선택 가이드

### 1. approval_notifier.py ⭐ **추천**
**승인 요청 감지 시 알림만 표시**

```bash
python approval_notifier.py
```

**특징:**
- 🔔 Windows 알림으로 승인 요청 알려줌
- 🔊 소리 알림 포함
- 💤 백그라운드에서 조용히 실행
- ✋ 자동 입력 없음 (사용자가 직접 "1" 입력)

**알림 형식:**
```
제목: 🔔 승인 요청
내용: 📟 터미널: MINGW64 (또는 창 이름)
      Claude Code가 승인을 기다리고 있습니다.
```

**언제 사용하나요?**
- 승인 요청을 놓치고 싶지 않을 때
- 자동 입력은 원하지 않고 알림만 받고 싶을 때
- 백그라운드에서 조용히 실행하고 싶을 때

---

### 2. simple_auto_approver.py
**Idle 상태 감지 시 자동으로 "1" 입력**

```bash
# 기본 실행 (3초 idle, 0.5초 체크)
python simple_auto_approver.py

# 커스텀 설정
python simple_auto_approver.py --idle 5 --interval 1
```

**특징:**
- ⏰ 사용자 idle 감지 (기본 3초)
- ⌨️ 자동으로 "1" 입력 (Enter는 누르지 않음)
- 🔄 모든 PyCharm 탭 순회하며 입력
- 📊 상태 출력 (10초마다)

**옵션:**
- `--idle SECONDS`: Idle 시간 (기본: 3초)
- `--interval SECONDS`: 체크 간격 (기본: 0.5초)

**언제 사용하나요?**
- 승인을 자동으로 처리하고 싶을 때
- 여러 터미널/탭에서 동시에 작업할 때
- 반복적인 승인 작업이 많을 때

---

### 3. hybrid_monitor.py
**콘솔 버퍼 + 화면 캡처 OCR로 승인 패턴 감지**

```bash
python hybrid_monitor.py
```

**특징:**
- 📋 콘솔 버퍼 직접 읽기 (빠름)
- 📸 화면 캡처 + OCR (느리지만 GUI 앱도 지원)
- 🎯 PyCharm, VSCode, 터미널 등 모두 지원
- ⌨️ 자동으로 "1" 입력

**필요 패키지:**
```bash
pip install pytesseract  # OCR 기능 (선택사항)
```

**언제 사용하나요?**
- GUI 앱(PyCharm, VSCode)에서도 자동 입력하고 싶을 때
- 모든 타입의 프로그램을 지원하고 싶을 때

---

## 🚀 빠른 시작

### 설치
```bash
# 1. 저장소 클론
git clone https://github.com/jahyunlee00299/Claude-Auto-Approver.git
cd Claude-Auto-Approver

# 2. 의존성 설치
pip install -r requirements.txt

# 3. Windows 알림 라이브러리 설치 (approval_notifier용)
pip install winotify
```

### 추천 사용법
```bash
# 1. 알림 프로그램을 백그라운드로 실행
python approval_notifier.py &

# 2. 작업 계속하기
# 승인 요청이 오면 자동으로 알림이 뜹니다!

# 3. 종료하려면
pkill -f approval_notifier
# 또는 Ctrl+C
```

---

## 📋 감지 패턴

모든 프로그램이 다음 패턴을 감지합니다:

```
Do you want to proceed?
1. Yes
2. Yes, and don't ask again for similar commands
3. No, and tell Claude what to do differently
```

추가 패턴:
- `1. Approve`
- `1. OK`
- `1) Yes`
- `option (1-`
- `Select (1)`

---

## ⚙️ 설정

### approval_notifier.py 설정
파일 내부에서 수정:
```python
self.min_notification_interval = 5  # 알림 간격 (초)
```

### simple_auto_approver.py 설정
```bash
python simple_auto_approver.py --idle 5 --interval 1
```
- `--idle 5`: 5초 idle 후 입력
- `--interval 1`: 1초마다 체크

---

## 🛑 중지 방법

### Ctrl+C로 중지
대부분의 프로그램은 `Ctrl+C`로 중지할 수 있습니다.

### 백그라운드 프로세스 종료
```bash
# Python 프로세스 확인
ps aux | grep python

# 특정 프로그램 종료
pkill -f approval_notifier
pkill -f simple_auto_approver
```

### Windows에서
```bash
# 프로세스 확인
tasklist | grep python

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F
```

---

## 💡 팁

1. **백그라운드 실행**: `&`를 사용하여 백그라운드 실행
   ```bash
   python approval_notifier.py &
   ```

2. **로그 보기**: 출력을 파일로 리다이렉션
   ```bash
   python approval_notifier.py > notifier.log 2>&1 &
   ```

3. **자동 시작**: Windows 시작 프로그램에 추가
   - `shell:startup` 폴더에 배치 파일 추가

4. **여러 프로그램 동시 실행**:
   ```bash
   # 알림 + 자동 입력 모두 사용
   python approval_notifier.py &
   python simple_auto_approver.py --idle 10
   ```

---

## 🔧 문제 해결

### 알림이 안 뜨는 경우
1. winotify 설치 확인: `pip install winotify`
2. Windows 알림 설정 확인
3. 콘솔에서 직접 실행하여 오류 확인

### 자동 입력이 안 되는 경우
1. 창이 활성화되어 있는지 확인
2. Idle 시간 조정: `--idle` 값 증가
3. 관리자 권한으로 실행

### 너무 자주 입력되는 경우
1. Idle 시간 증가: `--idle 10`
2. 체크 간격 증가: `--interval 2`
3. `min_approval_interval` 값 증가

---

## 📞 지원

문제가 있으면 GitHub Issues에 보고해주세요!
https://github.com/jahyunlee00299/Claude-Auto-Approver/issues
