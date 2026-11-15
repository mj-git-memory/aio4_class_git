# Day 11 학습 정리 — PostgreSQL·Supabase·방명록 DB 이전

정리 기준: 2026-10-29 현재 소스 코드와 수업 중 질문 내용.
표시: **⭐ 중요**는 꼭 기억할 개념, **🧪 테스트 포인트**는 예제로 확인한 동작입니다.

## 1. 어떤 파일에서 무엇을 배웠나?

| 파일 | 배운 내용 |
|---|---|
| `main.py` | JSON 설정 읽기, 비밀번호 입력, PostgreSQL 접속, DB·사용자 확인 |
| `main2.py` | 스키마·테이블 생성, INSERT·SELECT·UPDATE·DELETE, 여러 행 입력 |
| `day11-supabase/guestbook/main.py` | SQLite 코드를 PostgreSQL용으로 전환, HTML 폼 처리, 페이지 나누기 |
| `day11-supabase/guestbook/migrate_to_supabase.py` | 기존 SQLite 데이터 복사와 결과 검증, ID 순번 조정 |
| `day11-supabase/guestbook/test_guestbook.py` | 정상·오류·경계 입력, 보안 관련 동작, 데이터 유지 검사 |
| `my_lmstudio.py` | 로컬 AI 서버 연결과 모델 목록 확인, 주석으로 남긴 채팅 예제 |
| `../day1-day8/db_config.py` | 후속 실습: 로컬 설정 파일과 배포 환경변수 함께 사용 |
| `../day1-day8/test_db_config.py` | 후속 실습: 실제 DB 없이 설정 로딩 검사 |

> 이 문서는 코드를 설명한 학습 자료입니다. 정리 과정에서 실제 DB 접속·데이터 이전·배포·DB 테스트를 실행하지 않았습니다. 실습에 사용한 실제 비밀번호는 기록하지 않습니다.

## 2. SQLite와 Supabase는 무엇이 다를까?

| 구분 | SQLite | Supabase의 PostgreSQL |
|---|---|---|
| 저장 위치 | `guestbook.db` 같은 로컬 파일 | 별도 DB 서버 |
| 연결 도구 | Python 내장 `sqlite3` | 외부 패키지 `psycopg` |
| 접속에 필요한 것 | 파일 경로 | host, port, dbname, user, password |
| 값 자리표시자 | `?` | `%s` |
| 이름 공간 | 실습에서는 `entries` | `스키마.entries` |
| 앱 재배포 | 로컬 파일 보존 여부가 호스팅 환경에 달림 | 앱과 별도인 DB에 데이터를 저장 |

비유: SQLite는 내 컴퓨터의 공책이고, PostgreSQL은 여러 사람이 접속할 수 있는 중앙 기록실입니다. Supabase는 PostgreSQL DB 등을 제공하는 플랫폼입니다.

**⭐ 중요: 연결 함수만 바꾸면 이전이 끝나는 것이 아닙니다. SQL 문법·반환값·자동 ID·예외 처리도 확인해야 합니다.**

## 3. 접속정보와 JSON·Path·getpass

```python
import json
from pathlib import Path

config_path = Path(__file__).with_name("config.json")
config = json.loads(config_path.read_text(encoding="utf-8"))
```

- `__file__`: 지금 실행되는 파이썬 파일의 경로입니다.
- `with_name("config.json")`: 같은 폴더의 설정 파일을 가리킵니다.
- `read_text()`: 파일을 문자열로 읽습니다.
- `json.loads()`: JSON 문자열을 파이썬 딕셔너리로 바꿉니다.
- `config["host"]`: 반드시 있어야 하는 키를 읽습니다. 없으면 `KeyError`입니다.
- `config.get("dbname", config.get("database"))`: `dbname` 키가 없을 때 `database`를 대신 읽습니다. 값이 빈 문자열인 경우까지 자동 보완하는 것은 아닙니다.

설정 구조 예시 — 실제 접속정보가 아닙니다.

