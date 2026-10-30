# main.py 구성과 서버 시작 흐름

현재 소스 코드를 기준으로 설명합니다. 이 문서를 작성하면서 서버 실행이나 DB 검증은 하지 않았습니다.

## python main.py만 실행해도 상품이 추가되는 이유

`cd`는 작업 폴더를 바꾸는 명령이며, DB에 데이터를 넣는 명령은 아닙니다. `python main.py`를 실행하면 다음 코드들이 연결되어 동작합니다.

```text
python main.py
    ↓
ROOT 설정, .env 읽기, 함수와 요청 모델 정의
    ↓
FastAPI 객체 생성 및 API 경로 등록
    ↓
if __name__ == '__main__': 조건 만족
    ↓
uvicorn.run(app, host='127.0.0.1', port=8000)
    ↓
FastAPI 시작 과정에서 lifespan(app) 호출
    ↓
connect()로 Supabase PostgreSQL 접속
    ↓
schema.sql 파일 전체를 읽어 conn.execute()로 실행
    ↓
스키마·테이블·인덱스 생성 및 상품 INSERT
    ↓
오류 없이 with 블록 종료 → COMMIT
    ↓
yield → 시작 준비 완료, HTTP 요청 처리
```

핵심 코드는 다음 부분입니다.

```python
@asynccontextmanager
async def lifespan(app):
    with connect() as conn:
        conn.execute((ROOT / 'schema.sql').read_text(encoding='utf-8'))
    yield

app = FastAPI(title='소소상점 API', lifespan=lifespan)
```

- `lifespan=lifespan`: 앱의 시작·종료 절차에 사용할 함수를 등록합니다.
- `@asynccontextmanager`: `yield` 앞은 시작 준비, 뒤는 종료 정리로 사용할 수 있도록 합니다. 현재 함수에는 별도의 종료 정리 코드가 없습니다.
- `ROOT / 'schema.sql'`: `main.py`와 같은 폴더에 있는 SQL 파일 경로입니다.
- `read_text(encoding='utf-8')`: SQL 파일을 문자열로 읽습니다.
- `conn.execute(...)`: 읽은 SQL 문자열을 PostgreSQL에 전달해 실행합니다.
- `with connect() as conn`: 정상 종료 시 트랜잭션을 확정하고, 예외 발생 시 되돌린 뒤 연결을 닫습니다.
- `yield`: 여기까지 초기화가 성공하면 앱이 요청을 처리하도록 넘깁니다. DB 접속 또는 SQL 실행에 실패하면 정상 시작하지 못합니다.

따라서 SQL 파일을 수정한 것만으로 실행 중인 서버나 DB가 자동으로 바뀌지는 않습니다. 현재 서버를 종료하고 재시작해야 시작 절차에서 다시 읽습니다. `uvicorn main:app`으로 실행해도 앱 시작 시 lifespan은 실행됩니다.

## 예시 데이터는 어느 테이블에 들어가나요?

`schema.sql`은 6개 테이블을 만들지만, **초기 예시 행은 products에만 INSERT**합니다. 기존 6개에 30개를 추가했으므로 파일에는 총 36개 상품이 있습니다.

| 테이블 | 서버 시작 시 하는 일 | 실제 행이 추가되는 시점 |
|---|---|---|
| users | 테이블이 없으면 생성 | 회원가입 |
| products | 테이블 생성 및 예시 상품 추가 | 앱 시작 시 SQL 실행 |
| orders | 테이블이 없으면 생성 | 처음 상품을 담아 장바구니 생성 |
| order_items | 테이블이 없으면 생성 | 상품을 장바구니에 담기 |
| payments | 테이블이 없으면 생성 | 모의 결제 성공 |
| sessions | 테이블이 없으면 생성 | 로그인 성공 |

재실행 시 상품 중복을 막는 구문은 다음과 같습니다.

```sql
ON CONFLICT (name) DO NOTHING;
```

`products.name`에 UNIQUE 제약이 있어, 같은 이름의 상품이 이미 있으면 해당 행을 건너뜁니다. 따라서 구매로 감소한 기존 재고나 수정한 가격을 초기 예시값으로 덮어쓰지 않습니다. 기존 DB 상태에 따라 전체 상품 수는 36개와 다를 수 있습니다.

`CREATE TABLE IF NOT EXISTS`도 이미 있는 테이블을 다시 만들지 않습니다. 다만 기존 테이블의 열 구조를 자동으로 변경해주는 기능은 아닙니다.

## 환경설정과 DB 연결

| 코드·함수 | 역할 |
|---|---|
| `ROOT = Path(__file__).resolve().parent` | 현재 main.py가 들어 있는 폴더의 절대 경로 |
| `load_dotenv(ROOT / '.env')` | 쇼핑몰 폴더의 .env 값을 환경변수로 읽음 |
| `load_dotenv()` | 기본 탐색 규칙으로 .env를 찾아 추가 환경변수를 읽음 |
| `connect()` | DB 연결 생성. DATABASE_URL이 있으면 우선 사용하고, 없으면 소문자 host·port·dbname·user·password 사용 |

