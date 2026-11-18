# Day 13 학습 정리 — 환경변수부터 Supabase 인증·권한 관리까지

오늘 작성한 `main.py`, `main2.py`, `main3.py`와 질문한 내용을 중심으로 정리했습니다. 마지막에는 쇼핑몰에 적용한 인증·권한 관리도 연결했습니다. 오류 코드와 오류 해결 과정은 제외했습니다.

> 아래 코드는 개념별 발췌 예시입니다. 각각을 독립적으로 실행할 수 있는 완성 프로그램은 아닙니다. 실제 비밀번호·API 키·토큰은 예시에 포함하지 않았습니다.

## 1. 오늘 만든 기능의 큰 흐름

```text
.env에서 프로젝트 설정 읽기
→ FastAPI로 API 경로 만들기
→ Pydantic으로 요청 데이터 검사
→ Supabase Auth로 회원가입·로그인
→ 로그인 결과에서 사용자 정보·토큰 받기
→ 토큰으로 현재 사용자 확인
→ 확인한 사용자에게 허용된 데이터만 제공
```

파일별 역할을 먼저 기억하면 전체 코드를 읽기 쉬워집니다.

| 파일 | 핵심 학습 내용 |
|---|---|
| `main.py` | 환경변수, 회원가입·로그인, 입력·응답 모델 |
| `main2.py` | Bearer 토큰을 받아 현재 사용자 확인 |
| `main3.py` | 인증된 사용자만 자신의 SQLite 메모에 접근 |
| `../day12/shoppingmall/main.py`, `auth.py` | 쇼핑몰의 Supabase Auth 전환, 서버 세션, 일반 회원·관리자 권한 |

**로그인할 수 있는지 확인하는 것과, 어떤 데이터를 볼 수 있는지 결정하는 것은 별개의 일입니다.**

## 2. 환경변수와 `.env`: 코드 밖에서 설정 관리하기

환경변수는 프로그램이 실행될 때 읽는 이름과 값입니다. `.env`는 그 값을 적어두는 파일입니다.

```dotenv
# .env 예시: 실제 값은 자신의 프로젝트 설정 사용
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
NOTES_DB=notes.db
```

```python
import os
from dotenv import load_dotenv

# .env의 설정을 현재 Python 프로세스의 환경변수에 추가
load_dotenv(override=False)

# 이름으로 값을 조회. 없으면 두 번째 인자인 빈 문자열 반환
supabase_url = os.getenv('SUPABASE_URL', '')
```

- `load_dotenv()`: 파일을 읽어 환경변수에 추가합니다.
- `os.getenv()`: 환경변수 값을 조회합니다.
- `os.environ['이름'] = 값`: 현재 프로세스의 환경변수를 설정합니다.

### `override`는 어떤 값을 우선할지 정하는 옵션

```python
os.environ['host'] = '기존값'

# .env에 host=파일값이 있다고 가정
load_dotenv(override=False)
print(os.getenv('host'))  # 기존값 유지

load_dotenv(override=True)
print(os.getenv('host'))  # 파일값으로 교체
```

여기서 `host`는 직접 정한 이름입니다. 컴퓨터의 실제 호스트 주소가 자동으로 들어오는 특별한 변수는 아닙니다. 위 대입은 컴퓨터의 영구 설정이나 `.env` 파일 자체를 수정하지 않습니다.

```python
import socket

# 컴퓨터의 호스트 이름은 별도의 기능으로 조회
computer_name = socket.gethostname()
```

**비밀번호·토큰 같은 비밀값은 코드에 직접 쓰거나 화면에 출력하지 않습니다.** Publishable key는 비밀 서버 키와 다르며, 이 키가 있다고 관리자 권한을 얻는 것도 아닙니다.

## 3. 설정 파일의 위치: 현재 폴더와 소스 파일 위치 구분하기

현재 프로젝트는 다음 구조입니다.

```text
AIO_4_class/
├── .env
└── day13/
    └── main3.py
```

