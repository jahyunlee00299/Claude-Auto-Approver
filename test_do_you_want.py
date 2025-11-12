#!/usr/bin/env python3
"""
Test "Do you want" approval dialog
"""
import tkinter as tk
from tkinter import font
import time

def create_approval_dialog_3options():
    """Create a 3-option approval dialog"""
    root = tk.Tk()
    root.title("Claude Code - MINGW64")
    root.geometry("600x350")

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Stay on top
    root.attributes('-topmost', True)

    # Large fonts for OCR
    title_font = font.Font(family="Arial", size=16, weight="bold")
    option_font = font.Font(family="Arial", size=14)

    # Title
    title_label = tk.Label(
        root,
        text="Do you want to proceed?",
        font=title_font,
        pady=20
    )
    title_label.pack()

    # Options frame
    options_frame = tk.Frame(root, pady=20)
    options_frame.pack()

    option1 = tk.Label(
        options_frame,
        text="1. Yes, proceed once",
        font=option_font,
        anchor="w",
        pady=8
    )
    option1.pack(fill='x', padx=60)

    option2 = tk.Label(
        options_frame,
        text="2. Yes, and don't ask again",
        font=option_font,
        anchor="w",
        pady=8
    )
    option2.pack(fill='x', padx=60)

    option3 = tk.Label(
        options_frame,
        text="3. No, and tell Claude what to do differently",
        font=option_font,
        anchor="w",
        pady=8
    )
    option3.pack(fill='x', padx=60)

    # Instructions
    instruction_label = tk.Label(
        root,
        text="Select an option (1-3):",
        font=option_font,
        pady=15
    )
    instruction_label.pack()

    # Status
    status_label = tk.Label(
        root,
        text="Waiting for OCR auto-approver...",
        font=font.Font(family="Arial", size=12),
        fg="blue"
    )
    status_label.pack()

    def on_key(event):
        """Handle key press"""
        if event.char in ['1', '2', '3']:
            status_label.config(
                text=f"Option {event.char} selected by auto-approver!",
                fg="green",
                font=font.Font(family="Arial", size=12, weight="bold")
            )

            # Print results
            print(f"\n{'='*60}")
            print(f"[SUCCESS] Auto-approver detected the dialog!")
            print(f"[SUCCESS] Key '{event.char}' was pressed")

            if event.char == '2':
                print(f"[CORRECT] Option 2 selected (3-option dialog)")
                print(f"[INFO] Expected: Option 2 (yes, don't ask again)")
            else:
                print(f"[WARNING] Unexpected option selected!")
                print(f"[INFO] Expected option 2, got option {event.char}")

            print(f"{'='*60}\n")

            # Close after 2 seconds
            root.after(2000, root.destroy)

    root.bind('<Key>', on_key)

    print("="*60)
    print("3-Option Dialog Created: 'Do you want to proceed?'")
    print("="*60)
    print("\nExpected behavior:")
    print("  1. OCR detects 3 options (1, 2, 3)")
    print("  2. Auto-approver should select option 2")
    print("  3. Notification should show with detected text")
    print("\nWaiting for auto-approver...")
    print("(Make sure ocr_auto_approver.py is running!)\n")

    root.mainloop()

def create_approval_dialog_2options():
    """Create a 2-option approval dialog"""
    root = tk.Tk()
    root.title("Claude Code - MINGW64")
    root.geometry("550x300")

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Stay on top
    root.attributes('-topmost', True)

    # Large fonts for OCR
    title_font = font.Font(family="Arial", size=16, weight="bold")
    option_font = font.Font(family="Arial", size=14)

    # Title
    title_label = tk.Label(
        root,
        text="Do you want to allow this?",
        font=title_font,
        pady=20
    )
    title_label.pack()

    # Options frame
    options_frame = tk.Frame(root, pady=20)
    options_frame.pack()

    option1 = tk.Label(
        options_frame,
        text="1. Yes, allow",
        font=option_font,
        anchor="w",
        pady=10
    )
    option1.pack(fill='x', padx=60)

    option2 = tk.Label(
        options_frame,
        text="2. No, cancel",
        font=option_font,
        anchor="w",
        pady=10
    )
    option2.pack(fill='x', padx=60)

    # Instructions
    instruction_label = tk.Label(
        root,
        text="Select an option (1-2):",
        font=option_font,
        pady=15
    )
    instruction_label.pack()

    # Status
    status_label = tk.Label(
        root,
        text="Waiting for OCR auto-approver...",
        font=font.Font(family="Arial", size=12),
        fg="blue"
    )
    status_label.pack()

    def on_key(event):
        """Handle key press"""
        if event.char in ['1', '2']:
            status_label.config(
                text=f"Option {event.char} selected by auto-approver!",
                fg="green",
                font=font.Font(family="Arial", size=12, weight="bold")
            )

            # Print results
            print(f"\n{'='*60}")
            print(f"[SUCCESS] Auto-approver detected the dialog!")
            print(f"[SUCCESS] Key '{event.char}' was pressed")

            if event.char == '1':
                print(f"[CORRECT] Option 1 selected (2-option dialog)")
                print(f"[INFO] Expected: Option 1 (yes, allow)")
            else:
                print(f"[WARNING] Unexpected option selected!")
                print(f"[INFO] Expected option 1, got option {event.char}")

            print(f"{'='*60}\n")

            # Close after 2 seconds
            root.after(2000, root.destroy)

    root.bind('<Key>', on_key)

    print("="*60)
    print("2-Option Dialog Created: 'Do you want to allow this?'")
    print("="*60)
    print("\nExpected behavior:")
    print("  1. OCR detects 2 options (1, 2)")
    print("  2. Auto-approver should select option 1")
    print("  3. Notification should show with detected text")
    print("\nWaiting for auto-approver...")
    print("(Make sure ocr_auto_approver.py is running!)\n")

    root.mainloop()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing 'Do you want' approval dialogs")
    print("="*60)
    print("\nTest 1: 3-option dialog")
    print("Running in 2 seconds...\n")
    time.sleep(2)

    create_approval_dialog_3options()

    print("\n\nTest 1 complete. Starting Test 2 in 3 seconds...\n")
    time.sleep(3)

    print("Test 2: 2-option dialog")
    print("Running in 2 seconds...\n")
    time.sleep(2)

    create_approval_dialog_2options()

    print("\n\n" + "="*60)
    print("All tests complete!")
    print("="*60)
    print("\nCheck Windows Action Center for notifications!")
