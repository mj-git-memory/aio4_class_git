from fastapi import FastAPI
# FastAPI: API 앱을 만드는 클래스
from pydantic import BaseModel, Field
# BaseModel: 요청 데이터의 형식을 정하고 검사할 때 사용
# Field: 글자 수 같은 추가 조건이나 기본값을 설정

### 1. 앱과 데이터 만들기
app = FastAPI()
item = {"id": 1, "title": "처음", "done": True}
# item: 수정할 데이터를 담은 딕셔너리

### 2. PUT으로 받을 데이터 정의하기
class TaskPut(BaseModel):
    # TaskPut은 요청 데이터가 지켜야 할 형식
    title: str = Field(min_length=1) # 최소 한 글자인 문자열, 생략 불가능
    done: bool # 완료 여부, 생략 불가능
    # title, done 둘 다 기본값이 없어서 요청에 반드시 포함해야 함 (ex. {"title": "파이썬 공부", "done": false})
    # -> 필수 값을 빼거나 제목을 빈 문자열로 보내면 검증에 실패해 422 응답을 받음 

### 3. PUT 요청 처리하기
@app.put("/tasks/1")
# @app.put("/tasks/1")은 이 주소로 PUT 요청이 오면 아래 함수를 실행하도록 연결
# put은 전체 수정 
def replace_task(payload: TaskPut):
    # payload(함수의 매개변수)에는 TaskPut 형식으로 검사된 요청 데이터가 들어감 
    # payload: 전달받은 데이터를 담을 이름
    # TaskPut: 그 데이터의 타입
    # FastAPI가 요청 본문을 TaskPut 형식으로 검사한 뒤 payload에 전달
    item.update(payload.model_dump())
    # 이것은 Pydantic 모델을 딕셔너리로 변환
    # item.update(...): 기존 딕셔너리의 값을 수정 
    return item
    # id는 수정할 데이터에 없으므로 유지.
    # return item은 수정된 데이터를 반환하고, FastAPI가 JSON 응답으로 보내줌 
# 예를 들어 다음 JSON( {"title": "공부", "done": true} )을 보내면
# 함수 안에서 이렇게 사용 (payload.title: "공부", payload.done: True)


### 4. PATCH로 받을 데이터 정의하기
class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    # title: str | None: 제목은 문자열 또는 None일 수 있음 
    # default=None: 제목을 생략하면 None이 들어감 
    # min_length=1: 문자열을 보내면 최소 한 글자
    done: bool = False
    # done: bool = False -> 완료 여부를 생략하면 False가 들어감 
    # 둘 다 기본값이 있어서 요청에서 생략할 수 있음

### 5. 현재 PATCH 코드의 문제
@app.patch("/tasks/1")
# patch는 부분 수정  
def patch_task(payload: TaskPatch):
    item.update(payload.model_dump())
    # model_dump()가 생략한 필드의 기본값도 포함. 제목만 보내도 다음 딕셔너리가 만들어짐
    # 그래서 기존 done이 True였다면, 요청하지 않은 완료 여부까지 False로 바뀜 
    ### 부분 수정으로 동작하도록 고치기
    # item.update(payload.model_dump(exclude_unset=True))
    # -> exclude_unset=True : 요청에서 보내지 않은 필드를 제외하라는 뜻
    return item

# 초기 데이터에 제목만 수정하려고 다음 요청을 보내면:
# -> {"title": "새 제목"}
# model_dump()는 생략한 필드의 기본값도 포함해요.
# -> {"title": "새 제목", "done": False}
# 그래서 제목만 바꾸려 했는데 완료 여부도 True에서 False로 바뀜 

# # 요청: {"title": "새 제목"}

# payload.model_dump()
# # {"title": "새 제목", "done": False}

# payload.model_dump(exclude_unset=True)
# # {"title": "새 제목"}