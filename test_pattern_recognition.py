#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test pattern recognition for approval messages
"""
import sys
import io

# Set UTF-8 output for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Test texts that should be recognized
test_cases = [
    {
        "name": "Create file with 3 options",
        "text": """
Do you want to create test_approval_notification.py?
   1. Yes
   2. Yes, allow all edits during this session (shift+tab)
   3. No, and tell Claude what to do differently (esc)
        """,
        "expected_key": "2"
    },
    {
        "name": "Simple Yes/No",
        "text": """
Do you want to proceed?
   1. Yes
   2. No
        """,
        "expected_key": "1"
    },
    {
        "name": "Allow all edits",
        "text": """
Would you like to allow this edit?
   1. Yes, once
   2. Yes, and don't ask again
        """,
        "expected_key": "2"
    },
]

# Import the approval detection functions
from ocr_auto_approver import OCRAutoApprover

# Suppress initialization messages for clean test output
import os
old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
approver = OCRAutoApprover()
sys.stdout.close()
sys.stdout = old_stdout

print("="*70)
print("PATTERN RECOGNITION TEST")
print("="*70)
print()

passed = 0
failed = 0

for test in test_cases:
    print(f"\nTest: {test['name']}")
    print("-" * 70)
    print("Input text: [text content hidden to avoid encoding issues]")
    print()

    # Test pattern detection
    is_recognized = approver.check_approval_pattern(test['text'])

    if is_recognized:
        # Test key determination
        response_key = approver.determine_response_key(test['text'])
        print(f"✓ Pattern RECOGNIZED")
        print(f"  Response key: '{response_key}' (expected: '{test['expected_key']}')")

        if response_key == test['expected_key']:
            print(f"  ✓ CORRECT key selected")
            passed += 1
        else:
            print(f"  ✗ WRONG key selected")
            failed += 1
    else:
        print(f"✗ Pattern NOT RECOGNIZED")
        failed += 1

    print("-" * 70)

print()
print("="*70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*70)
