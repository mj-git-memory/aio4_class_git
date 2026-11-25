"""SQLite 직원정보·법인카드 조회 Tool과 재현 가능한 테스트 DB 생성기.

python -X utf8 custom_tools.py --init-db
python -X utf8 custom_tools.py --sql "SELECT department, COUNT(*) AS count FROM employees GROUP BY department"
"""
import argparse
from contextlib import closing
from datetime import date, timedelta
import inspect
import json
import os
from pathlib import Path
import random
import sqlite3
import time

ROOT = Path(__file__).resolve().parent
DATABASE_SCHEMA = """employees(
 employee_id TEXT PRIMARY KEY, name TEXT, hire_date TEXT [YYYY-MM-DD],
 department TEXT, annual_salary_krw INTEGER [연봉, 원],
 evaluation TEXT [S/A/B/C/D], job_title TEXT, corporate_card_id TEXT UNIQUE);
card_transactions(
 transaction_id TEXT PRIMARY KEY, corporate_card_id TEXT REFERENCES employees(corporate_card_id),
 used_at TEXT [YYYY-MM-DD], merchant TEXT, category TEXT, amount_krw INTEGER [원], description TEXT).
연결: employees.corporate_card_id = card_transactions.corporate_card_id.
모든 데이터는 생성된 가상 데이터. 카드 사용액은 모두 승인된 양수 지출(KRW).
SQL의 문자열/날짜 값은 가능하면 ?와 parameters로 전달.
테이블 데이터는 Tool 실행 시에만 읽을 수 있음. 원문에 없는 직원 ID/이름 매핑을 추측하지 말 것."""


def database_path() -> Path:
    value = Path(os.getenv("SQLITE_DB_PATH", "company.sqlite3"))
    return (value if value.is_absolute() else ROOT / value).resolve()


def _result(status, data=None, error=None):
    return {"status": status, "data": data, "error": error}


