"""외부 DB 도구 없이 sqlite3로 한 개의 테이블만 관리한다."""

import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

PAGE_SIZE = 10
MAX_ENTRIES = 1000
KST = timezone(timedelta(hours=9))


def connect(path: Path):
    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(path)) as db, db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 20),
                message TEXT NOT NULL CHECK(length(message) BETWEEN 1 AND 500),
                created_at TEXT NOT NULL
            )
        """)


def list_entries(path: Path, page: int):
    with closing(connect(path)) as db:
        total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(page, pages)
        rows = db.execute(
            "SELECT * FROM entries ORDER BY id DESC LIMIT ? OFFSET ?",
            (PAGE_SIZE, (page - 1) * PAGE_SIZE),
        ).fetchall()
    return rows, total, page, pages


def add_entry(path: Path, name: str, message: str):
    with closing(connect(path)) as db, db:
        # 개수 확인과 저장을 같은 쓰기 트랜잭션에서 처리한다.
        db.execute("BEGIN IMMEDIATE")
        total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        if total >= MAX_ENTRIES:
            raise ValueError("방명록이 가득 찼습니다. 관리자에게 문의해 주세요.")
        # 문자열을 SQL에 직접 이어 붙이지 않고 값 자리(?)에 전달한다.
        db.execute(
            "INSERT INTO entries (name, message, created_at) VALUES (?, ?, ?)",
            (name, message, datetime.now(KST).isoformat(timespec="minutes")),
        )
