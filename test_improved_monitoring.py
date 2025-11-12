#!/usr/bin/env python3
"""
개선된 모니터링 기능 테스트
"""
import sys
import io
import time

# UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ocr_auto_approver import OCRAutoApprover

def test_verbose_window_detection():
    """Verbose 모드로 윈도우 감지 테스트"""
    print("="*80)
    print("Verbose 윈도우 감지 테스트")
    print("="*80)
    print()

    approver = OCRAutoApprover()

    print("윈도우 스캔 중 (verbose 모드)...")
    print("-"*80)
    windows = approver.find_target_windows(verbose=True)
    print("-"*80)
    print(f"\n총 {len(windows)}개의 타겟 윈도우 발견\n")
    print("="*80)

if __name__ == "__main__":
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                     개선된 모니터링 기능 테스트                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()

    test_verbose_window_detection()

    print("\n✓ 테스트 완료\n")
