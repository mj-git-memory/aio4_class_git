# day15: 대화 기록과 임시 세션을 관리하는 API

`main1.py`부터 `main5.py`까지 실제 소스를 읽고 정리한 입문용 설명입니다. 대화에서 질문한 개념을 포함하고, 오류 원인과 해결 과정은 제외했습니다.

## 1. 무엇을 만드는 코드인가요?

**대화방과 메시지를 저장하고, 유효 시간이 있는 세션으로 대화방을 이용하는 서버**를 만듭니다.

식당에 비유하면 다음과 같습니다.

| 구성 요소 | 쉬운 비유 | 이 코드에서 맡는 일 |
|---|---|---|
| FastAPI | 주문을 접수하는 직원 | 요청을 받고 해당 파이썬 함수를 실행 |
| PostgreSQL | 오래 보관하는 장부 | 대화방과 메시지를 저장 |
| Supabase | 장부를 보관하고 관리하는 서비스 | PostgreSQL 데이터베이스 제공 |
| Redis | 빠르게 확인하는 임시 메모판 | 세션 ID와 대화방 ID의 연결을 일정 시간 저장 |
| 세션 ID | 유효 시간이 있는 이용권 번호 | 어떤 대화방을 이용할지 찾는 데 사용 |

두 저장소를 함께 쓰므로 **하이브리드 구조**라고 부릅니다. 여기서는 Redis에 메시지를 복사하지 않고, PostgreSQL에 저장된 메시지를 읽습니다.

```text
클라이언트(브라우저의 /docs 등)
    → FastAPI에 요청
    → Redis에서 세션 ID에 연결된 대화방 ID 확인
    → PostgreSQL에 해당 대화방 메시지 저장·조회
    → JSON으로 결과 응답
```

이 코드는 대화 기록을 다루는 백엔드 실습입니다. AI 답변 생성, 채팅 화면, 사용자 로그인 기능은 구현되어 있지 않습니다.

## 2. 파일별 기능과 주요 함수

각 파일은 별도로 실행하는 FastAPI 앱입니다. 뒤 파일은 앞 단계의 개념을 확장합니다.

| 파일 | 핵심 기능 | 한 문장으로 이해하기 |
|---|---|---|
| [main1.py](main1.py) | 연결 확인, 대화방·메시지 저장과 조회 | 장부와 메모판이 준비됐는지 확인하고 대화 기록 저장하기 |
| [main2.py](main2.py) | Redis 세션 발급·조회 | 유효 시간이 있는 이용권 만들기 |
| [main3.py](main3.py) | 세션을 확인한 뒤 DB 메시지 저장·조회 | 이용권으로 대화방을 찾아 기록하기 |
| [main4.py](main4.py) | 세션 상태 확인·연장·종료 | 이용권의 남은 시간 확인하고 관리하기 |
| [main5.py](main5.py) | 새 세션 발급과 최근 기록 조회를 묶은 대화 재개 | 새 이용권으로 예전 대화 이어가기 |

### main1.py: 연결 확인과 기본 저장

- `health()`: PostgreSQL에 `SELECT 1`을 실행하고 Redis에 `PING`을 보내 응답을 확인합니다. 두 서비스가 모두 응답하면 `ready`가 `True`입니다.
- `connect_db()`: PostgreSQL 연결을 만들어 반환합니다.
- `init_db()`: `kdt_hybrid` 스키마와 대화방·메시지 테이블을 준비합니다.
- `create_conversation()`: UUID를 생성하고 제목과 함께 대화방을 저장합니다.
- `list_conversation()`: 대화방 목록을 읽습니다.
- `create_messages()`: URL로 받은 대화방 ID를 확인하고 메시지를 저장합니다.
- `list_messages()`: 현재 소스에서는 저장된 메시지 전체를 읽습니다. URL에는 대화방 ID가 있지만 SQL에는 대화방별 필터가 없습니다.

대표 요청은 `GET /health`, `POST /conversations`, `GET /conversations`, `POST /conversation/{conversation_id}/messages`입니다.

**헬스 체크**는 서비스에 보내는 간단한 응답 확인입니다. 이 코드의 `SELECT 1`은 DB에 SQL을 실행할 수 있는지 확인하며, 특정 테이블의 상태까지 검사하지는 않습니다.

### main2.py: 만료되는 세션

