# docker run -d --name kdt-hybrid-redis -p 127.0.0.1:6379:6379 redis redis-server --save '' --appendonly no
# -> 내 컴퓨터에서 접속할 수 있는 Redis를 백그라운드로 실행하되, 데이터를 디스크에 자동 저장하지 않는 설정. (--save '')
# -> 이 설정에서는 Redis 서버가 종료되면 메모리에 있던 데이터를 복구할 수 없음 (--appendonly no)

# -> Docker 옵션은 이미지 이름인 redis 앞에, Redis 서버 옵션은 redis-server 뒤에 붙음
# -p 127.0.0.1:6379:6379
#    └───┬───┘ └┬┘ └┬┘
#      내 PC    내 PC  컨테이너
#       주소     포트    포트
# -> PC의 127.0.0.1:6379로 접속하면 컨테이너의 6379 포트로 연결됨
# -> 127.0.0.1은 자기 컴퓨터를 뜻하며, 이렇게 지정하면 해당 컴퓨터에서 접속하도록 제한

## 1. 전체 구조 & 2. Docker 부분
# -> docker run [Docker 옵션] 이미지이름 [컨테이너 안에서 실행할 명령어와 옵션]
# docker                        # : Docker 프로그램을 사용
#   run \                       # : 이미지로 새 컨테이너를 만들고 실행
#   -d \                        # : --detach의 줄임말. 백그라운드에서 실행하여 터미널을 계속 사용할 수 있게 함
#   --name kdt-hybrid-redis \   # : 컨테이너 이름을 kdt-hybrid-redis로 지정
#   -p 127.0.0.1:6379:6379 \    # -p : --publish의 줄임말. 내 컴퓨터의 6379 포트를 컨테이너의 6379 포트에 연결
#   redis \                     # : 실행에 사용할 Docker 이미지 이름
#   redis-server \              # : 컨테이너 안에서 Redis 서버를 실행하는 프로그램
#   --save '' \                 # : 주기적인 RDB 스냅샷 저장 끄기 (서버 시작 시 설정하는 옵션) 
#   --appendonly no             # : AOF 변경 기록 저장 끄기
# -> Docker로 Redis 서버를 백그라운드에서 실행하고, 내 컴퓨터의 6379 포트로 접속할 수 있게 하는 명령어

## 3. Redis의 저장 옵션
# -> Redis는 주로 메모리(RAM)에 데이터를 저장. 서버를 다시 시작했을 때 데이터를 복구하려면 디스크 저장 기능을 설정
#  옵션 예시	            뜻
# --save "60 1"	        60초 동안 데이터 변경이 1번 이상 있으면 전체 데이터의 스냅샷을 저장하도록 설정
# --save ""	            주기적인 스냅샷 저장을 끔
# --appendonly yes	    데이터를 변경하는 명령을 파일에 기록하는 AOF 저장을 켬
# --appendonly no	    AOF 저장을 끔
# -> RDB 스냅샷은 특정 시점의 전체 데이터를 찍어 저장하는 방식
# -> **AOF(Append Only File)**는 데이터 변경 명령을 기록하여 복구에 사용하는 방식이


### 이 코드는 /health에 요청이 오면 Supabase PostgreSQL과 Redis에 접속해서, 두 서비스가 정상적으로 응답하는지 확인하는 API
# GET /health 요청
#     ↓
# PostgreSQL에 SELECT 1 실행
#     ↓
# Redis에 PING 실행
#     ↓
# 둘 다 정상이면 HTTP 200
# 하나라도 실패하면 HTTP 503

## fastapi에서 supabase postgreSQL과 Redis의 응답을 확인 
import os
import psycopg # supabase 
from redis import Redis, RedisError

# .env http json
from dotenv import load_dotenv 
from fastapi import FastAPI
from fastapi.responses import JSONResponse
load_dotenv(override=True)

DB_URL = os.getenv('SUPABASE_DB_URL', '')
# DB_URL = os.getenv('SUPABASE_DB_URll', '') # 일부로 없는 값 써봄
REDIS_URL = os.getenv('REDIS_URL', '')

if not DB_URL :
    raise RuntimeError('SUPABASE_DB_URL 설정 확인')
    # raise RuntimeError

if not REDIS_URL :
    raise RuntimeError('REDIS_URL 설정 확인')

# backend api 
app = FastAPI()