`load_dotenv`는 기본적으로 이미 있는 환경변수를 덮어쓰지 않습니다. 기본 탐색도 가까운 .env를 먼저 찾으므로, 프로젝트 루트와 쇼핑몰 폴더에 .env가 동시에 있다면 루트 파일까지 항상 병합된다고 생각하면 안 됩니다.

DB 접속에는 SSL과 10초 연결 제한을 사용합니다. `row_factory=dict_row` 덕분에 조회한 행을 `row['name']`처럼 열 이름으로 사용할 수 있습니다.

## 입력 검증 모델

함수 실행 전에 JSON 요청의 형태와 값을 검사합니다. 규칙에 맞지 않으면 FastAPI가 422를 반환합니다.

| 모델·검증 함수 | 역할 |
|---|---|
| `Profile` / `valid_name()` | 이름·기본 배송지 입력 검증. 이름은 공백 없이 한글·영문만 허용 |
| `Signup` | Profile을 상속하고 이메일 형식과 비밀번호 8~128자 검사 추가 |
| `Login` | 로그인 이메일과 비밀번호 입력 검사 |
| `CartItem` | 상품 번호가 양수인지, 수량이 1~99의 정수인지 검사 |
| `Checkout` / `valid_address()` | 배송지 길이와 공백만 입력했는지 검사하고 앞뒤 공백 제거 |

## 인증과 공통 처리 함수

| 함수 | 역할 |
|---|---|
| `password_hash()` | 솔트를 포함한 PBKDF2 비밀번호 해시 생성. 로그인 시 저장된 솔트로 재계산 |
| `token_hash()` | 세션 토큰을 SHA-256 해시로 변환 |
| `current_user()` | 요청 쿠키의 토큰으로 세션·회원 조회. 미로그인·만료·탈퇴 상태면 401 |
| `lock_user()` | 활성 회원 행을 FOR UPDATE로 잠가 같은 회원의 동시 변경을 순서대로 처리 |
| `get_cart()` | 회원의 cart 주문 번호 조회. 없으면 생성해 번호 반환 |
| `csrf_check()` | 변경 요청의 Origin·Sec-Fetch-Site를 확인해 다른 출처 요청을 차단하고, API 응답에 캐시 금지 설정 |

예를 들어 `user=Depends(current_user)`는 해당 API를 실행하기 전에 `current_user()`를 실행하고, 반환된 회원 정보를 `user`에 넣으라는 뜻입니다. 인증이 실패하면 API 본문은 실행되지 않습니다.

## 화면·회원·상품 API 함수

| 함수 | 요청 | 하는 일 |
|---|---|---|
| `index()` | GET / | static/index.html 반환 |
| `health()` | GET /health | 서버 응답 상태 확인. DB를 따로 조회하지는 않음 |
| `signup()` | POST /api/signup | 비밀번호를 해시로 바꿔 회원 저장. 성공 201, 이메일 중복 409 |
| `login()` | POST /api/login | 비밀번호 확인, 랜덤 토큰·세션 생성, HttpOnly 쿠키 설정 |
| `logout()` | POST /api/logout | 현재 세션과 브라우저 쿠키 삭제 |
| `me()` | GET /api/me | 로그인 회원의 번호·이름·이메일·주소 반환 |
| `update_me()` | PATCH /api/me | 회원 이름과 기본 배송지 수정 |
| `delete_me()` | DELETE /api/me | 회원 비활성화·개인정보 익명화, 세션·장바구니 삭제, 과거 주문 배송지 제거 |
| `products()` | GET /api/products | 상품 목록 조회 |

`app.mount('/static', ...)`는 CSS·JavaScript 같은 정적 파일을 제공하는 설정입니다. 화면의 JavaScript가 `/api/...`로 요청하고, Python 함수가 DB를 읽거나 변경한 뒤 JSON으로 응답합니다.

## 장바구니·결제 API 함수

| 함수 | 요청 | 하는 일 |
|---|---|---|
| `cart()` | GET /api/cart | orders·order_items·products를 연결해 현재 장바구니 조회 |
| `add_cart()` | POST /api/cart | 상품 존재·재고·수량 확인, cart 생성 또는 재사용, 주문상품 추가 또는 수량 합산 |
| `remove_cart()` | DELETE /api/cart/{product_id} | 현재 회원 장바구니의 해당 상품 행 삭제 |
| `checkout()` | POST /api/checkout | 재고·가격 재확인, 재고 차감, 구매 가격 확정, 주문을 paid로 변경하고 모의 결제 기록 생성. 성공 201 |
| `orders()` | GET /api/orders | 현재 회원의 paid 주문과 각 주문상품 조회 |

`checkout()`의 변경들은 하나의 트랜잭션으로 처리됩니다. 중간에 재고 부족 등으로 실패하면 앞서 실행한 재고 차감까지 모두 되돌립니다. 실제 결제사에 청구하지는 않습니다.

상품 구매를 테이블의 예시 행으로 따라가려면 [상품구매시뮬레이션.md](상품구매시뮬레이션.md)를 참고하세요.