```python
from pathlib import Path
from dotenv import load_dotenv

# __file__: 현재 Python 파일의 경로
# resolve(): 절대 경로로 정리
# parent: 파일이 들어 있는 폴더
# parent.parent: 그 폴더의 상위 폴더

env_path = Path(__file__).resolve().parent.parent / '.env'

load_dotenv(
    env_path,
    override=False,      # 이미 있는 환경변수 우선
    interpolate=False,   # ${이름}을 다른 값으로 치환하지 않고 보존
)
```

`load_dotenv('.env')`처럼 상대 경로를 직접 주면 명령을 실행한 폴더를 기준으로 찾습니다. `__file__`을 이용하면 소스 파일 위치를 기준으로 경로를 정할 수 있습니다.

또한 `NOTES_DB=notes.db`도 상대 경로입니다. `main3.py`의 현재 코드에서는 실행한 폴더를 기준으로 SQLite 파일이 정해집니다.

## 4. 문자열 메서드: `strip`, `rstrip`, `rsplit`

메서드는 객체에 속한 함수입니다. 아래는 문자열에 사용하는 메서드입니다.

| 코드 | 기능 | 결과 타입 |
|---|---|---|
| `.strip()` | 양쪽 끝의 공백·줄바꿈 제거 | 문자열 `str` |
| `.rstrip('/')` | 오른쪽 끝에 이어진 `/` 제거 | 문자열 `str` |
| `.rsplit('/')` | `/`를 기준으로 나누기 | 리스트 `list` |

```python
print('  hello  '.strip())
# 'hello'

print('https://example.com///'.rstrip('/'))
# 'https://example.com' → 중간의 //는 유지

print('a/b/c'.rsplit('/', 1))
# ['a/b', 'c'] → 오른쪽부터 한 번 나눔
```

Supabase URL에는 문자열이 필요하므로 다음처럼 정리합니다.

```python
supabase_url = os.getenv('SUPABASE_URL', '').strip().rstrip('/')
```

**설정값의 공백을 정리하는 것과 비밀번호를 정리하는 것은 다릅니다. 비밀번호에는 임의로 `strip()`을 적용하지 않습니다.**

## 5. 패키지·클래스·함수·객체의 차이

```python
from supabase import Client, create_client, ClientOptions
```

| 이름 | 종류 | 역할 |
|---|---|---|
| `supabase` | 패키지 | Supabase 관련 기능을 묶어 제공 |
| `Client` | 클래스 | Supabase 클라이언트의 구조와 동작 정의 |
| `create_client` | 함수 | 클라이언트 객체를 만들어 반환 |
| `ClientOptions` | 클래스 | 연결 동작을 정할 설정 객체 생성 |

비유하면 **클래스는 설계도, 객체는 설계도로 만든 실제 물건**입니다.

```python
# 설정 클래스로 객체 생성
options = ClientOptions(persist_session=False)

# 함수를 호출해 클라이언트 객체 생성
supabase: Client = create_client(
    supabase_url,
    supabase_key,
    options=options,
)

# 만들어진 객체의 인증 기능과 메서드 사용
supabase.auth.sign_up({...})
```

대문자로 시작하는 이름은 보통 클래스, 소문자와 밑줄로 된 이름은 보통 함수입니다. 이름을 짓는 관례이며, 이름만으로 종류가 강제되지는 않습니다.

## 6. `=`와 `:`: 값 대입과 타입 표시

```python
name = '홍길동'       # = : 값을 넣음
name: str            # : : 타입을 표시함
name: str = '홍길동'  # 타입 표시 + 값 대입
```

Pydantic 모델에서의 예시입니다.

```python
class SignupRequest(BaseModel):
    # 실제 설정 객체를 만들어 대입
    model_config = ConfigDict(extra='forbid')

    # 나중에 받을 데이터의 타입 선언
    email: EmailStr

    # 타입 선언과 검증 조건을 함께 지정
    password: SecretStr = Field(min_length=8, max_length=128)
```

타입까지 표시하고 싶으면 아래처럼 쓸 수 있습니다.

```python
model_config: ConfigDict = ConfigDict(extra='forbid')
#             타입         실제 설정값
```

`:` 뒤에는 타입을 적습니다. `ConfigDict()`처럼 호출해서 만든 값은 `=` 오른쪽에 놓습니다.

