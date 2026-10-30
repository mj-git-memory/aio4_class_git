# Day 12 핵심 정리 — FastAPI 요청에서 DB 저장까지

오늘의 핵심은 **사용자 등록·조회 API를 만들며 HTTP 요청 → 입력 검증 → Python 함수 → SQL 실행 → DB 저장·조회 → JSON 응답의 흐름을 이해하는 것**입니다.

`day12/main.py`, `lesson01.py`, `lesson01.md`의 수업 내용과 대화에서 질문한 내용을 바탕으로 정리했습니다. 쇼핑몰 구현과 ERD 관련 내용은 제외했습니다. 아래 예시는 개념 설명용이며, 이 문서를 작성하면서 서버나 Supabase를 실행 검증하지 않았습니다.

## 1. 먼저 전체 흐름을 기억하기

```text
Swagger에서 POST /users 요청 + JSON 전송
    ↓
Uvicorn이 HTTP 요청을 받아 FastAPI 앱에 전달
    ↓
앱에 연결된 라우팅 정보로 요청 메서드·경로에 맞는 함수 선택
    ↓
UserCreate가 요청 본문을 검증
    ├─ 실패 → 422 응답, create_user() 실행 안 함
    └─ 성공 → create_user(user, request) 실행
                  ↓
              psycopg로 PostgreSQL 접속
                  ↓
              INSERT + RETURNING
                  ↓
              정상 종료 시 COMMIT
                  ↓
              Python 딕셔너리 반환 → JSON 응답, 201
```

쉽게 생각하면 **요청은 주문서, 검증 모델은 주문서 검사, 함수는 작업 담당자, DB는 기록 보관소**입니다. Swagger는 이 과정을 시험하는 요청 도구입니다.

## 2. 앱·API·라우터·경로의 차이

| 개념 | 뜻 | 수업 코드 예시 |
|---|---|---|
| 앱 | 요청을 처리하는 전체 애플리케이션 | `app = FastAPI()` |
| API | 다른 프로그램이 기능을 사용하는 규칙과 접점 | POST로 사용자를 등록하고 GET으로 조회하는 약속 |
| 경로 | 서버 주소 안에서 대상을 구분하는 부분 | `/users` |
| 라우터 | 관련 요청 경로와 처리 함수를 묶어 등록하는 객체 | `router = APIRouter(...)` |
| Uvicorn | HTTP 요청을 받아 FastAPI 앱을 실행하는 서버 | `uvicorn.run(app, ...)` |

```text
http://127.0.0.1:8000/users
       └ 서버 주소 ─┘└ 경로 ┘
```

경로가 같아도 **HTTP 메서드가 다르면 다른 동작**입니다.

| 요청 | 동작 | 정상 응답 |
|---|---|---|
| POST /users | 사용자 생성 | 201 Created |
| GET /users | 사용자 목록 조회 | 200 OK |

### 질문: 변수를 app 대신 AA라고 해도 앱인가?

맞습니다. 객체의 역할은 변수 이름이 아니라 `FastAPI()`로 만든 객체라는 사실로 결정됩니다.

```python
AA = FastAPI()
AA.include_router(router)
```

이 객체를 Uvicorn 명령으로 지정한다면 `main:AA`처럼 실제 변수 이름을 사용해야 합니다. 단, 현재 수업 코드는 DB 초기화 위치 때문에 실행 명령을 별도로 주의해야 합니다. 5절을 참고하세요.

## 3. 경로 등록과 앱 연결은 다른 단계

```python
app = FastAPI()
router = APIRouter(tags=["users"])

# ① 요청 경로와 처리 함수를 router에 등록
@router.post("/users", status_code=201)
def create_user(...):
    ...

@router.get("/users")
def list_users(...):
    ...

# ② router에 등록된 경로들을 app에 연결
app.include_router(router)
```

`@...`는 데코레이터입니다. 여기서는 함수를 정의할 때 해당 함수를 특정 요청의 처리 함수로 등록합니다. 등록할 때 사용자 저장 함수 본문까지 실행하는 것은 아닙니다.

**`app.include_router(router)`에서 router에 경로를 등록하는 것이 아닙니다.** 이미 등록된 경로들을 앱에 포함합니다. 이 줄이 없어도 서버는 켜질 수 있지만, 다른 곳에서 같은 경로를 등록하지 않았다면 `/users`는 404입니다.