```json
{
  "host": "your-db-host",
  "port": 5432,
  "dbname": "postgres",
  "user": "your-db-user"
}
```

접속정보의 뜻:

| 키 | 의미 | 비유 |
|---|---|---|
| host | DB 서버 주소 | 건물 주소 |
| port | DB 접속 포트 | 출입구 번호 |
| dbname | 접속할 데이터베이스 | 사용할 기록실 |
| user | DB 사용자 | 출입자 이름 |
| password | 해당 사용자의 DB 비밀번호 | 출입 비밀번호 |

```python
from getpass import getpass
password = getpass("Supabase 비밀번호: ")
```

`getpass()`는 터미널에서 입력 문자를 표시하지 않고 비밀번호를 받습니다.

**⭐ 중요: 터미널 실습에는 `getpass()`, Render 같은 무인 서버에는 환경변수가 적합합니다. 서버가 실행 중 키보드 입력을 기다리게 만들면 안 됩니다.**

`main.py`의 `print(config)`는 설정 확인용 코드입니다. password까지 들어 있는 설정을 출력하면 로그에 노출될 수 있으므로 실제 사용에서는 제거하거나 민감한 값을 가려야 합니다. 패키지 제거 명령의 올바른 이름도 `psycopg`입니다. 소스 주석의 `pycopg`는 오타입니다.

## 4. PostgreSQL 연결과 트랜잭션

```python
import psycopg

with psycopg.connect(
    host=config["host"],
    port=config["port"],
    dbname=config["dbname"],
    user=config["user"],
    password=password,
    sslmode="require",
    connect_timeout=10,
) as conn:
    row = conn.execute(
        "SELECT current_database(), current_user"
    ).fetchone()
    print(row[0], row[1])
```

- `sslmode="require"`: 암호화된 연결을 요구합니다. 인증서·호스트 검증까지 모두 뜻하는 설정은 아닙니다.
- `connect_timeout=10`: 연결 시도를 기다리는 제한입니다. 모든 SQL의 실행 시간이 10초로 제한되는 것은 아닙니다.
- `execute()`: SQL을 실행합니다.
- `fetchone()`: 결과 한 행을 가져옵니다. 행이 없으면 `None`입니다.
- `fetchall()`: 남은 결과 전체를 리스트로 가져옵니다.

**⭐ 중요: psycopg의 연결 컨텍스트는 정상 종료하면 커밋, 예외로 종료하면 롤백하고 연결을 닫습니다.**

트랜잭션은 여러 DB 작업을 한 묶음으로 처리하는 단위입니다. 예를 들어 글을 입력한 뒤 조회에서 예외가 나면, 같은 트랜잭션 안에서 입력한 글도 롤백될 수 있습니다.

```text
입력 성공 → print("저장 완료") → 조회 실패 → 블록에서 예외 발생 → 롤백
```

따라서 블록 안에서 출력한 “저장 완료”만 보고 최종 커밋까지 성공했다고 단정하지 않습니다.

`closing(connection)`은 연결을 닫는 역할이고 트랜잭션 커밋 자체를 담당하지 않습니다. 소스의 `with closing(connect(path)) as db, db:`는 연결 종료와 트랜잭션 처리를 함께 사용한 형태입니다.

## 5. ⭐ 중요: 데이터베이스 → 스키마 → 테이블

```text
postgres                  데이터베이스
├── public                스키마
│   └── entries           테이블
└── ch2                   스키마
    └── users             테이블
```

- 스키마: 테이블을 묶어 두는 폴더 같은 공간
- 테이블: 행과 열로 실제 데이터를 저장하는 곳
- `public.entries`: public 스키마 안의 entries 테이블

```sql
CREATE SCHEMA IF NOT EXISTS ch2;
CREATE TABLE IF NOT EXISTS ch2.users (...);
```

**`CREATE SCHEMA ch2`는 이후 SQL이 자동으로 ch2를 사용하게 만드는 명령이 아닙니다.** 스키마를 생략한 이름은 `search_path` 설정에 따라 해석됩니다. 실습에서는 `ch2.users`처럼 명시하면 혼동을 줄일 수 있습니다.

