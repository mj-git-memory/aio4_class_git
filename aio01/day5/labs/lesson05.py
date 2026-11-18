from typing import Annotated
from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
# pydantic은 FastAPI가 내부적으로 사용하는 데이터 검증 도구. BaseModel은 이를 사용해 모델을 정의할 때 상속하는 클래스.

# 변수들로만 이루어진 클래스, 상속을 하고 있음
class TaskInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=80)
    done: bool = Field(default=False, strict=True)

class TaskOut(TaskInput):
    id: int

app = FastAPI(title="Lesson 05")
tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}
next_id = 2


def require_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]
# esponse_model=list[TaskOut]: 응답이 리스트이고, 각 항목이 TaskOut의 구조와 규칙에 맞는지 검증. 필수로 사용하는 것은 아니지만, 문서화와 검증에 도움됨.
@app.get("/tasks", response_model=list[TaskOut]) 
def list_tasks():
    return list(tasks.values())
# [
#   {
#     "title": "FastAPI basics",
#     "done": false,
#     "id": 1
#   },
#   {
#     "title": "첫번째 추가한 데이터",
#     "done": false,
#     "id": 2
#   },
#   {
#     "title": "두번째 추가한 데이터",
#     "done": false,
#     "id": 3
#   }
# ]

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: Annotated[int, Path(ge=1)]):
    return require_task(task_id)


@app.post("/tasks", response_model=TaskOut, status_code=201) # status_code=201 : 정상 반환 시 "새 데이터 생성 성공"을 뜻하는 상태 코드를 보낸다.
def create_task(payload: TaskInput):
    global next_id
    task = {"id": next_id, **payload.model_dump()}
    tasks[next_id] = task
    next_id += 1
    return task
### post에서 데이터를 변경하고, excute하면, 데이터가 추가됨. GET /tasks를 통해 확인 가능.
# {
#   "title": "첫번째 추가한 데이터",
#   "done": false
# }
# {
#   "title": "두번째 추가한 데이터",
#   "done": false
# }

### dict를 풀어줄 때는, ** 두개
task = {"id": 2, **{"title": "숙제", "과목": "수학"}} # {"id": 2, "title": "숙제", "과목": "수학"}와 동일
print(task) # {'id': 2, 'title': '숙제', '과목': '수학' }

### list를 풀어줄 때는, * 한개
list_1 = [1, 2, 3, 4, 5]
list_2 = [10, 20, 30, 40, 50]
print([*list_1, *list_2])  # [1, 2, 3, 4, 5, 10, 20, 30, 40, 50]



