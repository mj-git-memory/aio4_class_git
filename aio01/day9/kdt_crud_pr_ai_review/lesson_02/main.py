### main.py: 현재는 없는 ID에도 200을 반환하는 API예

from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI()
tasks = {1: {"id": 1, "title": "Git 준비"}}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return tasks.get(task_id) # 상태 코드:200 발생
    # 위 코드에서는 데이터가 없어도 None을 정상적으로 반환하기 때문에 200이 나옴 

    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")
        # HTTPException(...) : FastAPI에서 HTTP 오류 응답을 만들 때 사용하는 예외 클래스
        # status_code : 응답 상태 코드, detail : 오류 설명
        # raise : 예외를 발생시키라는 키워드. 이 지점에서 함수의 정상 실행이 중단되므로 아래에 있는 return task는 실행되지 않음 
        # 서버 전체가 종료되는 게 아니라 이번 요청에 대해 404 오류 응답을 보내는 것
    return task  # 상태 코드:404 발생

# tasks는 **파이썬 딕셔너리(dict)**
# 딕셔너리에는 파이썬이 미리 만들어 둔 get() 메서드가 있어서, 직접 정의하지 않아도 사용할 수 있음 
# 키를 전달하면 해당 값을 반환
# tasks.get(1)  # {"id": 1, "title": "Git 준비"}
# tasks.get(2)  # None — 해당 키가 없으면
# tasks.get_task(1) → 딕셔너리에는 get_task라는 메서드가 없어서 오류 발생
# 점(.) 앞에 있는 객체가 제공하는 메서드를 호출하. 리스트의 tasks.append(...)를 사용하는 것과 같은 원리

# 200은 요청 성공, 404는 요청한 대상을 찾을 수 없다는 뜻
# 요청	     상황                 적절한 상태 코드
# /tasks/1	ID가 1인 할 일이 있음	200 OK
# /tasks/2	ID가 2인 할 일이 없음	404 Not Found