### 질문: `relation "ch2.users" does not exist`는 왜 났나?

생성·입력에서는 `users`를 사용하고 조회에서만 `ch2.users`를 사용했기 때문입니다. 생성·입력·조회에서 같은 전체 이름을 사용해야 합니다.

### 현재 두 방명록 프로젝트의 위치

| 프로젝트 | 현재 DB 테이블 | 특징 |
|---|---|---|
| `day11/day11-supabase/guestbook` | `public.entries` | 이름 30자, 내용 1,000자, 수정용 비밀번호 없음 |
| `day1-day8` | `guestbook.entries` | 이름 20자, 내용 500자, 수정용 비밀번호 해시 있음 |

**⭐ 중요: 테이블 이름이 같아도 스키마가 다르면 다른 테이블입니다.** 두 프로젝트의 설정·데이터·이전 스크립트를 혼용하지 않습니다.

Supabase에서 글이 안 보일 때는 프로젝트와 스키마를 먼저 확인합니다.

```sql
SELECT id, name, message, created_at
FROM guestbook.entries
ORDER BY id DESC;
```

Supabase 화면에 `public`만 선택되어 있으면 `guestbook.entries`는 보이지 않을 수 있습니다.

## 6. 테이블 제약조건과 자동 ID

```sql
CREATE TABLE IF NOT EXISTS ch2.users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);
```

| 구문 | 의미 | 예시 |
|---|---|---|
| PRIMARY KEY | 행을 고유하게 식별, NULL·중복 불가 | 사용자 번호 |
| NOT NULL | NULL 금지 | 이름 누락 방지. 빈 문자열까지 금지하는 것은 아님 |
| UNIQUE | 중복값 제한 | 같은 이메일 중복 가입 방지 |
| CHECK | 조건을 만족하는지 검사 | `CHECK(length(name) BETWEEN 1 AND 30)` |
| IDENTITY | 자동으로 번호 생성 | 새 글의 id 자동 발급 |
| IF NOT EXISTS | 이미 있으면 새로 만들지 않음 | 기존 테이블 자동 수정 기능은 아님 |

`GENERATED ALWAYS`는 일반 INSERT에서 ID 직접 지정을 제한합니다. `GENERATED BY DEFAULT`는 직접 ID를 넣을 수 있어 기존 번호를 보존하는 이전에 편리합니다.

**⭐ 중요: PostgreSQL의 `INTEGER PRIMARY KEY`만으로 SQLite처럼 ID가 자동 생성되지는 않습니다.**

`main2.py`는 실행 초반에 `DROP TABLE IF EXISTS ch2.users`를 수행합니다. 반복 실습을 위한 초기화이므로 기존 users 데이터가 사라집니다. 운영 코드에 그대로 복사하지 않습니다. 자동 ID는 삭제·롤백 후에도 빈 번호가 생길 수 있으므로 글 개수나 연속 순번으로 해석하지 않습니다.

## 7. CRUD와 자리표시자 — 실제 질문 정리

CRUD는 생성(Create), 조회(Read), 수정(Update), 삭제(Delete)입니다.

### INSERT: 값을 SQL과 분리하기

```python
conn.execute(
    "INSERT INTO ch2.users(name, email) VALUES (%s, %s)",
    ("이순신", "sample@example.com"),
)
```

**⭐ 중요: psycopg에서는 `%`가 아니라 `%s`입니다. 숫자 값에도 `%s`를 사용하고, `%s`에 따옴표를 붙이지 않습니다.** SQL 문자열에 f-string으로 사용자 값을 이어 붙이지 않습니다.

오류 예: `VALUES(%, %)` → `only '%s', '%b', '%t' are allowed ...`

여러 행은 `executemany()`로 전달합니다.

```python
users = [("이순신", "a@example.com"), ("윤봉길", "b@example.com")]
with conn.cursor() as cur:
    cur.executemany(
        "INSERT INTO ch2.users(name, email) VALUES (%s, %s)", users
    )
```