### tags는 경로가 아니라 문서 그룹 제목

```python
router = APIRouter(tags=["사용자 관리"])
```

Swagger의 `/docs` 화면에서 다음과 같은 그룹으로 보입니다.

```text
사용자 관리
  POST /users
  GET  /users
```

`tags`만 바꾸어도 URL은 바뀌지 않습니다.

## 4. 환경변수와 Python 환경

DB 접속 정보는 `.env`에서 읽어 사용했습니다.

```python
import os
from dotenv import load_dotenv

load_dotenv()  # .env를 읽어 환경변수에 반영
host = os.getenv("host")  # 환경변수에서 값 가져오기
```

**import는 도구를 가져오는 일이고, 함수 호출은 그 도구로 작업하는 일**입니다. `load_dotenv`를 import만 하면 파일을 읽지 않습니다.

`os.getenv("host")`에서 해당 환경변수를 찾지 못하면 기본적으로 `None`을 반환합니다. `host`·비밀번호가 없는 상태에서 DB 접속을 시도하면 의도한 Supabase가 아니라 로컬 소켓으로 접속하려다 실패할 수도 있습니다.

### 질문: 설치했는데 dotenv를 못 찾는 이유는?

패키지를 설치한 Python과 코드를 실행하는 Python이 다를 수 있습니다. 대화에서 `(py313)` 표시가 있어도 `python3` 명령은 macOS 기본 Python을 가리켰습니다.

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
python -m pip install python-dotenv
```

확인한 동일 Python으로 설치·실행하고, VS Code의 **Python: Select Interpreter**도 같은 환경으로 맞춥니다. 패키지 설치 이름은 `python-dotenv`, import 이름은 `dotenv`입니다.

수업의 `lesson01.py`에는 비밀번호를 출력하는 줄이 있습니다. 접속값을 확인하는 예제이지만 실제 비밀번호가 터미널·공유 화면에 노출될 수 있으므로 복습할 때는 값 대신 `os.getenv("password") is not None`처럼 설정 여부를 확인하세요.

## 5. 직접 실행과 import는 다르다

```python
if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 실행
    ...
```

| 명령 | main.py의 `__name__` | 위 블록 |
|---|---|---|
| `python main.py` | `"__main__"` | 실행 |
| `python -m uvicorn main:app` | `"main"` | 건너뜀 |

`main:app`은 **main 모듈을 import하고 그 안의 app 객체를 가져오라**는 뜻입니다. 개념적으로 `from main import app`과 비슷합니다. 함수 안에서도 import할 수 있으며, import 시 모듈 최상위 코드가 실행되지만 조건이 거짓인 `if __name__ ...` 안쪽은 실행하지 않습니다.

현재 수업 코드에서는 다음 작업이 직접 실행 블록 안에 있습니다.

```python
if __name__ == "__main__":
    db_config = {...}
    initialize_database(db_config)
    app.state.db_config = db_config
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

따라서 `python main.py`로 실행해야 이 DB 준비 작업을 거칩니다. Uvicorn이 import만 하면 설정을 저장하는 작업이 생략됩니다.

### 명령어 형식 읽기

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

| 부분 | 의미 |
|---|---|
| `python -m uvicorn` | 현재 Python 환경의 uvicorn 모듈 실행 |
| `main:app` | main.py의 app 객체 사용 |
| `--host 127.0.0.1` | 내 컴퓨터의 루프백 주소에서 접속 받기 |
| `--port 8000` | 8000번 포트 사용 |
| `--workers 1` | 서버 프로세스 1개 실행 |

worker 1개가 요청을 한 번에 무조건 1개만 처리한다는 뜻은 아닙니다.

**현재 소스 주의:** `main.py`의 직접 실행 블록 아래에는 `db.example.com`으로 접속하는 설명용 코드가 실제 실행문으로 남아 있습니다. import 시 그 코드도 실행되며, 직접 실행한 서버가 끝난 뒤에도 이어서 실행될 수 있습니다. 따라서 import 방식에서는 초기화 누락 외에 이 예시 접속에서 먼저 실패할 수도 있습니다. 이 문서에서는 소스를 수정하지 않았습니다.

## 6. 딕셔너리의 **는 키워드 인자로 풀어 전달

```python
db_config = {
    "host": "example-host",
    "port": "5432",
    "dbname": "postgres",
}

psycopg.connect(**db_config)
```