**일반 Python의 타입 힌트 자체가 값을 자동 검사하는 것은 아닙니다. Pydantic이 모델의 타입 정보를 읽어 실제 데이터 검증에 활용합니다.**

## 7. Pydantic: 받을 데이터의 형식과 규칙 정하기

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

class SignupRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128)
```

| 기능 | 기억할 내용 |
|---|---|
| `BaseModel` | 데이터 모델을 만드는 기본 클래스 |
| `ConfigDict` | 모델 전체의 처리 규칙 |
| `EmailStr` | 이메일 주소 형식 검사. 실제 메일함 존재 여부 확인은 아님 |
| `Field` | 최소·최대 길이 같은 세부 조건 |
| `SecretStr` | 출력할 때 비밀번호 같은 값을 가려주는 타입 |

### 설정값이란 구체적으로 어떤 규칙인가?

```python
model_config = ConfigDict(extra='forbid')
# 정한 항목 외에 다른 항목을 받지 않겠다는 규칙
```

| `extra` 값 | 모델에 없는 `nickname`이 들어오면 |
|---|---|
| `'forbid'` | 허용하지 않음 |
| `'ignore'` | 무시함 |
| `'allow'` | 추가 데이터도 보관함 |

`email`, `password`는 사용자가 보내는 **데이터**, `model_config`는 그 데이터를 처리하는 **규칙**입니다.

### 요청 JSON의 이름과 값 구분

```json
{
  "email": "user1@example.com",
  "password": "abcdefgh"
}
```

- `email`: 모델에 정의된 항목 이름
- `user1@example.com`: 사용자가 입력한 값

사용자가 user1이라고 해서 항목 이름을 `user1`로 바꾸는 것이 아닙니다. 항목 이름은 `email`로 유지합니다.

### `SecretStr`과 실제 비밀번호

```python
password = SecretStr('abcdefgh')

print(password)  # **********

# Supabase에 전송할 실제 문자열이 필요할 때 사용
actual_password = password.get_secret_value()
```

**`SecretStr`은 비밀번호 암호화나 해시 저장 기능이 아닙니다.** 출력 시 가려주는 기능입니다.

### `None`을 허용하는 것과 생략을 허용하는 것은 다름

```python
expires_at: int | None
# 정수 또는 None을 받을 수 있지만 항목 자체는 필수

expires_at: int | None = None
# 항목을 생략하면 기본값 None 사용
```

비유하면 첫 번째는 “선택 안 함이라고라도 적어야 하는 칸”, 두 번째는 “비워도 되는 칸”입니다.

## 8. FastAPI와 데코레이터: 주소에 함수를 연결하기

```python
from fastapi import FastAPI

app = FastAPI(title='Supabase Auth 학습')
# app: API 요청을 처리하는 앱 객체
# title: API 문서에 표시할 이름
```

```python
@app.post('/auth/signup', response_model=SignupResponse)
def signup(body: SignupRequest):
    ...
```

`@`로 시작하는 부분은 데코레이터입니다. 여기서는 FastAPI에 다음 규칙을 등록합니다.

> `/auth/signup`으로 POST 요청이 오면 아래 `signup()` 함수를 실행한다.

- `@app.get(...)`: 조회 경로 등록
- `@app.post(...)`: 생성·처리 요청 경로 등록
- `body: SignupRequest`: 요청 본문을 해당 모델로 읽고 검사
- `response_model=SignupResponse`: 응답 데이터의 구조를 지정

등록 시점에 회원가입을 실행하는 것은 아닙니다. 실제 요청이 와야 함수 본문이 실행됩니다.

## 9. 요청 모델·응답 모델·`Response` 구분하기

```python
class SignupResponse(BaseModel):
    message: str

@app.post('/auth/signup', response_model=SignupResponse)
def signup(body: SignupRequest):
    # 검증된 요청의 값 읽기
    email = str(body.email)

    # 모델 객체를 반환하면 FastAPI가 JSON으로 변환
    return SignupResponse(message='가입 요청을 처리했습니다.')
