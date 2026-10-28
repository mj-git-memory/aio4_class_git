"""도시별 사용자를 점수순으로 조회한다. LIMIT 0을 잃는 버그가 있다."""
import argparse
# argparse : 터미널에서 프로그램을 실행할 때 프로그램에 필요한 값을 함께 전달할 수 있음. 
# ex) python main.py --name 수진 : "main.py를 실행하고, 이름으로 수진을 사용해 줘”라는 뜻
# -> Python이 --name의 의미를 자동으로 아는 것은 아님. 코드에서 argparse를 이용해 알려줘야 함.
from pathlib import Path
# Path : 파일과 폴더 경로를 다룸
# -> 아래에서 기본 DB 파일 위치를 정할 때 사용
import sqlite3
# sqlite3 : Python에서 SQLite 데이터베이스를 사용할 수 있게 해주는 모듈



def prepare_database(db_path):
    users = [
        (1, "민지", "서울", 80),
        (2, "준호", "부산", 95),
        (3, "수아", "서울", 95),
        (4, "지훈", "대전", 70),
        (5, "하린", "서울", 95),
        (6, "O'Neil", "서울", 60),
    ]
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users2 ("
            "id INTEGER PRIMARY KEY, nickname TEXT NOT NULL, "
            "city TEXT NOT NULL, points INTEGER NOT NULL)"
        )
        connection.executemany(
            "INSERT OR IGNORE INTO users2 (id, nickname, city, points) "
            "VALUES (?, ?, ?, ?)"
            , users
        )
        connection.commit()
    finally:
        connection.close()


def normalize_limit(limit):
    if limit < 0:
        raise ValueError("limit은 0 이상이어야 합니다.")
    return limit or 2


def find_users(db_path, city, limit):
    effective_limit = normalize_limit(limit)
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        return connection.execute(
            "SELECT id, nickname, city, points FROM users2 "
            "WHERE city = ? "
            "ORDER BY points DESC, id ASC "
            "LIMIT ?"
            , (city, effective_limit)
        ).fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(Path(__file__).with_name("practice.db")))
    parser.add_argument("--city", default="서울")
    parser.add_argument("--limit", type=int, default=2)
    args = parser.parse_args()
    prepare_database(args.db)
    print(find_users(args.db, args.city, args.limit))
