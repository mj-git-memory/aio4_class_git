# 1. 데이터 조회 : get(/tasks)
# return tasks 
# 2. 데이터 추가 : post(/tasks)
# tasks.append({"id": 1, "title": "FastAPI basics", "done": "False"})
# 3. 특정 번호의 데이터 조회 : get(/tasks/{task_id})
# 4. 특정 번호의 데이터를 전부 수정 : put(/tasks/{task_id})
# 5. 특정 번호의 데이터 일부 수정 : patch(/tasks/{task_id})  

from typing import Annotated
from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class TaskInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=80)
    done: bool = Field(default=False, strict=True)

class TaskOut(TaskInput):
    id: int

app = FastAPI(title="Lesson 06")
tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}
next_id = 2


def require_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/tasks", response_model=list[TaskOut])

def list_tasks():
    return list(tasks.values())

@app.get("/tasks/{task_id}", response_model=TaskOut)

def read_task(task_id: Annotated[int, Path(ge=1)]):
    return require_task(task_id)

@app.post("/tasks", response_model=TaskOut, status_code=201)

def create_task(payload: TaskInput):
    global next_id
    task = {"id": next_id, **payload.model_dump()}
    tasks[next_id] = task
    next_id += 1
    return task

class TaskPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=80)
    done: bool | None = Field(default=None, strict=True)

    @field_validator("title", "done", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Explicit null is not allowed")
        return value

    @model_validator(mode="after")
    def require_field(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field")
        return self

@app.put("/tasks/{task_id}", response_model=TaskOut) # PUT 요청을 받는다. 이 예제에서는 제목과 완료 여부를 입력 양식의 결과로 통째로 교체한다.

def replace_task(task_id: Annotated[int, Path(ge=1)], payload: TaskInput):
    require_task(task_id)
    tasks[task_id] = {"id": task_id, **payload.model_dump()}
    return tasks[task_id]

@app.patch("/tasks/{task_id}", response_model=TaskOut) # PATCH 요청을 받는다. 이 예제에서는 사용자가 보낸 칸만 바꾸고 나머지는 유지한다.

def update_task(task_id: Annotated[int, Path(ge=1)], payload: TaskPatch):
    task = require_task(task_id)
    task.update(payload.model_dump(exclude_unset=True)) # model_dump(exclude_unset=True) : 사용자가 안 보낸 칸은 제외하고 딕셔너리로 만든다. 사용자가 안 보낸 칸은 뺀다.
    return task




# ==================== 여기부터 추가: 코드 + 쉬운 설명 ====================
# 위는 직접 작성하신 원본, 아래는 같은 코드를 설명과 함께 다시 적은 학습용 예제다.
# if False: 아래 코드를 실행하지 않고 읽기만 하도록 한다는 뜻이다.
# 같은 app과 API가 두 번 만들어지는 것을 막기 위한 장치이며, 위 원본으로 서버가 실행된다.
# 원본 메모 보충: TaskInput은 단순 변수 묶음뿐 아니라 입력값을 검사하는 기능도 상속한다.
if False:
    # Lesson 06: 할 일 카드를 조회·추가하고 전체 또는 일부를 수정하는 실습
    # 각 설명 바로 아래에 해당 실제 코드가 있다.
    # tasks는 번호별 숙제 카드를 담는 상자, TaskInput은 카드에 적을 내용을 검사하는 양식이다.

    # Annotated를 가져온다. 숫자라는 자료형 옆에 "1 이상" 같은 규칙을 함께 붙일 때 쓴다.
    from typing import Annotated
    # 앱 만들기(FastAPI), 오류 알리기(HTTPException), 주소 속 숫자 검사(Path)를 가져온다. Response는 현재
    # 코드에서 사용하지 않는다.
    from fastapi import FastAPI, HTTPException, Path, Response
    # 데이터 검사 도구를 가져온다. BaseModel은 입력 양식의 바탕, ConfigDict는 설정, Field는 칸별 규칙이다. 뒤의 두 검증
    # 도구는 Lesson 06에서 사용한다.
    from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

    # 할 일을 등록할 입력 양식이다. 비유하면 제목 칸과 완료 칸이 있는 신청서다. BaseModel의 검사 기능을 물려받는다(상속).
    class TaskInput(BaseModel):
        # 제목 앞뒤 공백을 지우고, 정해진 칸 이외의 입력은 거절한다. "  숙제  "는 "숙제"가 되고, 없는 칸인 price를 보내면 422다.
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        # 제목은 문자열이며 1~80자여야 한다. 제목은 꼭 보내야 한다. 빈 문자열이나 공백만 있는 제목은 검사에서 거절한다.
        title: str = Field(min_length=1, max_length=80)
        # 완료 여부는 참/거짓이다. 안 보내면 False(미완료). strict=True라서 JSON의 true/false만 받고 "true" 같은
        # 문자열이나 숫자 1은 거절한다.
        done: bool = Field(default=False, strict=True)

    # 보내줄 응답 양식이다. TaskInput의 title과 done 규칙을 물려받고, 아래에서 id를 더한다.
    class TaskOut(TaskInput):
        # 할 일 번호는 정수다. 응답에는 제목, 완료 여부에 더해 번호까지 들어간다.
        id: int

    # Lesson 06이라는 제목의 웹 앱을 만든다. Lesson 05의 앱과는 별개다.
    app = FastAPI(title="Lesson 06")
    # 메모리에 1번 할 일을 미리 넣는다. tasks[1]로 안쪽 정보를 꺼낸다. DB가 아니므로 재시작하면 초기 값으로 돌아간다.
    tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}
    # 다음에 새 할 일을 만들면 붙일 번호가 2라는 뜻이다. 이미 1번이 있어서 2부터 시작한다.
    next_id = 2

    # 번호로 할 일을 찾아 주는 보조 함수다. 여러 API가 같은 찾기 코드를 반복하지 않도록 함께 사용한다.
    def require_task(task_id: int):
        # 그 번호가 딕셔너리의 키에 없는지 검사한다. 현재 1번만 있다면 99번 요청은 이 조건이 참이다.
        if task_id not in tasks:
            # 없는 할 일이므로 정상 흐름을 멈추고 404와 오류 설명을 보낸다. 서버 전체를 끄는 명령은 아니다.
            raise HTTPException(status_code=404, detail="Task not found")
        # 해당 번호의 할 일 정보를 반환한다.
        return tasks[task_id]

    # GET /tasks를 아래 함수로 연결한다. 응답은 TaskOut 양식의 할 일 여러 개를 담은 리스트여야 한다.
    @app.get("/tasks", response_model=list[TaskOut])
    # 전체 할 일 목록 요청이 들어왔을 때 실행할 함수다.
    def list_tasks():
        # 바깥 번호표(키)는 빼고 할 일 정보(값)들을 꺼내 리스트로 만든다. {1: {...}}가 [{...}] 형태가 된다.
        return list(tasks.values())

    # GET /tasks/1처럼 번호 하나를 지정한 요청을 받는다. 응답은 목록이 아니라 할 일 한 개다.
    @app.get("/tasks/{task_id}", response_model=TaskOut)
    # 주소의 번호를 정수로 받아 1 이상인지 검사한다. /tasks/0이나 /tasks/abc는 함수 실행 전에 422로 거절된다.
    def read_task(task_id: Annotated[int, Path(ge=1)]):
        # 찾기 도우미에게 번호를 맡기고 결과를 반환한다. 번호가 없으면 도우미가 404를 발생시킨다.
        return require_task(task_id)

    # POST /tasks 요청을 받는다. 생성 성공 시 201과 번호가 포함된 할 일 한 개를 응답한다.
    @app.post("/tasks", response_model=TaskOut, status_code=201)
    # 요청 본문의 JSON을 검사한 TaskInput 객체로 받는다. payload는 "받아온 데이터"를 담는 변수 이름이다.
    def create_task(payload: TaskInput):
        # 이 함수 안에서 파일 바깥의 next_id 숫자를 바꾸겠다는 선언이다. 모든 사용자에게 같은 번호 변수를 사용한다.
        global next_id
        # 양식을 딕셔너리로 바꾸고 번호를 합친다. next_id=2, 제목="숙제"라면 {"id": 2, "title": "숙제", "done":
        # False}가 된다.
        task = {"id": next_id, **payload.model_dump()}
        # 새 할 일을 메모리 딕셔너리에 보관한다. 예: tasks[2] = 새 할 일. 이 줄이 실제 메모리 저장 작업이다.
        tasks[next_id] = task
        # 다음 번호를 1 늘린다. 지금 2번을 썼으면 다음 요청은 3번을 쓰도록 준비한다.
        next_id += 1
        # 생성 또는 수정한 할 일을 반환한다. FastAPI가 JSON 응답으로 보내 준다.
        return task

    # 일부만 고칠 때 쓸 입력 양식이다. 제목만 보내거나 완료 여부만 보낼 수 있다.
    class TaskPatch(BaseModel):
        # 제목 앞뒤 공백을 지우고, 정해진 칸 이외의 입력은 거절한다. "  숙제  "는 "숙제"가 되고, 없는 칸인 price를 보내면 422다.
        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
        # 제목을 안 보내도 되도록 기본값을 None으로 둔다. 제목을 보냈다면 1~80자여야 한다. null을 직접 보내는 것은 아래 검증 함수가
        # 막는다.
        title: str | None = Field(default=None, min_length=1, max_length=80)
        # 완료 여부를 생략할 수 있게 한다. 보내는 경우 true/false만 허용하며, null은 아래에서 막는다. None은 파이썬에서 값이
        # 없음을 나타낸다.
        done: bool | None = Field(default=None, strict=True)

        # title 또는 done을 직접 보냈을 때, 기본 자료형 검사 전에 아래 추가 검사를 실행하도록 등록한다.
        @field_validator("title", "done", mode="before")
        # 아래 함수를 클래스 단위로 사용하는 메서드로 만든다. 첫 인자 cls로 TaskPatch 클래스가 전달된다.
        @classmethod
        # 전달된 값이 null인지 확인하는 함수다. JSON null은 파이썬의 None으로 들어온다. cls는 여기서 따로 쓰지 않는다.
        def reject_null(cls, value):
            # 사용자가 이 칸에 null을 직접 보냈는지 검사한다.
            if value is None:
                # 값이 잘못됐다는 예외를 발생시킨다. Pydantic이 검증 오류로 모으고, FastAPI가 요청 오류 422로 응답한다.
                raise ValueError("Explicit null is not allowed")
            # null이 아니라면 받은 값을 다음 검사 단계로 넘긴다. 예: false는 False로 계속 전달된다.
            return value

        # 각 칸의 검사를 통과한 뒤, 입력 양식 전체를 검사하는 함수를 등록한다.
        @model_validator(mode="after")
        # 아무것도 안 적힌 빈 수정 요청인지 검사한다. self는 검사 중인 TaskPatch 객체다.
        def require_field(self):
            # 사용자가 직접 보낸 칸 이름 집합이 비었는지 확인한다. {}면 빈 집합, {"done": false}면 {"done"}이므로 비지 않는다.
            if not self.model_fields_set:
                # 바꿀 내용을 하나 이상 보내 달라는 오류를 낸다. 빈 JSON {} 요청은 422가 된다.
                raise ValueError("Provide at least one field")
            # 검사에 통과한 양식 객체를 그대로 돌려준다. 이 반환이 있어야 다음 처리에서 정상 객체를 사용할 수 있다.
            return self

    # PUT 요청을 받는다. 이 예제에서는 제목과 완료 여부를 입력 양식의 결과로 통째로 교체한다.
    @app.put("/tasks/{task_id}", response_model=TaskOut)
    # 주소에서는 번호, 본문에서는 새 정보를 받는다. 예: PUT /tasks/1, 본문 {"title": "수학 숙제", "done":
    # true}.
    def replace_task(task_id: Annotated[int, Path(ge=1)], payload: TaskInput):
        # 덮어쓰기 전에 그 번호가 존재하는지 확인한다. 없으면 404로 멈추며 새 항목을 만들지 않는다.
        require_task(task_id)
        # 같은 번호의 정보를 새 딕셔너리로 교체한다. done을 생략하면 TaskInput 기본값 False가 들어간다. 예전 done이 유지되는
        # 것은 아니다.
        tasks[task_id] = {"id": task_id, **payload.model_dump()}
        # 이 번호의 할 일 정보를 반환한다. PUT 함수에서는 방금 교체한 정보가 응답으로 나간다.
        return tasks[task_id]

    # PATCH 요청을 받는다. 이 예제에서는 사용자가 보낸 칸만 바꾸고 나머지는 유지한다.
    @app.patch("/tasks/{task_id}", response_model=TaskOut)
    # 고칠 번호와 일부 수정 양식을 받는다. 예: PATCH /tasks/1, 본문 {"done": true}.
    def update_task(task_id: Annotated[int, Path(ge=1)], payload: TaskPatch):
        # 기존 할 일 딕셔너리를 가져온다. 복사본이 아니라 tasks 안의 같은 객체를 가리키므로 아래 update로 원본도 바뀐다.
        task = require_task(task_id)
        # 사용자가 직접 보낸 칸만 딕셔너리로 꺼내 기존 값에 덮어쓴다. {"done": True}만 보내면 제목은 그대로 남는다.
        task.update(payload.model_dump(exclude_unset=True))
        # 생성 또는 수정한 할 일을 반환한다. FastAPI가 JSON 응답으로 보내 준다.
        return task

# ==================== 함수 사용법·실습 예시 시작 ====================
# [중요한 사용 형태 사전: 괄호 안에는 무엇을 넣을까?]
# 1. class 새이름(BaseModel): -> 입력/응답 데이터 양식을 정의한다. 함수가 아니라 클래스 정의다.
#    예: TaskInput(title="숙제") -> 규칙 검사 후 title="숙제", done=False인 객체 생성.
#    Pydantic 모델은 단순 변수 묶음이 아니라 입력값을 검사하는 기능도 가진다.
# 2. ConfigDict(설정이름=값, ...) -> 모델의 검사 설정을 만든다.
#    str_strip_whitespace=True: 문자열 양끝 공백 제거. 글자 사이의 공백은 남는다.
#    extra="forbid": 정하지 않은 칸을 추가로 보내면 거절한다.
# 3. Field(default=기본값, min_length=최소글자수, max_length=최대글자수, strict=True)
#    -> 한 칸의 기본값과 규칙을 지정한다. 모든 옵션을 항상 함께 쓰는 것은 아니다.
#    예: Field(default=False, strict=True) -> 생략하면 False, 보내면 진짜 bool만 허용.
# 4. Annotated[자료형, Path(ge=최솟값)] -> 경로 입력값에 자료형과 규칙을 붙인다.
#    Annotated는 함수 호출이 아니라 대괄호로 쓰는 자료형 표기다. ge=1은 1 이상.
# 5. HTTPException(status_code=오류번호, detail="설명") -> HTTP 오류 정보를 만든다.
#    raise HTTPException(...) -> 그 예외를 발생시켜 FastAPI가 오류 응답을 보내게 한다.
# 6. 딕셔너리.values() -> 키를 제외한 값들을 꺼낼 수 있게 한다.
#    list(여러값) -> 리스트로 만든다. list(tasks.values())는 전체 할 일 정보 목록이다.
# 7. 모델객체.model_dump() -> Pydantic 모델 객체를 파이썬 딕셔너리로 바꾼다.
#    JSON 문자열로 바꾸는 함수는 아니다. JSON 응답 변환은 FastAPI가 처리한다.
# 8. {"id": 번호, **딕셔너리} -> 딕셔너리의 항목들을 펼쳐 한 딕셔너리로 합친다.
#    **는 여기서 함수가 아니라 펼치기 문법이다. 예: {"id": 2, **{"title": "숙제"}}.
# 9. @app.get("경로", response_model=응답양식) -> GET 요청과 함수를 연결한다.
#    @app.post("경로", response_model=응답양식, status_code=201) -> POST 요청 등록.
#    response_model은 나갈 데이터의 양식이다. 검사/변환/문서화에 사용하며 DB 저장 기능은 아니다.
# 10. global 변수이름 / 변수 += 1 / return 값은 함수가 아니라 파이썬 문법이다.
#     각각 바깥 변수 사용 선언 / 1 증가 / 결과 반환을 뜻한다.

# [Lesson 06에서 더 쓰는 함수와 문법]
# 1. @field_validator("칸이름", ..., mode="before") -> 칸별 검사 전에 실행할 검사 함수 등록.
#    reject_null(cls, value) -> null이면 ValueError, 아니면 value 반환.
# 2. @classmethod -> 첫 인자로 객체(self) 대신 클래스(cls)를 받는 메서드를 만든다.
# 3. @model_validator(mode="after") -> 칸별 검사 후 양식 전체를 확인할 검사 함수 등록.
#    require_field(self) -> 직접 보낸 칸이 하나도 없으면 ValueError, 아니면 self 반환.
# 4. 객체.model_fields_set -> 직접 보낸 칸 이름의 집합. 괄호 없이 읽는 속성이다.
#    {"done": false} -> {"done"}. 값이 False여도 칸을 보냈으므로 빈 집합이 아니다.
# 5. raise ValueError("설명") -> 잘못된 값임을 알린다. 이 모델 검사 안에서는 422로 이어진다.
# 6. 모델객체.model_dump(exclude_unset=True) -> 안 보낸 칸을 빼고 딕셔너리로 만든다.
#    TaskPatch(done=False).model_dump(exclude_unset=True) -> {"done": False}.
#    False를 빼는 옵션이 아니다. 사용자가 안 보낸 칸만 뺀다.
# 7. 기존딕셔너리.update(바꿀딕셔너리) -> 같은 키는 덮어쓰고 없는 키는 추가한다.
#    예: {"title": "숙제", "done": False}에 {"done": True}로 update하면 제목은 유지된다.
#    update는 원본을 직접 바꾸고 반환값은 None이다. task = task.update(...)라고 쓰지 않는다.
# 8. @app.put("경로", ...) / @app.patch("경로", ...) -> 해당 요청의 담당 함수를 등록한다.

# [안 보낸 것과 null을 보낸 것은 다르다]
# PATCH 본문 {"done": true}: title은 안 보냄 -> 제목은 유지하고 완료만 바꿈.
# PATCH 본문 {"title": null}: title에 null을 직접 보냄 -> reject_null이 422로 거절.
# PATCH 본문 {}: 아무 칸도 안 보냄 -> require_field가 422로 거절.
# title과 done을 생략할 때의 내부 기본값 None과, 요청에서 직접 보내는 null을 구별하는 설계다.
# 이 예제의 before 검사 함수는 생략된 기본값에는 실행되지 않고 직접 보낸 값에 실행된다.

# [PUT과 PATCH 직접 비교: 숙제 카드의 전체 내용과 완료 칸]
# day5에서: python -m uvicorn labs.lesson06:app --reload
# 서버를 교체할 때는 기존 서버 터미널에서 Ctrl + C로 종료한 뒤 실행한다.
# http://127.0.0.1:8000/docs 에서 아래 순서대로 실행한다.
# 1. PATCH /tasks/1, 본문 {"done": true}
#    -> 200. 제목은 "FastAPI basics" 그대로, done만 true로 바뀐다.
# 2. PATCH /tasks/1, 본문 {"title": "수학 숙제"}
#    -> 200. 제목은 "수학 숙제", done은 이전 true 그대로다.
# 3. PUT /tasks/1, 본문 {"title": "영어 숙제"}
#    -> 200. 제목은 "영어 숙제", done은 입력 양식 기본값 false로 바뀐다.
#    PUT은 새 입력 양식의 결과로 전체 정보를 바꾸므로 안 보낸 done을 유지하지 않는다.
# 4. GET /tasks/1 -> 실제 반영된 제목과 완료 여부를 확인한다.
# 5. PATCH /tasks/1, 본문 {"done": false} -> 200. False도 직접 보냈으므로 반영한다.
# 6. PATCH /tasks/1, 본문 {} 또는 {"done": null} -> 422. 입력 규칙 위반.
# 7. PATCH /tasks/999, 본문 {"done": true} -> 404. 규칙은 맞지만 해당 할 일이 없다.
# PUT/PATCH라고 이런 처리가 자동으로 생기는 것은 아니다. 위 함수들의 구현이 차이를 만든다.
# 각 요청에서 본문은 위 예시의 JSON 객체 하나만 입력한다.
# 두 실습의 메모리는 서로 별개다. Lesson 05에서 만든 항목이 Lesson 06으로 이어지지 않는다.
# 이 파일도 DB가 아니므로 서버 재시작 시 변경 내용이 초기화된다.

# ==================== 함수 사용법·실습 예시 끝 ====================
