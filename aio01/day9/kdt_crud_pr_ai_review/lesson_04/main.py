from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

### 1. 앱과 데이터 준비
app = FastAPI()
tasks = [{"id": 1, "title": "첫째"}, {"id": 3, "title": "셋째"}]
# tasks는 딕셔너리 두 개가 들어 있는 리스트
# 리스트  위치(인덱스)	데이터의 id	제목
#   0	    1	        첫째
#   1	    3	        셋째

class TaskIn(BaseModel):
    title: str = Field(min_length=1)
    # title은 필수이며 최소 한 글자인 문자열이어야 함 
    # FastAPI가 리스트를 JSON 배열로 변환해서 응답

### 2. 전체 조회: GET
@app.get("/tasks")
def list_tasks():
    return tasks
    # GET /tasks 요청이 오면 전체 목록을 반환

# 3. 등록: POST
@app.post("/tasks", status_code=201) # 201은 새 데이터가 생성되었다는 상태 코드
def create_task(payload: TaskIn):
    task = {"id": max(task["id"] for task in tasks) + 1, "title": payload.title}
    # 이 부분은 현재 목록에서 가장 큰 ID를 찾음  # max(1, 3) → 3
    # 거기에 1을 더해 새 데이터를 만듦 : task = {"id": 4, "title": "새 할 일"}
    tasks.append(task) # 목록 끝에 추가
    return task # 추가한 데이터를 응답
# 목록이 비어 있으면 max()가 오류를 발생
# 가장 큰 ID를 삭제하면 그 번호를 다시 발급할 수 있음. 
# 앞서 원했던 “삭제된 ID 재사용 금지”를 만족하려면 별도 카운터가 필요

### 4. 수정: PUT
@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskIn):
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = payload.title
            return task
    raise HTTPException(status_code=404, detail="Task not found")
# PUT /tasks/3으로 다음 데이터({"title": "셋째 수정"})를 보내면:
# task_id에는 3, payload.title에는 "셋째 수정"이 들어감 
# 목록을 하나씩 확인하면서 ID가 일치하는 데이터를 찾습니다. 찾으면 제목을 수정하고 반환 
# task는 리스트 안의 딕셔너리를 가리키므로, 제목을 바꾸면 tasks 안의 데이터도 바뀜 
# 반복문이 끝날 때까지 찾지 못했다면 404를 반환

### 5. 삭제: DELETE — 현재 코드의 오류
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    tasks.pop(task_id)
# 204는 요청이 성공했고 응답 본문은 없다는 뜻
# 문제는 리스트의 pop()은 ID가 아니라 인덱스를 받는다는 것 
# 이 코드는 ID 1이 아니라 인덱스 1에 있는 ID 3 데이터를 삭제
# tasks.pop(3) : 초기 목록에는 인덱스 3이 없으므로 IndexError가 발생
## ID로 삭제하려면, 수정할 때처럼 데이터를 찾아야 함 
# @app.delete("/tasks/{task_id}", status_code=204)
# def delete_task(task_id: int):
#     for index, task in enumerate(tasks):
#         if task["id"] == task_id:
#             tasks.pop(index)
#             return
#     raise HTTPException(status_code=404, detail="Task not found")
