from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory


def create_database(db_path):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        connection.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, "
            "nickname TEXT NOT NULL, email TEXT NOT NULL UNIQUE, "
            "points INTEGER CHECK(points BETWEEN 0 AND 100))"
        )
        connection.commit()
    finally:
        connection.close()


def add_user(db_path, user_id, nickname, email, points):
    connection = sqlite3.connect(db_path, autocommit=False)

    if not nickname or not email or not points : # 3개 중 하나라도 null 이면 ?!
        raise ValueError
    
    try:
        connection.execute(
            "INSERT INTO users (id, nickname, email, points) VALUES (?, ?, ?, ?)",
            (user_id, nickname, email, points),
        )
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


def read_users(db_path):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        return connection.execute(
            "SELECT id, nickname, email, points FROM users ORDER BY id"
        ).fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    with TemporaryDirectory() as folder: ## 임시db 사용
        db_path = Path(folder) / "constraints.db"
        # db_path = Path(__file__) / "constraints.db"
        # -> lesson_04/main.py/constraints.db : main.py는 파일이므로 그 안에 DB를 만들 수 없어 오류가 발생

        # db_path = Path(__file__).with_name("constraints.db") ## 임시db 사용하지 않음 
        # main.py 두 번 실행 시키면 에러 발생 -> sqlite3.OperationalError: table users already exists
        # .with_name("constraints.db") : 경로의 마지막 이름인 main.py를 constraints.db로 바꿈

        create_database(db_path)
        add_user(db_path, 1, "민지", "minji@example.test", 80)
        try:
            add_user(db_path, 2, "수아", "sua@example.test", None)
        except sqlite3.IntegrityError as exc :  # 오류 시 실행
            print("NULL 점수 거절:", exc)
        else :  # 오류가 없을 때 실행
            print("문제: NULL 점수가 저장되었습니다.")
        print(read_users(db_path))


# db_path = Path(__file__).parent / "constraints.db"
# db_path = Path(__file__).with_name("constraints.db")

## ex) path = Path("/day10/lesson_04/main.py")

## .parent : 해당 파일이 들어 있는 폴더의 경로를 가져옴
# path.parent / "constraints.db"
# # /day10/lesson_04/constraints.db

## .with_name() : 경로의 마지막 이름을 다른 이름으로 바꾼 경로를 만듦 
# path.with_name("constraints.db")
# # /day10/lesson_04/constraints.db