아래 호출과 같은 방식으로 인자가 전달됩니다. 예시에는 설명에 필요한 항목만 넣었습니다.

```python
psycopg.connect(
    host="example-host",
    port="5432",
    dbname="postgres",
)
```

`**`는 문자열을 출력하는 문법이 아닙니다. 딕셔너리의 키를 인자 이름, 값을 인자 값으로 전달합니다. `print(**db_config)`는 print가 host 같은 키워드 인자를 받지 않아 사용할 수 없습니다.

### app.state와 Request

```python
app.state.db_config = db_config
```

앱에 DB 접속 설정을 보관한 뒤 요청 처리 함수에서 접근합니다.

```python
def get_connection(request: Request):
    return psycopg.connect(
        **request.app.state.db_config,
        row_factory=dict_row,
    )
```

| 표현 | 의미 |
|---|---|
| request | 현재 HTTP 요청 |
| request.app | 요청을 처리하는 앱 |
| request.app.state | 앱에서 공유할 값을 보관하는 공간 |
| request.app.state.db_config | 앞서 저장한 DB 접속 설정 |

접속 설정을 보관하는 것이지, 여기서 DB 연결 하나를 영구 공유하는 것은 아닙니다. `get_connection()`은 호출할 때 새 연결을 만듭니다. state는 프로세스 메모리이므로 서버 재시작 후에도 남는 DB 데이터와는 다릅니다.

## 7. Pydantic 모델은 요청의 모양과 값을 검사

```python
class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=100)
```

| 코드 | 검사·설정 |
|---|---|
| BaseModel 상속 | 요청 데이터를 검증할 모델 정의 |
| `name: str` | 이름을 문자열 필드로 정의 |
| `Field(...)` | 길이 등 필드 조건 지정 |
| `EmailStr` | 이메일 형식 검사. email-validator 패키지 필요 |
| `str_strip_whitespace=True` | 문자열 앞뒤 공백 제거 설정 |
| `extra="forbid"` | name·email 외 추가 필드 거부 |

```python
def create_user(user: UserCreate, request: Request):
    ...
```

FastAPI는 JSON 본문을 UserCreate로 검증한 뒤 `user`에 전달합니다. JSON의 키가 필드에 대응하므로 JSON에 email을 먼저 쓴다고 이름·이메일이 뒤바뀌지는 않습니다.

**EmailStr는 실제 메일함 존재 여부나 소유권을 확인하지 않습니다.** 형식 검사입니다. 또한 요청 모델은 DB 테이블이 아니며, 모델을 정의했다고 DB에 테이블이 자동 생성되지는 않습니다.

## 8. validator·classmethod·isinstance 이해하기

밸리데이터는 데이터가 정해진 조건에 맞는지 검사하는 함수입니다.

```python
@field_validator("name", mode="before")
@classmethod
def validate_name(cls, value: str) -> str:
    if not isinstance(value, str):
        return value
    if re.fullmatch(r"[가-힣ㄱ-ㅎㅏ-ㅣA-Za-z]+", value) is None:
        raise ValueError("이름에는 공백 없이 한글과 영문만 사용할 수 있습니다.")
    return value
```

| 코드 | 기능 |
|---|---|
| `@field_validator("name", ...)` | name 검증 과정에 이 함수를 등록 |
| `mode="before"` | 기본 필드 검증·자동 공백 제거 전에 원래 입력 검사 |
| `@classmethod` | 클래스 자체를 첫 인자로 받는 메서드로 만듦 |
| `cls` | UserCreate 클래스. 현재 함수에서는 직접 사용하지 않음 |
| `value` | 전달받은 입력값 |
| `-> str` | 문자열 반환을 의도한다는 타입 표시 |
| `raise ValueError(...)` | 검증 실패 알림. 요청 검증에서는 422로 이어짐 |
| `return value` | 값을 다음 검증 단계로 전달 |

`@classmethod` 자체가 검증하는 것은 아닙니다. 함수 안의 조건문이 검사하고, `@field_validator`가 Pydantic의 검증 과정에 연결합니다.

### isinstance와 not

```python
isinstance("김하늘", str)  # True
isinstance(123, str)       # False
isinstance(123, int)       # True
isinstance("123", int)     # False: 숫자 모양의 문자열
```

