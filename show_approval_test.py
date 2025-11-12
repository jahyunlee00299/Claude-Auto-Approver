#!/usr/bin/env python3
"""
간단한 승인 요청 대화상자 - OCR 테스트용
"""
import tkinter as tk
import time

def show_approval_dialog():
    """Show approval dialog that stays open"""
    root = tk.Tk()
    root.title("Claude Code - Question")
    root.geometry("600x350")
    root.configure(bg='#ffffff')

    # Center the window
    root.update_idletasks()
    width = 600
    height = 350
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Main frame
    main_frame = tk.Frame(root, bg='#ffffff', padx=40, pady=30)
    main_frame.pack(fill='both', expand=True)

    # Title with icon
    title_frame = tk.Frame(main_frame, bg='#ffffff')
    title_frame.pack(pady=(0, 20))

    title_label = tk.Label(
        title_frame,
        text="⚠️  Would you like to proceed?",
        font=('Segoe UI', 16, 'bold'),
        bg='#ffffff',
        fg='#2c3e50'
    )
    title_label.pack()

    # Description
    desc_label = tk.Label(
        main_frame,
        text="Claude Code wants to create a new file:\n\ntest_implementation.py\n\nDo you want to approve this action?",
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#555555',
        justify='center'
    )
    desc_label.pack(pady=(0, 30))

    # Options frame with border
    options_container = tk.Frame(main_frame, bg='#e8e8e8', relief='solid', borderwidth=1)
    options_container.pack(fill='x', padx=20)

    options_inner = tk.Frame(options_container, bg='#ffffff', padx=15, pady=15)
    options_inner.pack(fill='both', expand=True, padx=2, pady=2)

    # Option 1
    opt1_label = tk.Label(
        options_inner,
        text="1. Yes, proceed",
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#333333',
        anchor='w',
        padx=10,
        pady=8
    )
    opt1_label.pack(fill='x')

    # Separator
    tk.Frame(options_inner, height=1, bg='#e8e8e8').pack(fill='x', pady=5)

    # Option 2
    opt2_label = tk.Label(
        options_inner,
        text="2. Yes, and don't ask again",
        font=('Segoe UI', 11, 'bold'),
        bg='#ffffff',
        fg='#27ae60',
        anchor='w',
        padx=10,
        pady=8
    )
    opt2_label.pack(fill='x')

    # Separator
    tk.Frame(options_inner, height=1, bg='#e8e8e8').pack(fill='x', pady=5)

    # Option 3
    opt3_label = tk.Label(
        options_inner,
        text="3. No, and tell Claude what to do differently",
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#e74c3c',
        anchor='w',
        padx=10,
        pady=8
    )
    opt3_label.pack(fill='x')

    # Instruction at bottom
    instruction_label = tk.Label(
        main_frame,
        text="Press 1, 2, or 3 to select • ESC to cancel",
        font=('Segoe UI', 9),
        bg='#ffffff',
        fg='#999999'
    )
    instruction_label.pack(pady=(15, 0))

    # Result tracking
    result = {'selected': None, 'closed': False}

    def on_key_press(event):
        if event.char in ['1', '2', '3']:
            result['selected'] = event.char
            # Update display
            instruction_label.config(
                text=f"✓ Option {event.char} selected! Closing in 2 seconds...",
                fg='#27ae60',
                font=('Segoe UI', 10, 'bold')
            )
            root.after(2000, lambda: close_window())
        elif event.keysym == 'Escape':
            close_window()

    def close_window():
        result['closed'] = True
        root.destroy()

    root.bind('<Key>', on_key_press)

    # Keep on top temporarily
    root.lift()
    root.attributes('-topmost', True)
    root.focus_force()

    # Print info
    print("\n" + "="*70)
    print("Test Approval Dialog Displayed")
    print("="*70)
    print("\n[OK] Dialog shown in center of screen")
    print("\nThis dialog contains approval patterns:")
    print("  - 'Would you like to proceed?' - approval request pattern")
    print("  - 'Do you want to approve' - approval keyword")
    print("  - '1. Yes, proceed' - option 1")
    print("  - '2. Yes, and don't ask again' - option 2 (recommended)")
    print("  - '3. No, and tell Claude' - option 3")
    print("\nIf OCR Auto Approver is running:")
    print("  -> It should auto-detect this dialog")
    print("  -> It should auto-press '2' key")
    print("\nWaiting... (Press 1, 2, 3 to test or ESC to cancel)")
    print("="*70 + "\n")

    root.mainloop()

    # Print result
    if result['selected']:
        print(f"\n[OK] Option {result['selected']} was selected!\n")
    elif result['closed']:
        print("\nDialog closed (no selection)\n")

if __name__ == "__main__":
    show_approval_dialog()
