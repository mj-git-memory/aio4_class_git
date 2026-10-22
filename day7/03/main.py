from fastapi import FastAPI
import httpx
import os

app = FastAPI() # 서버 생성
BASE_URL = 'http://127.0.0.1:9000' # 접속 주소


@app.get('/health')
async def health() : 
    return {'status': 'ok'}

import asyncio
from time import perf_counter

async def fetch(client, item_id) : # -> 접속(fetch)하기 위한 함수
    response = await client.get(f'/items/{item_id}')
    response.raise_for_status() # 통신을 통한 요청 결과 에러가 4xx, 5xx(서버에러)이면 멈추게 함?
    return response.json() # -> 딕셔너리로 반한됨 

@app.get('/summary') # 비동기 순차 실행. (ex.하나 실행하는데 하루 걸린다면, 3일 걸림. but 3일 동안 다른 일 실행 가능)
async def summary():
    start = perf_counter()
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=3, trust_env=False) as client:
        items = []
        for item_id in [1, 2, 3]:
            items.append(await fetch(client, item_id))
    return {'items': items, 'elapsed': round(perf_counter() - start, 3)}

@app.get('/labels') # 비동기 병렬 실행  (ex.하나 실행하는데 하루 걸려도, 모든 작업 수행하는데 하루 걸림)
async def labels():
    ids = [1, 2, 3]
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=3, trust_env=False) as client:
        tasks = [fetch(client, item_id) for item_id in ids]
        completed = []
        for task in asyncio.as_completed(tasks): # -> 완료된 작업부터 받는다 
            completed.append(await task)
    return [{'requested_id': item_id, 'data': data}
            for item_id, data in zip(ids, completed)]