자리표시자 개수와 각 튜플의 값 개수가 일치해야 합니다. 자리표시자는 **값**을 위한 것이며 테이블 이름을 `%s`로 전달하는 용도가 아닙니다.

### SELECT: 결과 꺼내기

```python
rows = conn.execute(
    "SELECT id, name, email FROM ch2.users ORDER BY id"
).fetchall()
for user_id, name, email in rows:
    print(user_id, name, email)
```

### UPDATE: SET과 인자 위치 기억하기

```python
conn.execute(
    "UPDATE ch2.users SET name = %s WHERE email = %s",
    ("강감찬", "a@example.com"),
)
```

질문에서 `UPDATE ch2.users name = ...`는 `SET`이 빠졌습니다. 값 튜플도 `execute()` 괄호 **안의 두 번째 인자**로 전달해야 합니다.

### DELETE: 값이 하나여도 튜플

```python
conn.execute(
    "DELETE FROM ch2.users WHERE email = %s",
    ("a@example.com",),
)
```

**⭐ 중요: `(value,)`는 원소 한 개인 튜플, `(value)`는 괄호로 감싼 값입니다.** UPDATE·DELETE에서 WHERE를 생략하면 전체 행에 영향을 줄 수 있습니다.

## 8. SQLite → PostgreSQL 전환 체크

| SQLite | PostgreSQL 실습 코드 |
|---|---|
| `sqlite3.connect(path)` | `psycopg.connect(...)` |
| `sqlite3.Row` | `row_factory=dict_row` |
| `VALUES (?, ?)` | `VALUES (%s, %s)` |
| `INTEGER PRIMARY KEY` 자동 번호 | `BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY` |
| `PRAGMA table_info(...)` | PostgreSQL에 그대로 실행 불가 |
| `BEGIN IMMEDIATE` | 실습에서는 트랜잭션 안에서 `LOCK TABLE ... IN EXCLUSIVE MODE` |
| `sqlite3.Error` | `psycopg.Error` |

### dict_row와 COUNT(*)

```python
from psycopg.rows import dict_row
# psycopg.connect(..., row_factory=dict_row)
total = conn.execute(
    "SELECT COUNT(*) AS total FROM public.entries"
).fetchone()["total"]
```

기본 튜플이면 `row[0]`, 딕셔너리 행이면 `row["total"]`로 읽습니다. 기존 `.fetchone()[0]`를 그대로 두지 않습니다.

### 왜 테이블을 잠갔을까?

최대 1,000개인데 현재 999개일 때, 두 요청이 동시에 999를 확인하면 둘 다 입력해 1,001개가 될 수 있습니다. 현재 실습은 개수 확인과 입력을 같은 트랜잭션에 두고 테이블 잠금으로 쓰기를 차례대로 진행합니다. 읽기는 일반 SELECT 기준으로 가능하지만 다른 쓰기는 대기할 수 있습니다. 이 잠금은 실습의 간단한 동시성 처리이며 모든 서비스에 적용할 유일한 방법은 아닙니다.

### 질문: 화면에서 created_at 때문에 500 오류가 난 이유

SQLite TEXT는 문자열이지만 PostgreSQL의 timestamp 열은 `datetime`으로 반환될 수 있습니다. 날짜 객체를 `html.escape()`에 전달하면 문자열용 `replace()` 호출에서 실패합니다.

```python
from datetime import datetime
from html import escape

value = record["created_at"]
text = value.isoformat() if isinstance(value, datetime) else str(value)
safe_text = escape(text)
```

**⭐ 중요: DB를 바꾸면 SQL뿐 아니라 파이썬으로 돌아오는 자료형도 확인합니다.** 현재 생성 SQL은 TEXT이지만 이미 존재하던 열이 timestamp라면 `CREATE TABLE IF NOT EXISTS`로 바뀌지 않습니다. 시간대 없는 날짜에 UTC라고 표시만 붙이면 시간대 변환이 되는 것도 아닙니다.