- `connect_redis()`: Redis 명령을 실행할 클라이언트를 만듭니다.
- `create_session()`: 새 세션 ID를 만들고 `세션 ID → 대화방 ID`를 만료 시간과 함께 저장합니다.
- `read_session()`: 세션에 연결된 대화방 ID와 남은 유효 시간을 조회합니다.

| API | 기능 |
|---|---|
| `POST /sessions` | 세션 발급 |
| `GET /sessions/{session_id}` | 세션과 남은 시간 조회 |

이 파일은 PostgreSQL에 연결하지 않습니다. 입력한 대화방 ID가 UUID 형식인지만 검사합니다.

### main3.py: Redis와 PostgreSQL 연결

대화방을 만든 후, 그 대화방에 대한 세션을 발급받고 메시지를 저장합니다.

```text
POST /conversations → 대화방 ID 받기
POST /sessions      → 그 대화방의 세션 ID 받기
POST /messages      → 세션 ID를 헤더에 넣어 메시지 저장
GET /messages       → 같은 세션 ID로 메시지 조회
```

- `create_session()`: DB에 대화방이 실제로 있는지 확인한 뒤 세션을 발급합니다.
- `resolve_conversation()`: 요청 헤더의 세션 ID를 확인하고 Redis에서 대화방 ID를 찾아 반환합니다.
- `create_message()`: 찾은 대화방 ID와 메시지 내용을 PostgreSQL에 저장합니다.
- `list_messages()`: 그 대화방의 메시지만 조회합니다.

**헤더(Header)**는 요청에 붙이는 부가 정보입니다. 본문에 메시지 내용을 넣고, 헤더에는 세션 ID를 넣습니다.

```text
헤더: X-Session-Id: 발급받은 세션 ID
본문: {"content": "오늘은 Redis를 배웠어요."}
```

### main4.py: 세션 관리

`main3.py`의 기능에 아래 기능을 추가합니다.

| 함수 | API | 기능 |
|---|---|---|
| `session_status()` | `GET /session` | 현재 대화방과 남은 시간 확인 |
| `renew_session()` | `POST /session/renew` | 현재 시점부터 설정한 시간만큼 유효하도록 재설정 |
| `end_session()` | `DELETE /session` | Redis 세션 키 삭제 |

예를 들어 기본 시간이 300초이고 100초가 남았을 때 연장하면, 남은 시간이 다시 300초가 됩니다. 400초로 더하는 방식은 아닙니다.

메시지를 저장하거나 조회하는 것만으로는 시간이 연장되지 않습니다. 세션을 종료해도 PostgreSQL의 대화방과 메시지는 남습니다.

### main5.py: 이전 대화 이어가기

`main4.py`에 `resume_conversation()`을 추가합니다.

```text
POST /conversations/{conversation_id}/resume?limit=3
```

1. 기존 대화방을 확인합니다.
2. 최근 메시지 3개를 DB에서 읽습니다.
3. 선택한 메시지를 오래된 순서로 정렬합니다.
4. 새 세션 ID와 메시지 목록을 함께 반환합니다.

SQL의 `ORDER BY id DESC LIMIT 3`으로 최근 3개를 선택한 뒤, `rows.reverse()`로 선택한 목록의 순서를 뒤집습니다.

`limit`은 기본 10개이며 1~50개로 제한됩니다. 복원은 **DB에 남아 있는 기록을 다시 읽고 새 세션을 발급하는 것**입니다.

파일마다 Redis 키에 `l03`, `l04`, `l05`, `l06`을 사용하므로 각 단계의 세션은 서로 구분됩니다.

## 3. 꼭 알아둘 데이터 개념

### 스키마, 테이블, 행, 컬럼

```text
데이터베이스
└─ kdt_hybrid          ← 스키마: 테이블을 묶는 폴더 같은 공간
   ├─ conversation    ← 테이블: 대화방 목록을 담는 표
   └─ message         ← 테이블: 메시지를 담는 표
```

- **행(row)**: 메시지 한 건처럼 표에 들어가는 기록 하나.
- **컬럼(column)**: `id`, `title`, `content`처럼 기록의 항목.
- **기본 키(PRIMARY KEY)**: 각 행을 구별하는 고유 번호.
- **외래 키(REFERENCES)**: 메시지가 어느 대화방에 속하는지 연결하는 값.
- **UUID**: 긴 고유 식별자. 이 코드에서는 대화방과 세션에 사용합니다.
- **IDENTITY**: DB가 메시지의 정수 ID를 자동으로 생성하는 기능.

