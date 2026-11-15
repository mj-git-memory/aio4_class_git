# Day 10 복습 정리 — Python과 SQLite

이 문서는 `lesson_01`~`lesson_08`의 `main.py`, `solution.py`, 직접 작성한 `main1.py`·`main2.py`·`main3.py`, 그리고 대화에서 질문했던 내용을 바탕으로 정리했다. 마지막에는 `demo_pythonanywhere`에서 기초 개념이 어떻게 활용되는지도 연결했다.

`main.py`에는 실습용 버그나 작성 중인 코드가 있으므로, 올바른 동작은 `solution.py`와 비교해서 이해하자. 아래 SQL은 별도 표시가 없으면 원본 실습의 `users` 테이블 기준이다. 직접 작성한 파일에서는 `users2`, `users3`처럼 이름이 다를 수 있다.

## 목차

1. [꼭 기억할 핵심 개념](#1-꼭-기억할-핵심-개념)
2. [DB와 SQL 기본](#2-db와-sql-기본)
3. [조회 결과와 함수 반환](#3-조회-결과와-함수-반환)
4. [저장 확정과 트랜잭션](#4-저장-확정과-트랜잭션)
5. [조회 조건과 LIMIT 0](#5-조회-조건과-limit-0)
6. [수정·삭제와 rowcount](#6-수정삭제와-rowcount)
7. [오류 처리와 raise](#7-오류-처리와-raise)
8. [제약 조건과 None·0의 차이](#8-제약-조건과-none0의-차이)
9. [테이블 관계와 외래키](#9-테이블-관계와-외래키)
10. [JOIN과 개수 세기](#10-join과-개수-세기)
11. [대화 이력과 사용자 권한](#11-대화-이력과-사용자-권한)
12. [argparse와 실행 옵션](#12-argparse와-실행-옵션)
13. [파일 경로와 임시 폴더](#13-파일-경로와-임시-폴더)
14. [종료 코드](#14-종료-코드)
15. [실습별 찾아보기와 확인 방법](#15-실습별-찾아보기와-확인-방법)
16. [스스로 확인하기](#16-스스로-확인하기)

## 1. 꼭 기억할 핵심 개념

| 개념 | 기억할 문장 |
|---|---|
| Python 리스트와 DB 파일 | 리스트는 실행 중 메모리의 값이고, DB는 확정한 데이터를 파일에 남긴다. |
| `return` | 함수의 결과를 호출한 곳에 전달한다. DB 저장 명령이 아니다. |
| `commit()` | 지금까지의 DB 변경을 확정한다. |
| `rollback()` | 아직 확정하지 않은 DB 변경을 취소한다. 이미 commit한 변경은 취소하지 못한다. |
| `close()` | 연결을 닫는다. 이 실습의 `autocommit=False`에서는 자동 저장하지 않는다. |
| 트랜잭션 | 함께 성공하거나 함께 취소해야 하는 작업의 묶음이다. |
| `?`와 매개변수 | SQL과 입력값을 분리해서 전달한다. |
| `0`과 `None` | 0은 유효한 숫자이고, None은 값이 없음을 나타낸다. |
| 제약 조건 | 잘못된 데이터가 DB에 들어오지 못하게 하는 규칙이다. |
| 외래키 | 다른 테이블의 실제 행을 참조하도록 하는 규칙이다. |
| 접근 제한 | 데이터가 존재하는지뿐 아니라 요청한 사용자의 것인지도 확인한다. |

이 문서의 `autocommit` 인자를 쓰는 실습은 **Python 3.12 이상**이 필요하다.

## 2. DB와 SQL 기본

참조: [lesson_01/solution.py](lesson_01/solution.py)

### DB 파일, 테이블, 행, 열

DB 파일을 여러 명단을 보관하는 파일이라고 생각해 보자.

- DB 파일: `practice.db`
- 테이블: `users`라는 사용자 명단
- 행: 사용자 한 명의 정보
- 열: `id`, `nickname` 같은 정보의 종류

| id | nickname |
|---|---|
| 1 | 민지 |
| 2 | 준호 |

SQLite는 별도 DB 서버 없이 파일을 사용한다. `sqlite3`는 Python에서 SQLite를 다루는 표준 라이브러리다.

### 연결 만들기

```python
connection = sqlite3.connect(db_path, autocommit=False)
```

`db_path`의 DB 파일을 열고 연결 객체를 만든다. 파일이 없으면 만들지만, 파일을 넣을 부모 폴더까지 자동으로 만들지는 않는다.

`autocommit=False`는 저장 확정을 직접 관리하겠다는 뜻이다.

### CRUD: 추가·조회·수정·삭제

| 동작 | SQL | 예시 |
|---|---|---|
| 추가(Create) | `INSERT` | 사용자 등록 |
| 조회(Read) | `SELECT` | 사용자 목록 보기 |
| 수정(Update) | `UPDATE` | 점수 변경 |
| 삭제(Delete) | `DELETE` | 사용자 삭제 |

`CREATE TABLE`은 데이터를 담을 테이블 자체를 만드는 명령이다.

```python
connection.execute(
    "CREATE TABLE IF NOT EXISTS users ("
    "id INTEGER PRIMARY KEY, nickname TEXT NOT NULL)"
)
```

`IF NOT EXISTS`는 테이블이 이미 있으면 다시 만들지 않는다는 뜻이다. 기존 테이블의 구조를 고쳐주는 기능은 아니다.

### execute, executemany, executescript

| 메서드 | 용도 |
|---|---|
| `execute(sql, parameters)` | SQL 문 하나 실행 |
| `executemany(sql, records)` | 여러 데이터에 같은 SQL 반복 실행 |
| `executescript(script)` | 여러 SQL 문으로 된 스크립트 실행. 실습에서는 테이블 여러 개 준비에 사용 |

```python
connection.execute(
    "INSERT INTO users (nickname) VALUES (?)", ("민지",)
)

connection.executemany(
    "INSERT INTO users (nickname) VALUES (?)",
    [("준호",), ("수아",)],
)
```

### 왜 ?와 (nickname,)을 쓸까?

```python
connection.execute(
    "INSERT INTO users (nickname) VALUES (?)", (nickname,)
)
```

`?`에는 뒤에 전달한 값이 들어간다. SQL 문법과 값을 분리하므로 `O'Neil`처럼 따옴표가 있는 이름도 처리할 수 있다. 입력값을 SQL 문자열에 직접 이어 붙이는 방식은 피한다.

```python
(nickname)    # 단순히 괄호로 감싼 값
(nickname,)  # 값이 하나인 튜플
```

튜플 하나를 만들 때는 쉼표가 필요하다. `?`가 두 개면 값도 순서에 맞게 두 개 전달한다.

```python
connection.execute(
    "UPDATE users SET points = ? WHERE id = ?", (90, 1)
)
# 첫 번째 ? = 90, 두 번째 ? = 1
```

## 3. 조회 결과와 함수 반환

참조: [lesson_01/solution.py](lesson_01/solution.py)

### rows에는 무엇이 들어갈까?

```python
rows = connection.execute(
    "SELECT id, nickname FROM users ORDER BY id"
).fetchall()
```

실행 과정을 나누면 다음과 같다.

```python
cursor = connection.execute("SELECT id, nickname FROM users ORDER BY id")
rows = cursor.fetchall()
```

`execute()`가 반환하는 것은 **커서 객체**다. `fetchall()`이 조회한 행을 Python 값으로 가져온다.

```python
rows = [(1, "민지"), (2, "준호")]
```

- 바깥 `[]`: 여러 행을 담는 리스트
- 안쪽 `(1, "민지")`: 한 행의 값을 담는 튜플
- 조회한 행이 없으면: `[]`

기본 실습에서는 튜플로 가져온다. 뒤의 웹 데모처럼 `row_factory`를 설정하면 행 표현이 달라질 수 있다.

### return은 무엇을 할까?

```python
def read_users(db_path):
    # 연결과 조회 과정은 생략
    return rows

result = read_users(db_path)
```

`return rows`는 `rows`의 값을 호출한 곳에 전달한다. 따라서 반환된 목록이 `result`에 들어간다.

실제 실습처럼 다음과 같이 쓰면 반환한 목록을 바로 출력한다.

```python
print(read_users(db_path))
```

`return`은 DB에 쓰는 명령이 아니다. `return`이 없는 함수는 정상 종료 시 `None`을 반환한다. `prepare_database()`는 데이터를 준비하는 일을 하고 별도 결과를 반환하지 않는 예다.

### fetchall과 fetchone

| 메서드 | 기본 반환 형태 |
|---|---|
| `fetchall()` | 모든 남은 행의 리스트. 없으면 `[]` |
| `fetchone()` | 다음 한 행의 튜플. 없으면 `None` |

```python
owner = connection.execute(
    "SELECT id FROM conversations WHERE id = ? AND user_id = ?", (1, 1)
).fetchone()
# 조건에 맞으면 (1,), 없으면 None
```

## 4. 저장 확정과 트랜잭션

참조: [lesson_01/solution.py](lesson_01/solution.py), [lesson_03/solution.py](lesson_03/solution.py)

### 같은 연결에서는 보이는데, 왜 다시 열면 없을까?

새 DB에서 다음 작업을 한다고 가정하자. 테이블 준비는 이미 확정한 상태다.

```python
connection.execute("INSERT INTO users (nickname) VALUES (?)", ("민지",))
rows = connection.execute("SELECT id, nickname FROM users").fetchall()
# rows는 [(1, "민지")]
```

아직 `commit()`하지 않아도 **작업한 연결 안에서는 자신의 변경이 보인다.**

하지만 이 설정에서 저장 확정 없이 연결을 닫으면 추가 내용은 취소된다. Python 리스트로 이미 가져온 `rows`는 DB 변경 취소와 별개로 그 값을 가지고 있다.

| 순서 | Python에서 가져온 rows | 새 연결로 조회한 DB |
|---|---|---|
| 추가 → 조회 → commit 없이 닫기 | `[(1, "민지")]` | `[]` |
| 추가 → 조회 → commit → 닫기 | `[(1, "민지")]` | `[(1, "민지")]` |

다른 연결에서 확인할 때는 기존 조회를 계속하는 것이 아니라, 실습의 `read_users()`처럼 **새 연결을 만들어 조회**한다.

```python
connection.commit()  # DB 변경 확정
return rows          # Python 값을 호출한 곳에 전달
```

### commit, rollback, close 구분

| 명령 | 의미 | 기억할 점 |
|---|---|---|
| `commit()` | DB 변경 확정 | 그 뒤의 rollback으로 되돌릴 수 없음 |
| `rollback()` | 현재 미확정 변경 취소 | Python 변수나 출력까지 되돌리는 것은 아님 |
| `close()` | DB 연결 종료 | `autocommit=False`에서 미확정 변경은 취소됨 |

### 수정과 삭제를 한 묶음으로 처리하기

요구 사항: 민지의 점수를 수정하고 수아를 삭제하되, 하나라도 실패하면 둘 다 취소한다.

문제가 있는 흐름:

```text
민지 점수 수정 → commit → 삭제 실패 → rollback
```

점수 수정은 이미 확정했기 때문에 남는다.

올바른 흐름:

```text
민지 점수 수정 → 삭제 성공 → commit
                  삭제 실패 → rollback으로 수정도 취소
```

작업 중간의 `commit()`을 없애고 마지막에 한 번만 호출하는 것이 `lesson_03/solution.py`의 핵심이다.

## 5. 조회 조건과 LIMIT 0

참조: [lesson_02/solution.py](lesson_02/solution.py), [lesson_02/main2.py](lesson_02/main2.py)

```sql
SELECT id, nickname, city, points FROM users
WHERE city = ?
ORDER BY points DESC, id ASC
LIMIT ?
```

| 문법 | 의미 |
|---|---|
| `WHERE city = ?` | 지정한 도시의 사용자만 선택 |
| `ORDER BY points DESC` | 점수가 높은 순서 |
| `id ASC` | 점수가 같으면 번호가 작은 순서 |
| `LIMIT ?` | 최대 조회 행 수 |

서울 사용자 중 2명을 조회하면 수아와 하린이 나온다. 둘 다 95점이므로 id가 3인 수아가 id가 5인 하린보다 먼저 나온다.

```python
[(3, "수아", "서울", 95), (5, "하린", "서울", 95)]
```

### return limit or 2의 문제

```python
return limit or 2
```

Python에서 `0`은 거짓으로 취급되므로 `limit=0`을 넣으면 `2`가 반환된다.

| 입력 | 위 코드의 결과 | 원하는 결과 |
|---|---|---|
| `3` | `3` | `3` |
| `0` | `2` | `0` |

SQL의 `LIMIT 0`은 아무 행도 가져오지 않는다는 뜻이다. 유효한 0을 기본값으로 바꾸면 안 된다.

```python
def normalize_limit(limit):
    if limit < 0:
        raise ValueError("limit은 0 이상이어야 합니다.")
    return limit
```

이 실습에서는 기본값 2를 `argparse`에서 이미 정한다.

`INSERT OR IGNORE`도 기억하자. 같은 id가 있어서 추가할 수 없는 행 등을 건너뛰며, 기존 행의 정보를 갱신하지는 않는다. 모든 DB 오류를 무시하는 명령은 아니다.

## 6. 수정·삭제와 rowcount

참조: [lesson_03/solution.py](lesson_03/solution.py), [lesson_03/main3.py](lesson_03/main3.py)

### apply_changes는 무엇을 할까?

```python
counts = apply_changes(db_path, 1, 90, 3)
```

이는 다음 요청이다.

1. `db_path`의 DB를 연다.
2. id가 1인 사용자의 점수를 90으로 수정한다.
3. id가 3인 사용자를 삭제한다.
4. 둘 다 성공하면 확정하고 처리 행 수를 반환한다.
5. 실패하면 미확정 변경을 취소하고 오류를 전달한다.
6. 성공 여부와 관계없이 연결을 닫는다.

### rowcount는 내장 함수일까?

아니다. **커서 객체의 속성**이다.

```python
updated = connection.execute(
    "UPDATE users SET points = ? WHERE id = ?", (90, 1)
)
print(updated.rowcount)
```

- 조건에 맞는 행 1개를 처리했으면 `1`
- 조건에 맞는 행이 없으면 `0`

값이 원래부터 90이었는지와 관계없이 조건에 맞는 행을 처리할 수 있으므로, 반드시 '이전과 달라진 값의 개수'라는 뜻은 아니다.

| 표현 | 종류 | 사용 방식 |
|---|---|---|
| `len(rows)` | 내장 함수 | 괄호로 호출 |
| `connection.execute(...)` | 메서드 | 객체의 기능을 괄호로 호출 |
| `updated.rowcount` | 속성 | 괄호 없이 값을 읽음 |

`SELECT` 결과의 행 수를 알아낼 때는 `rowcount`를 쓰지 않는다. sqlite3의 SELECT에서는 보통 `-1`이다. 이미 가져온 목록은 `len(rows)`, SQL에서 직접 세려면 `COUNT(...)`를 쓴다.

### counts에 왜 (1, 1)이 들어갈까?

함수 마지막에 다음 코드가 있다.

```python
return updated.rowcount, deleted.rowcount
```

수정 1행, 삭제 1행이면 다음과 같다.

```python
return 1, 1
# return (1, 1)과 같은 의미
```

그 반환값을 호출한 곳에서 받는다.

```python
counts = apply_changes(db_path, 1, 90, 3)
# counts == (1, 1)
```

`(1, 1)`은 사용자 번호가 아니라 **수정한 행 수와 삭제한 행 수**다. 오류가 바깥으로 전달되면 이 호출은 정상 반환하지 않으므로 해당 대입도 완료되지 않는다.

## 7. 오류 처리와 raise

참조: [lesson_03/solution.py](lesson_03/solution.py)

```python
try:
    # 시도할 작업
    ...
except ValueError as exc:
    # ValueError가 발생했을 때
    print(exc)
else:
    # try 부분에서 오류가 없었을 때
    ...
finally:
    # 정상 종료·오류·return 여부와 관계없이 실행할 정리 작업
    ...
```

실습에서는 `finally`에서 `connection.close()`를 실행한다. `return`을 만나도 `finally`의 정리 작업은 실행된다.

### raise ValueError와 단독 raise

```python
raise ValueError("삭제 대상은 정확히 1명이어야 합니다.")
```

오류를 발생시킨다. 이어지는 정상 작업을 중단하고 해당 오류를 처리할 `except`를 찾는다.

```python
except (ValueError, sqlite3.Error):
    connection.rollback()
    raise
```

여기의 단독 `raise`는 **현재 처리 중인 오류를 바깥으로 다시 전달**한다.

- `rollback()`: DB 쪽의 미확정 변경 정리
- `raise`: 호출한 쪽에 '작업 실패' 알림

`rollback()`이 오류 메시지를 출력해 주는 것은 아니다.

### except ValueError as exc를 쉽게 읽기

```python
try:
    counts = apply_changes(db_path, 1, 90, 999)
    print(counts)
except ValueError as exc:
    print("오류:", exc)
```

'함수를 실행해 보고, ValueError가 오면 그 오류를 exc라는 이름으로 받아 출력하라'는 뜻이다.

`exc`는 마음대로 정할 수 있는 변수명이다. 오류 객체가 들어가고, `print(exc)`는 오류에 담긴 설명을 보여 준다.

```text
apply_changes 안에서 999번 사용자 삭제 실패
    ↓
ValueError 발생
    ↓
함수 안 except에서 rollback
    ↓
단독 raise로 바깥에 오류 전달
    ↓
호출한 곳의 except ValueError as exc가 받음
    ↓
오류: 삭제 대상은 정확히 1명이어야 합니다.
```

바깥 코드가 `ValueError`만 잡으면 `sqlite3.Error`까지 처리하지는 않는다. 잡히지 않은 오류는 더 바깥으로 전달되어 프로그램을 중단시킬 수 있다.

## 8. 제약 조건과 None·0의 차이

참조: [lesson_04/main.py](lesson_04/main.py), [lesson_04/solution.py](lesson_04/solution.py)

DB 제약 조건은 데이터가 지켜야 할 규칙이다.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    nickname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    points INTEGER NOT NULL CHECK(points BETWEEN 0 AND 100)
)
```

| 규칙 | 역할 | 거절되는 예 |
|---|---|---|
| `PRIMARY KEY` | 행을 구분하는 기본키 | 같은 id 중복 |
| `NOT NULL` | NULL 금지 | 이름이나 점수에 None 전달 |
| `UNIQUE` | 같은 값 중복 금지 | 이미 사용 중인 이메일 |
| `CHECK` | 조건을 만족하는지 검사 | 점수 -1, 101 |

`BETWEEN 0 AND 100`에는 양 끝값인 0과 100도 포함된다.

### CHECK만 쓰면 NULL도 막힐까?

```sql
points INTEGER CHECK(points BETWEEN 0 AND 100)
```

이 규칙만으로는 NULL 점수를 막지 못한다. NULL을 검사한 결과는 참·거짓과 다른 NULL이 될 수 있고, SQLite의 CHECK는 이 경우 행을 거절하지 않는다.

점수 필수 입력과 범위를 함께 보장하려면:

```sql
points INTEGER NOT NULL CHECK(points BETWEEN 0 AND 100)
```

### 현재 main.py의 if not points는 왜 문제일까?

```python
if not nickname or not email or not points:
    raise ValueError
```

`not points`는 `None`뿐 아니라 유효한 점수 `0`도 거절한다.

| 값 | 의미 | bool로 판단하면 |
|---|---|---|
| `None` | 값이 없음 | 거짓 |
| `0` | 숫자 0 | 거짓 |
| `""` | 빈 문자열 | 거짓 |
| `80` | 숫자 80 | 참 |

'점수가 없는가?'만 확인하려면:

```python
if points is None:
    raise ValueError("점수는 필수입니다.")
```

다만 `solution.py`에서는 이 문제를 DB의 `NOT NULL`과 `CHECK`로 보장한다. Python 입력 검사와 DB 제약 조건의 역할을 구분하자.

현재 `main.py`는 위 검사를 연결을 만든 뒤 `try`에 들어가기 전에 수행한다. 그 위치에서 오류가 나면 아래의 `finally`로 연결을 닫지 못한다. 입력 검사는 연결 생성 전에 하거나, 정리를 보장하는 `try` 안에 두어야 한다.

또한 `ValueError`는 `sqlite3.IntegrityError`와 다른 종류다. 현재 호출부처럼 `except sqlite3.IntegrityError`만 있으면 직접 발생시킨 `ValueError`는 잡지 못한다.

`NOT NULL`은 빈 문자열 `""`이나 공백만 있는 문자열까지 금지하지 않는다. 그런 요구 사항에는 별도 검사가 필요하다.

## 9. 테이블 관계와 외래키

참조: [lesson_05/solution.py](lesson_05/solution.py), [lesson_06/solution.py](lesson_06/solution.py)

### 사용자 → 대화방 → 메시지

```text
사용자 1명
 ├─ 대화방 A
 │   ├─ 메시지 1
 │   └─ 메시지 2
 └─ 대화방 B
     └─ 메시지 3
```

- 사용자 한 명은 대화방 여러 개를 가질 수 있다: 1:N
- 대화방 하나는 메시지 여러 개를 가질 수 있다: 1:N
- 각 행은 기본키 `id`로 구분한다.
- 다른 테이블을 가리키는 번호는 `user_id`, `conversation_id` 등에 저장한다.

### user_id에 UNIQUE를 붙이면?

```sql
user_id INTEGER NOT NULL UNIQUE
```

같은 사용자 번호를 대화방 테이블에 한 번만 넣을 수 있다. 민지가 두 번째 대화방을 만드는 순간 충돌한다.

사용자가 여러 대화방을 가질 수 있어야 한다면 `user_id`의 `UNIQUE`를 제거한다. 대화방 자체를 구분하는 기본키 `id`는 그대로 유지한다.

`lesson_05`는 관계와 UNIQUE 문제를 다루며, 실제 외래키 제약은 `lesson_06`에서 추가한다. 열 이름을 `user_id`로 짓는 것만으로 DB가 관계를 강제하지는 않는다.

### REFERENCES와 ON DELETE RESTRICT

```sql
user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT
```

- `REFERENCES users(id)`: 실제로 존재하는 사용자를 참조해야 한다.
- `ON DELETE RESTRICT`: 그 사용자를 참조하는 대화방이 있으면 사용자 삭제를 막는다.

```sql
conversation_id INTEGER NOT NULL
    REFERENCES conversations(id) ON DELETE RESTRICT
```

대화방 999가 없다면, 그 방에 속한 메시지를 추가할 수 없도록 한다. 부모가 없는 데이터를 흔히 '고아 데이터'라고 부른다.

### SQLite에서는 연결마다 외래키 검사를 켠다

실습의 수정 코드는 다음 순서를 사용한다.

```python
def connect_database(db_path):
    connection = sqlite3.connect(db_path, autocommit=True)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.autocommit = False
    return connection
```

`autocommit=False`로 시작하면 트랜잭션이 이미 열린다. SQLite에서는 트랜잭션 중에 `PRAGMA foreign_keys = ON`을 실행해도 설정 변경이 적용되지 않는다.

따라서 이 실습에서는 **트랜잭션 밖에서 외래키 검사를 켠 다음**, `autocommit=False`로 바꾼다. 새 연결을 만들 때마다 설정한다.

```python
enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
# 1이면 켜짐, 0이면 꺼짐
```

## 10. JOIN과 개수 세기

참조: [lesson_07/solution.py](lesson_07/solution.py)

### JOIN은 여러 테이블의 정보를 연결한다

대화방에는 사용자 번호가 있고, 사용자 테이블에는 이름이 있다. 이름까지 함께 보여 주려면 연결해서 조회한다.

```sql
FROM conversations AS c
JOIN users AS u ON u.id = c.user_id
```

- `AS c`, `AS u`: 테이블에 짧은 별명 붙이기
- `ON`: 어떤 값이 같은 행끼리 연결할지 지정
- `JOIN`: 여기서는 연결되는 상대 행이 있는 결과를 가져옴

### 메시지가 없는 방도 보여 주려면 LEFT JOIN

```sql
LEFT JOIN messages AS m ON m.conversation_id = c.id
```

왼쪽의 대화방은 유지한다. 연결되는 메시지가 없으면 메시지 쪽 열들은 NULL로 채워진다.

### COUNT(*)와 COUNT(m.id)의 차이

메시지가 없는 방도 LEFT JOIN 결과에는 한 행이 남는다.

| c.id | c.title | m.id |
|---|---|---|
| 10 | 빈 대화 | NULL |

- `COUNT(*)`: 결과 행 자체를 세므로 1
- `COUNT(m.id)`: NULL이 아닌 메시지 id를 세므로 0

따라서 메시지 수에는 다음을 사용한다.

```sql
COUNT(m.id) AS message_count
```

### GROUP BY는 방별로 묶는다

```sql
SELECT c.id, u.nickname, c.title, COUNT(m.id) AS message_count
FROM conversations AS c
JOIN users AS u ON u.id = c.user_id
LEFT JOIN messages AS m ON m.conversation_id = c.id
WHERE c.user_id = ?
GROUP BY c.id, u.nickname, c.title
ORDER BY c.id
```

사용자 1의 방을 조회한 수정본의 결과는 다음과 같다.

```python
[(10, "민지", "빈 대화", 0), (20, "민지", "파이썬", 2)]
```

## 11. 대화 이력과 사용자 권한

참조: [lesson_08/solution.py](lesson_08/solution.py)

### 쓰기와 읽기 모두 소유자 확인이 필요하다

대화방 번호가 존재한다고 해서 누구나 볼 수 있는 것은 아니다.

```sql
WHERE c.id = ? AND c.user_id = ?
```

'해당 방인가?'와 '요청한 사용자의 방인가?'를 함께 확인한다.

`main.py`의 `list_history()`는 `user_id`를 인자로 받지만 SQL에서 사용하지 않는다. 방 번호만 맞으면 다른 사람의 이력도 조회할 수 있다. `solution.py`는 사용자 조건을 추가한다.

```python
list_history(db_path, 1, 1)  # 민지가 자기 방 조회: 메시지 목록
list_history(db_path, 2, 1)  # 준호가 민지 방 조회: []
```

실제 웹 서비스에서는 이 사용자 번호를 임의의 요청값에 맡기지 않고 로그인한 사용자 정보에서 가져와야 한다. 실습은 권한 조건 자체를 연습한다.

### 질문과 답변을 함께 저장한다

`save_turn()`은 다음 일을 한다.

1. 해당 사용자의 대화방인지 확인한다.
2. 사용자 질문을 저장한다.
3. assistant 답변을 저장한다.
4. 둘 다 성공하면 한 번만 commit한다.
5. 하나라도 실패하면 rollback한다.

```python
return first.lastrowid, second.lastrowid
```

`lastrowid`는 INSERT로 추가한 행의 id를 확인하는 커서 속성이다.

- `rowcount`: 처리한 행의 수
- `lastrowid`: 추가한 행의 번호

### 메시지 내용도 검사한다

```sql
role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
content TEXT NOT NULL CHECK(length(trim(content)) > 0)
```

- role은 `user` 또는 `assistant`만 허용한다.
- 내용은 NULL을 금지한다.
- 빈 문자열과 보통의 공백만 있는 문자열도 거절한다.
- SQLite의 기본 `trim()`이 모든 종류의 공백 문자를 제거하는 것은 아니다.

답변이 빈 내용이라 두 번째 INSERT가 실패하면, 첫 번째 질문도 함께 취소되어야 한다. 이것도 트랜잭션의 활용이다.

## 12. argparse와 실행 옵션

참조: [lesson_02/solution.py](lesson_02/solution.py), [lesson_03/solution.py](lesson_03/solution.py)

### 터미널에서 값을 함께 전달하기

```bash
python main.py --city 서울 --limit 2
```

| 부분 | 의미 |
|---|---|
| `python main.py` | 파일 실행 |
| `--city` | 도시 옵션을 지정 |
| `서울` | 도시 옵션의 값 |
| `--limit 2` | 최대 조회 개수로 2를 전달 |

코드를 직접 바꾸지 않고 실행할 때마다 값을 바꾸기 위해 사용한다.

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--city", default="서울")
parser.add_argument("--limit", type=int, default=2)
args = parser.parse_args()

print(args.city)   # 서울
print(args.limit)  # 정수 2
```

- `import argparse`: 도구 가져오기. 이 줄만으로 입력을 읽지는 않는다.
- `ArgumentParser()`: 입력을 해석할 객체 만들기
- `add_argument()`: 받을 옵션과 기본값 등록하기
- `parse_args()`: 실제 터미널 입력 읽고 해석하기
- `type=int`: 입력값을 정수로 변환하기
- `default`: 옵션 생략 시 사용할 값

### parser는 무슨 뜻일까?

parser는 입력을 규칙에 따라 해석하는 것을 뜻한다. 여기서는 그런 일을 하는 객체에 붙인 변수 이름이다. Python 예약어가 아니므로 다른 변수명을 써도 된다.

```python
parser.add_argument("--update-id", type=int, default=1)
# 사용할 때는 args.update_id
```

옵션 이름의 `-`는 기본적으로 속성 이름에서 `_`로 바뀐다.

### if __name__ == "__main__"

```python
if __name__ == "__main__":
    ...
```

이 파일을 직접 실행했을 때만 안쪽 코드를 실행한다. 검사 코드가 `import main`으로 함수를 가져올 때는 실행 옵션 처리와 데모 실행이 자동으로 시작되지 않게 한다.

같은 이름의 함수를 두 번 정의하면 나중 정의가 앞의 이름을 덮어쓴다. 이전에 중복됐던 `read_users()`는 하나만 남기면 된다.

## 13. 파일 경로와 임시 폴더

참조: [lesson_04/main.py](lesson_04/main.py), [lesson_03/solution.py](lesson_03/solution.py)

### __file__, parent, with_name

예시 경로:

```python
path = Path("/day10/lesson_04/main.py")
```

| 표현 | 결과 | 의미 |
|---|---|---|
| `path.parent` | `/day10/lesson_04` | 파일이 들어 있는 폴더의 경로 |
| `path.parent / "constraints.db"` | `/day10/lesson_04/constraints.db` | 폴더 경로에 파일 이름 연결 |
| `path.with_name("constraints.db")` | `/day10/lesson_04/constraints.db` | 경로의 마지막 이름을 바꾼 새 경로 |

`__file__`은 현재 Python 파일의 경로다. 파일 옆에 DB를 두려면 다음 중 하나를 쓴다.

```python
db_path = Path(__file__).parent / "constraints.db"
# 또는
db_path = Path(__file__).with_name("constraints.db")
```

`parent`는 속성이라 괄호가 없고, `with_name()`은 메서드라 새 이름을 괄호 안에 전달한다.

**이 코드는 경로만 만든다. 실제 파일을 생성하거나 main.py의 이름을 변경하지 않는다.** 기존 `path` 값도 그대로다. 이후 `sqlite3.connect()`가 그 경로로 DB를 연다.

### unable to open database file 오류의 원인

```python
db_path = Path(__file__) / "constraints.db"
```

이렇게 쓰면 다음처럼 잘못된 경로가 만들어진다.

```text
/day10/lesson_04/main.py/constraints.db
```

`main.py`는 파일인데 폴더처럼 취급했기 때문이다. 위의 `parent`나 `with_name()`으로 고친다. 같은 오류는 부모 폴더가 없거나 쓰기 권한이 없을 때도 발생할 수 있다.

영구 DB를 쓰면서 `CREATE TABLE users ...`를 매번 실행하면 두 번째 실행에 `table users already exists` 오류가 날 수 있다. 새 DB를 쓰거나, 필요한 경우 `IF NOT EXISTS`를 사용한다. 기존 데이터를 무작정 삭제할 필요는 없다.

### 임시 폴더는 무엇일까?

```python
with TemporaryDirectory() as folder:
    db_path = Path(folder) / "practice.db"
    prepare_database(db_path)
    print(read_users(db_path))
```

운영체제의 임시 파일 위치에 실습용 폴더를 만들고, 그 경로 문자열을 `folder`에 넣는다. 경로는 실행마다 달라질 수 있다.

```text
운영체제의 임시 위치/
└─ 새 임시 폴더/
   └─ practice.db
```

- `TemporaryDirectory()`가 폴더를 만든다.
- `Path(folder) / "practice.db"`는 그 안의 DB 경로를 만든다.
- DB 준비 함수의 연결 작업이 DB 파일을 만든다.
- `with` 블록을 벗어나면 폴더와 내용물이 자동으로 정리된다.

임시 DB도 commit해야 재연결 시 데이터가 보인다. 다만 임시 폴더 정리 때 파일 자체가 삭제되므로 장기 보관용은 아니다.

## 14. 종료 코드

참조: [lesson_03/solution.py](lesson_03/solution.py), 각 실습의 `check.py`

```python
raise SystemExit(1 if failed else 0)
```

프로그램을 끝내면서 성공 여부를 운영체제·터미널·자동 실행 도구에 전달한다.

| 값 | 일반적인 의미 |
|---|---|
| `0` | 성공 |
| `0이 아닌 값` | 실패 또는 비정상 결과 |
| `1` | 일반적인 실패를 나타내는 데 자주 사용 |

1이 모든 프로그램에서 똑같은 오류를 뜻하지는 않는다. 구체적인 코드는 프로그램이 정한다.

```python
1 if failed else 0
```

는 `failed`가 True면 1, 아니면 0을 고르는 조건 표현식이다.

```python
raise SystemExit(0)  # 성공 코드로 종료
raise SystemExit(1)  # 실패 코드로 종료
```

`SystemExit`는 종료를 위한 특별한 예외다. 여기서는 잡는 코드가 없으므로 프로그램이 종료된다. `except` 안의 단독 `raise`가 '처리 중인 오류 다시 전달'인 것과 구분하자.

### 왜 종료 코드가 필요할까?

자동 실행 도구는 '오류가 났습니다'라는 문장을 분석하지 않고도, 숫자로 성공 여부를 판단할 수 있다.

```text
종료 코드 0 → 다음 작업 진행
종료 코드 1 → 실패 기록 또는 실행 중단
```

오류를 출력했다고 자동으로 실패 코드가 되는 것은 아니다. `except`에서 오류를 처리한 뒤 정상 종료하면 0이 될 수 있다. 그래서 실습에서는 `failed`로 실패 여부를 기억했다가 코드를 지정한다.

Mac 터미널에서 실행 직후 확인:

```bash
python main.py --delete-id 999
echo $?
```

`echo $?`는 바로 직전 명령의 종료 코드를 보여 준다.

## 15. 실습별 찾아보기와 확인 방법

### 실습별 핵심 문제

| 실습 | 핵심 개념 | main.py의 문제 또는 확인점 | 비교할 수정본 |
|---|---|---|---|
| 01 | 저장과 재연결 | INSERT 후 commit 누락 | [solution.py](lesson_01/solution.py) |
| 02 | WHERE·ORDER BY·LIMIT | `limit or 2`가 0을 2로 바꿈 | [solution.py](lesson_02/solution.py) |
| 03 | 트랜잭션 | 중간 commit 때문에 부분 수정이 남음 | [solution.py](lesson_03/solution.py) |
| 04 | NOT NULL·UNIQUE·CHECK | 점수 NOT NULL 누락, 작성한 검사에서 0과 None 혼동 | [solution.py](lesson_04/solution.py) |
| 05 | 1:N 관계 | user_id의 UNIQUE가 대화방 여러 개 생성을 막음 | [solution.py](lesson_05/solution.py) |
| 06 | 외래키 | 트랜잭션 안에서 foreign_keys 설정 변경 시도 | [solution.py](lesson_06/solution.py) |
| 07 | JOIN·GROUP BY·COUNT | COUNT(*)가 빈 대화방도 1개로 셈 | [solution.py](lesson_07/solution.py) |
| 08 | 소유자 확인·원자적 저장 | 이력 조회에 사용자 조건 누락 | [solution.py](lesson_08/solution.py) |

### 소스코드에서 자주 만나는 함수

| 이름 | 역할 |
|---|---|
| `prepare_database()` / `create_database()` | 테이블·초기 데이터 준비. 정확한 준비 범위는 각 파일마다 다름 |
| `save_user()` / `add_user()` | 사용자 추가 |
| `read_users()` | 사용자 목록 조회 |
| `normalize_limit()` | 조회 개수 확인 |
| `find_users()` | 도시·정렬·개수 조건으로 조회 |
| `apply_changes()` | 수정과 삭제 실행 |
| `connect_database()` | 외래키 설정 등을 포함한 공통 연결 생성 |
| `conversation_summary()` | 대화방별 메시지 수 조회 |
| `message_history()` / `list_history()` | 대화방 메시지 이력 조회 |
| `save_turn()` | 질문과 답변을 함께 저장 |

### 검사는 성공 예시만 보지 않는다

각 `check.py`는 임시 DB에서 데이터를 만들고 함수를 호출해 결과를 비교한다. 입력 경계값과 오류 뒤의 DB 상태까지 확인하는 것이 핵심이다.

| 기능 | 확인할 입력 |
|---|---|
| 이름 저장 | 일반 이름, `O'Neil`, None |
| 조회 개수 | 0, 1, 음수 |
| 수정·삭제 | 존재하는 번호, 없는 번호, 두 번째 작업 실패 |
| 점수 | None, -1, 0, 100, 101 |
| 관계 | 한 사용자의 대화방 2개, 없는 대화방을 참조하는 메시지 |
| 집계 | 메시지가 없는 대화방 |
| 권한 | 본인 방과 다른 사람 방 |

예를 들어 **lesson_03 폴더에서** 다음 명령을 실행하면 수정본을 검사한다.

```bash
python check.py solution
echo $?
```

같은 폴더에서 `python check.py main`은 원본 또는 현재 작업 중인 코드를 검사한다. 실습용 버그나 작성 중인 오류 때문에 실패할 수 있다. 이 복습 문서에 적은 출력 예시는 소스 흐름을 설명하기 위한 것이며, 전체 검사를 이번 문서 작성 중 새로 실행했다는 의미는 아니다.

### 웹 데모에서는 어떻게 이어질까?

추가 참조: [app/db.py](demo_pythonanywhere/app/db.py), [app/guestbook.py](demo_pythonanywhere/app/guestbook.py)

`demo_pythonanywhere`는 같은 개념을 Flask 방명록에 적용한 예다.

- `get_db()`: 웹 요청에서 사용할 연결을 가져온다.
- `close_db()`: 요청 처리 뒤 연결을 정리한다.
- `sqlite3.Row`: `row[0]` 대신 `row["nickname"]`처럼 열 이름으로도 접근하게 한다.
- JOIN: 글 목록에 작성자의 닉네임을 함께 가져온다.
- `WHERE id=? AND author_id=?`: 글 번호와 작성자 조건을 함께 사용한다.
- `with db:`: 해당 데모의 연결 설정에서 정상 종료 시 commit, 예외 시 rollback을 처리한다. 연결을 닫는 역할은 별도다.

이 데모의 `sqlite3.connect()`는 기초 실습의 `autocommit=False`를 명시한 코드와 연결 설정이 다르다. 외래키 설정 순서나 트랜잭션 코드를 그대로 섞지 말고, 각 연결의 설정과 사용 방식을 함께 확인하자.

## 16. 스스로 확인하기

먼저 답을 가리고 설명해 보자.

1. `rows`에 민지가 있는데 새 DB 연결에서는 왜 안 보일 수 있을까?
2. `return`과 `commit()`은 각각 무엇을 바꾸는가?
3. 중간에 commit한 수정은 왜 rollback으로 취소되지 않을까?
4. `(nickname,)`에는 왜 쉼표가 필요한가?
5. `limit or 2`와 `if not points`가 공통으로 놓치는 값은 무엇인가?
6. `updated.rowcount`와 `first.lastrowid`는 무엇이 다른가?
7. `raise ValueError(...)`, 단독 `raise`, `raise SystemExit(1)`은 각각 무엇을 하는가?
8. CHECK만으로 NULL 점수를 막을 수 있을까?
9. 한 사용자가 방 여러 개를 만들려면 `conversations.user_id`에 UNIQUE가 있어도 될까?
10. 메시지가 없는 방의 메시지 수는 왜 `COUNT(m.id)`로 세는가?
11. 방 번호만 확인하면 왜 다른 사람의 대화가 노출될 수 있을까?
12. `Path(__file__) / "test.db"`는 왜 잘못된 경로인가?

<details>
<summary>답 확인하기</summary>

1. 같은 연결은 자신의 미확정 변경도 볼 수 있지만, 저장 확정 없이 닫으면 해당 변경이 취소되기 때문이다.
2. return은 Python 값을 호출한 곳에 전달하고, commit은 DB 변경을 확정한다.
3. rollback은 현재 미확정 변경만 취소하기 때문이다.
4. 값 하나짜리 튜플을 만들기 위해 필요하다.
5. 유효한 숫자 0이다. 값 없음과 구분해야 한다.
6. rowcount는 처리한 행 수, lastrowid는 INSERT한 행의 id다.
7. 새 오류 발생 / 현재 오류 다시 전달 / 실패 종료 코드로 프로그램 종료다.
8. 아니다. NOT NULL도 함께 필요하다.
9. 안 된다. 같은 사용자의 두 번째 방이 거절된다.
10. LEFT JOIN의 빈 방 행은 남지만 m.id는 NULL이므로, NULL이 아닌 id만 세어야 0이 된다.
11. 요청자의 소유인지 확인하지 않았기 때문이다. 방 번호와 사용자 번호 조건을 함께 확인한다.
12. main.py 같은 파일을 폴더로 취급하기 때문이다. parent 또는 with_name()을 사용한다.

</details>