## 9. 데이터 이전: 원본 보존·검증·ID 조정

앱의 DB 연결 변경과 기존 데이터 복사는 별도 작업입니다. 연결을 바꿨다고 `.db` 파일의 글이 자동으로 옮겨지지 않습니다.

현재 이전 스크립트의 순서:

1. 앱을 멈춰 이전 중 새 글이 생기지 않게 합니다.
2. SQLite 원본을 `mode=ro`로 읽기 전용으로 엽니다.
3. 원본의 ID·이름·내용·작성일을 읽습니다.
4. PostgreSQL 테이블을 준비합니다.
5. 대상을 잠그고 기존 데이터가 있으면 덮어쓰지 않고 중단합니다.
6. 한 트랜잭션에서 복사한 후 원본과 모든 값을 비교합니다.
7. 다음 자동 ID를 `기존 최대 ID + 1`로 맞춥니다.
8. 정상 종료 후 커밋합니다. 원본 SQLite는 남습니다.

예: 1번·2번 글을 복사했다면 새 글이 3번부터 생기도록 자동 번호를 조정합니다.

```sql
SELECT setval(
    pg_get_serial_sequence('public.entries', 'id'),
    3,
    false
);
```

세 번째 인자 `false`는 다음 번호가 바로 3이 되게 합니다. 명시적으로 ID를 복사했다고 자동 시퀀스까지 맞춰지는 것은 아닙니다.

**⭐ 중요: 이전 스크립트를 Render의 시작 명령에 넣지 않습니다. 기존 글 이전은 일회성 작업입니다.** 현재 스크립트는 대상에 데이터가 있으면 재실행을 중단합니다. 대상이 기존 timestamp 구조라면 문자열 원본과의 비교 방식도 별도로 조정해야 합니다.

## 10. 🧪 방명록 테스트에서 기억할 개념

아래는 `day11-supabase/guestbook/test_guestbook.py`의 테스트 의도입니다.

**⭐ 중요: 이 파일은 SQLite 시절 작성한 테스트입니다. 현재 `connect()`는 임시 DB 경로를 무시하고 Supabase에 연결합니다. 그대로 전체 pytest를 실행하면 실제 DB에 테스트 글을 쓸 수 있습니다. 별도 테스트 DB와 PostgreSQL용 검증으로 바꾼 후 실행해야 합니다.**

과거 `VERIFICATION.md`의 `15 passed`는 2026-10-23 당시 코드의 기록이며 현재 Supabase 코드의 전체 통과를 뜻하지 않습니다. `sqlite_master` 검사와 `sqlite3.OperationalError` 예외 모킹도 현재 구현에 맞게 바꿔야 합니다.

| 테스트 | 확인하는 동작 | 기억할 개념 |
|---|---|---|
| 빈 화면·health | 글이 없어도 200, 빈 목록 안내 | 데이터 0개도 정상 상태 |
| 글 작성·새로고침 | POST 후 303, GET을 반복해도 글 1개 | PRG 패턴으로 재전송 방지 |
| 잘못된 입력 | 공백, 누락, 추가 필드, 길이 초과는 422 | 화면뿐 아니라 서버에서 검증 |
| 한글 최대 길이 | 이름 30자·내용 1,000자 허용 | 경계값 바로 안·밖을 검사 |
| HTML·SQL·템플릿 문자 | 위험 문자열을 실행하지 않고 표시 | 출력 이스케이프와 SQL 바인딩 구분 |
| 재시작 후 유지 | 다시 실행해도 글 유지 | 메모리 변수와 영구 저장 구분 |
| 페이지·정렬 | 21개면 20개+1개, 최신 글 먼저 | LIMIT·OFFSET·ORDER BY |
| 최대 개수 | 한도를 넘으면 409, 기존 글 유지 | 실패가 기존 데이터 손상으로 이어지지 않음 |
| 형식·크기·출처 | JSON·중복 필드·과대 요청 등 거절 | 입력 규칙과 HTTP 상태 코드 |
| DB 오류 | 503, 내부 경로는 화면에 숨김 | 오류 처리와 민감정보 보호 |

