### 이 코드는 대화방에 연결되는 임시 세션을 만들고, 유효 시간이 남아 있는지 조회하는 API
### 데이터는 PostgreSQL 대신 Redis에 저장


"""3교시: Redis에 만료되는 대화 세션을 발급하고 조회한다."""
import os
from uuid import UUID, uuid4  # 대화방 ID 검사와 세션 ID 생성에 사용한다.

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from redis import Redis, RedisError

# 현재 폴더의 .env를 읽되 기존 환경변수와 ${...} 원문을 보존한다.
load_dotenv(override=False, interpolate=False)
REDIS_URL = os.getenv("REDIS_URL", "")
TTL_TEXT = os.getenv("SESSION_TTL_SECONDS", "")

if not REDIS_URL.strip():
    raise RuntimeError("REDIS_URL 설정이 필요합니다.")
if not REDIS_URL.startswith(("redis://", "rediss://")):
    raise RuntimeError("REDIS_URL의 연결 방식을 확인하세요.")
if not TTL_TEXT.strip():
    raise RuntimeError("SESSION_TTL_SECONDS 설정이 필요합니다.")
try:
    SESSION_TTL_SECONDS = int(TTL_TEXT)  # .env의 문자열을 초 단위 정수로 바꾼다.
except ValueError:
    raise RuntimeError("SESSION_TTL_SECONDS는 양의 정수여야 합니다.") from None
if SESSION_TTL_SECONDS <= 0:
    raise RuntimeError("SESSION_TTL_SECONDS는 양의 정수여야 합니다.")


app = FastAPI()

class SessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 오타 등 알 수 없는 필드를 거절한다.
    conversation_id: UUID  # UUID 형식만 검사한다. 이 차시에는 DB 연결이 없다.

def connect_redis():
    # 호출한 쪽이 with로 닫는다. URI 해석 뒤 실제 명령에서 서버와 통신한다.
    return Redis.from_url(
        REDIS_URL,
        decode_responses=True,  # GET 결과를 bytes 대신 문자열로 읽는다. 기본은 False다.
        socket_connect_timeout=3,  # 연결 수립 대기 제한(초).
        socket_timeout=3,  # 소켓 응답 대기 제한(초). 전체 HTTP 제한이 아니다.
    )

# Redis 통신/인증 오류 때만 실행되는 오류 처리기를 등록한다.
@app.exception_handler(RedisError)
def redis_error(_request, _exc):
    return JSONResponse(status_code=503, content={"detail": "Redis 연결을 확인하세요."})


@app.post("/sessions", status_code=201)
def create_session(body: SessionCreate):
    session_id = str(uuid4())  # 클라이언트에 돌려줄 새 세션 ID. 대화방 ID와 다르다.
    key = f"kdt:hybrid:l03:session:{session_id}"  # 다른 차시와 키를 구분한다.
    with connect_redis() as client:
        client.set(
            key,  # 저장할 Redis 키.
            str(body.conversation_id),  # 값은 대화방 ID 하나만 보관한다.
            ex=SESSION_TTL_SECONDS,  # SET과 만료 설정을 한 명령으로 실행한다. 단위는 초.
        )
    return {"session_id": session_id, "expires_in": SESSION_TTL_SECONDS}


@app.get("/sessions/{session_id}")
def read_session(session_id: UUID):
    # 경로 UUID를 문자열로 정규화해야 발급 때 사용한 키와 일치한다.
    key = f"kdt:hybrid:l03:session:{session_id}"
    with connect_redis() as client:
        conversation_id = client.get(key)  # 없는 키는 None이다. 조회로 TTL을 늘리지 않는다.
        ttl = client.ttl(key)  # 남은 초. -2는 키 없음, -1은 만료 설정 없음이다.
    if conversation_id is None or ttl == -2:
        raise HTTPException(status_code=401, detail="세션이 없거나 만료되었습니다.")
    if ttl == -1:
        raise HTTPException(status_code=503, detail="세션 만료 설정을 확인하세요.")
    return {"session_id": str(session_id), "conversation_id": conversation_id, "ttl": ttl}



## 1. 세션을 쉽게 이해하면
# -> 대화방 ID는 방 번호, 세션 ID는 유효 시간이 있는 임시 이용권 번호라고 생각
# 대화방 ID: A
#     ↓ 세션 발급
# 세션 ID: B / 유효 시간: 300초
#     ↓ Redis에 저장
# B → A
# -> 이후 세션 ID B로 조회하면 연결된 대화방 A와 남은 시간을 알 수 있음. 300초가 지나면 Redis가 해당 데이터를 자동으로 만료시킴 
# -> 이 코드는 대화방이나 메시지를 생성하지 않음. 전달받은 대화방 ID와 임시 세션 ID의 연결만 저장
# -> DB에 접속하지 않으므로 대화방이 실제로 존재하는지는 확인하지 않음

## 2. 제공하는 API 두 가지
# API	                        기능
# POST /sessions	            새 세션 발급
# GET /sessions/{session_id}	세션 조회 및 남은 시간 확인
# 세션 생성 요청 예시:
# {
#   "conversation_id": "428d9e12-1c8b-451e-b308-d4cc87910039"
# }
# -> 서버는 새 세션 ID를 만들고 Redis에 다음 구조로 저장
# 키: kdt:hybrid:l03:session:새로운세션ID
# 값: 428d9e12-1c8b-451e-b308-d4cc87910039
# 만료: 300초 후
# 생성 응답은 다음 형태
# {
#   "session_id": "새로운세션ID",
#   "expires_in": 300
# }
# 이 응답의 session_id로 조회하면:
# {
#   "session_id": "새로운세션ID",
#   "conversation_id": "428d9e12-1c8b-451e-b308-d4cc87910039",
#   "ttl": 280  # ttl이 280이면 만료까지 약 280초가 남았다는 뜻입
# }

