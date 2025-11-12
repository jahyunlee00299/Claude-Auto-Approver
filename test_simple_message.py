#!/usr/bin/env python3
"""
Simple message box test with sound
"""
import ctypes
import winsound
import time
import threading

def show_windows_message_box(title, message, style=0x40):
    """
    Show Windows message box using ctypes
    Style: 0x40 = Information icon
    """
    # Play sound
    try:
        winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
    except:
        pass

    # Show message box (non-blocking)
    def show_msg():
        ctypes.windll.user32.MessageBoxW(0, message, title, style)

    thread = threading.Thread(target=show_msg, daemon=True)
    thread.start()
    return thread

def show_balloon_tip(title, msg):
    """
    Show Windows balloon notification using ctypes
    """
    try:
        # Play sound
        winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)

        # Try to show balloon tip (may not work on all Windows versions)
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(
            title,
            msg,
            duration=5,
            threaded=True
        )
        return True
    except:
        return False

def main():
    print("=" * 60)
    print("Windows Approval Message Test")
    print("=" * 60)
    print()

    # Test 1: Message Box
    print("[TEST 1] Windows Message Box")
    timestamp = time.strftime('%H:%M:%S')
    title = f"Auto Approval [{timestamp}]"
    message = "Claude Code request has been automatically approved!\n\nOption 2 selected: Yes, don't ask again"

    print(f"  Title: {title}")
    print(f"  Message: {message}")

    thread1 = show_windows_message_box(title, message)

    time.sleep(2)

    # Test 2: Try balloon notification
    print("\n[TEST 2] Trying Balloon Notification")
    if show_balloon_tip("Approval Success", "Request processed automatically"):
        print("  Balloon notification sent")
    else:
        print("  Balloon notification not available")

    # Test 3: Console beep and message
    print("\n[TEST 3] Console Alert with Sound")
    print("  Playing sounds...")

    # Multiple beeps
    for i in range(3):
        winsound.Beep(1000 + i * 200, 200)  # Frequency, Duration
        time.sleep(0.1)

    print("  Sound played!")

    # Test 4: System sounds
    print("\n[TEST 4] System Sounds")
    sounds = [
        ('SystemAsterisk', 'Asterisk'),
        ('SystemExclamation', 'Exclamation'),
        ('SystemHand', 'Error'),
        ('SystemQuestion', 'Question')
    ]

    for sound_name, display_name in sounds:
        print(f"  Playing: {display_name}")
        try:
            winsound.PlaySound(sound_name, winsound.SND_ALIAS)
            time.sleep(0.5)
        except:
            print(f"    Could not play {display_name}")

    print("\n" + "=" * 60)
    print("[SUCCESS] Tests completed!")
    print("Check for:")
    print("  1. Message box popup")
    print("  2. Sound notifications")
    print("  3. Any balloon tips (if supported)")
    print("=" * 60)

    # Wait for message box to be closed
    print("\n[INFO] Close the message box to exit...")
    thread1.join()

if __name__ == "__main__":
    main()