```

| 항목 | 역할 |
|---|---|
| `SignupRequest` | 사용자 → 서버 데이터 구조 |
| `SignupResponse` | 서버 → 사용자 데이터 구조 |
| FastAPI의 `Response` | 응답 헤더 등을 설정하는 객체 |

```python
from fastapi import Response

@app.post('/auth/login', response_model=TokenResponse)
def login(body: LoginRequest, response: Response):
    # 토큰이 포함된 응답을 캐시에 저장하지 않도록 지시
    response.headers['Cache-Control'] = 'no-store'
    ...
```

**응답 모델 클래스와 실제 HTTP 응답을 제어하는 `Response`는 역할이 다릅니다.**

## 10. HTTPX와 `with`: 외부 서버와 통신하기

우리 API 서버는 Supabase라는 외부 서버에 요청을 보냅니다. HTTPX는 이 HTTP 통신을 담당합니다.

```python
import httpx

with httpx.Client(timeout=10.0) as http_client:
    # 이 블록에서 HTTP 클라이언트 사용
    ...
# 블록을 벗어나면 연결 등의 자원을 정리
```

- `Client()`: 통신 객체 생성
- `timeout=10.0`: 통신 단계별 대기 제한 설정
- `as http_client`: 만든 객체를 사용할 변수 이름
- `with`: 작업이 끝나면 자원을 정리하는 문법

10초는 전체 회원가입이 반드시 10초 안에 끝난다는 의미는 아닙니다.

```python
supabase = create_client(
    supabase_url=supabase_url,
    supabase_key=supabase_key,
    options=ClientOptions(
        persist_session=False,     # SDK 세션 저장소에 세션을 저장하지 않음
        auto_refresh_token=False,  # SDK의 자동 토큰 갱신을 사용하지 않음
        httpx_client=http_client,  # 위에서 만든 HTTP 클라이언트 사용
    ),
)
```

같은 이름이 반복되어도 왼쪽과 오른쪽의 역할이 다릅니다.

```python
supabase_url=supabase_url
# 왼쪽: 함수가 받는 인자 이름
# 오른쪽: 전달할 값을 담은 변수
```

## 11. Supabase Auth: 회원가입과 로그인

Supabase의 **DB 기능**과 **Auth 기능**은 구분해야 합니다. DB는 상품·주문 등의 데이터를 저장하고, Auth는 계정 인증과 토큰 발급을 담당합니다.

```python
# 회원가입 요청
supabase.auth.sign_up({
    'email': str(body.email),
    'password': body.password.get_secret_value(),
})
```

```python
# 이메일·비밀번호로 로그인
result = supabase.auth.sign_in_with_password({
    'email': str(body.email),
    'password': body.password.get_secret_value(),
})

session = result.session  # 토큰·만료 정보
user = result.user        # 사용자 ID·이메일 등의 정보
```

이메일 확인을 사용하는 경우에는 확인 메일의 링크를 눌러 이메일 소유를 확인합니다. 입력 형식 검사인 `EmailStr`과 다른 단계입니다.

### 프로젝트 키와 사용자 토큰의 차이

| 값 | 용도 |
|---|---|
| `SUPABASE_URL` | 연결할 프로젝트의 API 주소 |
| `SUPABASE_PUBLISHABLE_KEY` | 프로젝트 API를 사용하는 공개용 키 |
| Access token | 로그인한 사용자를 인증할 때 사용 |
| Refresh token | 새 토큰 발급에 사용 |
| DB host·user·password | 백엔드가 PostgreSQL에 직접 연결할 때 사용 |

**프로젝트 키는 사용자 로그인 토큰이 아니며, DB 비밀번호도 아닙니다.**

## 12. 토큰: 유효기간이 있는 인증 증표

| 항목 | 의미 |
|---|---|
| `access_token` | 인증이 필요한 요청에 사용하는 토큰 |
| `refresh_token` | 새 access token을 발급받는 데 사용하는 토큰 |
| `token_type` | 토큰 사용 방식. 일반적으로 `bearer` |
| `expires_in` | 발급 시점 기준 유효기간, 초 단위 |
| `expires_at` | 절대 만료 시각, Unix timestamp |

Access token은 **유효기간이 있는 출입증**, refresh token은 **새 출입증을 발급받기 위한 증표**라고 생각하면 됩니다. 둘 다 다른 사람이 사용하지 못하도록 보호해야 합니다.

JWT는 토큰 형식 중 하나입니다. JWT의 내용을 읽을 수 있다고 해서 유효한 토큰임이 증명되는 것은 아니며, 기본적으로 암호화된 비밀문서도 아닙니다.

## 13. Bearer 인증·`Annotated`·`Depends`

`main2.py`, `main3.py`에서는 로그인으로 받은 access token을 다음 HTTP 헤더에 넣습니다.

```http
Authorization: Bearer ACCESS_TOKEN
```

```python
from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# 헤더에서 Bearer 인증 정보를 추출하는 객체
bearer = HTTPBearer(auto_error=False)