### 예시 A: 새로고침해도 왜 중복 저장되지 않을까?

```text
POST /entries → 저장 → 303 Redirect → GET /
```

새로고침 대상이 조회 요청이 되기 때문입니다. 이 패턴이 모든 중복 클릭이나 네트워크 재시도까지 막는 것은 아닙니다.

### 예시 B: SQL 삽입 방어와 HTML 삽입 방어는 다른 문제

사용자가 `'); DROP TABLE entries; --`를 입력하면 값 바인딩으로 SQL 명령이 아닌 데이터로 전달합니다. `<script>...</script>`를 입력하면 `html.escape()`로 HTML 실행 대신 글자로 표시합니다.

**⭐ 중요: `%s`는 SQL 값 전달, `escape()`는 HTML 출력 보호입니다. 하나로 다른 하나를 대체할 수 없습니다.**

`@@name@@` 같은 문자열도 사용자 글 안에서는 그대로 남도록 템플릿 처리를 검사합니다. 입력값에 치환을 반복하면 사용자 글이 템플릿으로 오해될 수 있습니다.

### 예시 C: 페이지 계산

```python
last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
offset = (page - 1) * PAGE_SIZE
```

총 21개, 한 페이지 20개라면 2페이지입니다. 2페이지는 `OFFSET 20`으로 앞의 20개를 건너뜁니다. 글 0개라도 페이지를 최소 1로 둡니다.

### 예시 D: 글자 수와 요청 바이트 수

한글 한 글자는 UTF-8에서 보통 3바이트입니다. 테스트의 내용 1,000자는 글자 수 제한이고, `MAX_BODY_BYTES = 16384`는 인코딩된 요청 전체의 바이트 제한입니다. 서로 다른 기준입니다.

| 상태 코드 | 실습에서의 의미 |
|---|---|
| 200 | 조회 성공 또는 리다이렉트 후 최종 조회 성공 |
| 303 | 저장 후 다른 GET 페이지로 이동 |
| 403 | cross-site 폼 요청 거절 |
| 409 | 최대 글 개수 초과 |
| 413 | 요청 본문이 너무 큼 |
| 415 | 허용하지 않는 본문 형식 |
| 422 | 필드·길이·인코딩·페이지 값 검증 실패 |
| 500 | 처리하지 못한 프로그램 오류 |
| 503 | DB 이용 불가 등에 대한 안내 응답 |

`follow_redirects=False`로 검사하면 저장 응답 303을 볼 수 있고, 자동으로 따라가면 마지막 GET의 200을 볼 수 있습니다.

`tmp_path`는 임시 폴더를, `monkeypatch`는 테스트 중 설정·함수를 잠깐 바꾸는 도구입니다. 변경한 한도를 1로 만들어 경계 상황을 빠르게 확인할 수 있습니다. 하지만 **실제 connect()가 tmp_path를 사용하는지까지 확인해야 테스트 DB가 격리됩니다.**

## 11. 후속 질문: 비밀번호·환경변수·Render·Python 환경

### DB 비밀번호와 방명록 수정 비밀번호는 다르다

- DB 비밀번호: 앱이 Supabase에 접속하는 서버용 비밀정보
- 수정용 비밀번호: 글 작성자가 자신의 글을 수정할 때 쓰는 값

`day1-day8`은 수정용 비밀번호의 원문 대신 `password_hash`를 저장합니다. 따라서 화면의 “비밀번호는 저장되지 않습니다”는 엄밀히는 “원문은 저장되지 않고 검증용 해시가 저장됩니다”라고 이해해야 합니다. `day11`의 작은 방명록에는 이 수정 비밀번호 기능이 없습니다.

### config.json을 Git에 안 올리면 Render는 어떻게 연결할까?

`day1-day8/db_config.py`의 우선순위는 **환경변수 → 로컬 config.json → 일부 기본값**입니다.

