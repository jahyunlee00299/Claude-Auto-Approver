#!/usr/bin/env python3
"""
Test Approval Dialog - Claude Code 스타일의 승인 대화상자 테스트
"""
import tkinter as tk
from tkinter import ttk

def create_approval_dialog():
    """Create a test approval dialog similar to Claude Code"""
    root = tk.Tk()
    root.title("Question")
    root.geometry("500x250")
    root.resizable(False, False)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Question text
    question_label = ttk.Label(
        main_frame,
        text="Do you want to proceed?",
        font=('Arial', 12, 'bold')
    )
    question_label.pack(pady=(0, 20))

    # Options frame
    options_frame = ttk.Frame(main_frame)
    options_frame.pack(fill=tk.BOTH, expand=True)

    # Option 1
    option1 = ttk.Label(
        options_frame,
        text="1. Yes",
        font=('Arial', 10)
    )
    option1.pack(anchor=tk.W, pady=5)

    # Option 2
    option2 = ttk.Label(
        options_frame,
        text="2. Yes, and don't ask again",
        font=('Arial', 10)
    )
    option2.pack(anchor=tk.W, pady=5)

    # Option 3
    option3 = ttk.Label(
        options_frame,
        text="3. No, and tell Claude",
        font=('Arial', 10)
    )
    option3.pack(anchor=tk.W, pady=5)

    # Instruction
    instruction = ttk.Label(
        main_frame,
        text="Select option (1-3):",
        font=('Arial', 9)
    )
    instruction.pack(pady=(20, 0))

    # Entry field
    entry = ttk.Entry(main_frame, width=10, font=('Arial', 10))
    entry.pack(pady=(5, 0))
    entry.focus()

    result_label = ttk.Label(main_frame, text="", foreground="green")
    result_label.pack(pady=(10, 0))

    def on_key(event):
        key = event.char
        if key in ['1', '2', '3']:
            result_label.config(text=f"Selected option {key}!")
            root.after(1000, root.destroy)

    root.bind('<Key>', on_key)

    print("\n" + "="*60)
    print("Test Approval Dialog Created")
    print("="*60)
    print("This window should be detected by OCR Auto Approver")
    print("It contains the pattern: 'Do you want to proceed?'")
    print("And options: '1. Yes', '2. Yes, and don't ask again'")
    print("\nThe approver should automatically send '2'")
    print("="*60 + "\n")

    root.mainloop()

if __name__ == "__main__":
    create_approval_dialog()