대화방 하나에 메시지 여러 개가 속합니다. 메시지의 `conversation_id`는 대화방의 `id`를 가리킵니다.

| SQL 표현 | 의미 |
|---|---|
| `CREATE SCHEMA / CREATE TABLE` | 저장 공간의 구조 준비 |
| `IF NOT EXISTS` | 같은 이름의 대상이 없을 때 생성 |
| `INSERT INTO` | 새 기록 저장 |
| `SELECT` | 기록 조회 |
| `WHERE` | 조건에 맞는 기록만 선택 |
| `ORDER BY` | 정렬 순서 지정 |
| `LIMIT` | 가져올 개수 제한 |
| `RETURNING` | 방금 저장한 기록의 값을 돌려받기 |
| `NOT NULL` | 값 생략을 허용하지 않음 |
| `CHECK` | 저장할 값의 조건 검사 |
| `DEFAULT CURRENT_TIMESTAMP` | 값을 생략하면 현재 시각 저장 |

`VARCHAR(100)`은 최대 100글자 문자열, `TIMESTAMPTZ`는 시간대를 고려하는 날짜·시간 타입입니다. `trim()`은 양끝 공백을 제거하고 `length()`는 길이를 구합니다.

### 세션과 TTL

**세션**은 일정 기간 유지하는 연결 정보입니다. 이 코드에서는 세션 ID로 대화방 ID를 찾습니다.

**TTL(Time To Live)**은 만료까지 남은 시간입니다. 예를 들어 300초는 5분입니다.

| 표현 | 뜻 |
|---|---|
| `conversation_id` | 대화방 자체의 ID |
| `session_id` | 해당 대화방에 연결된 임시 세션의 ID |
| `expires_in` | 발급·연장 시 설정한 유효 시간 |
| `ttl` | 조회 시점에 실제로 남아 있는 시간 |

세션이 만료되어도 DB의 기록은 유지됩니다. 이 세션 구조만으로 사용자 신원을 확인하는 로그인 기능이 완성되는 것은 아닙니다.

## 4. 기능 구현에 사용한 파이썬 기본 문법

### 함수 정의와 호출

```python
def make_title(name: str = "연습"):
    return f"{name} 대화방"

title = make_title("파이썬")  # 결과: "파이썬 대화방"
```

- `def`: 함수를 정의합니다. 정의만 하면 본문은 실행되지 않습니다.
- `name`: 함수가 입력받는 매개변수입니다. `"파이썬"`은 호출할 때 전달한 인자입니다.
- `: str`: 문자열을 기대한다는 타입 표시입니다. 일반 파이썬 함수에서 자동 검증을 강제하지는 않습니다.
- `= "연습"`: 입력을 생략했을 때 쓸 기본값입니다.
- `return`: 결과를 반환하고 함수를 끝냅니다.
- 콜론 `:` 뒤의 들여쓰기 영역이 함수 본문입니다.

`connect_db`는 함수 자체이고 `connect_db()`는 함수를 호출하는 표현입니다. `conn.execute()`처럼 객체에 속한 함수는 **메서드**라고 부릅니다.

### FastAPI와 데코레이터

```python
app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "안녕하세요"}
```

`@`는 데코레이터 문법입니다. 여기서는 아래 함수를 특정 요청 경로에 연결합니다. `GET /hello` 요청이 오면 FastAPI가 `hello()`를 실행합니다.

| 표현 | 역할 |
|---|---|
| `@app.get(...)` | 조회 요청에 함수 연결 |
| `@app.post(...)` | 생성·처리 요청에 함수 연결 |
| `@app.delete(...)` | 삭제 요청에 함수 연결 |
| `JSONResponse(status_code=200, content={...})` | JSON 본문과 HTTP 상태 코드를 지정해 응답 |

JSON은 프로그램끼리 주고받는 데이터 형식입니다. Python 딕셔너리와 비슷하게 보이지만 별도의 전송 형식이며, Python의 `True`는 JSON에서 `true`로 표현됩니다.

### 요청 데이터 검증: Pydantic

```python
class ConversationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=100)
```