@app.get('/me', response_model=CurrentUser)
def me(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer),
    ],
):
    # 실제 코드에서는 누락 여부 등을 확인한 후 사용
    token = credentials.credentials
    ...
```

| 기능 | 의미 |
|---|---|
| `HTTPBearer` | 헤더에서 Bearer 방식과 토큰 문자열 추출 |
| `credentials.scheme` | 인증 방식. 예: `Bearer` |
| `credentials.credentials` | 토큰 문자열 |
| `Annotated` | 타입과 추가 처리 정보를 함께 표시 |
| `Depends` | 필요한 함수를 FastAPI가 먼저 실행하고 결과 전달 |

**`HTTPBearer` 자체가 JWT의 진위와 만료를 검증하지는 않습니다.**

```python
# 추출한 토큰을 Supabase Auth에 전달해 사용자 확인
result = supabase.auth.get_user(token)
```

공통 사용자 확인 기능은 다음처럼 재사용합니다.

```python
@app.get('/me', response_model=CurrentUser)
def me(user: Annotated[CurrentUser, Depends(get_current_user)]):
    return user
```

`Depends(get_current_user)`는 “이 함수가 필요하니 먼저 실행해줘”라는 뜻입니다. `get_current_user()`처럼 즉시 호출해서 넣는 것이 아닙니다.

비유하면 음식점에서 주문을 받기 전에 직원 확인 절차를 거치고, 확인 결과를 담당자에게 넘기는 방식입니다.

## 14. 인증과 권한 관리: 누구인지와 무엇을 할 수 있는지

| 개념 | 질문 | 예시 |
|---|---|---|
| 인증 Authentication | 누구인가? | access token으로 사용자 확인 |
| 인가 Authorization | 이 작업을 할 수 있는가? | 본인 메모만 조회, 관리자만 재고 수정 |

로그인한 A와 B가 있다고 해도 A가 B의 메모나 주문을 볼 수 있어서는 안 됩니다.

### 메모 저장: 소유자는 서버가 정하기

```python
# owner_id를 요청 JSON에서 받지 않고 인증된 사용자 ID로 지정
note = Note(
    id=str(uuid4()),
    owner_id=user.id,
    content=body.content,
)
```

사용자 입력으로 소유자를 정하면 다른 사람의 ID를 넣을 수 있기 때문입니다.

### 메모 조회: SQL에서도 소유자 제한

```python
# 메모 ID와 현재 사용자 ID를 함께 조건으로 사용
row = db.execute(
    'SELECT id, owner_id, content FROM notes WHERE id = ? AND owner_id = ?',
    (note_id, user.id),
).fetchone()
```

**화면에서 다른 사람의 메모를 숨기는 것만으로는 부족합니다. 서버와 DB 조회 조건에서 접근을 제한해야 합니다.**

## 15. SQLite·SQL·트랜잭션의 기초

`main3.py`는 사용자 인증을 Supabase Auth에 맡기고, 메모는 로컬 SQLite 파일에 저장합니다. 두 기능이 반드시 같은 DB를 써야 하는 것은 아닙니다.

```python
# SQL 문장과 입력값을 분리해 전달
# SQLite의 ? 위치에 값이 안전하게 바인딩됨
conn.execute(
    'INSERT INTO notes (id, owner_id, content) VALUES (?, ?, ?)',
    (note.id, note.owner_id, note.content),
)
conn.commit()  # 변경 확정
```

사용자 값을 SQL 문자열에 직접 붙이지 않고 바인딩합니다. 쇼핑몰의 psycopg에서는 같은 목적에 `%s`를 사용합니다.

```python
# PostgreSQL + psycopg 예시. 문자열 포맷팅 연산이 아니라 DB 드라이버에 값 전달
conn.execute(
    'SELECT * FROM shoppingmall.orders WHERE user_id=%s',
    (user['id'],),
)
```

트랜잭션은 여러 DB 변경을 하나의 작업 단위로 묶는 것입니다. 쇼핑몰 결제의 재고 차감·주문 확정·결제 기록을 함께 확정하거나 함께 취소하는 데 사용합니다.

### `yield`로 연결 전달 후 정리

```python
def get_db():
    conn = sqlite3.connect(notes_db, check_same_thread=False)
    try:
        yield conn  # FastAPI가 이 연결을 API 함수에 전달
    finally:
        conn.close()  # 요청 처리 후 연결 정리
