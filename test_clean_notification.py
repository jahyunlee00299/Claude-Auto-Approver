"""
개선된 알림 최종 테스트
"""
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_auto_approver import show_notification_popup

def test_clean_notification():
    """깔끔한 알림 테스트"""
    print("=" * 60)
    print("개선된 알림 시스템 최종 테스트")
    print("=" * 60)

    print("\n알림 예시:")
    print("-" * 40)

    # 테스트
    show_notification_popup(
        title="자동 승인 완료",
        message="'Y' 키가 전송되었습니다",
        window_info="PowerShell - Administrator: Claude Code",
        duration=5
    )

    print("\n알림 내용:")
    print("제목: [체크] 자동 승인 완료")
    print("내용:")
    print("  [폰] 윈도우: PowerShell - Administrator: Claude Code")
    print("  [시계] 시간: [현재시간]")
    print("  ")
    print("  'Y' 키가 전송되었습니다")
    print("\n아이콘: 256x256 크기의 귀여운 캐릭터")

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_clean_notification()