`class`는 객체의 설계도를 정의합니다. 여기서는 `BaseModel`의 기능을 물려받아 **요청 데이터의 규칙**을 만듭니다.

- `title: str`: 제목을 문자열로 받습니다. 기본값이 없어서 필수 항목입니다.
- `Field(...)`: 제목 길이를 1~100글자로 제한합니다.
- `extra="forbid"`: 정의하지 않은 추가 항목을 허용하지 않습니다.
- `str_strip_whitespace=True`: 문자열 양끝 공백을 제거합니다. `"  공부  "`는 `"공부"`가 됩니다.

```python
def create_conversation(body: ConversationCreate):
    title = body.title
```

FastAPI가 JSON 본문을 모델로 검증한 뒤 함수에 전달합니다. `body.title`은 그 안의 제목에 접근하는 문법입니다.

### 본문, 경로, 헤더, 쿼리

| 입력 위치 | 코드 예시 | 요청에서의 모습 |
|---|---|---|
| 본문 | `body: MessageCreate` | JSON `{"content": "안녕"}` |
| 경로 | `conversation_id: UUID` | `/conversations/대화방ID/resume` |
| 헤더 | `x_session_id: str \| None = Header(default=None)` | `X-Session-Id: 세션ID` |
| 쿼리 | `limit: int = Query(default=10, ge=1, le=50)` | URL 뒤의 `?limit=3` |

`str | None`은 문자열 또는 값이 없는 상태를 나타냅니다. `ge=1`은 1 이상, `le=50`은 50 이하라는 조건입니다. FastAPI의 `Header`는 기본적으로 변수명의 밑줄을 하이픈으로 바꿔 헤더 이름에 대응시킵니다.

### 연결 관리와 SQL 실행

```python
with connect_db() as conn:
    row = conn.execute(
        "SELECT id, title FROM kdt_hybrid.conversation WHERE id = %s",
        (conversation_id,),
    ).fetchone()
```

`with`는 사용 후 정리할 자원을 관리하는 문법입니다. 이 코드의 psycopg 연결에서는 정상 종료 시 변경을 확정(commit)하고, 예외 시 변경을 취소(rollback)한 뒤 연결을 닫습니다.

| 함수·설정 | 기능 |
|---|---|
| `psycopg.connect(...)` | PostgreSQL 연결 생성 |
| `conn.cursor()` | SQL 실행과 결과 읽기를 담당하는 커서 생성 |
| `conn.execute(...)` / `cur.execute(...)` | SQL 실행 |
| `fetchone()` | 결과 한 행 읽기 |
| `fetchall()` | 결과 전체를 리스트로 읽기 |
| `row_factory=dict_row` | 행을 `{"id": ..., "title": ...}` 형태로 받기 |

`%s`는 값이 들어갈 자리입니다. 실제 값은 두 번째 인자로 별도 전달합니다. `(conversation_id,)`는 값 하나가 담긴 튜플이며, 쉼표가 튜플을 나타냅니다.

### Redis 명령

```python
session_id = str(uuid4())
key = f"kdt:hybrid:l03:session:{session_id}"

with connect_redis() as client:
    client.set(key, str(conversation_id), ex=300)
    value = client.get(key)
    remaining = client.ttl(key)
```

| 함수·설정 | 기능 |
|---|---|
| `Redis.from_url(...)` | 접속 URL로 Redis 클라이언트 생성 |
| `decode_responses=True` | 읽은 값을 바이트 대신 문자열로 받기 |
| `ping()` | Redis가 응답하는지 확인 |
| `set(key, value, ex=300)` | 키와 값을 저장하고 300초 후 만료하도록 설정 |
| `get(key)` | 값 읽기. 키가 없으면 `None` |
| `ttl(key)` | 남은 초 읽기. `-2`는 키 없음, `-1`은 만료 설정 없음 |
| `expire(key, 300)` | 기존 키의 남은 시간을 현재부터 300초로 설정 |
| `delete(key)` | 키 삭제 |

`uuid4()`는 새 UUID를 만들고, `UUID(문자열)`은 문자열을 UUID 객체로 해석합니다. `str()`은 문자열로 변환하며, `f"...{변수}..."`는 문자열 안에 값을 넣는 문법입니다.

### 환경변수와 앱 실행

```python
load_dotenv(override=False, interpolate=False)
ttl = int(os.getenv("SESSION_TTL_SECONDS", "300"))
```

