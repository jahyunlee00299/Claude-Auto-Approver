#!/usr/bin/env python3
"""
Direct popup window test - guaranteed visible
"""
import tkinter as tk
from tkinter import messagebox
import ctypes
import winsound
import time
import threading

def show_message_box_direct(title, message):
    """
    Show a direct Windows message box that WILL appear
    """
    # Play sound
    winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)

    # Show message box (blocking)
    ctypes.windll.user32.MessageBoxW(
        0,
        message,
        title,
        0x40 | 0x1000  # Information icon + Stay on top
    )

def show_tkinter_popup(title, message, counter=1):
    """
    Show a custom Tkinter popup window with counter badge
    """
    # Play sound
    winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)

    # Create window
    root = tk.Tk()
    root.withdraw()  # Hide main window

    # Create popup
    popup = tk.Toplevel(root)
    popup.title(f"Auto Approval [{counter}]")

    # Window settings
    popup.attributes('-topmost', True)  # Always on top
    popup.attributes('-toolwindow', True)  # Remove from taskbar

    # Set size and position (bottom-right corner)
    width = 350
    height = 150
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = screen_width - width - 50
    y = screen_height - height - 100
    popup.geometry(f'{width}x{height}+{x}+{y}')

    # Colors
    bg_color = '#2b2b2b'
    fg_color = '#ffffff'
    accent_color = '#0084ff'

    popup.configure(bg=bg_color)

    # Create badge-like counter display
    counter_frame = tk.Frame(popup, bg=accent_color, width=50, height=50)
    counter_frame.place(x=10, y=10)

    counter_label = tk.Label(
        counter_frame,
        text=str(counter),
        font=('Arial', 20, 'bold'),
        fg='white',
        bg=accent_color
    )
    counter_label.place(relx=0.5, rely=0.5, anchor='center')

    # Title
    title_label = tk.Label(
        popup,
        text=title,
        font=('Arial', 12, 'bold'),
        fg=fg_color,
        bg=bg_color
    )
    title_label.place(x=70, y=15)

    # Message
    msg_label = tk.Label(
        popup,
        text=message,
        font=('Arial', 10),
        fg='#cccccc',
        bg=bg_color,
        justify='left'
    )
    msg_label.place(x=70, y=45)

    # Timestamp
    timestamp = time.strftime('%H:%M:%S')
    time_label = tk.Label(
        popup,
        text=f"Time: {timestamp}",
        font=('Arial', 8),
        fg='#888888',
        bg=bg_color
    )
    time_label.place(x=10, y=120)

    # OK button
    ok_button = tk.Button(
        popup,
        text="OK",
        command=lambda: [popup.destroy(), root.destroy()],
        bg=accent_color,
        fg='white',
        font=('Arial', 10, 'bold'),
        padx=20
    )
    ok_button.place(x=280, y=110)

    # Auto-close after 5 seconds
    def auto_close():
        time.sleep(5)
        try:
            popup.destroy()
            root.destroy()
        except:
            pass

    threading.Thread(target=auto_close, daemon=True).start()

    # Show window
    popup.deiconify()
    root.mainloop()

def main():
    print("=" * 60)
    print("Direct Popup Test - These WILL be visible!")
    print("=" * 60)
    print()

    # Test 1: Windows Message Box
    print("[Test 1] Windows Message Box")
    print("  This will show a standard Windows message box")
    print("  You MUST see this - it's a system dialog")
    print()

    show_message_box_direct(
        "Auto Approval [1] - Test",
        "This is a direct Windows message box.\n\nIf you can see this, notifications work!\n\nClick OK to continue to Test 2."
    )

    print("  [OK] Message box was closed\n")

    # Test 2: Custom Tkinter Popups with counters
    print("[Test 2] Custom Popup Windows with Counter Badges")
    print("  These will appear in the bottom-right corner")
    print("  Each has a blue counter badge showing the number")
    print()

    for i in range(1, 4):
        print(f"  Showing popup #{i}...")

        # Run in thread to not block
        thread = threading.Thread(
            target=show_tkinter_popup,
            args=(
                f"Auto Approval #{i}",
                f"Claude Code request approved\nTotal approvals: {i}",
                i
            )
        )
        thread.start()

        # Wait a bit between popups
        time.sleep(1.5)

    print()
    print("=" * 60)
    print("Results:")
    print()
    print("1. You should have seen a Windows message box")
    print("2. You should see 3 popup windows in the corner")
    print("   Each with a blue badge showing numbers 1, 2, 3")
    print()
    print("If you saw these, then notifications ARE working!")
    print("The issue was with Windows Toast notifications specifically.")
    print("=" * 60)

if __name__ == "__main__":
    main()