## 3. 환경설정을 읽는 함수
# load_dotenv(override=False, interpolate=False)
# -> .env 파일에서 환경설정을 불러옴 
# -> - override=False: 이미 설정된 환경변수를 덮어쓰지 않음
# -> - interpolate=False: ${...} 형태를 다른 환경변수 값으로 치환하지 않음

## 4. 요청 데이터를 검사하는 클래스
# class SessionCreate(BaseModel):
#     model_config = ConfigDict(extra="forbid")
#     conversation_id: UUID
# -> 이 클래스는 클라이언트가 보내는 JSON의 규칙
# 코드	                    의미
# BaseModel	               Pydantic의 데이터 검증 기능 사용
# extra="forbid"	       정의하지 않은 필드를 보내면 거절
# conversation_id: UUID	   대화방 ID가 UUID 형식인지 검사

## 5. Redis 클라이언트를 만드는 함수
# def connect_redis():
#     return Redis.from_url(
#         REDIS_URL,
#         decode_responses=True,
#         socket_connect_timeout=3,
#         socket_timeout=3,
#     )
# -> connect_redis() : Redis 명령을 실행할 클라이언트 객체를 만듦
# 옵션	                        기능
# Redis.from_url()	           URL에 들어 있는 주소·포트 등의 정보로 클라이언트 생성
# decode_responses=True	       조회 결과를 bytes 대신 Python 문자열로 반환
# socket_connect_timeout=3	   연결 수립 대기 시간 제한
# socket_timeout=3	           명령 응답 대기 시간 제한
# with connect_redis() as client:
# -> with 안에서 클라이언트를 사용하고, 블록을 나올 때 관련 자원을 정리. 실제 서버 통신은 set(), get() 같은 명령을 실행할 때 이루어짐

## 6. 세션을 생성하는 함수
# @app.post("/sessions", status_code=201)
# def create_session(body: SessionCreate):
# -> POST /sessions 요청을 처리. body에는 검증된 요청 데이터가 들어 있음
# session_id = str(uuid4()) # uuid4(): 새로운 임의 UUID 생성
# key = f"kdt:hybrid:l03:session:{session_id}"
# -> Redis에 저장할 키를 만듦. 앞부분은 다른 데이터와 구별하기 위한 이름표. :는 여기서 키 이름을 읽기 쉽게 나누는 구분자
# client.set(
#     key,   # key → 대화방 ID
#     str(body.conversation_id),
#     ex=SESSION_TTL_SECONDS,  # ex는 만료 시간을 초 단위로 지정
# )
# -> set()은 키와 값을 저장하는 함수  

## 7. 세션을 조회하는 함수
# @app.get("/sessions/{session_id}")
# def read_session(session_id: UUID):
# -> URL에서 세션 ID를 받아 UUID 형식을 검사한 뒤 조회
# conversation_id = client.get(key)
# ttl = client.ttl(key)
# 함수	      기능
# get(key)	저장된 대화방 ID를 읽음. 키가 없으면 None
# ttl(key)	키의 남은 유효 시간을 초 단위로 확인   # TTL은 Time To Live, 즉 남은 유효 시간을 뜻함
# TTL 결과	    의미
# 0 이상	    만료까지 남은 초
# -2	       키가 없음 또는 이미 만료됨
# -1	       키는 있지만 만료 시간 설정이 없음
# raise HTTPException(status_code=401, ...)
# -> 세션이 없거나 만료됐으면 요청 처리를 중단하고 401을 반환
# raise HTTPException(status_code=503, ...)
# -> 만료 설정이 없는 세션이라면 코드에서 기대한 상태가 아니므로 503을 반환

## 8. Redis 오류를 처리하는 함수
# @app.exception_handler(RedisError)   # exception_handler() : **app 객체에 속한 메서드(함수)**
# -> 아래 함수를 RedisError가 발생했을 때 실행할 오류 처리 함수로 등록
# -> @는 데코레이터 문법. 아래 함수에 역할을 붙여주는 방식
# -> “요청을 처리하다가 RedisError가 발생하면, 아래의 redis_error()를 실행해 줘.”
# -> exception_handler()가 Redis 오류를 발생시키는 것은 아니고, 오류 발생 시 사용할 처리 함수를 지정하는 역할
# def redis_error(_request, _exc):   # redis_error(): 오류가 발생하면 실제로 실행되어 응답을 만드는 함수
#     return JSONResponse(
#         status_code=503,
#         content={"detail": "Redis 연결을 확인하세요."}
#     )
# -> 요청 처리 중 Redis 관련 오류가 발생하면 JSON 형태의 503 응답으로 바꿈 
# 상태 코드	     이 코드에서의 의미
# 201	      세션 생성 성공
# 200	      유효한 세션 조회 성공
# 401	      세션이 없거나 만료됨
# 422	      요청 데이터의 형식이 잘못됨
# 503	      Redis 처리 오류 또는 세션 만료 설정 이상
# -> 여기서 만든 세션은 대화방 ID를 잠시 보관하는 용도