```

SQLite 연결의 `with`만으로 연결이 닫히는 것은 아닙니다. 트랜잭션 처리와 연결 종료는 구분해야 합니다. `main3.py`는 시작 시 `closing(...)`, 요청 처리 시 `finally`로 연결을 닫습니다.

## 16. 쇼핑몰 적용: 사용자 인증과 프로필을 분리하기

기존 쇼핑몰은 자체 `users` 테이블의 비밀번호 해시로 로그인했습니다. 개선한 구조는 다음과 같습니다.

| 저장소 | 담당 |
|---|---|
| Supabase Auth | 계정·비밀번호 인증·이메일 확인·토큰 |
| `shoppingmall.users` | 이름·배송지·이용 상태·역할 |
| `users.auth_user_id` | 쇼핑몰 프로필과 Auth 사용자를 연결하는 UUID |
| `shoppingmall.auth_sessions` | 쇼핑몰 서버 세션과 암호화한 Auth 토큰 |

기존 `users.id`를 유지하면 주문·결제와의 연결을 보존할 수 있습니다. 기존 회원과 새 Auth 계정은 이메일만 같다는 이유로 자동 연결하지 않고 소유권 확인 후 연결합니다.

### 역할과 소유권은 따로 검사

- 일반 회원: 자신의 장바구니·프로필·주문·결제 정보만 접근
- 관리자: 상품·재고·판매 상태와 전체 결제 주문·배송 관리
- 관리자도 고객용 주문 API에서는 본인 주문만 조회

```python
# 관리자 API를 실행하기 전에 서버가 DB 역할을 확인
if user['role'] != 'admin':
    # 실제 구현에서는 여기서 요청 진행을 중단
    ...
