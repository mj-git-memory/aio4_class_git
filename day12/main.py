from getpass import getpass

import psycopg
import uvicorn
from fastapi import APIRouter, FastAPI, Request
from psycopg.rows import dict_row
# 변경 전: from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator  # 수정: 이메일 및 필드 검증 추가

import os
import re  # 수정: 이름에 허용된 문자만 있는지 검사
from dotenv import load_dotenv # python3 -m pip install python-dotenv
load_dotenv()

app = FastAPI(title="사용자 등록·조회 실습")
router = APIRouter(tags=["users. 사용자 관리"])
# APIRouter(...) : 관련 API 경로를 모아 둘 라우터 객체를 생성
# tags=["users"] : Swagger 문서에서 해당 API들을 users라는 그룹으로 표시하는 설정


# 변경 전: 두 필드 모두 문자열 길이만 검증
# class UserCreate(BaseModel):
#     model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
#     name: str = Field(min_length=1, max_length=50)
#     email: str = Field(min_length=1, max_length=100)
class UserCreate(BaseModel): 
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid") 
    # str_strip_whitespace=True : 문자열의 앞뒤 공백을 제거하도록 설정. extra="forbid" : 정의하지 않은 추가 필드가 들어오면 거부
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=100)  # 수정: 이메일 형식 검증 (email-validator 패키지 필요)

    # 변경 전: @field_validator("name")
    @field_validator("name", mode="before")  # 수정: 자동 공백 제거 전에 원래 입력을 검사
    # -> name을 검증할 때 이 함수를 자동으로 호출해라. 기본 타입 검증과 공백 제거보다 먼저 실행해라
    # mode="before" 덕분에 " 김하늘 "이 자동으로 "김하늘"로 바뀌기 전에 공백을 발견하고 거부
    @classmethod
    def validate_name(cls, value: str) -> str: # 이름에 허용하지 않는 문자가 있는지 검사
        # 수정: 문자열이 아닌 입력은 아래의 str 타입 검증에 맡김
        if not isinstance(value, str):
            return value
        # 수정: 한글·영문만 허용하며 앞뒤·중간 공백, 탭, 줄바꿈도 거부
        if re.fullmatch(r"[가-힣ㄱ-ㅎㅏ-ㅣA-Za-z]+", value) is None:
            raise ValueError("이름에는 공백 없이 한글과 영문만 사용할 수 있습니다.")
        return value


