### Redis에 연결해서 데이터 저장 → 조회 → 자동 만료 → 직접 삭제를 실습하는 코드

import os
import redis
from dotenv import load_dotenv

import uuid  # uuid는 고유한 식별자(ID)를 만드는 파이썬 기본 모듈
import time

load_dotenv()

host = os.getenv("REDIS_HOST")
port_text = os.getenv("REDIS_PORT")
port = int(port_text) 

key = f'day14:message:{uuid.uuid4().hex}' # 매번 실행할 때 마다 다른 키를 생성 
        # uuid.uuid4(): 무작위 UUID 생성. 같은 값이 나올 가능성이 매우 낮음 
with redis.Redis(
    host=host,
    port=port,
    decode_responses=True, # 바이트(bytes)가 아닌 문자열(str)로 반환
    socket_connect_timeout=2, # 연결 설정 2초 제한 
    socket_timeout=2, # 연결 후 응답 2초 제한 (읽기 쓰기 제한시간 2초)
) as client : 
    print(f'PING : {client.ping()}') # Redis 서버에 연결 확인
    
    client.set(key, 'Redis 연결 성공')
    print(f'저장 후 GET : {client.get(key)}') # 저장 후 GET : Redis 연결 성공
    print(f'TTL : {client.ttl(key)}') # TTL : -1 (만료시간 없음)

    client.set(key, '잠시 보관할 메시지', ex=2)
    print(f'저장 후 GET : {client.get(key)}') # 저장 후 GET : 잠시 보관할 메시지
    print(f'TTL : {client.ttl(key)}') # TTL : 2

    time.sleep(3) # 3초 대기
    print(f'저장 후 GET : {client.get(key)}') # 저장 후 GET : None
    print(f'TTL : {client.ttl(key)}') # TTL :  -2

    client.set(key, '삭제할 메시지', ex=30) # ex=30은 비정상 종료 시 잔여키를 줄임
    print(f'DELETE 개수: {client.delete(key)}') # DELETE 개수: 1
    print(f'삭제 후 GET: {client.get(key)}') # 삭제 후 GET: None