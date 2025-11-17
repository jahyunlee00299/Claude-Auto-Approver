#!/usr/bin/env python3
"""
Test pattern detection with the actual Claude Code prompt
"""

# Simulate the approval pattern check logic
def check_approval_pattern(text):
    """Check if text contains approval pattern"""
    if not text:
        return False

    text_lower = text.lower()
    text_normalized = ' '.join(text_lower.split())

    # Question patterns
    question_patterns = [
        'do you want',
        'would you like',
        'would you',
    ]

    # Action patterns
    action_patterns = [
        'to proceed',
        'proceed',
        'to approve',
        'approve',
        'to create',
        'create',
        'to allow',
        'allow',
        'select',
        'choose',
    ]

    # Specific patterns
    specific_patterns = [
        'select an option',
        'choose an option',
        'yes, and don\'t ask again',
        'yes, and remember',
        'yes, allow all edits',
        'approve this action',
        'allow this action',
        'grant permission',
        'proceed with',
        'continue with',
        'select one of the following',
        'choose one of the following',
        'no, and tell claude',
        'tell claude what to do differently'
    ]

    # Check option numbers
    has_option_1 = ('1.' in text or '1)' in text) and any('1.' in line or '1)' in line for line in text.split('\n'))
    has_option_2 = ('2.' in text or '2)' in text) and any('2.' in line or '2)' in line for line in text.split('\n'))

    print(f"[DEBUG] has_option_1={has_option_1}, has_option_2={has_option_2}")

    if not (has_option_1 and has_option_2):
        print("[DEBUG] Missing option numbers - REJECTED")
        return False

    # Check for specific patterns
    for pattern in specific_patterns:
        if pattern in text_normalized:
            print(f"[DEBUG] Matched specific pattern: '{pattern}' - APPROVED")
            return True

    # Check for question + action combination
    has_question = any(q in text_normalized for q in question_patterns)
    has_action = any(a in text_normalized for a in action_patterns)

    print(f"[DEBUG] has_question={has_question}, has_action={has_action}")

    if has_question and has_action:
        matched_q = [q for q in question_patterns if q in text_normalized]
        matched_a = [a for a in action_patterns if a in text_normalized]
        print(f"[DEBUG] Matched question+action: {matched_q[0]} + {matched_a[0]} - APPROVED")
        return True

    # Fallback
    if has_question or has_action:
        print(f"[DEBUG] Matched approval pattern (fallback) - APPROVED")
        return True

    print("[DEBUG] No pattern matched - REJECTED")
    return False


# Test with the actual Claude Code prompt
test_text = """Do you want to proceed?
 > 1. Yes
   2. Tell Claude what to do differently"""

print("="*70)
print("Testing Claude Code Approval Pattern")
print("="*70)
print("\nTest text:")
print(test_text.encode('ascii', 'ignore').decode('ascii'))
print("\n" + "="*70)
print("Pattern check result:")
print("="*70 + "\n")

result = check_approval_pattern(test_text)

print("\n" + "="*70)
if result:
    print("FINAL RESULT: WILL AUTO-APPROVE (will send '1')")
else:
    print("FINAL RESULT: WILL NOT AUTO-APPROVE")
print("="*70)
