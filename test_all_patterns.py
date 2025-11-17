#!/usr/bin/env python3
"""
Test all approval patterns including edge cases
"""

def check_approval_pattern(text):
    """Check if text contains approval pattern"""
    if not text:
        return False

    text_lower = text.lower()
    text_normalized = ' '.join(text_lower.split())

    question_patterns = ['do you want', 'would you like', 'would you']
    action_patterns = ['to proceed', 'proceed', 'to approve', 'approve', 'to create', 'create', 'to allow', 'allow', 'select', 'choose']
    specific_patterns = [
        'select an option', 'choose an option', 'yes, and don\'t ask again',
        'yes, and remember', 'yes, allow all edits', 'approve this action',
        'allow this action', 'grant permission', 'proceed with', 'continue with',
        'select one of the following', 'choose one of the following',
        'no, and tell claude', 'tell claude what to do differently'
    ]

    has_option_1 = ('1.' in text or '1)' in text) and any('1.' in line or '1)' in line for line in text.split('\n'))
    has_option_2 = ('2.' in text or '2)' in text) and any('2.' in line or '2)' in line for line in text.split('\n'))

    if not (has_option_1 and has_option_2):
        return False

    for pattern in specific_patterns:
        if pattern in text_normalized:
            return True

    has_question = any(q in text_normalized for q in question_patterns)
    has_action = any(a in text_normalized for a in action_patterns)

    if has_question and has_action:
        return True

    if has_question or has_action:
        return True

    return False


# Test cases
test_cases = [
    {
        'name': 'Claude Code standard prompt',
        'text': """Do you want to proceed?
 > 1. Yes
   2. Tell Claude what to do differently"""
    },
    {
        'name': 'Three option prompt',
        'text': """Do you want to proceed?
 1. Yes
 2. Yes, and don't ask again
 3. No"""
    },
    {
        'name': 'Simple approval',
        'text': """Would you like to approve?
1. Yes
2. No"""
    },
    {
        'name': 'Select option format',
        'text': """Select an option:
1. Proceed
2. Cancel"""
    },
    {
        'name': 'Missing option numbers (should FAIL)',
        'text': """Do you want to proceed?
Yes
No"""
    },
    {
        'name': 'Only one option (should FAIL)',
        'text': """Do you want to proceed?
1. Yes"""
    },
]

print("="*70)
print("Testing All Approval Patterns")
print("="*70)

for i, test in enumerate(test_cases, 1):
    print(f"\n[Test {i}] {test['name']}")
    print("-"*70)
    result = check_approval_pattern(test['text'])
    status = "PASS (will approve)" if result else "FAIL (will not approve)"
    print(f"Result: {status}")

print("\n" + "="*70)
print("All tests completed!")
print("="*70)
