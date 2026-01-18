"""
회사 용어 위키 - 스타일 정의
공통 색상, 폰트, 스타일 설정
"""

import tkinter as tk
from tkinter import ttk


# 색상 팔레트
COLORS = {
    'primary': '#3498db',       # 메인 블루
    'primary_dark': '#2980b9',
    'secondary': '#2ecc71',     # 그린
    'warning': '#f39c12',       # 오렌지
    'danger': '#e74c3c',        # 레드
    'background': '#f5f6fa',    # 배경
    'surface': '#ffffff',       # 카드 배경
    'text': '#2c3e50',          # 기본 텍스트
    'text_light': '#7f8c8d',    # 보조 텍스트
    'border': '#dcdde1',        # 테두리
    'sidebar': '#2c3e50',       # 사이드바
    'sidebar_text': '#ecf0f1',  # 사이드바 텍스트
    'sidebar_hover': '#34495e', # 사이드바 호버
}

# 폰트 설정
FONTS = {
    'title': ('맑은 고딕', 16, 'bold'),
    'subtitle': ('맑은 고딕', 12, 'bold'),
    'body': ('맑은 고딕', 10),
    'small': ('맑은 고딕', 9),
    'mono': ('Consolas', 10),
}

# 크기
SIZES = {
    'sidebar_width': 180,
    'padding': 10,
    'padding_small': 5,
    'button_padding': (15, 8),
    'entry_padding': 8,
}


def apply_styles(root: tk.Tk):
    """ttk 스타일 적용"""
    style = ttk.Style(root)
    
    # 테마 설정
    style.theme_use('clam')
    
    # 프레임 스타일
    style.configure(
        'Card.TFrame',
        background=COLORS['surface']
    )
    
    style.configure(
        'Sidebar.TFrame',
        background=COLORS['sidebar']
    )
    
    # 레이블 스타일
    style.configure(
        'TLabel',
        background=COLORS['surface'],
        foreground=COLORS['text'],
        font=FONTS['body']
    )
    
    style.configure(
        'Title.TLabel',
        font=FONTS['title'],
        foreground=COLORS['text']
    )
    
    style.configure(
        'Subtitle.TLabel',
        font=FONTS['subtitle'],
        foreground=COLORS['text']
    )
    
    style.configure(
        'Sidebar.TLabel',
        background=COLORS['sidebar'],
        foreground=COLORS['sidebar_text'],
        font=FONTS['body']
    )
    
    # 버튼 스타일
    style.configure(
        'TButton',
        font=FONTS['body'],
        padding=SIZES['button_padding']
    )
    
    style.configure(
        'Primary.TButton',
        background=COLORS['primary'],
        foreground='white'
    )
    style.map(
        'Primary.TButton',
        background=[('active', COLORS['primary_dark'])]
    )
    
    style.configure(
        'Danger.TButton',
        background=COLORS['danger'],
        foreground='white'
    )
    
    # 엔트리 스타일
    style.configure(
        'TEntry',
        padding=SIZES['entry_padding'],
        font=FONTS['body']
    )
    
    # Treeview 스타일
    style.configure(
        'Treeview',
        font=FONTS['body'],
        rowheight=30,
        background=COLORS['surface'],
        fieldbackground=COLORS['surface']
    )
    style.configure(
        'Treeview.Heading',
        font=FONTS['subtitle'],
        background=COLORS['background'],
        foreground=COLORS['text']
    )
    style.map(
        'Treeview',
        background=[('selected', COLORS['primary'])],
        foreground=[('selected', 'white')]
    )
    
    # Notebook 스타일 (탭)
    style.configure(
        'TNotebook',
        background=COLORS['background']
    )
    style.configure(
        'TNotebook.Tab',
        font=FONTS['body'],
        padding=(15, 8)
    )


def create_sidebar_button(parent, text: str, command=None) -> tk.Button:
    """사이드바 버튼 생성"""
    btn = tk.Button(
        parent,
        text=text,
        font=FONTS['body'],
        bg=COLORS['sidebar'],
        fg=COLORS['sidebar_text'],
        activebackground=COLORS['sidebar_hover'],
        activeforeground=COLORS['sidebar_text'],
        bd=0,
        padx=20,
        pady=12,
        anchor='w',
        cursor='hand2',
        command=command
    )
    
    # 호버 효과
    btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['sidebar_hover']))
    btn.bind('<Leave>', lambda e: btn.configure(bg=COLORS['sidebar']))
    
    return btn