환경변수는 코드 밖에서 전달하는 설정입니다. `.env`에는 접속 주소와 만료 시간 등을 적습니다. 실제 비밀번호나 접속값은 이 문서에 포함하지 않습니다.

- `load_dotenv()`: `.env`를 찾아 값을 환경변수로 불러옵니다. 기본 탐색은 실행 방식에 따라 소스 위치 등의 기준에서 상위 폴더로 이어질 수 있습니다.
- `override=False`: 이미 있는 환경변수를 우선합니다. `main1.py`는 `True`를 사용합니다.
- `interpolate=False`: `${...}` 형태를 다른 환경변수 값으로 치환하지 않습니다.
- `os.getenv(이름, 기본값)`: 설정을 읽습니다.
- `int()`: `"300"` 같은 문자열을 정수로 바꿉니다.

```python
if __name__ == "__main__":
    init_db()
```

파일을 직접 실행할 때만 실행하는 영역입니다. `main3.py`~`main5.py`는 이 방식으로 DB 구조를 준비하고, `main1.py`는 파일을 불러올 때 `init_db()`를 호출합니다.

`day15` 폴더에서 `main5.py`를 사용하는 예시는 다음과 같습니다.

```bash
python main5.py
python -m uvicorn main5:app --host 127.0.0.1 --port 8000 --reload
```

첫 명령은 DB 구조를 준비하고 종료합니다. 두 번째 명령은 서버를 실행합니다. `main5:app`은 `main5.py` 안의 `app`을 뜻하며, `--reload`는 파이썬 파일 변경 시 서버를 다시 불러옵니다. `/docs`에서는 API를 시험할 수 있습니다.

### 질문했던 exception_handler()의 의미

```python
@app.exception_handler(RedisError)
def redis_error(_request, _exc):
    return JSONResponse(status_code=503, content={"detail": "Redis 연결을 확인하세요."})
```

`exception_handler()`는 **`app` 객체의 메서드**입니다. 지정한 종류의 예외가 요청 처리 중 발생하면 실행할 함수를 등록합니다. 아래의 `redis_error()`는 실제 응답을 만드는 처리 함수입니다. `_request`, `_exc` 앞의 밑줄은 여기서 그 값을 사용하지 않는다는 관례적 표시입니다.

`try/except`는 특정 코드 블록의 예외를 처리하는 문법이고, `raise`는 예외를 발생시키는 문법입니다. `HTTPException`은 FastAPI에서 정해진 HTTP 응답으로 요청 처리를 중단할 때 사용합니다.

### 그 밖에 자주 나오는 표현

| 표현 | 의미 |
|---|---|
| `{"supabase": "up"}` | 이름과 값으로 구성한 딕셔너리 |
| `[row1, row2]` | 여러 항목을 순서대로 담은 리스트 |
| `if value is None:` | 값이 없는 상태인지 검사 |
| `all(v == "up" for v in checks.values())` | 모든 상태가 `"up"`인지 확인 |
| `200 if ready else 503` | 조건이 참이면 200, 아니면 503 선택 |
| `rows.reverse()` | 리스트 자체의 순서를 뒤집음 |
| `pass` | 아무 작업도 하지 않고 통과 |

## 5. 질문했던 Docker 명령어 정리

Docker는 프로그램과 실행 환경을 **컨테이너**라는 단위로 실행하는 도구입니다. 이미지는 실행에 사용할 준비된 틀이고, 컨테이너는 그 틀로 실행한 실제 인스턴스입니다.

```bash
docker run -d --name kdt-hybrid-redis -p 127.0.0.1:6379:6379 redis redis-server --save '' --appendonly no
```

| 부분 | 의미 |
|---|---|
| `docker run` | 새 컨테이너 생성·실행 |
| `-d` | 백그라운드 실행 |
| `--name kdt-hybrid-redis` | 컨테이너 이름 지정 |
| `-p 127.0.0.1:6379:6379` | 내 PC의 6379 포트를 컨테이너의 6379 포트에 연결 |
| `redis` | 사용할 이미지 이름 |
| `redis-server` | 컨테이너 안에서 실행할 프로그램 |
| `--save ''` | 주기적인 RDB 스냅샷 저장 끄기 |
| `--appendonly no` | AOF 변경 기록 저장 끄기 |

