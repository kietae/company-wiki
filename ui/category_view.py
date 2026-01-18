"""
회사 용어 위키 - 카테고리 관리 뷰
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Category, User
from repository import CategoryRepository
from ui.styles import COLORS, FONTS, SIZES


class CategoryView(ttk.Frame):
    """카테고리 관리 뷰"""
    
    def __init__(self, parent, current_user: User):
        super().__init__(parent, style='Card.TFrame')
        self.current_user = current_user
        
        self._create_widgets()
        self.refresh_list()
    
    def _create_widgets(self):
        """위젯 생성"""
        # 제목
        title_frame = ttk.Frame(self, style='Card.TFrame')
        title_frame.pack(fill='x', padx=SIZES['padding'], pady=SIZES['padding'])
        
        ttk.Label(
            title_frame,
            text="📁 카테고리 관리",
            style='Title.TLabel'
        ).pack(side='left')
        
        # 추가 버튼
        ttk.Button(
            title_frame,
            text="➕ 새 카테고리",
            command=self._on_add_click
        ).pack(side='right')
        
        # 카테고리 목록
        list_frame = ttk.Frame(self, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True, padx=SIZES['padding'])
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(
            list_frame,
            columns=('name', 'description', 'color'),
            show='headings',
            selectmode='browse',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('name', text='카테고리명')
        self.tree.heading('description', text='설명')
        self.tree.heading('color', text='색상')
        
        self.tree.column('name', width=150)
        self.tree.column('description', width=300)
        self.tree.column('color', width=100)
        
        self.tree.pack(fill='both', expand=True)
        
        # 더블클릭 편집
        self.tree.bind('<Double-1>', lambda e: self._on_edit_click())
        
        # 하단 버튼
        btn_frame = ttk.Frame(self, style='Card.TFrame')
        btn_frame.pack(fill='x', padx=SIZES['padding'], pady=SIZES['padding'])
        
        self.edit_btn = ttk.Button(
            btn_frame,
            text="✏️ 편집",
            command=self._on_edit_click,
            state='disabled'
        )
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.delete_btn = ttk.Button(
            btn_frame,
            text="🗑️ 삭제",
            command=self._on_delete_click,
            state='disabled'
        )
        self.delete_btn.pack(side='left')
        
        # 선택 이벤트
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def refresh_list(self):
        """목록 새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        categories = CategoryRepository.get_all()
        
        for cat in categories:
            self.tree.insert('', 'end', iid=cat.id, values=(
                cat.name,
                cat.description,
                cat.color
            ))
        
        self._update_button_states()
    
    def _on_select(self, event):
        """선택 이벤트"""
        self._update_button_states()
    
    def _update_button_states(self):
        """버튼 상태 업데이트"""
        selection = self.tree.selection()
        state = 'normal' if selection else 'disabled'
        self.edit_btn.config(state=state)
        self.delete_btn.config(state=state)
    
    def _on_add_click(self):
        """새 카테고리 추가"""
        dialog = CategoryDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_list()
    
    def _on_edit_click(self):
        """카테고리 편집"""
        selection = self.tree.selection()
        if not selection:
            return
        
        cat_id = int(selection[0])
        categories = CategoryRepository.get_all()
        category = next((c for c in categories if c.id == cat_id), None)
        
        if category:
            dialog = CategoryDialog(self, category)
            self.wait_window(dialog)
            if dialog.result:
                self.refresh_list()
    
    def _on_delete_click(self):
        """카테고리 삭제"""
        selection = self.tree.selection()
        if not selection:
            return
        
        cat_id = int(selection[0])
        values = self.tree.item(selection[0])['values']
        cat_name = values[0]
        
        if messagebox.askyesno(
            "삭제 확인",
            f"'{cat_name}' 카테고리를 삭제하시겠습니까?\n\n연결된 용어에서 이 카테고리가 제거됩니다."
        ):
            CategoryRepository.delete(cat_id)
            self.refresh_list()


class CategoryDialog(tk.Toplevel):
    """카테고리 추가/편집 다이얼로그"""
    
    def __init__(self, parent, category: Optional[Category] = None):
        super().__init__(parent)
        self.category = category
        self.result = False
        self.selected_color = category.color if category else "#3498db"
        
        self.title("카테고리 편집" if category else "새 카테고리")
        self.geometry("400x300")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # 중앙 정렬
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """위젯 생성"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # 카테고리명
        ttk.Label(main_frame, text="카테고리명 *", style='Subtitle.TLabel').pack(anchor='w')
        self.name_var = tk.StringVar(value=self.category.name if self.category else "")
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, font=FONTS['body'])
        self.name_entry.pack(fill='x', pady=(5, 15))
        
        # 설명
        ttk.Label(main_frame, text="설명", style='Subtitle.TLabel').pack(anchor='w')
        self.desc_var = tk.StringVar(value=self.category.description if self.category else "")
        self.desc_entry = ttk.Entry(main_frame, textvariable=self.desc_var, font=FONTS['body'])
        self.desc_entry.pack(fill='x', pady=(5, 15))
        
        # 색상
        ttk.Label(main_frame, text="색상", style='Subtitle.TLabel').pack(anchor='w')
        
        color_frame = ttk.Frame(main_frame)
        color_frame.pack(fill='x', pady=(5, 15))
        
        self.color_label = tk.Label(
            color_frame,
            text="     ",
            bg=self.selected_color,
            relief='solid',
            width=5
        )
        self.color_label.pack(side='left')
        
        ttk.Button(
            color_frame,
            text="색상 선택",
            command=self._choose_color
        ).pack(side='left', padx=10)
        
        self.color_code_label = ttk.Label(
            color_frame,
            text=self.selected_color,
            style='TLabel'
        )
        self.color_code_label.pack(side='left')
        
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
            command=self._save
        ).pack(side='right')
    
    def _choose_color(self):
        """색상 선택"""
        color = colorchooser.askcolor(
            initialcolor=self.selected_color,
            title="카테고리 색상 선택"
        )
        if color[1]:
            self.selected_color = color[1]
            self.color_label.config(bg=self.selected_color)
            self.color_code_label.config(text=self.selected_color)
    
    def _save(self):
        """저장"""
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showerror("오류", "카테고리명을 입력해주세요.")
            self.name_entry.focus()
            return
        
        if self.category:
            self.category.name = name
            self.category.description = self.desc_var.get().strip()
            self.category.color = self.selected_color
            CategoryRepository.update(self.category)
            messagebox.showinfo("완료", "카테고리가 수정되었습니다.")
        else:
            new_cat = Category(
                name=name,
                description=self.desc_var.get().strip(),
                color=self.selected_color
            )
            CategoryRepository.create(new_cat)
            messagebox.showinfo("완료", "새 카테고리가 추가되었습니다.")
        
        self.result = True
        self.destroy()
