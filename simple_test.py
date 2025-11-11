#!/usr/bin/env python3
import sys
print("Python version:", sys.version)
print("Starting import...")

try:
    from approval_notifier import ApprovalNotifier
    print("Import successful!")

    notifier = ApprovalNotifier()
    print("Notifier created!")

    # Test pattern detection
    test_text = "Do you want to proceed?\n1. Yes"
    result = notifier.check_approval_pattern(test_text)
    print(f"Pattern test: {result}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
