"""앱을 종료한 뒤 실행: python day1-day8/migrate_to_supabase.py."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

import psycopg

from database import init_db
from db_config import load_db_config

BASE = Path(__file__).resolve().parent


def migrate():
    path = Path(os.environ.get("GUESTBOOK_DB", BASE / "data" / "guestbook.db")).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"원본 SQLite 파일이 없습니다: {path}")
    # 원본을 변경하지 않고 열 정보와 데이터를 같은 스냅샷에서 읽습니다.
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as source:
        source.execute("BEGIN")
        columns = {row[1] for row in source.execute("PRAGMA table_info(entries)")}
        password_column = "password_hash" if "password_hash" in columns else "''"
        rows = source.execute(
            "SELECT id, name, message, created_at, "
            + password_column + " FROM entries ORDER BY id"
        ).fetchall()

    init_db(path)
    with psycopg.connect(**load_db_config(), sslmode="require", connect_timeout=10) as target:
        target.execute("SET LOCAL lock_timeout = '10s'")
        target.execute("LOCK TABLE guestbook.entries IN EXCLUSIVE MODE")
        if target.execute("SELECT COUNT(*) FROM guestbook.entries").fetchone()[0]:
            raise RuntimeError("대상 테이블에 데이터가 있습니다. 덮어쓰지 않고 중단합니다.")
        with target.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO guestbook.entries
                    (id, name, message, created_at, password_hash)
                VALUES (%s, %s, %s, %s, %s)
            """, rows)
        copied = target.execute("""
            SELECT id, name, message, created_at, password_hash
            FROM guestbook.entries ORDER BY id
        """).fetchall()
        if copied != rows:
            raise RuntimeError("복사 결과가 원본과 다릅니다. 이전을 취소합니다.")
        next_id = max(1, max((row[0] for row in rows), default=0) + 1)
        target.execute("""
            SELECT setval(pg_get_serial_sequence('guestbook.entries', 'id'), %s, false)
        """, (next_id,))
    print(f"{len(rows)}개 이전 완료. 원본 SQLite 파일은 변경하지 않았습니다.")


if __name__ == "__main__":
    migrate()
