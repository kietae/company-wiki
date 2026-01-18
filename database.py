"""
회사 용어 위키 - 데이터베이스 모듈
SQLite 연결 및 테이블 초기화
"""

import sqlite3
import os
from pathlib import Path


def get_db_path() -> Path:
    """데이터베이스 파일 경로 반환"""
    return Path(__file__).parent / "wiki.db"


def get_connection() -> sqlite3.Connection:
    """SQLite 연결 객체 반환"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # 딕셔너리 스타일 접근 가능
    conn.execute("PRAGMA foreign_keys = ON")  # 외래키 제약 활성화
    return conn


def init_database():
    """데이터베이스 테이블 초기화"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 사용자 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 카테고리 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#3498db'
        )
    """)
    
    # 용어 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            definition TEXT NOT NULL,
            example TEXT,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 동의어 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS synonyms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_id INTEGER REFERENCES terms(id) ON DELETE CASCADE,
            synonym_name TEXT NOT NULL
        )
    """)
    
    # 용어-카테고리 연결 (다대다)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS term_categories (
            term_id INTEGER REFERENCES terms(id) ON DELETE CASCADE,
            category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
            PRIMARY KEY (term_id, category_id)
        )
    """)
    
    # 변경 이력 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS term_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_id INTEGER REFERENCES terms(id) ON DELETE CASCADE,
            action_type TEXT NOT NULL,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            changed_by INTEGER REFERENCES users(id),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 검색 성능을 위한 인덱스
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_terms_name ON terms(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_synonyms_name ON synonyms(synonym_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_term ON term_history(term_id)")
    
    conn.commit()
    conn.close()
    
    print(f"데이터베이스 초기화 완료: {get_db_path()}")


def insert_sample_data():
    """테스트용 샘플 데이터 삽입"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 기본 관리자 사용자
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, role) VALUES ('admin', 'admin')
    """)
    
    # 샘플 카테고리
    categories = [
        ('개발', '개발팀에서 사용하는 기술 용어', '#e74c3c'),
        ('마케팅', '마케팅/영업 관련 용어', '#2ecc71'),
        ('재무', '재무/회계 관련 용어', '#f39c12'),
        ('일반', '공통으로 사용하는 용어', '#3498db'),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO categories (name, description, color) VALUES (?, ?, ?)
    """, categories)
    
    conn.commit()
    conn.close()
    
    print("샘플 데이터 삽입 완료")


if __name__ == "__main__":
    init_database()
    insert_sample_data()
