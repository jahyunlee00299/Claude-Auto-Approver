#!/usr/bin/env python3
"""
Comprehensive notification test with various scenarios
"""
import sys
import os
import time
import winsound

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the notification function
from ocr_auto_approver import show_notification_popup

def test_with_sound():
    """Test notification with system sounds"""
    print("\n" + "="*60)
    print("TEST 1: Notifications with Different Sounds")
    print("="*60)

    sounds = [
        ('SystemAsterisk', 'Information'),
        ('SystemExclamation', 'Alert'),
        ('SystemHand', 'Critical')
    ]

    for i, (sound_type, level) in enumerate(sounds, 1):
        print(f"\n[{level} Level - Test {i}/3]")

        # Play sound
        try:
            winsound.PlaySound(sound_type, winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        # Show notification
        show_notification_popup(
            f"[{i}] {level} Approval",
            f"Test notification with {level.lower()} priority"
        )

        print(f"  Sound: {sound_type}")
        print(f"  Level: {level}")

        if i < len(sounds):
            time.sleep(2)

def test_rapid_notifications():
    """Test multiple rapid notifications"""
    print("\n" + "="*60)
    print("TEST 2: Rapid Fire Notifications (5 in quick succession)")
    print("="*60)

    for i in range(1, 6):
        print(f"\n[Quick Test {i}/5]")
        show_notification_popup(
            f"Rapid Approval [{i}]",
            f"Quick approval #{i} of 5"
        )
        time.sleep(0.5)  # Half second delay

def test_long_messages():
    """Test with longer messages"""
    print("\n" + "="*60)
    print("TEST 3: Long Message Notifications")
    print("="*60)

    messages = [
        ("Short", "OK"),
        ("Medium Length", "This is a medium length message for testing"),
        ("Long Message", "This is a much longer message to test how the notification system handles extended text content in the notification body")
    ]

    for i, (title_type, message) in enumerate(messages, 1):
        print(f"\n[{title_type} - Test {i}/3]")
        show_notification_popup(
            f"[{i}] {title_type} Approval",
            message
        )
        print(f"  Message length: {len(message)} chars")

        if i < len(messages):
            time.sleep(2)

def test_special_characters():
    """Test with special characters"""
    print("\n" + "="*60)
    print("TEST 4: Special Characters in Notifications")
    print("="*60)

    special_cases = [
        ("Numbers & Symbols", "Approval #123 @ 50% complete!"),
        ("Brackets [Test]", "Testing (parentheses) and [brackets]"),
        ("Path C:\\Test", "Window: C:\\Users\\Test\\file.py")
    ]

    for i, (title, message) in enumerate(special_cases, 1):
        print(f"\n[Special Char Test {i}/3]")
        show_notification_popup(
            f"[{i}] {title}",
            message
        )
        print(f"  Title: {title}")
        print(f"  Message: {message}")

        if i < len(special_cases):
            time.sleep(2)

def test_counter_simulation():
    """Simulate real approval counter"""
    print("\n" + "="*60)
    print("TEST 5: Simulated Real Approvals (Counter)")
    print("="*60)

    windows = [
        "PowerShell - Admin Mode",
        "Git Bash - Claude Project",
        "Command Prompt - System32",
        "Python - test.py",
        "VS Code - main.py"
    ]

    total_approvals = 0

    for window in windows:
        total_approvals += 1
        print(f"\n[Approval #{total_approvals}]")
        print(f"  Window: {window}")

        # Show notification with counter
        show_notification_popup(
            f"Auto Approval #{total_approvals}",
            f"Window: {window}"
        )

        # Play ascending beep for each approval
        try:
            winsound.Beep(800 + (total_approvals * 100), 200)
        except:
            pass

        time.sleep(1.5)

    print(f"\n  Total Approvals Completed: {total_approvals}")

def main():
    print("\n" + "="*70)
    print(" COMPREHENSIVE NOTIFICATION TEST SUITE")
    print("="*70)
    print("\nThis will run 5 different test scenarios:")
    print("  1. Different sound levels")
    print("  2. Rapid notifications")
    print("  3. Various message lengths")
    print("  4. Special characters")
    print("  5. Counter simulation")
    print("\nStarting tests in 2 seconds...")
    time.sleep(2)

    # Run all tests
    test_with_sound()
    time.sleep(2)

    test_rapid_notifications()
    time.sleep(2)

    test_long_messages()
    time.sleep(2)

    test_special_characters()
    time.sleep(2)

    test_counter_simulation()

    # Final summary
    print("\n" + "="*70)
    print(" ALL TESTS COMPLETED!")
    print("="*70)
    print("\nYou should have received approximately 19 notifications")
    print("\nCheck Windows Action Center (Win+N) for:")
    print("  - All notifications grouped under 'Claude Auto Approver'")
    print("  - Various message lengths and special characters")
    print("  - Timestamps on each notification")
    print("\nIf notifications appeared: SUCCESS!")
    print("If not, check Windows Settings > Notifications")
    print("="*70)

if __name__ == "__main__":
    main()