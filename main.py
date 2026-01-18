"""
회사 용어 위키 - 메인 진입점
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sys
import os

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_database, insert_sample_data
from repository import UserRepository
from ui.main_window import MainWindow
from ui.styles import COLORS, FONTS


class LoginDialog(tk.Tk):
    """로그인 다이얼로그"""
    
    def __init__(self):
        super().__init__()
        self.title("🏢 회사 용어 위키 - 로그인")
        self.geometry("400x250")
        self.resizable(False, False)
        
        self.configure(bg=COLORS['background'])
        
        self.result_user = None
        
        self._create_widgets()
        
        # 중앙 정렬
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Enter 키 바인딩
        self.bind('<Return>', lambda e: self._login())
    
    def _create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = tk.Frame(self, bg=COLORS['surface'], padx=30, pady=30)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # 제목
        tk.Label(
            main_frame,
            text="🏢 회사 용어 위키",
            font=FONTS['title'],
            bg=COLORS['surface'],
            fg=COLORS['text']
        ).pack(pady=(0, 20))
        
        # 안내 문구
        tk.Label(
            main_frame,
            text="사용자 이름을 입력하세요",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_light']
        ).pack()
        
        # 입력 필드
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            main_frame,
            textvariable=self.username_var,
            font=FONTS['body'],
            width=25
        )
        self.username_entry.pack(pady=15)
        self.username_entry.focus()
        
        # 로그인 버튼
        login_btn = tk.Button(
            main_frame,
            text="시작하기",
            font=FONTS['body'],
            bg=COLORS['primary'],
            fg='white',
            activebackground=COLORS['primary_dark'],
            activeforeground='white',
            bd=0,
            padx=30,
            pady=8,
            cursor='hand2',
            command=self._login
        )
        login_btn.pack()
        
        # 안내 문구
        tk.Label(
            main_frame,
            text="* 처음 입력하면 자동으로 계정이 생성됩니다",
            font=FONTS['small'],
            bg=COLORS['surface'],
            fg=COLORS['text_light']
        ).pack(pady=(15, 0))
    
    def _login(self):
        """로그인 처리"""
        username = self.username_var.get().strip()
        
        if not username:
            messagebox.showwarning("알림", "사용자 이름을 입력해주세요.")
            self.username_entry.focus()
            return
        
        if len(username) < 2:
            messagebox.showwarning("알림", "사용자 이름은 2자 이상이어야 합니다.")
            self.username_entry.focus()
            return
        
        # 사용자 조회 또는 생성
        self.result_user = UserRepository.get_or_create(username)
        self.destroy()


def main():
    """메인 함수"""
    # 데이터베이스 초기화
    init_database()
    insert_sample_data()
    
    # 로그인
    login = LoginDialog()
    login.mainloop()
    
    if login.result_user:
        # 메인 윈도우 실행
        app = MainWindow(login.result_user)
        app.mainloop()


if __name__ == "__main__":
    main()
