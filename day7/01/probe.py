### *** main.py는 요청을 받는 서버, probe.py는 그 서버에 요청을 보내는 클라이언트 ***

### 서버가 켜져 있는 상태에서, 별도 터미널에서 이 파일을 실행시켜야 돌아감
# 터미널에서 uvicorn day7.01.main:app --reload --port 8000 실행 후, 
# 다른 터미널에서 이 파이썬 파일 실행 (python day7/probe.py)
# 둘 다 프로젝트 폴더인 AIO_4_class에서 실행하면 됨 

## api : 내가 만든 주소, 서버가 호출되는 것
## 요청 3개를 동시에 보내는경우

import asyncio 
from time import perf_counter
import httpx 

async def request_one(client, path, number) : 
    start = perf_counter() # 서버 시간 확인

    response = await client.get(path)
    response.raise_for_status() # 브라우저의 상태 코드 반환 

    elapsed = perf_counter() - start
    print(f'{path} 요청 {number}: {response.status_code}, {elapsed :.2f}') 
    return response.json()


async def compare(client, path) : 
    print(f'\n{path}: 요청 3개 시작')
    start = perf_counter() # 서버 시간 확인
    await asyncio.gather(
        request_one(client, path, 1),
        request_one(client, path, 2),
        request_one(client, path, 3)
    )
    print(f'전체 완료 시간: {perf_counter() - start :.2f}초')

async def main() : 
    # async with : 비동기로 여러개의 요청을 동시에 처리하겠다 라는 의미 
    # httpx.AsyncClient : httpx패키지의 AsyncClient 클래스 사용
    async with httpx.AsyncClient(
        base_url = 'http://127.0.0.1:8000',
        timeout = 20.0,
        trust_env=False
    ) as client : 
        await compare(client, '/bad') # /bad 3번 요청. 여기서 client는 부라우저를 의미 
        await compare(client, '/good') # /good 3번 요청 

if __name__ == '__main__' :
    asyncio.run(main())

        
