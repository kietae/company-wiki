"""
회사 용어 위키 - 메인 윈도우
사이드바 + 콘텐츠 영역 레이아웃
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User
from repository import UserRepository
from ui.styles import COLORS, FONTS, SIZES, apply_styles, create_sidebar_button
from ui.term_list_view import TermListView
from ui.category_view import CategoryView
from ui.history_view import HistoryView


class MainWindow(tk.Tk):
    """메인 윈도우"""
    
    def __init__(self, current_user: User):
        super().__init__()
        self.current_user = current_user
        
        self.title("🏢 회사 용어 위키")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # 배경색
        self.configure(bg=COLORS['background'])
        
        # 스타일 적용
        apply_styles(self)
        
        self._create_widgets()
        
        # 첫 화면: 용어 목록
        self._show_terms()
    
    def _create_widgets(self):
        """위젯 생성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True)
        
        # 사이드바
        self._create_sidebar(main_container)
        
        # 콘텐츠 영역
        self.content_frame = ttk.Frame(main_container, style='Card.TFrame')
        self.content_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # 현재 뷰
        self.current_view = None
    
    def _create_sidebar(self, parent):
        """사이드바 생성"""
        sidebar = tk.Frame(
            parent,
            bg=COLORS['sidebar'],
            width=SIZES['sidebar_width']
        )
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # 로고/제목
        title_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        title_frame.pack(fill='x', pady=20)
        
        tk.Label(
            title_frame,
            text="🏢",
            font=('Segoe UI Emoji', 28),
            bg=COLORS['sidebar'],
            fg=COLORS['sidebar_text']
        ).pack()
        
        tk.Label(
            title_frame,
            text="용어 위키",
            font=FONTS['title'],
            bg=COLORS['sidebar'],
            fg=COLORS['sidebar_text']
        ).pack()
        
        # 메뉴 버튼
        menu_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        menu_frame.pack(fill='x', pady=20)
        
        buttons = [
            ("📚 용어 목록", self._show_terms),
            ("📁 카테고리", self._show_categories),
            ("📜 히스토리", self._show_history),
        ]
        
        self.menu_buttons = []
        for text, command in buttons:
            btn = create_sidebar_button(menu_frame, text, command)
            btn.pack(fill='x')
            self.menu_buttons.append(btn)
        
        # 구분선
        tk.Frame(
            sidebar,
            bg=COLORS['sidebar_hover'],
            height=1
        ).pack(fill='x', pady=10, padx=20)
        
        # 관리자 메뉴 (관리자만 표시)
        if self.current_user.is_admin:
            admin_label = tk.Label(
                sidebar,
                text="관리자",
                font=FONTS['small'],
                bg=COLORS['sidebar'],
                fg=COLORS['text_light']
            )
            admin_label.pack(anchor='w', padx=20, pady=(0, 5))
            
            admin_btn = create_sidebar_button(
                sidebar,
                "⚙️ 사용자 관리",
                self._show_user_management
            )
            admin_btn.pack(fill='x')
        
        # 하단 사용자 정보
        user_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        user_frame.pack(side='bottom', fill='x', pady=15, padx=10)
        
        role_text = "👑 관리자" if self.current_user.is_admin else "👤 사용자"
        
        tk.Label(
            user_frame,
            text=f"{self.current_user.username}",
            font=FONTS['subtitle'],
            bg=COLORS['sidebar'],
            fg=COLORS['sidebar_text']
        ).pack()
        
        tk.Label(
            user_frame,
            text=role_text,
            font=FONTS['small'],
            bg=COLORS['sidebar'],
            fg=COLORS['text_light']
        ).pack()
    
    def _clear_content(self):
        """콘텐츠 영역 초기화"""
        if self.current_view:
            self.current_view.destroy()
    
    def _show_terms(self):
        """용어 목록 뷰"""
        self._clear_content()
        self.current_view = TermListView(self.content_frame, self.current_user)
        self.current_view.pack(fill='both', expand=True)
    
    def _show_categories(self):
        """카테고리 뷰"""
        self._clear_content()
        self.current_view = CategoryView(self.content_frame, self.current_user)
        self.current_view.pack(fill='both', expand=True)
    
    def _show_history(self):
        """히스토리 뷰"""
        self._clear_content()
        self.current_view = HistoryView(self.content_frame, self.current_user)
        self.current_view.pack(fill='both', expand=True)
    
    def _show_user_management(self):
        """사용자 관리 다이얼로그"""
        dialog = UserManagementDialog(self)


class UserManagementDialog(tk.Toplevel):
    """사용자 관리 다이얼로그"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("⚙️ 사용자 관리")
        self.geometry("500x400")
        
        self.transient(parent)
        
        self._create_widgets()
        self.refresh_list()
        
        # 중앙 정렬
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """위젯 생성"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # 사용자 목록
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(
            main_frame,
            columns=('username', 'role', 'created'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('username', text='사용자명')
        self.tree.heading('role', text='권한')
        self.tree.heading('created', text='가입일')
        
        self.tree.column('username', width=150)
        self.tree.column('role', width=100)
        self.tree.column('created', width=150)
        
        self.tree.pack(fill='both', expand=True)
        
        # 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="👑 관리자로 변경",
            command=lambda: self._change_role('admin')
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="👤 일반 사용자로 변경",
            command=lambda: self._change_role('user')
        ).pack(side='left')
        
        ttk.Button(
            btn_frame,
            text="닫기",
            command=self.destroy
        ).pack(side='right')
    
    def refresh_list(self):
        """목록 새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        users = UserRepository.get_all()
        
        for user in users:
            role_text = "👑 관리자" if user.is_admin else "👤 사용자"
            self.tree.insert('', 'end', iid=user.id, values=(
                user.username,
                role_text,
                user.created_at or ""
            ))
    
    def _change_role(self, new_role: str):
        """권한 변경"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("알림", "사용자를 선택해주세요.")
            return
        
        user_id = int(selection[0])
        UserRepository.update_role(user_id, new_role)
        self.refresh_list()
        
        role_text = "관리자" if new_role == 'admin' else "일반 사용자"
        messagebox.showinfo("완료", f"권한이 {role_text}(으)로 변경되었습니다.")
