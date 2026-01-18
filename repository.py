"""
회사 용어 위키 - 리포지토리
데이터 액세스 레이어
"""

from typing import List, Optional, Tuple
from datetime import datetime
from database import get_connection
from models import User, Category, Term, TermHistory


class UserRepository:
    """사용자 관리 리포지토리"""
    
    @staticmethod
    def get_or_create(username: str) -> User:
        """사용자 조회 또는 생성"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            user = User(
                id=row['id'],
                username=row['username'],
                role=row['role'],
                created_at=row['created_at']
            )
        else:
            cursor.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
            conn.commit()
            user = User(id=cursor.lastrowid, username=username, role='user')
        
        conn.close()
        return user
    
    @staticmethod
    def get_all() -> List[User]:
        """모든 사용자 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY username")
        
        users = [
            User(
                id=row['id'],
                username=row['username'],
                role=row['role'],
                created_at=row['created_at']
            )
            for row in cursor.fetchall()
        ]
        conn.close()
        return users
    
    @staticmethod
    def update_role(user_id: int, role: str):
        """사용자 권한 변경"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
        conn.close()


class CategoryRepository:
    """카테고리 관리 리포지토리"""
    
    @staticmethod
    def get_all() -> List[Category]:
        """모든 카테고리 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")
        
        categories = [
            Category(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                color=row['color']
            )
            for row in cursor.fetchall()
        ]
        conn.close()
        return categories
    
    @staticmethod
    def create(category: Category) -> int:
        """카테고리 생성"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, description, color) VALUES (?, ?, ?)",
            (category.name, category.description, category.color)
        )
        conn.commit()
        category_id = cursor.lastrowid
        conn.close()
        return category_id
    
    @staticmethod
    def update(category: Category):
        """카테고리 수정"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE categories SET name = ?, description = ?, color = ? WHERE id = ?",
            (category.name, category.description, category.color, category.id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(category_id: int):
        """카테고리 삭제"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        conn.close()


class TermRepository:
    """용어 관리 리포지토리"""
    
    @staticmethod
    def get_all(search_query: str = "", category_id: Optional[int] = None) -> List[Term]:
        """용어 목록 조회 (검색 및 필터링)"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT DISTINCT t.*, u.username as creator_name
            FROM terms t
            LEFT JOIN users u ON t.created_by = u.id
            LEFT JOIN term_categories tc ON t.id = tc.term_id
            LEFT JOIN synonyms s ON t.id = s.term_id
            WHERE 1=1
        """
        params = []
        
        if search_query:
            query += " AND (t.name LIKE ? OR t.definition LIKE ? OR s.synonym_name LIKE ?)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        
        if category_id:
            query += " AND tc.category_id = ?"
            params.append(category_id)
        
        query += " ORDER BY t.name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        terms = []
        for row in rows:
            term = Term(
                id=row['id'],
                name=row['name'],
                definition=row['definition'],
                example=row['example'],
                created_by=row['created_by'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                creator_name=row['creator_name'] or ""
            )
            
            # 동의어 조회
            cursor.execute(
                "SELECT synonym_name FROM synonyms WHERE term_id = ?",
                (term.id,)
            )
            term.synonyms = [r['synonym_name'] for r in cursor.fetchall()]
            
            # 카테고리 조회
            cursor.execute("""
                SELECT c.* FROM categories c
                JOIN term_categories tc ON c.id = tc.category_id
                WHERE tc.term_id = ?
            """, (term.id,))
            term.categories = [
                Category(
                    id=r['id'],
                    name=r['name'],
                    description=r['description'],
                    color=r['color']
                )
                for r in cursor.fetchall()
            ]
            
            terms.append(term)
        
        conn.close()
        return terms
    
    @staticmethod
    def get_by_id(term_id: int) -> Optional[Term]:
        """ID로 용어 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*, u.username as creator_name
            FROM terms t
            LEFT JOIN users u ON t.created_by = u.id
            WHERE t.id = ?
        """, (term_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        term = Term(
            id=row['id'],
            name=row['name'],
            definition=row['definition'],
            example=row['example'],
            created_by=row['created_by'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            creator_name=row['creator_name'] or ""
        )
        
        # 동의어 조회
        cursor.execute(
            "SELECT synonym_name FROM synonyms WHERE term_id = ?",
            (term.id,)
        )
        term.synonyms = [r['synonym_name'] for r in cursor.fetchall()]
        
        # 카테고리 조회
        cursor.execute("""
            SELECT c.* FROM categories c
            JOIN term_categories tc ON c.id = tc.category_id
            WHERE tc.term_id = ?
        """, (term.id,))
        term.categories = [
            Category(
                id=r['id'],
                name=r['name'],
                description=r['description'],
                color=r['color']
            )
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return term
    
    @staticmethod
    def create(term: Term, user_id: int, category_ids: List[int] = None) -> int:
        """용어 생성"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO terms (name, definition, example, created_by)
               VALUES (?, ?, ?, ?)""",
            (term.name, term.definition, term.example, user_id)
        )
        term_id = cursor.lastrowid
        
        # 동의어 저장
        for synonym in term.synonyms:
            if synonym.strip():
                cursor.execute(
                    "INSERT INTO synonyms (term_id, synonym_name) VALUES (?, ?)",
                    (term_id, synonym.strip())
                )
        
        # 카테고리 연결
        if category_ids:
            for cat_id in category_ids:
                cursor.execute(
                    "INSERT INTO term_categories (term_id, category_id) VALUES (?, ?)",
                    (term_id, cat_id)
                )
        
        # 히스토리 기록
        cursor.execute(
            """INSERT INTO term_history 
               (term_id, action_type, field_name, new_value, changed_by)
               VALUES (?, 'create', 'term', ?, ?)""",
            (term_id, term.name, user_id)
        )
        
        conn.commit()
        conn.close()
        return term_id
    
    @staticmethod
    def update(term: Term, user_id: int, category_ids: List[int] = None):
        """용어 수정 (히스토리 자동 기록)"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 기존 데이터 조회
        old_term = TermRepository.get_by_id(term.id)
        if not old_term:
            conn.close()
            return
        
        # 변경 사항 기록
        changes = []
        if old_term.name != term.name:
            changes.append(('name', old_term.name, term.name))
        if old_term.definition != term.definition:
            changes.append(('definition', old_term.definition, term.definition))
        if old_term.example != term.example:
            changes.append(('example', old_term.example, term.example))
        
        # 용어 업데이트
        cursor.execute(
            """UPDATE terms 
               SET name = ?, definition = ?, example = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (term.name, term.definition, term.example, term.id)
        )
        
        # 동의어 업데이트 (기존 삭제 후 재삽입)
        old_synonyms = set(old_term.synonyms)
        new_synonyms = set(s.strip() for s in term.synonyms if s.strip())
        
        if old_synonyms != new_synonyms:
            changes.append(('synonyms', ', '.join(old_synonyms), ', '.join(new_synonyms)))
        
        cursor.execute("DELETE FROM synonyms WHERE term_id = ?", (term.id,))
        for synonym in new_synonyms:
            cursor.execute(
                "INSERT INTO synonyms (term_id, synonym_name) VALUES (?, ?)",
                (term.id, synonym)
            )
        
        # 카테고리 업데이트
        cursor.execute("DELETE FROM term_categories WHERE term_id = ?", (term.id,))
        if category_ids:
            for cat_id in category_ids:
                cursor.execute(
                    "INSERT INTO term_categories (term_id, category_id) VALUES (?, ?)",
                    (term.id, cat_id)
                )
        
        # 히스토리 기록
        for field_name, old_val, new_val in changes:
            cursor.execute(
                """INSERT INTO term_history 
                   (term_id, action_type, field_name, old_value, new_value, changed_by)
                   VALUES (?, 'update', ?, ?, ?, ?)""",
                (term.id, field_name, old_val, new_val, user_id)
            )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(term_id: int, user_id: int):
        """용어 삭제"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 삭제 전 이름 조회
        cursor.execute("SELECT name FROM terms WHERE id = ?", (term_id,))
        row = cursor.fetchone()
        if row:
            term_name = row['name']
            
            # 히스토리 기록
            cursor.execute(
                """INSERT INTO term_history 
                   (term_id, action_type, field_name, old_value, changed_by)
                   VALUES (?, 'delete', 'term', ?, ?)""",
                (term_id, term_name, user_id)
            )
            
            # 삭제
            cursor.execute("DELETE FROM terms WHERE id = ?", (term_id,))
        
        conn.commit()
        conn.close()


class HistoryRepository:
    """변경 이력 리포지토리"""
    
    @staticmethod
    def get_all(limit: int = 100) -> List[TermHistory]:
        """전체 히스토리 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT h.*, u.username as changer_name, t.name as term_name
            FROM term_history h
            LEFT JOIN users u ON h.changed_by = u.id
            LEFT JOIN terms t ON h.term_id = t.id
            ORDER BY h.changed_at DESC
            LIMIT ?
        """, (limit,))
        
        history = [
            TermHistory(
                id=row['id'],
                term_id=row['term_id'],
                action_type=row['action_type'],
                field_name=row['field_name'],
                old_value=row['old_value'],
                new_value=row['new_value'],
                changed_by=row['changed_by'],
                changed_at=row['changed_at'],
                changer_name=row['changer_name'] or "알 수 없음",
                term_name=row['term_name'] or "(삭제됨)"
            )
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return history
    
    @staticmethod
    def get_by_term(term_id: int) -> List[TermHistory]:
        """특정 용어의 히스토리 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT h.*, u.username as changer_name, t.name as term_name
            FROM term_history h
            LEFT JOIN users u ON h.changed_by = u.id
            LEFT JOIN terms t ON h.term_id = t.id
            WHERE h.term_id = ?
            ORDER BY h.changed_at DESC
        """, (term_id,))
        
        history = [
            TermHistory(
                id=row['id'],
                term_id=row['term_id'],
                action_type=row['action_type'],
                field_name=row['field_name'],
                old_value=row['old_value'],
                new_value=row['new_value'],
                changed_by=row['changed_by'],
                changed_at=row['changed_at'],
                changer_name=row['changer_name'] or "알 수 없음",
                term_name=row['term_name'] or "(삭제됨)"
            )
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return history