이것은 파이썬 함수가 아닌 **터미널 명령어와 옵션**입니다. Docker 옵션은 이미지 이름 앞에, Redis 서버 옵션은 `redis-server` 뒤에 옵니다.

`127.0.0.1`은 자기 컴퓨터의 주소이고, 포트는 같은 컴퓨터에서 어떤 서비스로 연결할지 구별하는 번호입니다. 이 설정은 내 컴퓨터의 Redis 접속을 컨테이너로 연결합니다.

Redis의 **RDB**는 특정 시점의 데이터를 통째로 저장하는 방식이고, **AOF**는 데이터 변경 명령을 기록하는 방식입니다. 위 명령은 두 자동 저장 방식을 끄므로 Redis를 재시작해도 현재 세션이 복구된다고 기대할 수 없습니다.

## 6. 한 가지 예시로 전체 흐름 복습

`main5.py` 기준으로 다음 순서로 이용할 수 있습니다.

1. 제목 `"파이썬 공부"`로 대화방을 만듭니다. → PostgreSQL에 대화방 저장.
2. 그 대화방 ID로 세션을 발급합니다. → Redis에 300초짜리 연결 정보 저장(설정값이 300일 때).
3. 세션 ID를 헤더에 넣고 `"오늘은 함수를 배웠어요"`를 보냅니다. → PostgreSQL에 메시지 저장.
4. 같은 세션으로 메시지를 조회합니다. → 해당 대화방 기록 반환.
5. 필요하면 세션을 연장하거나 종료합니다. → Redis 정보만 변경.
6. 나중에 `resume`을 호출합니다. → 새 세션과 DB의 최근 메시지를 받아 대화 재개.

**기록은 PostgreSQL에, 임시 연결은 Redis에, 요청 처리는 FastAPI에 맡기는 구조**로 기억하면 됩니다.

## 7. 추가 질문: body와 클래스의 필드 이름

```python
class SessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conversation_id: UUID

@app.post("/sessions", status_code=201)
def create_session(body: SessionCreate):
    convers_id = body.conversation_id
```

| 표현 | 의미 |
|---|---|
| `body` | 함수가 입력받는 매개변수 이름. 개발자가 정함 |
| `: SessionCreate` | 어떤 구조의 객체를 받을지 나타내는 타입 표시 |
| `conversation_id` | 모델에 정의된 필드(데이터 항목) 이름 |
| `body.conversation_id` | 전달받은 객체에서 해당 필드 값 꺼내기 |
| `convers_id` | 꺼낸 값을 담는 새 변수 이름. 자유롭게 정할 수 있음 |

FastAPI는 요청 JSON을 검증한 뒤 `SessionCreate` 객체를 만들어 `body`에 전달합니다.

```text
요청 JSON: {"conversation_id": "UUID 형식의 문자열"}
    ↓ FastAPI와 Pydantic이 검증·변환
body: SessionCreate 객체
└─ conversation_id: UUID 객체
```

여기서 `body`에 들어 있는 데이터 필드는 `conversation_id` 하나입니다. `session_id`는 함수 안에서 새로 생성하므로 요청 객체에 포함된 값이 아닙니다.

`body`를 `data`로 바꾸면 사용하는 곳도 `data.conversation_id`로 바꾸면 됩니다. 필드 자체를 `convers_id`로 바꾸려면 **모델 정의, 필드 접근, 요청 JSON의 항목 이름**을 함께 맞춰야 합니다(별칭을 설정하지 않은 현재 코드 기준).

```python
class SessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    convers_id: UUID

def create_session(body: SessionCreate):
    value = str(body.convers_id)
```

이 경우 요청 항목도 `"convers_id"`입니다. 파이썬 모델의 이름을 바꾼다고 DB 컬럼이 자동으로 변경되지는 않습니다.

## 8. 추가 질문: 세션은 직접 만드는 기능인가요?

**이 실습에서는 Redis의 저장·조회·만료 기능을 조합해 세션 기능을 직접 구현합니다.**

`create_session`이라는 이름 자체에 특별한 기능이 있지는 않습니다. 함수 안에서 실행하는 작업이 기능을 결정합니다. `SessionCreate` 역시 세션을 자동으로 만드는 클래스가 아니라 요청 데이터의 규칙입니다.

