"""외부 DB 도구 없이 sqlite3로 한 개의 테이블만 관리한다."""

import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from passwords import hash_password, verify_password

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
                created_at TEXT NOT NULL,
                password_hash TEXT NOT NULL DEFAULT ''
            )
        """)
        # 이전 DB를 삭제하지 않고 같은 테이블에 열 하나만 추가한다.
        columns = {row["name"] for row in db.execute("PRAGMA table_info(entries)")}
        if "password_hash" not in columns:
            db.execute("ALTER TABLE entries ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''")


def list_entries(path: Path, page: int):
    with closing(connect(path)) as db:
        total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(page, pages)
        rows = db.execute(
            "SELECT id, name, message, created_at FROM entries ORDER BY id DESC LIMIT ? OFFSET ?",
            (PAGE_SIZE, (page - 1) * PAGE_SIZE),
        ).fetchall()
    return rows, total, page, pages


def add_entry(path: Path, name: str, message: str, password: str):
    password_hash = hash_password(password)
    with closing(connect(path)) as db, db:
        # 개수 확인과 저장을 같은 쓰기 트랜잭션에서 처리한다.
        db.execute("BEGIN IMMEDIATE")
        total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        if total >= MAX_ENTRIES:
            raise ValueError("방명록이 가득 찼습니다. 관리자에게 문의해 주세요.")
        # 문자열을 SQL에 직접 이어 붙이지 않고 값 자리(?)에 전달한다.
        db.execute(
            "INSERT INTO entries (name, message, created_at, password_hash) VALUES (?, ?, ?, ?)",
            (name, message, datetime.now(KST).isoformat(timespec="minutes"), password_hash),
        )


def get_entry(path: Path, entry_id: int):
    with closing(connect(path)) as db:
        return db.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()


def update_entry(path: Path, entry_id: int, name: str, message: str, password: str):
    entry = get_entry(path, entry_id)
    if entry is None:
        raise LookupError("방명록을 찾을 수 없습니다.")
    if not entry["password_hash"]:
        raise PermissionError("비밀번호 기능 추가 전에 작성된 글은 수정할 수 없습니다.")
    if not verify_password(password, entry["password_hash"]):
        raise PermissionError("비밀번호가 일치하지 않습니다.")
    with closing(connect(path)) as db, db:
        db.execute(
            "UPDATE entries SET name = ?, message = ? WHERE id = ?",
            (name, message, entry_id),
        )