`if not isinstance(value, str):`는 **문자열이 아니라면**이라는 뜻입니다. 문자열이 아닌 값을 반환하는 이유는 허용하려는 것이 아니라 정규식 처리를 건너뛰고 이후 Pydantic의 str 검증에 맡기기 위해서입니다. before 함수에서 반환해도 전체 검증이 끝난 것은 아닙니다.

`value: str` 타입 표시만으로 함수에 다른 타입이 들어오는 것을 막지는 않습니다. before 검증에는 아직 변환·검사되지 않은 원래 입력이 들어올 수 있습니다.

### 공백 제거와 공백 금지는 다르다

- 공백 제거 후 검사: `" 김하늘 "`이 `"김하늘"`로 바뀌어 통과할 수 있습니다.
- 제거 전 검사: 원래 공백을 발견하고 거부할 수 있습니다.

이름에 공백 자체를 금지하려고 `mode="before"`를 사용했습니다.

### 정규식 형식 읽기

```python
re.fullmatch(r"[가-힣ㄱ-ㅎㅏ-ㅣA-Za-z]+", value)
```

| 표현 | 의미 |
|---|---|
| `r"..."` | 역슬래시 등을 다루기 편한 원시 문자열 표기 |
| `[...]` | 안에 지정한 문자 중 하나 |
| `가-힣` | 완성된 한글 글자 |
| `ㄱ-ㅎ`, `ㅏ-ㅣ` | 한글 자음·모음 |
| `A-Z`, `a-z` | 영문 대문자·소문자 |
| `+` | 앞의 허용 문자가 1개 이상 |
| `fullmatch` | 일부가 아니라 입력 전체가 규칙에 맞는지 검사 |
| `is None` | 일치 결과가 없음 |

통과 예: `김하늘`, `Hana`, `김Hana`. 거부 예: `김 하늘`, ` 김하늘`, `김1`, `김@`, 이모지, 빈 문자열.

현재 패턴은 `ㅋㅋ` 같은 자음만의 입력도 통과합니다. 허용 문자 검사와 실제 사람 이름인지 판단하는 것은 다른 문제입니다.

## 9. SQL 열 순서와 값 순서는 반드시 일치

오늘의 중요한 오류는 **201인데 이름과 이메일이 뒤바뀌는 문제**였습니다.

```python
conn.execute(
    """
    INSERT INTO kdt_api01.users (name, email)
    VALUES (%s, %s)
    RETURNING id, name, email;
    """,
    (user.name, user.email),
)
```

| SQL 위치 | 대상 열 | 전달해야 할 값 |
|---|---|---|
| 첫 번째 %s | name | user.name |
| 두 번째 %s | email | user.email |

`(user.email, user.name)`으로 전달하면 잘못된 열에 저장합니다. psycopg는 변수 이름을 보고 열을 찾아주지 않고 **위치대로** 값을 연결합니다.

두 값이 문자열이고 DB 열도 모두 `TEXT NOT NULL`이라면 DB가 의미상 뒤바뀜을 감지하지 못합니다. EmailStr를 추가했어도 검증 통과 후 튜플을 만드는 코드가 뒤집으면 막지 못합니다.

**따라서 상태 코드만 보지 말고 POST 응답과 GET 재조회에서 값까지 확인해야 합니다.** 응답 키만 바꾸면 DB의 잘못된 저장은 그대로 남습니다. 코드 수정도 기존 잘못된 행을 자동 복구하지는 않습니다.

`%s`는 값의 자리 표시자입니다. SQL에 값을 f-string으로 끼우지 않고 별도의 튜플로 전달합니다. `%s`를 따옴표로 감싸지 않습니다.

## 10. RETURNING·dict_row·fetchone·fetchall

```sql
RETURNING id, name, email;
```

INSERT한 행의 실제 값을 바로 돌려받습니다. 자동 생성된 id도 받을 수 있습니다. RETURNING 자체가 commit을 의미하지는 않습니다.

```python
row_factory=dict_row
```

각 행을 튜플 대신 딕셔너리로 받는 설정입니다.

```python
# 기본 행 예시
(1, "김하늘", "hana@example.com")

# dict_row 사용 시
{"id": 1, "name": "김하늘", "email": "hana@example.com"}
```

| 코드 | 결과 |
|---|---|
| `.fetchone()` | 다음 행 하나. 없으면 None |
| `.fetchall()` | 남은 행 목록. 없으면 빈 리스트 |