```python
session_id = str(uuid4())
key = f"kdt:hybrid:l06:session:{session_id}"
client.set(key, str(body.conversation_id), ex=300)
```

`main5.py`의 방식에서 대화방 ID를 A, 세션 ID를 B라고 부르면 다음 연결을 저장합니다. A와 B는 설명을 위한 이름이며 실제 값은 UUID입니다.

```text
Redis 키: kdt:hybrid:l06:session:B
Redis 값: A
유효 시간: 300초
```

Redis는 이 데이터가 세션인지 모릅니다. 만료 시간이 있는 키와 값으로 저장할 뿐입니다. 서버가 이를 이용 상태를 기억하는 데 사용하므로 세션이 됩니다.

클라이언트는 세션 ID B를 헤더로 보냅니다. `resolve_conversation()`은 같은 규칙으로 전체 키를 만들어 값을 읽고, 대화방 ID A를 얻습니다.

```text
세션 ID B 전달
    → Redis에서 kdt:hybrid:l06:session:B 조회
    → 대화방 ID A 확인
    → DB에서 A에 속한 메시지 저장·조회
```

**대화방은 메시지를 묶는 기록의 단위**입니다. `conversation`의 한 행이 대화방 하나를 나타내고, 그 대화방 ID가 같은 메시지들이 하나의 대화 기록을 이룹니다.

세션은 그 대화방을 가리키는 임시 연결입니다. 하나의 대화방에 서로 다른 세션을 여러 번 발급할 수도 있습니다. 세션이 만료되어도 대화방과 메시지는 남습니다.

## 9. 추가 질문: PK·FK 관계가 JOIN인가요?

**PK·FK는 데이터 사이의 관계와 제약이고, JOIN은 데이터를 합쳐 조회하는 작업**입니다. FK를 설정해도 자동으로 JOIN되지는 않습니다.

```text
conversation                 message
id(PK)  title                id(PK)  conversation_id(FK)  content
A       파이썬 공부           1       A                    안녕하세요
B       여행 계획             2       A                    함수가 궁금해요
                             3       B                    제주도 가자
```

`message.conversation_id`는 메시지가 어느 대화방에 속하는지 나타냅니다. FK 제약은 존재하지 않는 대화방 ID를 참조하지 못하게 합니다.

대화방 제목과 메시지 내용을 함께 보고 싶다면 JOIN을 사용할 수 있습니다.

```sql
SELECT c.title, m.content
FROM kdt_hybrid.conversation AS c
JOIN kdt_hybrid.message AS m
    ON c.id = m.conversation_id;
```

하지만 현재 `main3.py`~`main5.py`는 JOIN 대신 Redis에서 대화방 ID를 얻고, 그 ID로 메시지를 필터링합니다.

```sql
SELECT id, content
FROM kdt_hybrid.message
WHERE conversation_id = %s;
```

두 종류의 연결을 구별하면 이해하기 쉽습니다.

| 연결 | 저장소 | 목적 |
|---|---|---|
| 세션 ID → 대화방 ID | Redis | 요청이 이용할 대화방을 임시로 기억 |
| 메시지의 FK → 대화방의 PK | PostgreSQL | 메시지가 어느 대화방에 속하는지 기록 |

## 10. 추가 질문: 백엔드에서 세션을 왜 사용하나요?

HTTP는 기본적으로 요청마다 독립적입니다. 서버가 여러 요청을 같은 사용자나 작업에 연결하려면 이전 상태를 기억할 방법이 필요합니다.

일반적인 서버 저장형 세션은 다음 순서로 사용합니다.

1. 서버가 세션 ID를 만듭니다.
2. 저장소에 세션 ID와 기억할 정보를 저장합니다.
3. 클라이언트에게 세션 ID를 전달합니다.
4. 클라이언트가 다음 요청에 ID를 보내면 서버가 정보를 조회합니다.

| 사용 예 | 기억하는 연결 |
|---|---|
| 로그인 | 세션 ID → 로그인한 사용자 ID |
| 현재 실습 | 세션 ID → 이용할 대화방 ID |

로그인에서는 인증에 성공한 뒤 세션을 발급하고, 브라우저에는 보통 쿠키로 세션 ID를 전달합니다. 현재 실습에서는 JSON 응답으로 전달하고 요청 헤더로 다시 받습니다. 현재 코드는 사용자 로그인이나 대화방 소유 권한을 검증하는 기능은 포함하지 않습니다.

