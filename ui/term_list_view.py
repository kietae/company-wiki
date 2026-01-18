"""
회사 용어 위키 - 용어 목록 뷰
용어 검색, 필터링, 목록 표시
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Term, Category, User
from repository import TermRepository, CategoryRepository
from ui.styles import COLORS, FONTS, SIZES


class TermListView(ttk.Frame):
    """용어 목록 뷰"""
    
    def __init__(self, parent, current_user: User, on_term_select: Callable[[Term], None] = None):
        super().__init__(parent, style='Card.TFrame')
        self.current_user = current_user
        self.on_term_select = on_term_select
        self.selected_term: Optional[Term] = None
        
        self._create_widgets()
        self.refresh_list()
    
    def _create_widgets(self):
        """위젯 생성"""
        # 상단 검색 영역
        search_frame = ttk.Frame(self, style='Card.TFrame')
        search_frame.pack(fill='x', padx=SIZES['padding'], pady=SIZES['padding'])
        
        # 검색 입력
        ttk.Label(search_frame, text="🔍 검색:").pack(side='left')
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_list())
        
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30
        )
        self.search_entry.pack(side='left', padx=(5, 15))
        
        # 카테고리 필터
        ttk.Label(search_frame, text="카테고리:").pack(side='left')
        
        self.category_var = tk.StringVar(value="전체")
        self.category_combo = ttk.Combobox(
            search_frame,
            textvariable=self.category_var,
            state='readonly',
            width=15
        )
        self.category_combo.pack(side='left', padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_list())
        
        self._update_category_combo()
        
        # 새로고침 버튼
        refresh_btn = ttk.Button(
            search_frame,
            text="🔄",
            width=3,
            command=self.refresh_list
        )
        refresh_btn.pack(side='left', padx=5)
        
        # 용어 목록 (Treeview)
        list_frame = ttk.Frame(self, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True, padx=SIZES['padding'])
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(
            list_frame,
            columns=('name', 'definition', 'categories'),
            show='headings',
            selectmode='browse',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # 컬럼 설정
        self.tree.heading('name', text='용어명')
        self.tree.heading('definition', text='정의')
        self.tree.heading('categories', text='카테고리')
        
        self.tree.column('name', width=150, minwidth=100)
        self.tree.column('definition', width=400, minwidth=200)
        self.tree.column('categories', width=150, minwidth=100)
        
        self.tree.pack(fill='both', expand=True)
        
        # 선택 이벤트
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # 하단 버튼 영역
        button_frame = ttk.Frame(self, style='Card.TFrame')
        button_frame.pack(fill='x', padx=SIZES['padding'], pady=SIZES['padding'])
        
        self.add_btn = ttk.Button(
            button_frame,
            text="➕ 새 용어",
            command=self._on_add_click
        )
        self.add_btn.pack(side='left', padx=(0, 5))
        
        self.edit_btn = ttk.Button(
            button_frame,
            text="✏️ 편집",
            command=self._on_edit_click,
            state='disabled'
        )
        self.edit_btn.pack(side='left', padx=5)
        
        self.delete_btn = ttk.Button(
            button_frame,
            text="🗑️ 삭제",
            command=self._on_delete_click,
            state='disabled'
        )
        self.delete_btn.pack(side='left', padx=5)
        
        # 용어 수 표시
        self.count_label = ttk.Label(button_frame, text="")
        self.count_label.pack(side='right')
    
    def _update_category_combo(self):
        """카테고리 콤보박스 업데이트"""
        categories = CategoryRepository.get_all()
        values = ["전체"] + [c.name for c in categories]
        self.category_combo['values'] = values
        self._categories = {c.name: c for c in categories}
    
    def refresh_list(self):
        """목록 새로고침"""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 검색 및 필터 적용
        search_query = self.search_var.get()
        category_name = self.category_var.get()
        
        category_id = None
        if category_name != "전체" and category_name in self._categories:
            category_id = self._categories[category_name].id
        
        # 용어 조회
        terms = TermRepository.get_all(search_query, category_id)
        
        for term in terms:
            categories_str = ", ".join(c.name for c in term.categories)
            definition_preview = term.definition[:80] + "..." if len(term.definition) > 80 else term.definition
            
            self.tree.insert('', 'end', iid=term.id, values=(
                term.name,
                definition_preview,
                categories_str
            ))
        
        # 용어 수 표시
        self.count_label.config(text=f"총 {len(terms)}개 용어")
        
        # 카테고리 콤보 업데이트
        self._update_category_combo()
        
        # 선택 초기화
        self.selected_term = None
        self._update_button_states()
    
    def _on_select(self, event):
        """용어 선택 이벤트"""
        selection = self.tree.selection()
        if selection:
            term_id = int(selection[0])
            self.selected_term = TermRepository.get_by_id(term_id)
            self._update_button_states()
            
            if self.on_term_select and self.selected_term:
                self.on_term_select(self.selected_term)
    
    def _on_double_click(self, event):
        """더블클릭 편집"""
        if self.selected_term:
            self._on_edit_click()
    
    def _update_button_states(self):
        """버튼 상태 업데이트"""
        state = 'normal' if self.selected_term else 'disabled'
        self.edit_btn.config(state=state)
        self.delete_btn.config(state=state)
    
    def _on_add_click(self):
        """새 용어 추가"""
        from ui.term_detail_dialog import TermDetailDialog
        dialog = TermDetailDialog(self, self.current_user)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_list()
    
    def _on_edit_click(self):
        """용어 편집"""
        if not self.selected_term:
            return
        
        from ui.term_detail_dialog import TermDetailDialog
        dialog = TermDetailDialog(self, self.current_user, self.selected_term)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_list()
    
    def _on_delete_click(self):
        """용어 삭제"""
        if not self.selected_term:
            return
        
        if messagebox.askyesno(
            "삭제 확인",
            f"'{self.selected_term.name}' 용어를 삭제하시겠습니까?\n\n삭제 후에도 히스토리에서 확인할 수 있습니다."
        ):
            TermRepository.delete(self.selected_term.id, self.current_user.id)
            self.refresh_list()
            messagebox.showinfo("완료", "용어가 삭제되었습니다.")