def initialize_database(db_config):
    with psycopg.connect(**db_config) as conn:  # **db_config 딕셔너리 타입을 풀어서 넣어줌?
        conn.execute("CREATE SCHEMA IF NOT EXISTS kdt_api01;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kdt_api01.users (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)


def get_connection(request: Request):
    return psycopg.connect(
        **request.app.state.db_config, 
        # **request.app.state.db_config는 앱에 저장해 둔 DB 접속 딕셔너리를 풀어 전달
        row_factory=dict_row, # row_factory=dict_row는 조회 결과의 각 행을 딕셔너리로 받도록 설정
    )
# request :	현재 들어온 HTTP 요청
# request.app :	그 요청을 처리하는 FastAPI 앱
# request.app.state : 앱에서 공유할 값을 보관하는 공간
# request.app.state.db_config :	앞서 app.state.db_config = db_config로 저장한 접속 정보

# # 예: SELECT id, name, email FROM ...
# # 기본 결과: 튜플
# (1, "홍길동", "hong@example.com")
# # row_factory=dict_row 설정 결과: 딕셔너리
# {"id": 1, "name": "홍길동", "email": "hong@example.com"}

@router.post("/users", status_code=201) # POST /users 경로를 router에 등록
def create_user(user: UserCreate, request: Request):
    with get_connection(request) as conn:
        row = conn.execute(
            """
            INSERT INTO kdt_api01.users (name, email)
            VALUES (%s, %s)
            RETURNING id, name, email;
            """,
            # 변경 전: (user.email, user.name),
            (user.name, user.email), # 수정: INSERT 열 (name, email)과 전달 값의 순서를 일치시킴
        ).fetchone()
    return row
    # 그래서 조회한 값을 row["name"]처럼 열 이름으로 꺼낼 수 있고, FastAPI에서 JSON 응답으로 반환하기에도 편리


@router.get("/users") # GET /users 경로를 router에 등록
def list_users(request: Request):
    with get_connection(request) as conn:
        rows = conn.execute("""
            SELECT id, name, email
            FROM kdt_api01.users
            ORDER BY id;
        """).fetchall()
    return rows


app.include_router(router) # 라우터에 등록한 경로들을 실제 FastAPI 앱에 연결

# GET /users  ─┐
#              ├─ router ── app.include_router(router) ── app
# POST /users ─┘

# -> app.include_router(router)가 없어도 서버는 실행. 
# -> 하지만 이 라우터의 /users 경로가 앱에 연결되지 않아서, 
# -> 접속하면 404 Not Found가 나오고 Swagger에도 해당 API가 표시되지 않습음 


if __name__ == "__main__":  # “이 파일을 직접 실행했을 때만 아래 코드를 실행 (__name__ 값이 "__main__"이므로 조건이 참)
    db_config = {
        "host": os.getenv('host'),
        "port": os.getenv('port'),
        "dbname": os.getenv('dbname'),
        "user": os.getenv('user'),
        "password": os.getenv('password'),
        "sslmode": "require",
        "connect_timeout": 10,
    }
    initialize_database(db_config)
    app.state.db_config = db_config
    print("DB 준비 완료. http://127.0.0.1:8000/docs 에 접속하세요.")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # -> 위에 명령어 써줘서 아래처럼 실행 안해도 됨
    # python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
    # : main.py에 있는 FastAPI 앱을 Uvicorn 서버로 실행한다는 뜻

    # python -m uvicorn main:app으로 실행하면 Uvicorn이 main.py를 import
    # : main.py 모듈을 import하고, 그 안의 app 객체를 가져와 서버를 실행하는 명령
    # 이때 main.py의 __name__ 값은 "main"이라서 조건이 거짓 (if __name__ == "__main__":)
    # Uvicorn은 서버를 켜지만, 앱에는 db_config가 저장되지 않음 
    # 이후 /users에서 다음 줄을 사용하면 오류가 발생 
    # -> request.app.state.db_config  # 저장된 값이 없음
    ### 지금 코드에서는 초기화부터 서버 실행까지 이어지도록 python main.py를 사용하라는 의미
   
    # python -m uvicorn	: 현재 Python 환경에 설치된 Uvicorn 실행
    # main:app : main.py 파일의 app 객체 사용
    # --host 127.0.0.1 : 내 컴퓨터에서 접속할 주소에 서버 실행
    # --port 8000 : 8000번 포트 사용
    # --workers 1 :	요청을 처리하는 서버 프로세스를 1개 실행  # worker는 요청을 처리하는 서버 프로세스
    # --workers 1은 프로세스를 하나 띄운다는 의미이며, 동시에 요청을 하나만 처리한다는 뜻은 아님


db_config = {
    "host": "db.example.com",
    "port": "5432",
    "dbname": "postgres",
    "user": "test_user",
    "password": "example_password",
    "sslmode": "require",
    "connect_timeout": 10,
}
psycopg.connect(**db_config)
# **db_config : 딕셔너리를 풀어서 함수의 키워드 인자로 전달하는 문법
# -> 딕셔너리의 키를 인자 이름으로, 값을 인자 값으로 전달하는 기능
psycopg.connect(
    host="db.example.com",
    port="5432",
    dbname="postgres",
    user="test_user",
    password="example_password",
    sslmode="require",
    connect_timeout=10,
)
# print(**db_config)로 확인하는 방식은 사용할 수 없음
# -> print()는 host, port 같은 인자를 받지 않기 때문



# app = FastAPI() 
# ### 앱 : 요청을 받아 응답하는 프로그램
# # -> FastAPI() : 웹 요청을 처리할 애플리케이션 객체를 만듦(여기서는 사용자 등록과 조회 기능을 제공하는 프로그램)
# # -> app : 그 객체에 붙인 변수 이름일 뿐
# # AA = FastAPI()
# # AA.include_router(router)
# # python -m uvicorn main:AA

# ### API : 다른 프로그램이 기능을 요청하는 약속
# # POST /users -> 사용자를 등록한다
# # GET /users  -> 사용자 목록을 돌려준다
# # 브라우저 화면, 모바일 앱, 다른 서버 등이 이 약속대로 요청하면 우리 프로그램의 기능을 사용할 수 있음 

# ### API 경로 : 요청을 보낼 주소에서 기능을 구분하는 부분
# # http://127.0.0.1:8000/users
# # └──── 서버 주소 ─────┘└ 경로 ┘
# # 어떤 동작인지는 경로뿐 아니라 HTTP 메서드까지 함께 봐야 함
# # POST + /users → 등록
# # GET  + /users → 조회

# ### 라우터 : 관련 요청 경로를 묶어 두는 객체
# router = APIRouter(tags=["users"])  # tags=["users"]는 Swagger 화면의 그룹 제목
# router = APIRouter(tags=["사용자 관리"]) # Swagger의 그룹 제목이 사용자 관리로 바뀜

# # -> 이 코드는 라우터를 만듦. 다음 코드로 “어떤 요청이 오면 어떤 함수를 실행할지” 등록
# @router.post("/users")
# # -> POST /users를 router에 등록
# def create_user():
#     return {"message": "사용자 등록"}
# # -> POST /users 요청이 오면 create_user()를 실행하도록 등록

# @router.get("/users")
# # -> GET /users를 router에 등록 
# def list_users():
#     return {"message": "사용자 목록 조회"}
# # -> GET /users 요청이 오면 list_users()를 실행하도록 등록

# app.include_router(router)
# # -> router에 등록해 둔 POST /users와 GET /users를 앱에 연결
# # -> 주소는 같지만 요청 방식이 달라서 서로 다른 기능으로 구분

# # ① router에 등록                ② app에 연결

# # POST /users ─┐
# #              ├─ router ──────────→ app
# # GET /users  ─┘          include_router(router)


# # 클라이언트가 GET /users 요청
# #             ↓
# # Uvicorn이 요청을 받아 FastAPI 앱에 전달
# #             ↓
# # 앱이 등록된 경로와 메서드를 확인
# #             ↓
# # list_users() 실행
# #             ↓
# # 실행 결과를 응답으로 전달