GET에서는 다음 SQL로 실제 저장된 내용을 읽습니다.

```sql
SELECT id, name, email
FROM kdt_api01.users
ORDER BY id;
```

`ORDER BY id`는 id 기준으로 정렬합니다. FastAPI는 반환된 딕셔너리를 JSON 객체로, 리스트를 JSON 배열로 응답합니다.

## 11. with와 트랜잭션 — 실행과 저장 확정 구분

```python
with get_connection(request) as conn:
    row = conn.execute(sql, values).fetchone()

return row
```

현재 수업처럼 psycopg 연결 컨텍스트를 사용하면:

- with 블록 정상 종료 → COMMIT으로 확정하고 연결 종료
- 블록에서 예외 발생 → ROLLBACK으로 되돌리고 연결 종료

`return row`를 밖에 두어 commit 완료 후 응답합니다. `execute()`가 호출됐다는 사실만으로 영구 저장 완료라고 판단하면 안 됩니다.

정상 확정한 데이터는 Python 메모리가 아닌 Supabase PostgreSQL에 있으므로 FastAPI 서버를 재시작해도 남습니다.

## 12. 수업 코드에서 각 함수가 맡은 일

| 함수 | 실행 시점 | 역할 |
|---|---|---|
| initialize_database(db_config) | 직접 실행 블록에서 서버 시작 전 | kdt_api01 스키마와 users 테이블 준비 |
| get_connection(request) | API 함수에서 호출 | 앱에 보관한 설정으로 DB 연결 생성 |
| create_user(user, request) | POST /users, 요청 검증 통과 후 | INSERT하고 생성 행 반환 |
| list_users(request) | GET /users | 저장된 사용자 목록 SELECT |
| validate_name(cls, value) | 이름 필드의 기본 검증 전 | 허용 문자 검사 |

`CREATE ... IF NOT EXISTS`는 없으면 생성하고 있으면 건너뜁니다. 이미 있는 테이블을 새 모델에 맞게 자동 변경하지는 않습니다. `id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`는 DB가 번호를 자동 생성하고 행을 유일하게 구분하도록 합니다.

## 13. 꼭 기억할 검증 예시

아래는 직접 확인할 때의 기준이며, 이 문서에서 실행한 결과가 아닙니다.

| 요청 | 기대 결과 | 확인할 내용 |
|---|---|---|
| POST: 정상 이름·이메일 | 201 | 반환 필드 값과 생성 id |
| GET /users | 200 | 같은 id의 값이 POST와 일치 |
| POST: 이름이 공백 | 422 | 새 행 없음 |
| POST: 이름에 @·숫자·중간/앞뒤 공백 | 422 | 처리 함수 실행 전에 거부 |
| POST: 이메일 형식 오류 | 422 | 같은 문자열이라는 이유로 통과하지 않음 |
| POST: name 또는 email 누락 | 422 | 필수 입력 검사 |
| POST: 정의하지 않은 추가 필드 | 422 | extra=forbid 적용 |

오류를 추적할 때는 다음 순서로 봅니다.

```text
JSON 키와 값
 → 모델의 user.name / user.email
 → SQL의 열 순서
 → %s에 대응하는 튜플 순서
 → RETURNING 결과
 → COMMIT
 → GET 재조회
```

## 14. 복습할 때 스스로 답할 질문

1. `@router.post(...)`와 `app.include_router(router)`의 차이는?
2. `app`을 AA로 바꿔도 앱인 이유는?
3. load_dotenv를 import만 하면 안 되는 이유는?
4. `python main.py`와 `uvicorn main:app`의 초기화 차이는?
5. `**db_config`와 `(user.name, user.email)`은 각각 어떻게 전달되는가?
6. `mode='before'`가 없으면 앞뒤 공백이 허용될 수 있는 이유는?
7. EmailStr를 써도 INSERT 튜플의 순서를 확인해야 하는 이유는?
8. 201만 보고 올바른 데이터가 저장됐다고 확신하면 안 되는 이유는?
9. dict_row, fetchone, fetchall은 각각 어떤 역할인가?
10. DB 데이터와 app.state 중 서버 재시작 후에도 남는 것은?

이 질문들을 코드의 흐름으로 설명할 수 있으면 오늘 배운 핵심을 이해한 것입니다.
