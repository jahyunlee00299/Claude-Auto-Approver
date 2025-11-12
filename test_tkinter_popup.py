"""
Tkinter 팝업 테스트 - 확실하게 보이는 알림
"""
import tkinter as tk
from tkinter import messagebox
import time

def show_popup(title, message):
    """Tkinter 팝업 창 표시"""
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기
    root.attributes('-topmost', True)  # 항상 위에 표시

    # 메시지 박스 표시
    messagebox.showinfo(title, message)

    root.destroy()

def show_custom_popup(title, message, duration=3):
    """자동으로 사라지는 커스텀 팝업"""
    root = tk.Tk()
    root.title(title)

    # 창 크기 및 위치 설정
    width = 300
    height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - width - 20  # 우측 하단
    y = screen_height - height - 60

    root.geometry(f'{width}x{height}+{x}+{y}')
    root.attributes('-topmost', True)  # 항상 위에
    root.overrideredirect(True)  # 타이틀바 제거

    # 배경색
    root.configure(bg='#2d2d2d')

    # 메시지 레이블
    label = tk.Label(
        root,
        text=message,
        bg='#2d2d2d',
        fg='white',
        font=('Arial', 10),
        wraplength=280,
        justify='center'
    )
    label.pack(expand=True, pady=20, padx=10)

    # duration초 후 자동으로 닫기
    root.after(duration * 1000, root.destroy)

    root.mainloop()

if __name__ == "__main__":
    print("Tkinter 팝업 테스트 1: 클릭해야 닫히는 팝업")
    show_popup("테스트", "이 팝업이 보이나요?")

    print("\nTkinter 팝업 테스트 2: 3초 후 자동으로 닫히는 팝업")
    print("우측 하단을 확인하세요!")
    show_custom_popup("Claude Auto Approver", "자동 승인 완료!\nOption 2 전송됨", duration=3)

    print("\n테스트 완료!")
