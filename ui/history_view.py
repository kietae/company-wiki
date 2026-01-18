"""
회사 용어 위키 - 히스토리 뷰
변경 이력 조회
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Term, TermHistory, User
from repository import HistoryRepository
from ui.styles import COLORS, FONTS, SIZES


class HistoryView(ttk.Frame):
    """전체 히스토리 뷰"""
    
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
            text="📜 변경 히스토리",
            style='Title.TLabel'
        ).pack(side='left')
        
        ttk.Button(
            title_frame,
            text="🔄 새로고침",
            command=self.refresh_list
        ).pack(side='right')
        
        # 히스토리 목록
        list_frame = ttk.Frame(self, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True, padx=SIZES['padding'])
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(
            list_frame,
            columns=('time', 'user', 'term', 'action', 'detail'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('time', text='시간')
        self.tree.heading('user', text='사용자')
        self.tree.heading('term', text='용어')
        self.tree.heading('action', text='작업')
        self.tree.heading('detail', text='상세')
        
        self.tree.column('time', width=150)
        self.tree.column('user', width=100)
        self.tree.column('term', width=120)
        self.tree.column('action', width=80)
        self.tree.column('detail', width=300)
        
        self.tree.pack(fill='both', expand=True)
        
        # 더블클릭 상세보기
        self.tree.bind('<Double-1>', self._on_double_click)
    
    def refresh_list(self):
        """목록 새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        history = HistoryRepository.get_all(limit=200)
        
        for h in history:
            action_text = self._get_action_text(h.action_type)
            detail_text = self._get_detail_text(h)
            
            self.tree.insert('', 'end', iid=h.id, values=(
                h.changed_at or "",
                h.changer_name,
                h.term_name,
                action_text,
                detail_text
            ))
    
    def _get_action_text(self, action_type: str) -> str:
        """작업 유형 텍스트"""
        mapping = {
            'create': '➕ 생성',
            'update': '✏️ 수정',
            'delete': '🗑️ 삭제'
        }
        return mapping.get(action_type, action_type)
    
    def _get_detail_text(self, h: TermHistory) -> str:
        """상세 텍스트"""
        if h.action_type == 'create':
            return f"새 용어 '{h.new_value}' 생성"
        elif h.action_type == 'delete':
            return f"용어 '{h.old_value}' 삭제"
        elif h.action_type == 'update':
            field_names = {
                'name': '용어명',
                'definition': '정의',
                'example': '예시',
                'synonyms': '동의어'
            }
            field = field_names.get(h.field_name, h.field_name)
            return f"{field} 변경"
        return ""
    
    def _on_double_click(self, event):
        """상세 정보 보기"""
        selection = self.tree.selection()
        if not selection:
            return
        
        history_id = int(selection[0])
        history = HistoryRepository.get_all(limit=500)
        h = next((item for item in history if item.id == history_id), None)
        
        if h:
            dialog = HistoryDetailDialog(self, h)


class HistoryDetailDialog(tk.Toplevel):
    """히스토리 상세 다이얼로그"""
    
    def __init__(self, parent, history: TermHistory):
        super().__init__(parent)
        self.history = history
        
        self.title("변경 상세")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.transient(parent)
        
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
        
        h = self.history
        
        # 정보
        info = [
            ("시간", h.changed_at),
            ("사용자", h.changer_name),
            ("용어", h.term_name),
            ("작업", h.action_type),
            ("필드", h.field_name or "-"),
        ]
        
        for label, value in info:
            row = ttk.Frame(main_frame)
            row.pack(fill='x', pady=3)
            ttk.Label(row, text=f"{label}:", width=10, style='Subtitle.TLabel').pack(side='left')
            ttk.Label(row, text=str(value)).pack(side='left')
        
        # 이전 값
        if h.old_value:
            ttk.Label(main_frame, text="이전 값:", style='Subtitle.TLabel').pack(anchor='w', pady=(15, 5))
            old_text = tk.Text(main_frame, height=4, font=FONTS['body'], wrap='word')
            old_text.insert('1.0', h.old_value)
            old_text.config(state='disabled', bg='#ffebee')
            old_text.pack(fill='x')
        
        # 새 값
        if h.new_value:
            ttk.Label(main_frame, text="새 값:", style='Subtitle.TLabel').pack(anchor='w', pady=(15, 5))
            new_text = tk.Text(main_frame, height=4, font=FONTS['body'], wrap='word')
            new_text.insert('1.0', h.new_value)
            new_text.config(state='disabled', bg='#e8f5e9')
            new_text.pack(fill='x')
        
        # 닫기 버튼
        ttk.Button(
            main_frame,
            text="닫기",
            command=self.destroy
        ).pack(pady=(20, 0))


class TermHistoryDialog(tk.Toplevel):
    """특정 용어의 히스토리 다이얼로그"""
    
    def __init__(self, parent, term: Term):
        super().__init__(parent)
        self.term = term
        
        self.title(f"'{term.name}' 변경 이력")
        self.geometry("600x400")
        
        self.transient(parent)
        
        self._create_widgets()
        
        # 중앙 정렬
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """위젯 생성"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # 히스토리 목록
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side='right', fill='y')
        
        tree = ttk.Treeview(
            main_frame,
            columns=('time', 'user', 'action', 'field', 'old', 'new'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=tree.yview)
        
        tree.heading('time', text='시간')
        tree.heading('user', text='사용자')
        tree.heading('action', text='작업')
        tree.heading('field', text='필드')
        tree.heading('old', text='이전 값')
        tree.heading('new', text='새 값')
        
        tree.column('time', width=120)
        tree.column('user', width=80)
        tree.column('action', width=60)
        tree.column('field', width=70)
        tree.column('old', width=120)
        tree.column('new', width=120)
        
        tree.pack(fill='both', expand=True)
        
        # 데이터 로드
        history = HistoryRepository.get_by_term(self.term.id)
        
        for h in history:
            tree.insert('', 'end', values=(
                h.changed_at or "",
                h.changer_name,
                h.action_type,
                h.field_name or "-",
                (h.old_value or "")[:30] + "..." if h.old_value and len(h.old_value) > 30 else h.old_value or "",
                (h.new_value or "")[:30] + "..." if h.new_value and len(h.new_value) > 30 else h.new_value or ""
            ))
        
        # 닫기 버튼
        ttk.Button(
            main_frame,
            text="닫기",
            command=self.destroy
        ).pack(pady=(10, 0))
