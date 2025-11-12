#!/usr/bin/env python3
"""
Test full approval workflow with notification
Simulates an approval dialog window
"""
import tkinter as tk
from tkinter import font
import time
import sys

def create_approval_dialog():
    """Create a fake approval dialog to test OCR detection"""

    root = tk.Tk()
    root.title("Claude Code - Approval Request")
    root.geometry("500x300")

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Make window stay on top
    root.attributes('-topmost', True)

    # Large, clear font for OCR
    title_font = font.Font(family="Arial", size=14, weight="bold")
    option_font = font.Font(family="Arial", size=12)

    # Title
    title_label = tk.Label(
        root,
        text="Would you like to proceed with this edit?",
        font=title_font,
        pady=20
    )
    title_label.pack()

    # Options
    options_frame = tk.Frame(root, pady=10)
    options_frame.pack()

    option1 = tk.Label(
        options_frame,
        text="1. Yes, proceed once",
        font=option_font,
        anchor="w",
        pady=5
    )
    option1.pack(fill='x', padx=50)

    option2 = tk.Label(
        options_frame,
        text="2. Yes, and don't ask again",
        font=option_font,
        anchor="w",
        pady=5
    )
    option2.pack(fill='x', padx=50)

    # Instructions
    instruction_label = tk.Label(
        root,
        text="Select an option (1-2):",
        font=option_font,
        pady=20
    )
    instruction_label.pack()

    # Selected option display
    selected_label = tk.Label(
        root,
        text="Waiting for OCR detection...",
        font=option_font,
        fg="blue"
    )
    selected_label.pack()

    def on_key(event):
        """Handle key press"""
        if event.char in ['1', '2']:
            selected_label.config(
                text=f"✓ Option {event.char} selected by auto-approver!",
                fg="green"
            )
            print(f"\n[SUCCESS] Key '{event.char}' received!")
            print("[SUCCESS] Auto-approval worked!")
            print("[INFO] Notification should have appeared!")
            # Close after 2 seconds
            root.after(2000, root.destroy)

    root.bind('<Key>', on_key)

    print("="*60)
    print("Approval Dialog Created")
    print("="*60)
    print("\nThis window simulates a Claude Code approval request.")
    print("The OCR auto-approver should:")
    print("  1. Detect this dialog")
    print("  2. Read the text using OCR")
    print("  3. Determine which option to select")
    print("  4. Send the key press")
    print("  5. Show a notification with detected text")
    print("\nWaiting for auto-approver to detect and respond...")
    print("(Make sure ocr_auto_approver.py is running!)\n")

    root.mainloop()

    print("\n[INFO] Dialog closed.")

if __name__ == "__main__":
    create_approval_dialog()
