### 

import os
import redis
from dotenv import load_dotenv

import uuid  # uuid는 고유한 식별자(ID)를 만드는 파이썬 기본 모듈
import time

load_dotenv()

host = os.getenv("REDIS_HOST")
port_text = os.getenv("REDIS_PORT")
port = int(port_text) 

prefix = f'day14:message:{uuid.uuid4().hex}' # 매번 실행할 때 마다 다른 키를 생성 
            # uuid.uuid4(): 무작위 UUID 생성. 같은 값이 나올 가능성이 매우 낮음 
string_key = f'{prefix}:status'
hash_key = f'{prefix}:profile'
list_key = f'{prefix}:messages'

with redis.Redis(
    host=host,
    port=port,
    decode_responses=True, # 바이트(bytes)가 아닌 문자열(str)로 반환
    socket_connect_timeout=2, # 연결 설정 2초 제한 
    socket_timeout=2, # 연결 후 응답 2초 제한 (읽기 쓰기 제한시간 2초)
) as client : 
    print(f'PING : {client.ping()}') # Redis 서버에 연결 확인

    try : 
        client.set(string_key, 'ready', ex=60)
        added =client.hset(
            hash_key, # 사용자 프로필을 담을 키
            mapping={
                'name': 'hongildong',
                'level': 'basic'}
                )
        client.expire(hash_key, 60) # 해시 키에 만료시간 설정
        print(f'hash의 새 필드 수: {added}')
        print(f'hash의 이름: {client.hget(hash_key, "name")}')
        client.hset(hash_key, 'level', 'practice') # 해시 키의 필드 값 변경
        print(f'hash 전체: {client.hgetall(hash_key)}')

    except Exception as e : 
        print(f'에러 발생: {e}')
