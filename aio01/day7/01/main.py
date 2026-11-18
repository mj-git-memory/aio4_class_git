import asyncio 
import time
from fastapi import FastAPI

app = FastAPI() # 서버 생성 

def legacy_lookup() : 
    ''' 기존 동기 라이브러리의 느린 조회를 흉내내는 함수''' # -> 함수에 대한 설명이 생성됨(cml+마우스오버)
    # time.sleep(10)
    time.sleep(3) # 호출한 스레드를 3초간 멈춤. 그동안 같은 이벤트 루프가 담당하는 다른 요청도 진행하지 못함.
    return {'name':'학습자'} 
    # 직렬화(serialize) : dict -> str. Ex) {'key':'value'} -> 문자화 

@app.get('/bad')
async def bad() : 
    # 의도된 버그 : 비동기 함수에서 동기 함수를 직접 호출
    user1 = legacy_lookup() # 일반 함수 legacy_lookup()을 직접 호출. 같은 스레드에서 실행
    # # 함수를 전달해서 별도 스레드에서 실행하도록 맡김
    # user1 = await asyncio.to_thread(legacy_lookup)
    # -> egacy_lookup을 별도 작업 스레드에서 실행하고, 결과가 나오면 받아 줘. 
    # -> 기다리는 동안 이벤트 루프는 다른 요청을 처리해
    # -> 비동기 코드 안에서, 기다리는 동안 스레드를 붙잡는 기존 동기 함수를 호출해야 할 때 유용
    return {'route':'bad', 'user':user1}

@app.get('/good')
async def good() : 
    # 실제 api 호출을 흉내.. 응답을 기다리는 시간을 흉내
    # await asyncio.sleep(10)
    await asyncio.sleep(3) # 현재 요청의 실행만 잠시 쉬고, 이벤트 루프가 다른 요청을 진행. 세 요청의 3초 대기가 겹침(기다리는 시간을 함께 사용)
    return {'route':'good', 'user':{'name':'학습자'}}

@app.get('/health')
async def health() :
    return {'status':'ok'}

### uvicorn day7.main:app 명령어로 서버 실행? (기본 포트 : 8000)
# uvicorn day7.01.main:app --reload -> --reload : 서버 자동 재실행
# uvicorn day7.01.main:app --port 8500 -> 8500 port로 실행 

## 비동기화 확인 
# http://127.0.0.1:8000/good 실행 중에 http://127.0.0.1:8000/health 실행하면, 
# -> 바로 http://127.0.0.1:8000/health 열림
## 동기화 확인 
# http://127.0.0.1:8000/bad 실행 중에 http://127.0.0.1:8000/health 실행하면, 
# -> http://127.0.0.1:8000/bad 실행 후 http://127.0.0.1:8000/health 열림

## Terminal에서 아래 명령어 실행해도 됨 
# curl http://localhost:8000/bad & curl http://localhost:8000/health
# curl http://localhost:8000/good & curl http://localhost:8000/health

# 스레드(thread)는 프로그램 안에서 코드를 실행하는 일꾼이라고 생각
# 하나의 프로그램 안에 여러 스레드가 있을 수 있음
# 프로세스: 카페 한 곳
# 스레드: 카페에서 일하는 직원
# 이벤트 루프: 여러 주문을 번갈아 챙기는 접수 직원의 업무 방식
# 현재 서버의 /bad에서는 접수 직원이 legacy_lookup()까지 직접 처리
# user1 = legacy_lookup()
# 이 코드는 실행 중인 직원을 3초 동안 멈춤. 접수 직원이 멈췄으니 다른 주문도 챙기지 못하는 것

# | 코드                                      | 실행을 담당하는 직원 | 기다리는 동안                |
# |------------------------------------------|-----------------|---------------------------|
# | `legacy_lookup()`                        | 이벤트 루프 직원    | 그 직원이 멈춤               |
# | `await asyncio.to_thread(legacy_lookup)` | 별도 작업 직원     | 이벤트 루프 직원은 다른 요청 처리 |
# ------------------------------------------------------------------------------------------
# | 해야 할 일                    | 일반적인 선택                         |
# |-----------------------------|------------------------------------|
# | 단순히 몇 초 기다리기            | `await asyncio.sleep(3)`           |
# | 비동기 기능이 있는 라이브러리 호출  | 해당 비동기 함수를 `await`              |
# | 동기 라이브러리의 입출력 대기      | `await asyncio.to_thread(...)` 검토 |
# | 대량 계산처럼 CPU를 오래 쓰는 작업 | 별도 프로세스 등 검토                   |