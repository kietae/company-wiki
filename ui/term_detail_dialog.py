"""
회사 용어 위키 - 용어 상세/편집 다이얼로그
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Term, Category, User
from repository import TermRepository, CategoryRepository
from ui.styles import COLORS, FONTS, SIZES


class TermDetailDialog(tk.Toplevel):
    """용어 상세/편집 다이얼로그"""
    
    def __init__(self, parent, current_user: User, term: Optional[Term] = None):
        super().__init__(parent)
        self.current_user = current_user
        self.term = term
        self.result = False
        
        self.title("용어 편집" if term else "새 용어 추가")
        self.geometry("600x550")
        self.resizable(False, False)
        
        # 모달
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._load_data()
        
        # 중앙 정렬
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """위젯 생성"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # 용어명
        ttk.Label(main_frame, text="용어명 *", style='Subtitle.TLabel').pack(anchor='w')
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, font=FONTS['body'])
        self.name_entry.pack(fill='x', pady=(5, 15))
        
        # 정의
        ttk.Label(main_frame, text="정의 *", style='Subtitle.TLabel').pack(anchor='w')
        self.definition_text = tk.Text(main_frame, height=5, font=FONTS['body'], wrap='word')
        self.definition_text.pack(fill='x', pady=(5, 15))
        
        # 예시
        ttk.Label(main_frame, text="예시 문장", style='Subtitle.TLabel').pack(anchor='w')
        self.example_text = tk.Text(main_frame, height=3, font=FONTS['body'], wrap='word')
        self.example_text.pack(fill='x', pady=(5, 15))
        
        # 동의어
        ttk.Label(
            main_frame,
            text="동의어 (쉼표로 구분)",
            style='Subtitle.TLabel'
        ).pack(anchor='w')
        self.synonyms_var = tk.StringVar()
        self.synonyms_entry = ttk.Entry(main_frame, textvariable=self.synonyms_var, font=FONTS['body'])
        self.synonyms_entry.pack(fill='x', pady=(5, 15))
        
        # 카테고리
        ttk.Label(main_frame, text="카테고리", style='Subtitle.TLabel').pack(anchor='w')
        
        cat_frame = ttk.Frame(main_frame)
        cat_frame.pack(fill='x', pady=(5, 15))
        
        self.category_vars = {}
        self.categories = CategoryRepository.get_all()
        
        for i, cat in enumerate(self.categories):
            var = tk.BooleanVar()
            self.category_vars[cat.id] = var
            
            cb = ttk.Checkbutton(
                cat_frame,
                text=cat.name,
                variable=var
            )
            cb.grid(row=i // 3, column=i % 3, sticky='w', padx=10, pady=2)
        
        # 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(
            btn_frame,
            text="취소",
            command=self.destroy
        ).pack(side='right', padx=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="저장",
            style='Primary.TButton',
            command=self._save
        ).pack(side='right')
        
        # 히스토리 보기 버튼 (편집 모드일 때만)
        if self.term:
            ttk.Button(
                btn_frame,
                text="📜 히스토리",
                command=self._show_history
            ).pack(side='left')
    
    def _load_data(self):
        """기존 데이터 로드 (편집 모드)"""
        if not self.term:
            return
        
        self.name_var.set(self.term.name)
        self.definition_text.insert('1.0', self.term.definition)
        self.example_text.insert('1.0', self.term.example or "")
        self.synonyms_var.set(", ".join(self.term.synonyms))
        
        for cat in self.term.categories:
            if cat.id in self.category_vars:
                self.category_vars[cat.id].set(True)
    
    def _save(self):
        """저장"""
        name = self.name_var.get().strip()
        definition = self.definition_text.get('1.0', 'end-1c').strip()
        example = self.example_text.get('1.0', 'end-1c').strip()
        synonyms_str = self.synonyms_var.get()
        
        # 유효성 검사
        if not name:
            messagebox.showerror("오류", "용어명을 입력해주세요.")
            self.name_entry.focus()
            return
        
        if not definition:
            messagebox.showerror("오류", "정의를 입력해주세요.")
            self.definition_text.focus()
            return
        
        # 동의어 파싱
        synonyms = [s.strip() for s in synonyms_str.split(',') if s.strip()]
        
        # 카테고리 선택
        category_ids = [cat_id for cat_id, var in self.category_vars.items() if var.get()]
        
        # 저장
        if self.term:
            # 수정
            self.term.name = name
            self.term.definition = definition
            self.term.example = example
            self.term.synonyms = synonyms
            
            TermRepository.update(self.term, self.current_user.id, category_ids)
            messagebox.showinfo("완료", "용어가 수정되었습니다.")
        else:
            # 새로 생성
            new_term = Term(
                name=name,
                definition=definition,
                example=example,
                synonyms=synonyms
            )
            TermRepository.create(new_term, self.current_user.id, category_ids)
            messagebox.showinfo("완료", "새 용어가 추가되었습니다.")
        
        self.result = True
        self.destroy()
    
    def _show_history(self):
        """히스토리 보기"""
        if not self.term:
            return
        
        from ui.history_view import TermHistoryDialog
        dialog = TermHistoryDialog(self, self.term)
        self.wait_window(dialog)
