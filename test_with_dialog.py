#!/usr/bin/env python3
"""
Auto Yes 테스트 - 승인 대화상자를 띄우고 자동 승인 확인
"""
import sys
import time
import threading
import io
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from auto_yes import AutoYesApprover

def show_dialog_after_delay():
    """3초 후에 대화상자 띄우기"""
    import tkinter as tk
    from tkinter import messagebox

    time.sleep(3)

    root = tk.Tk()
    root.withdraw()

    print("\n📋 테스트 대화상자 표시!")
    result = messagebox.askyesno("Question", "Auto Yes가 자동으로 '1'을 입력할까요?")

    print(f"\n결과: {'Yes' if result else 'No'}")
    root.destroy()

def main():
    print("=" * 70)
    print("🧪 Auto Yes 테스트")
    print("=" * 70)
    print()
    print("테스트 순서:")
    print("  1. Auto Yes Approver 시작")
    print("  2. 3초 후 승인 대화상자 표시")
    print("  3. Auto Yes가 자동으로 다른 창에 '1' 입력")
    print()
    print("=" * 70)

    # Auto Yes 시작
    approver = AutoYesApprover()
    approver.start()

    print("\n✅ Auto Yes Approver 시작됨")
    print("⏰ 3초 후 대화상자가 나타납니다...")

    # 대화상자 스레드 시작
    dialog_thread = threading.Thread(target=show_dialog_after_delay)
    dialog_thread.daemon = True
    dialog_thread.start()

    # 15초 동안 모니터링
    for i in range(15):
        time.sleep(1)
        if i == 14:
            print(f"\n⏱️ {15-i}초 남음...")

    approver.stop()

    print("\n" + "=" * 70)
    print(f"📊 결과: {approver.approval_count}회 자동 승인")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 중단됨")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