# api 동작 확인 
@app.get('/health')
def health() : 
    checks = {'supabase':'down', 'redis':'down'}
    
    try : 
        with psycopg.connect(
            DB_URL,
            connect_timeout=5,
            sslmode='require' #,
        ) as conn : 
            with conn.cursor() as cur : # sql 실행과 결과 담당 
                cur.execute('SELECT 1 AS ok')

                row = cur.fetchone() # 기본 반환형은 튜플 (1,)
                print(f'row = {row}')
                
                if row == (1,) : 
                    checks['supabase'] = 'up'
    except psycopg.Error : 
        pass 

    try : 
        with Redis.from_url(
            REDIS_URL,
            socket_connect_timeout = 3,
            socket_timeout = 3,
        ) as client : 
            if client.ping() :
                checks['redis'] = 'up'
    except (RedisError, ValueError) : 
        pass 

    ready = all(value == 'up' for value in checks.values())
    return JSONResponse( # JSONResponse : 문자열로 리턴 
        status_code = 200 if ready else 503,
        content= {'ready': ready, 'checks':checks}
    ) 

## 실행 명령어
# python -m uvicorn main1:app --host 127.0.0.1 --port 8000



from pydantic import BaseModel, ConfigDict, Field
from fastapi import HTTPException

class ConversationCreate(BaseModel) : 
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True) # str_strip_whitespace=True : 문자열 양끝의 공백 제거
    title:str = Field(min_length=1, max_length=100)

class MessageCreate(BaseModel) : 
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True) 
    content:str = Field(min_length=1, max_length=1000)

from psycopg.rows import dict_row # 컬럼을 딕셔너리 형으로 받음 
def connect_db() : 
    # 호출한 쪽의 with 정상 -> commit / 예외 -> rollback / 연결 종료 담당
    return psycopg.connect(
        DB_URL,
        connect_timeout=5,
        sslmode='require',
        row_factory=dict_row # 기본 튜플 대신에 {컬럼:값} 형태로 읽음
    )

def init_db() :
    with connect_db() as conn : 
        conn.execute('CREATE SCHEMA IF NOT EXISTS kdt_hybrid;')
        conn.execute('''
                        CREATE TABLE IF NOT EXISTS kdt_hybrid.conversation (
                            id uuid PRIMARY KEY,
                            title varchar(100) NOT NULL CHECK(length(trim(title))> 0),
                            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                    ''')
        conn.execute('''
                        CREATE TABLE IF NOT EXISTS kdt_hybrid.message (
                            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            conversation_id uuid NOT NULL 
                                REFERENCES kdt_hybrid.conversation(id), -- kdt_hybrid.conversation의 id를 참조 
                            content varchar(1000) NOT NULL CHECK(length(trim(content))> 0), -- trim(content) : 좌우 공백 제거 
                            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP 
                        );
                    ''')
    print('테이블 준비 완료')
init_db() # 추가: 실제로 스키마와 테이블 생성 실행

@app.exception_handler(psycopg.Error)
def database_error(_request, _exc) : 
    # FastAPI가 전달하는 요청 / 예외는 여기서 출력하지 않음. 모든 오류를 잡지는 않음
    return JSONResponse(
        status_code=503, # 서비스 이용 불가
        content={'detail':'db 처리에 실패했습니다. 연결 정보와 테이블 상태를 확인하세요.'}
    )

from uuid import UUID, uuid4
@app.post('/conversations', status_code=201) # 성공시 201 반환 (디폴트는 200 반환)
def create_conversation(body: ConversationCreate) : 
    conversation_id = uuid4() 
    with connect_db() as conn : 
        row = conn.execute('''
                        INSERT INTO kdt_hybrid.conversation(id, title)
                        VALUES(%s, %s) RETURNING id, title, created_at
                        ''',
                        (conversation_id, body.title),
                        ).fetchone() # returning이 돌려준 행 하나를 읽음
        return row

# 전체 데이터를 반환하는 구조여서, 소량의 데이터일 때만 사용
@app.get('/conversations')
def list_conversation() :
    with connect_db() as conn : 
        rows = conn.execute('SELECT id, title, created_at FROM kdt_hybrid.conversation ORDER BY created_at, id'
                     ).fetchall()
        return rows


@app.post('/conversation/{conversation_id}/messages', status_code= 201) 
def create_messages(conversation_id:UUID, body:MessageCreate) :
    with connect_db() as conn : 
        found = conn.execute(
            'SELECT id FROM kdt_hybrid.conversation WHERE id = %s', (conversation_id, )
        ).fetchone()
        if found is None :
            raise HTTPException(status_code=404, detail='대화방을 찾을 수 없습니다.')
        row = conn.execute('''
                            INSERT INTO kdt_hybrid.message(conversation_id, content)
                            VALUES(%s, %s) RETURNING id, conversation_id, content
                        '''
                        , (conversation_id, body.content), ).fetchone()
        return row 

@app.get('/conversation/{conversation_id}/messages', status_code=201)
def list_messages() :
    with connect_db() as conn : 
        rows = conn.execute('SELECT id, content, created_at FROM kdt_hybrid.message ORDER BY created_at, id').fetchall()
        return rows 