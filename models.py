"""
회사 용어 위키 - 데이터 모델
데이터 클래스 정의
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class User:
    """사용자 모델"""
    id: Optional[int] = None
    username: str = ""
    role: str = "user"  # 'admin' or 'user'
    created_at: Optional[datetime] = None
    
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


@dataclass
class Category:
    """카테고리 모델"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    color: str = "#3498db"


@dataclass
class Term:
    """용어 모델"""
    id: Optional[int] = None
    name: str = ""
    definition: str = ""
    example: str = ""
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # 관계 데이터 (조회 시 채워짐)
    synonyms: List[str] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)
    creator_name: str = ""


@dataclass
class TermHistory:
    """용어 변경 이력 모델"""
    id: Optional[int] = None
    term_id: int = 0
    action_type: str = ""  # 'create', 'update', 'delete'
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: Optional[int] = None
    changed_at: Optional[datetime] = None
    
    # 조회 시 채워짐
    changer_name: str = ""
    term_name: str = ""