| 환경변수 | 설정 파일의 키 |
|---|---|
| PGHOST | host |
| PGPORT | port |
| PGDATABASE | dbname |
| PGUSER | user |
| PGPASSWORD | password |

Render 서비스의 Environment에서 직접 입력합니다. 따옴표는 입력하지 않습니다. `.env`를 만들어도 현재 로더는 자동으로 읽지 않습니다. `day11` 앱은 다른 구현으로 `GUESTBOOK_CONFIG`가 가리키는 파일 또는 같은 폴더의 config.json을 읽습니다. day1-day8용 PG 환경변수 로더가 day11에도 자동 적용되는 것은 아닙니다.

**⭐ 중요: `.gitignore`는 이미 Git이 추적하는 파일의 기록을 지워 주지 않습니다.** 비밀정보를 제외했는지 확인하는 명령은 다음과 같습니다.

```bash
git check-ignore day1-day8/config.json
git ls-files day1-day8/config.json
```

첫 명령은 제외 경로를 보여 주고, 두 번째는 추적 여부를 보여 줍니다. 공개한 실제 비밀번호는 새 값으로 변경해야 합니다.

### 🧪 실제 DB 없이 설정만 검사하기

`day1-day8/test_db_config.py`에서 다음 네 상황을 검사합니다.

1. 로컬 파일을 읽고 환경변수 비밀번호로 덮어쓸 수 있는가?
2. 파일 없이 Render 환경변수만으로 연결 설정을 만들 수 있는가?
3. 필수 설정 누락을 명확하게 알려 주는가?
4. 잘못된 포트 오류 메시지에 비밀번호가 섞이지 않는가?

임시 파일과 `patch.dict()`로 테스트 환경을 만듭니다. DB에 접속하지 않는 설정 단위 테스트입니다. 이전 작업에서 이 네 검사는 통과했지만, 그것이 실제 DB 접속이나 배포 성공까지 보장하지는 않습니다.

### 설치했는데 VS Code에 경고 2개가 남는 이유

터미널의 `conda activate py313`은 그 셸의 실행 환경을 바꿉니다. Pylance는 VS Code에서 선택한 인터프리터를 기준으로 분석합니다. 서로 다를 수 있습니다.

```bash
python -c "import sys, psycopg; print(sys.executable); print(psycopg.__version__)"
```

설치된 환경은 확인한 뒤 VS Code의 `Python: Select Interpreter`에서도 같은 환경을 선택합니다. 경고 두 개는 `psycopg`, `psycopg.rows` import 탐색 실패였습니다. 코드 옆 숫자는 문제 개수이지 실행 횟수가 아닙니다.

### 실행 위치·설치 버전·배포

```bash
# 프로젝트 루트에서 실행하는 예시
cd day11/day11-supabase/guestbook
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

`requirements.txt`, `main.py`가 없는 부모 폴더에서 실행하면 파일 없음 또는 `Could not import module "main"`이 발생합니다. `python -m pip`는 현재 Python에 연결된 pip를 사용합니다.

`psycopg[binary]==3.2.10`에서 `[binary]`는 설치 옵션이고 `==3.2.10`은 버전 고정입니다. 버전 없이 설치할 수도 있지만 같은 배포 결과를 위해 검증한 버전을 고정할 수 있습니다. 이 숫자가 항상 최신이라는 뜻은 아닙니다.

Render에서 `day1-day8`을 배포할 때의 실습 설정:

```text
Root Directory: day1-day8
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

**⭐ 중요: Git Push와 배포 성공은 같은 뜻이 아닙니다.** 연결 브랜치·자동 배포 설정·빌드 로그·DB 환경변수·실제 서비스의 조회·작성·수정을 확인해야 합니다. 이전 스크립트는 시작 명령에 넣지 않습니다.

## 12. 보충: LM Studio 로컬 AI 연결 예제

`my_lmstudio.py`는 로컬 서버 `http://localhost:1235/v1`로 연결하고 모델 목록을 조회합니다. 이 주소의 포트는 이 실습의 설정이며 모든 환경에서 같지는 않습니다. 코드의 `api_key="lm-studio"`는 로컬 서버 예제 값으로, Supabase 비밀번호와 다른 항목입니다.