# ==================== 여기부터 추가: 코드 + 쉬운 설명 ====================
# 위는 직접 작성하신 원본, 아래는 같은 코드를 설명과 함께 다시 적은 학습용 예제다.
# if False: 아래 코드를 실행하지 않고 읽기만 하도록 한다는 뜻이다.
# 같은 app과 API가 두 번 만들어지는 것을 막기 위한 장치이며, 위 원본으로 서버가 실행된다.
# 원본 메모 보충: TaskInput은 단순 변수 묶음뿐 아니라 입력값을 검사하는 기능도 상속한다.
if False:
    # Lesson 05: 할 일 카드를 조회하고 새로 추가하는 실습
    # 각 설명 바로 아래에 해당 실제 코드가 있다.
    # tasks는 번호별 숙제 카드를 담는 상자, TaskInput은 카드에 적을 내용을 검사하는 양식이다.

    # Annotated를 가져온다. 숫자라는 자료형 옆에 "1 이상" 같은 규칙을 함께 붙일 때 쓴다.
    from typing import Annotated
    # 앱 만들기(FastAPI), 오류 알리기(HTTPException), 주소 속 숫자 검사(Path)를 가져온다. 
    from fastapi import FastAPI, HTTPException, Path, Response
    # 데이터 검사 도구를 가져온다. BaseModel은 입력 양식의 바탕, ConfigDict는 설정, Field는 칸별 규칙이다. 
    # pydantic은 FastAPI가 내부적으로 사용하는 데이터 검증 도구다. BaseModel은 이를 사용해 모델을 정의할 때 상속하는 클래스다.
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

    # Lesson 05라는 제목의 웹 앱을 만든다. 제목은 /docs에서 확인한다.
    app = FastAPI(title="Lesson 05")
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
        # 해당 번호의 할 일 정보를 반환한다. require_task의 아래쪽에서는 존재하는 번호일 때만 이 줄에 도착한다.
        return tasks[task_id]

    # GET /tasks를 아래 함수로 연결한다. 응답은 TaskOut 양식의 할 일 여러 개를 담은 리스트여야 한다.
    @app.get("/tasks", response_model=list[TaskOut])
    # 전체 할 일 목록 요청이 들어왔을 때 실행할 함수다.
    def list_tasks():
        # 바깥 번호표(키)는 빼고 할 일 정보(값)들을 꺼내 리스트로 만든다. {1: {...}}가 [{...}] 형태가 된다.
        return list(tasks.values())
    # [
    #   {
    #     "title": "FastAPI basics",
    #     "done": false,
    #     "id": 1
    #   },
    #   {
    #     "title": "첫번째 추가한 데이터",
    #     "done": false,
    #     "id": 2
    #   },
    #   {
    #     "title": "두번째 추가한 데이터",
    #     "done": false,
    #     "id": 3
    #   }
    # ]

    # GET /tasks/1처럼 번호 하나를 지정한 요청을 받는다. 응답은 목록이 아니라 할 일 한 개다.
    @app.get("/tasks/{task_id}", response_model=TaskOut)
    # 주소의 번호를 정수로 받아 1 이상인지 검사한다. /tasks/0이나 /tasks/abc는 함수 실행 전에 422로 거절된다.
    def read_task(task_id: Annotated[int, Path(ge=1)]):
        # 찾기 도우미에게 번호를 맡기고 결과를 반환한다. 번호가 없으면 도우미가 404를 발생시킨다.
        return require_task(task_id)


    @app.post("/tasks", response_model=TaskOut, status_code=201) # status_code=201 : 정상 반환 시 "새 데이터 생성 성공"을 뜻하는 상태 코드를 보낸다.
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
    # POST /tasks의 본문을 입력하고 Execute하면 새 항목이 추가된다. GET /tasks로 확인한다.
    # 아래 두 JSON은 한 요청에 이어 붙이지 말고, 한 개씩 각각 요청한다.
    # {
    #   "title": "첫번째 추가한 데이터",
    #   "done": false
    # }
    # {
    #   "title": "두번째 추가한 데이터",
    #   "done": false
    # }

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

# [Lesson 05 직접 해 보기: 숙제 카드를 새로 만들기]
# day5에서: python -m uvicorn labs.lesson05:app --reload
# 기존 서버가 실행 중이면 해당 터미널에서 Ctrl + C로 종료한 뒤 실행한다.
# http://127.0.0.1:8000/docs 에서 다음 순서대로 해 본다.
# 1. POST /tasks -> Try it out -> 본문을 {"title": "수학 숙제", "done": false}로 바꾼다.
# 2. Execute -> 처음 추가했다면 201과 {"title": "수학 숙제", "done": false, "id": 2} 응답.
# 3. GET /tasks -> Execute -> 원래 1번과 새로 추가한 2번이 함께 보인다.
# 4. GET /tasks/{task_id} -> task_id에 2 입력 -> Execute -> 수학 숙제 한 개만 보인다.
# title을 "  수학 숙제  "로 보내도 앞뒤 공백을 지운 "수학 숙제"로 저장한다.
# {"title": "숙제"}만 보내면 done은 기본값 false가 된다.
# {"title": ""} 또는 {"title": "숙제", "done": "false"}는 422다. 따옴표의 유무에 주의한다.
# {"title": "숙제", "price": 100}도 없는 칸을 보냈기 때문에 422다.
# 한 번의 POST 본문은 JSON 객체 하나다. 두 객체를 나란히 붙이지 말고 각각 요청한다.
# POST는 새 항목 추가다. 기존 번호의 내용을 수정하려면 Lesson 06의 PUT/PATCH를 사용한다.
# 저장은 메모리에만 한다. --reload로 재시작해도 추가 내용은 사라져 1번만 남는다.
# 번호 증가 방식은 한 프로세스에서 배우기 위한 간단한 예제다. DB의 자동 번호 기능은 아니다.

# ==================== 함수 사용법·실습 예시 끝 ====================