```

관리자 역할은 서버가 DB에서 읽습니다. 사용자가 수정할 수 있는 `user_metadata`나 요청 JSON의 `role`을 믿고 권한을 주면 안 됩니다.

### 화면 검사가 아닌 서버 검사

관리자 버튼을 숨기는 것은 화면 편의 기능입니다. 누군가는 API 주소로 직접 요청할 수 있으므로 **각 관리자 API에도 권한 검사가 필요**합니다.

또한 결제 가격·총액·재고도 사용자가 보낸 값이 아니라 서버가 DB에서 확인한 값으로 계산합니다.

## 17. 브라우저 쿠키와 서버 세션 방식

`day13`의 Bearer 학습 API와 개선한 쇼핑몰은 토큰 전달 방식이 다릅니다.

| 구분 | `day13` 학습 API | 개선한 쇼핑몰 |
|---|---|---|
| 브라우저가 사용하는 인증값 | access token | 무작위 세션 ID 쿠키 |
| 전달 방식 | Authorization 헤더 | 브라우저가 보내는 쿠키 |
| Auth 토큰 보관 | 호출자가 관리 | 서버 DB에 암호화해 보관 |
| 사용자 확인 | Supabase `get_user()` | Supabase `/user`와 쇼핑몰 프로필 확인 |

쇼핑몰은 SDK 대신 Supabase Auth HTTP API를 직접 호출합니다. 같은 Auth 기능을 사용하는 다른 호출 방식입니다.

### 쿠키 속성의 의미

- `HttpOnly`: JavaScript에서 쿠키 값을 읽지 못하게 함
- `Secure`: HTTPS 연결에서만 쿠키 전송
- `SameSite=Lax`: 다른 사이트에서 시작한 요청에 쿠키가 전송되는 범위를 제한

쿠키만 설정하면 모든 보안 문제가 해결되는 것은 아닙니다. 쇼핑몰은 변경 요청에 출처 확인과 별도 요청 헤더도 사용합니다.

### 암호화와 해시는 다름

- 세션 ID는 **해시**로 저장: 받은 쿠키와 같은 값인지 비교하면 되므로 원문 복원이 필요 없음
- Auth 토큰은 **암호화**해 저장: Supabase에 다시 보내야 하므로 복원이 필요함
- 암호화 키는 DB 토큰과 분리해 환경변수로 관리

로그아웃하면 쇼핑몰 서버의 세션을 삭제해 해당 쿠키를 재사용하지 못하게 합니다. Supabase 세션 해제도 요청하지만, 이미 발급된 JWT 자체는 만료 전까지 다른 서비스에서 유효할 수 있습니다.

## 18. 로컬 실행과 검증

### day13 서버 실행

```bash
conda activate py313
cd /Users/imijeong/Downloads/AIO_4_class/day13

# main.py의 app 실행
python -m uvicorn main:app --reload

# 현재 서버를 종료한 뒤, 학습할 다른 파일 선택
# python -m uvicorn main2:app --reload
# python -m uvicorn main3:app --reload
```

`main:app`에서 `main`은 파일 이름, `app`은 그 안의 FastAPI 객체입니다. `--reload`는 소스 변경 시 서버를 다시 실행하는 개발 옵션입니다.

- API 문서: http://127.0.0.1:8000/docs
- 다른 파일을 실행하려면 현재 서버를 `Ctrl + C`로 종료
- `.env` 변경 후에는 완전히 종료하고 다시 실행
- 같은 포트에서 여러 서버를 동시에 실행하지 않기

### 직접 확인할 정상 사용 흐름

1. 회원가입하고 필요한 경우 이메일을 확인합니다.
2. 로그인해 사용자 정보와 토큰을 받습니다.
3. Bearer 토큰을 넣어 `/me`에서 내 정보를 확인합니다.
4. `main3.py`에서는 메모를 만들고 내 메모 목록을 봅니다.
5. 다른 계정으로 로그인하면 앞 계정의 메모가 보이지 않는지 확인합니다.

쇼핑몰 실행·관리자 지정·두 계정 테스트 방법은 [쇼핑몰 로컬테스트.md](../day12/shoppingmall/로컬테스트.md)에 있습니다. 자동 검증의 모의 Auth 테스트와 실제 Supabase 로그인·메일 발송 검증은 구분해야 합니다.

## 꼭 기억할 핵심 10가지

1. **`.env`는 설정 파일, `load_dotenv()`는 불러오기, `os.getenv()`는 조회입니다.**
2. **`=`는 값 대입, `:`는 타입 표시입니다.** Pydantic이 모델의 타입 정보를 활용해 검증합니다.
3. **`rstrip()`은 끝부분 제거, `rsplit()`은 나누기입니다.** 반환 타입도 다릅니다.
4. **입력 모델은 받을 데이터, 응답 모델은 돌려줄 데이터를 정의합니다.**
5. **`SecretStr`은 출력 가리기이며 암호화나 비밀번호 해시가 아닙니다.**
6. **데코레이터는 함수를 API 경로에 등록합니다.** 실제 요청이 오면 함수가 실행됩니다.
7. **프로젝트 API 키와 사용자 access token은 다릅니다.**
8. **토큰을 추출하거나 읽는 것과 유효성을 검증하는 것은 다릅니다.**
9. **인증은 누구인지 확인, 인가는 무엇을 할 수 있는지 결정하는 것입니다.**
10. **소유자 ID·권한·결제 금액은 사용자 입력을 믿지 않고 서버가 결정합니다.**
