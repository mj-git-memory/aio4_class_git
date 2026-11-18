import os
import httpx 
from fastapi import FastAPI, HTTPException

BASE_URL = 'https://jsonplaceholder.typicode.com'

app = FastAPI()

async def fetch_todo(todo_id) : 
    async with httpx.AsyncClient(
        base_url= BASE_URL,
        timeout= 10.0
    ) as client : 
        response = await client.get(f'/todos/{todo_id}')
        print(response.status_code)
        return response.json()

@app.get('/todos/{todo_id}')
async def read_todo(todo_id:int) : 
    try : 
        data = await fetch_todo(todo_id)
    except httpx.HTTPStatusError as er : 
        print(er.response.status_code)
    return {
        'id': data.get('id', todo_id), 
        'title': data.get('title', '제목 없음'), # title을 가져오고, title 값이 없으면 '제목 없음' 가져옴
        'completed': data.get('completed', False) 
    }

# uvicorn day7.02.main:app --reload 로 서버 실행 
# python -m uvicorn day7.02.main:app --reload  (이 방법도 있음)
#            └ 모듈명 └ 불러올 파일과 FastAPI 객체
# python -m uvicorn main:app --app-dir day7/02 --reload --port 8000 (이렇게 디렉토리 지정 가능)

# http://127.0.0.1:8000/todos/1
# http://127.0.0.1:8000/todos/999


## main2.py는 사용자의 요청을 받아 외부 API에서 할 일 정보를 가져온 뒤 응답하는 서버 
## 외부 API의 응답을 기다리는 작업이므로 현재처럼 비동기를 사용하는 것이 적합
# 이 코드는 비동기로 외부 api를 호출하고 있음. 
# 이 코드를 비동기가 아닌 동기로 호출하면 어떻게 될까?
# 동기로 호출하면 외부 api 호출 하기 전에, 사용자에게 응답할까?