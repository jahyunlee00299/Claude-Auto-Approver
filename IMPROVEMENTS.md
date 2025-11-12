# OCR Auto Approver - 승인 로직 개선 사항

## 문제점
- 윈도우 알림 센터에서도 승인 요청이 감지될 수 있음
- 시스템 UI, 작은 팝업 등에서 false positive 발생 가능
- 너무 느슨한 패턴 매칭으로 인한 잘못된 승인

## 개선 사항

### 1. 시스템 창 필터링 (is_system_window)
**제외되는 창:**
- Windows.UI.Core.CoreWindow (알림 센터)
- Shell_TrayWnd (작업 표시줄)
- NotifyIconOverflowWindow (시스템 트레이)
- ApplicationFrameWindow (UWP 앱 컨테이너)
- Windows.Internal.Shell.TabProxyWindow (윈도우 셸)
- ImmersiveLauncher (시작 메뉴)
- MultitaskingViewFrame (작업 보기)
- ForegroundStaging (시스템 스테이징 창)

**추가 검증:**
- 'notification', 'toast', 'windows.ui', 'xaml' 클래스명 제외
- WS_EX_TOOLWINDOW 스타일 창 제외 (도구 창)
- WS_EX_NOACTIVATE 스타일 창 제외 (활성화 불가 창)

### 2. 창 크기 검증
- **최소 크기: 200x100 픽셀**
- 작은 팝업이나 토스트 알림 제외

### 3. 승인 패턴 검증 강화 (check_approval_pattern)

#### 방법 1: Claude 키워드 존재 시
- 승인 패턴 1개 + Claude 키워드 1개 = 즉시 승인
- Claude 키워드: 'claude', 'tool', 'bash', 'edit', 'read', 'write'

#### 방법 2: Claude 키워드 없을 시
- **최소 2개 이상의 승인 지표 필요**
- 승인 지표:
  - 'proceed' 포함
  - 'approve' 포함
  - 'yes' 포함
  - 'option' + ('select' 또는 숫자)
  - 'permission' 또는 'allow' 포함

### 4. Quick Detection 개선
- **이전:** 승인 키워드만 확인 → 너무 느슨함
- **현재:** 승인 키워드 + Claude 관련 키워드 **모두 필요**

**Quick detect 키워드:**
- 'question', 'approve', 'confirm', 'permission', 'allow'

**Claude 관련 키워드:**
- 'claude', 'tool', 'bash', 'edit', 'mingw', 'powershell', 'cmd'

## 테스트 방법

```bash
cd "C:\Users\Jahyun\PycharmProjects\Claude-Auto-Approver"
python ocr_auto_approver.py
```

## 예상 효과

### ✅ 승인됨 (True Positive)
1. Claude Code의 Bash 승인 요청 - 'approve' + 'bash'
2. PowerShell 창의 승인 요청 - 'question' + 'powershell'
3. OCR 텍스트: "Proceed with tool execution?" - 'proceed' + 'tool'

### ❌ 승인 안됨 (False Positive 방지)
1. 윈도우 알림 센터 - 시스템 창 필터링
2. 작은 토스트 알림 (100x50) - 크기 필터링
3. 일반 대화상자 "Are you sure?" - Claude 키워드 없음 + 지표 부족
4. 브라우저 팝업 - Claude 관련 키워드 없음

## 주의 사항

- **첫 실행 시 테스트**: 실제 Claude Code 승인 요청이 올 때까지 대기하여 정상 작동 확인
- **로그 확인**: 승인 시 상세한 로그가 출력됨 (창 제목, HWND, 감지 방법)
- **알림 확인**: 윈도우 알림으로 승인 내역 확인 가능

## 문제 발생 시 대처

### 승인이 안 되는 경우
1. Claude Code 창 제목에 'claude', 'tool', 'bash' 등이 있는지 확인
2. OCR이 텍스트를 제대로 읽고 있는지 로그 확인

### 잘못 승인되는 경우
1. `exclude_keywords`에 제외할 키워드 추가 (50-53번 줄)
2. `system_classes`에 제외할 창 클래스 추가 (56-66번 줄)
3. `claude_keywords`에서 너무 일반적인 키워드 제거 (227번 줄)