현재 실행되는 부분은 모델 목록 조회와 모델 ID 출력입니다. 반복 채팅 코드는 **주석 상태**입니다.

주석 예제에서 기억할 점:

- `messages`는 system·user·assistant 역할별 대화 기록입니다.
- user 메시지를 추가하고, 받은 답변을 assistant 메시지로 저장하면 대화 맥락을 만들 수 있습니다.
- 그런데 현재 주석의 요청 코드는 저장한 `messages` 대신 고정된 인사 메시지를 보냅니다. 주석만 풀어도 대화 기록이 자동으로 모델에 전달되는 것은 아닙니다.
- 모델 목록이 비어 있지 않아도 하드코딩한 모델 ID가 실제 사용 가능한지는 별도 확인해야 합니다.
- 빈 입력, 종료 명령, 답변 없음, 서버 오류를 각각 처리하는 흐름을 배울 수 있습니다.

## 13. 복습 확인 문제

1. `CREATE SCHEMA ch2` 다음에 `CREATE TABLE users`를 실행하면 반드시 ch2에 생길까?
2. `VALUES(%, %)`는 무엇으로 고쳐야 할까?
3. 값 한 개를 전달할 때 `(email,)`의 쉼표는 왜 필요할까?
4. `dict_row`로 연결한 뒤 `.fetchone()[0]`를 유지해도 될까?
5. 블록 안에서 “저장 완료”를 출력했다면 최종 커밋도 보장될까?
6. 같은 `entries`인데 Supabase에서 글이 안 보이면 무엇부터 확인할까?
7. SQLite 데이터를 복사한 뒤 ID 순번을 조정하는 이유는?
8. 패키지가 설치됐는데 Pylance가 못 찾는다면 무엇을 비교할까?
9. DB 이전 후 기존 `tmp_path` 테스트는 자동으로 안전할까?
10. SQL 값 바인딩과 HTML 이스케이프는 같은 보호 기능일까?

### 답

1. 아니요. 이름을 생략하면 search_path에 따라 결정됩니다. `ch2.users`로 명시합니다.
2. `VALUES(%s, %s)`로 고칩니다.
3. 원소 한 개인 튜플로 만들기 위해서입니다.
4. 아니요. `COUNT(*) AS total`과 `["total"]`처럼 열 이름으로 읽습니다.
5. 아니요. 같은 트랜잭션에서 뒤의 예외로 롤백될 수 있습니다.
6. 접속 프로젝트·DB와 스키마를 확인합니다. `public.entries`와 `guestbook.entries`는 다릅니다.
7. 직접 복사한 ID와 이후 자동 발급 ID가 겹치지 않게 하기 위해서입니다.
8. 터미널의 `sys.executable`과 VS Code에서 선택한 인터프리터를 비교합니다.
9. 아니요. 현재 connect()가 그 경로를 무시하므로 별도 테스트 DB로 격리해야 합니다.
10. 아니요. SQL 바인딩은 DB 명령과 값을 분리하고, HTML 이스케이프는 화면에서 태그 실행을 막습니다.

## 꼭 기억할 7가지

- **⭐ 스키마와 테이블을 구분하고 SQL에서 같은 전체 이름을 사용한다.**
- **⭐ psycopg 값은 `%s`와 별도 인자로 전달한다.**
- **⭐ 트랜잭션은 정상 종료 시 커밋, 예외 시 롤백한다.**
- **⭐ DB 전환은 연결·SQL·반환 자료형·ID·테스트를 함께 바꾸는 작업이다.**
- **⭐ 원본 보존·복사 검증·자동 ID 조정을 확인한 뒤 이전을 마친다.**
- **⭐ 비밀번호는 소스에 올리지 않고 배포 환경에서 별도로 설정한다.**
- **⭐ 테스트는 실제 사용자 데이터와 분리하고, 실행·배포 성공을 실제 동작으로 확인한다.**