## 11. 추가 질문: 세션 저장 위치별 장단점

| 위치 | 장점 | 단점 | 활용 예 |
|---|---|---|---|
| 파이썬 메모리의 `dict` | 간단하고 빠르며 별도 저장소가 필요 없음 | 프로세스 종료 시 사라짐. 여러 프로세스 간 자동 공유되지 않음 | 작은 실습·임시 테스트 |
| Redis | 빠른 조회, 공통 저장소로 공유 가능, TTL로 자동 만료 | 별도 운영 필요. 메모리 용량과 저장·복구 설정을 고려해야 함 | 여러 서버가 이용하는 만료형 세션 |
| PostgreSQL | 디스크에 기록 보관. 기존 데이터와 연결해 관리하기 편함 | DB 부하 발생. 만료 시각 검사와 오래된 행 정리 필요 | 기존 DB를 활용한 세션 관리 |

Redis도 메모리를 사용하는 저장소지만, **앱과 별도의 프로세스로 실행되며 여러 앱이 접속할 수 있다**는 점이 파이썬의 일반 딕셔너리와 다릅니다.

### 서버가 여러 개인 실제 예: 쇼핑몰

접속자가 많으면 요청 분배기(로드 밸런서)가 요청을 여러 서버에 나눠 보낼 수 있습니다.

```text
                         ┌→ 서버 A: 로그인 요청 처리
사용자 → 요청 분배기 ────┤
                         └→ 서버 B: 다음 주문 조회 요청 처리
```

세션을 A의 딕셔너리에만 저장했다면 B는 그 세션을 알지 못합니다. 같은 사용자가 보낸 요청이어도 서버마다 가진 데이터가 다르기 때문입니다.

```text
서버 A의 메모리: session-123 → 사용자 10
서버 B의 메모리: 비어 있음
```

공통 Redis나 DB를 쓰면 어느 서버든 같은 정보를 조회할 수 있습니다.

```text
서버 A ─┐
        ├→ 공통 저장소: session-123 → 사용자 10
서버 B ─┘
```

컴퓨터 한 대에서도 프로세스를 여러 개 실행하면 일반 변수는 자동 공유되지 않습니다. 예를 들어 아래 명령은 요청을 처리하는 작업 프로세스를 두 개 실행합니다.

```bash
python -m uvicorn main3:app --workers 2
```

## 12. 추가 질문: 파이썬 메모리는 어떻게 사용하나요?

변수를 만들면 값이 프로그램의 메모리(RAM)에 저장됩니다. 메모리를 사용하기 위한 별도 연결은 필요 없습니다.

```python
name = "지민"              # 문자열
messages = ["안녕하세요"]   # 리스트
sessions = {}              # 딕셔너리
```

세션을 딕셔너리로 저장하는 간단한 예시입니다. 별도 학습용 예시이며 실제 소스의 Redis를 대체한 코드는 아닙니다.

```python
from uuid import uuid4

sessions = {}  # 함수 밖에 두어 같은 프로세스에서 여러 호출이 사용

def create_session(conversation_id):
    session_id = str(uuid4())
    sessions[session_id] = conversation_id
    return session_id

# 생성·저장
sid = create_session("대화방-A")

# 조회
conversation_id = sessions.get(sid)
print(conversation_id)  # 대화방-A

# 삭제: 키가 없어도 None을 반환
sessions.pop(sid, None)
```

| 작업 | 파이썬 딕셔너리 | Redis 클라이언트 |
|---|---|---|
| 저장 | `sessions[sid] = value` | `client.set(sid, value)` |
| 조회 | `sessions.get(sid)` | `client.get(sid)` |
| 삭제 | `sessions.pop(sid, None)` | `client.delete(sid)` |

`sessions = {}`를 생성 함수 안에 두면 호출할 때마다 새 딕셔너리를 만듭니다. 위 예시는 여러 호출에서 같은 딕셔너리를 쓰려고 함수 밖에 둡니다.

일반 딕셔너리는 자동 만료 기능이 없습니다. 세션을 직접 삭제하거나 프로세스가 종료되기 전까지 해당 딕셔너리에 남아 있습니다. 시간 제한을 넣으려면 만료 시각을 함께 저장하고 검사·정리하는 로직을 작성해야 합니다.
