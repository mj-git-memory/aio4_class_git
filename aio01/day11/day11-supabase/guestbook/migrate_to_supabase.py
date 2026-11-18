"""앱을 종료한 후 이 폴더에서 python migrate_to_supabase.py로 한 번 실행합니다."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

import main

BASE = Path(__file__).resolve().parent


def read_source(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"원본 SQLite 파일이 없습니다: {path}")
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as source:
        return source.execute(
            "SELECT id, name, message, created_at FROM entries ORDER BY id"
        ).fetchall()


def migrate():
    path = Path(os.environ.get("GUESTBOOK_DB_PATH", BASE / "data" / "guestbook.db"))
    rows = read_source(path)
    # 앱과 동일한 연결 정보와 테이블 생성 코드를 사용합니다.
    main.init_db(path)
    with main.connect(path) as target:
        target.execute("SET LOCAL lock_timeout = '10s'")
        target.execute("LOCK TABLE public.entries IN EXCLUSIVE MODE")
        count = target.execute(
            "SELECT COUNT(*) AS total FROM public.entries"
        ).fetchone()["total"]
        if count:
            raise RuntimeError("대상 테이블에 데이터가 있습니다. 덮어쓰지 않고 중단합니다.")
        with target.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO public.entries (id, name, message, created_at)
                VALUES (%s, %s, %s, %s)
            """, rows)
        copied = target.execute("""
            SELECT id, name, message, created_at
            FROM public.entries ORDER BY id
        """).fetchall()
        values = [(row["id"], row["name"], row["message"], row["created_at"]) for row in copied]
        if values != rows:
            raise RuntimeError("복사 결과가 원본과 다릅니다. 이전을 취소합니다.")
        next_id = max(1, max((row[0] for row in rows), default=0) + 1)
        target.execute("""
            SELECT setval(
                pg_get_serial_sequence('public.entries', 'id'),
                %s, false
            )
        """, (next_id,))
    print(f"{len(rows)}개 이전 완료. 원본 SQLite 파일은 변경하지 않았습니다.")


if __name__ == "__main__":
    migrate()