def initialize_database(path: Path | None = None, *, seed: int = 20261119,
                        end_date: date = date(2026, 11, 19)) -> dict:
    """최초 실행 시 직원 100명/내역 1000건 생성. 기존 데이터는 수정/재생성하지 않음."""
    path = Path(path).resolve() if path is not None else database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        with connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id TEXT PRIMARY KEY, name TEXT NOT NULL,
                    hire_date TEXT NOT NULL, department TEXT NOT NULL,
                    annual_salary_krw INTEGER NOT NULL CHECK(annual_salary_krw>0),
                    evaluation TEXT NOT NULL CHECK(evaluation IN ('S','A','B','C','D')),
                    job_title TEXT NOT NULL, corporate_card_id TEXT NOT NULL UNIQUE
                );
                CREATE TABLE IF NOT EXISTS card_transactions (
                    transaction_id TEXT PRIMARY KEY, corporate_card_id TEXT NOT NULL,
                    used_at TEXT NOT NULL, merchant TEXT NOT NULL, category TEXT NOT NULL,
                    amount_krw INTEGER NOT NULL CHECK(amount_krw>0), description TEXT NOT NULL,
                    FOREIGN KEY(corporate_card_id) REFERENCES employees(corporate_card_id)
                );
                CREATE INDEX IF NOT EXISTS idx_employee_name ON employees(name);
                CREATE INDEX IF NOT EXISTS idx_employee_department ON employees(department);
                CREATE INDEX IF NOT EXISTS idx_card_date ON card_transactions(corporate_card_id, used_at);
            """)
            # 동시 실행 시에도 중복 생성하지 않도록 쓰기 잠금 안에서 건수를 확인합니다.
            connection.execute("BEGIN IMMEDIATE")
            counts = [connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                      for table in ("employees", "card_transactions")]
            created = counts == [0, 0]
            if created:
                rng = random.Random(seed)
                surnames = ("김", "이", "박", "최", "정", "강", "조", "윤", "장", "임")
                given_names = ("가온", "다온", "라온", "서준", "서윤", "도윤", "하린", "유진", "지안", "수현")
                departments = ("개발팀", "영업팀", "인사팀", "재무팀", "연구팀", "마케팅팀", "운영팀", "기획팀")
                titles = ("사원", "대리", "과장", "차장", "팀장")
                categories = (
                    ("식비", "사내식당", "업무 식사"), ("교통", "비즈교통", "업무 이동"),
                    ("숙박", "비즈호텔", "출장 숙박"), ("사무용품", "오피스상점", "업무용 소모품"),
                    ("교육", "직무교육원", "직무 교육"), ("회의비", "미팅센터", "외부 회의"),
                )
                employees, transactions = [], []
                for index in range(100):
                    employee_id = f"E{index + 1:03d}"
                    card_id = f"CARD-{1001 + index}"
                    employees.append((
                        employee_id, surnames[index // 10] + given_names[index % 10],
                        (date(2016, 1, 1) + timedelta(days=rng.randrange(3500))).isoformat(),
                        departments[index % len(departments)], rng.randrange(76, 281) * 500000,
                        rng.choices(("S", "A", "B", "C", "D"), weights=(10, 35, 35, 15, 5))[0],
                        titles[index % len(titles)], card_id,
                    ))
                    for number in range(10):
                        category, merchant, description = rng.choice(categories)
                        # 모든 카드에 기준월 거래가 최소 1건 존재합니다.
                        days_ago = index % 15 if number == 0 else rng.randrange(90)
                        transactions.append((
                            f"TX-{index * 10 + number + 1:06d}", card_id,
                            (end_date - timedelta(days=days_ago)).isoformat(),
                            f"가상{merchant}{rng.randrange(1, 6)}호점", category,
                            rng.randrange(50, 5001) * 100, description,
                        ))
                connection.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", employees)
                connection.executemany("INSERT INTO card_transactions VALUES (?,?,?,?,?,?,?)", transactions)
            employee_count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
            transaction_count = connection.execute("SELECT COUNT(*) FROM card_transactions").fetchone()[0]
            period = connection.execute("SELECT MIN(used_at), MAX(used_at) FROM card_transactions").fetchone()
            violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    return {"database": str(path), "created": created, "employees": employee_count,
            "card_transactions": transaction_count, "transaction_period": list(period),
            "foreign_key_violations": len(violations)}


def _authorize(action, first, second, database, trigger):
    # SQLite 파서가 판정한 작업을 제한합니다. 주석/대소문자로 우회할 수 없습니다.
    if action == sqlite3.SQLITE_READ:
        return sqlite3.SQLITE_OK if first in {"employees", "card_transactions"} else sqlite3.SQLITE_DENY
    if action in {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE}:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION:
        return sqlite3.SQLITE_DENY if (second or "").lower() in {"load_extension", "writefile", "readfile"} else sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def query_database(sql: str, parameters: list | None = None, row_limit: int = 200) -> dict:
    """두 테이블의 SELECT/JOIN/집계. 변경/ATTACH/PRAGMA 차단, 최대 200행, 실행량 제한."""
    if not isinstance(sql, str) or not sql.strip():
        return _result("invalid_input", error="sql은 비어 있지 않은 문자열이어야 합니다.")
    if parameters is None:
        parameters = []
    if not isinstance(parameters, list) or any(not isinstance(p, (str, int, float, type(None))) for p in parameters):
        return _result("invalid_input", error="parameters는 문자열/숫자/null 값의 배열이어야 합니다.")
    if type(row_limit) is not int or not 1 <= row_limit <= 200:
        return _result("invalid_input", error="row_limit은 1~200 정수여야 합니다.")
    path = database_path()
    if not path.is_file():
        return _result("error", error="SQLite DB가 없습니다. custom_tools.py --init-db를 실행하세요.")
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as connection:
            connection.row_factory = sqlite3.Row
            connection.set_authorizer(_authorize)
            deadline = time.monotonic() + 2
            connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
            cursor = connection.execute(sql, parameters)
            if cursor.description is None:
                return _result("invalid_input", error="조회 SQL만 허용됩니다.")
            columns = [column[0] for column in cursor.description]
            if len(columns) != len(set(columns)):
                return _result("invalid_input", error="중복 출력 열에 SQL AS로 서로 다른 별칭을 지정하세요.")
            rows = cursor.fetchmany(row_limit + 1)
            return _result("success", {
                "columns": columns, "rows": [dict(row) for row in rows[:row_limit]],
                "returned_count": min(len(rows), row_limit), "truncated": len(rows) > row_limit,
                "row_limit": row_limit,
            })
    except sqlite3.Error as error:
        return _result("error", error=f"조회 SQL 실행 실패: {error}")


TOOL_DEFINITIONS = [{
    "name": "query_database",
    "description": "질문과 DB 스키마에 맞게 직접 작성한 읽기 전용 SQL 실행. 직원/카드 조회, JOIN, 필터, 집계, 순위를 모두 이 Tool로 수행.",
    "parameters": {
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "Gemini가 작성한 SQLite SELECT 또는 WITH ... SELECT"},
            "parameters": {
                "type": ["array", "null"],
                "items": {"anyOf": [{"type": "string"}, {"type": "number"}, {"type": "null"}]},
                "description": "?에 순서대로 바인딩할 값. 문자열/숫자/null 타입을 그대로 유지. 값이 없으면 [] 또는 null.",
            },
            "row_limit": {"type": ["integer", "null"], "description": "반환 행 상한 1~200. null이면 200."},
        },
        "required": ["sql"],
        "additionalProperties": False,
    },
}]

TOOL_REGISTRY = {"query_database": query_database}


def execute_tool(name: str, arguments: str) -> dict:
    """등록 함수와 인수명만 허용. 모델 출력은 JSON 파싱하며 코드로 실행하지 않음."""
    if name not in TOOL_REGISTRY:
        return _result("invalid_input", error="등록되지 않은 Tool입니다.")
    try:
        args = json.loads(arguments)
        if not isinstance(args, dict):
            raise ValueError
        # strict tool schema는 생략 가능 인수를 null로 전달할 수 있습니다.
        args = {key: value for key, value in args.items() if value is not None}
        inspect.signature(TOOL_REGISTRY[name]).bind(**args)
    except (ValueError, TypeError):
        return _result("invalid_input", error="Tool 인수가 올바른 JSON 객체/함수 인수가 아닙니다.")
    return TOOL_REGISTRY[name](**args)


def main() -> int:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False, encoding="utf-8-sig")
    parser = argparse.ArgumentParser(description="SQLite DB 생성 또는 지정 SQL 단독 검증")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--init-db", action="store_true", help="직원 100명/카드 사용내역 1000건 최초 생성")
    action.add_argument("--sql", help="검증할 읽기 전용 SQL")
    parser.add_argument("--parameters", default="[]", help="? 바인딩 값의 JSON 배열")
    parser.add_argument("--row-limit", type=int, default=200)
    parser.add_argument("--db-path")
    args = parser.parse_args()
    if args.db_path:
        os.environ["SQLITE_DB_PATH"] = args.db_path
    if args.init_db:
        result = initialize_database()
    else:
        try:
            parameters = json.loads(args.parameters)
        except ValueError:
            parser.error("--parameters는 올바른 JSON 배열이어야 합니다.")
        result = query_database(args.sql, parameters, args.row_limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result.get("status") in {"error", "invalid_input"})


if __name__ == "__main__":
    raise SystemExit(main())
