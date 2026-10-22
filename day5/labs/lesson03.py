### Lesson 03: 주소에서 할 일 번호를 받아 조회하고, 잘못된 요청을 구분하기
# day5 폴더에서 실행: python -m uvicorn labs.lesson03:app --reload
# 다른 실습 서버가 실행 중이면 해당 터미널에서 Ctrl + C로 먼저 종료한다.
# 예: http://127.0.0.1:8000/tasks/1 -> 1번 할 일 조회

from typing import Annotated
from fastapi import FastAPI, HTTPException, Path

app = FastAPI(title="Lesson 03")
tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}

# Fixed paths must be declared before the variable route.
@app.get("/tasks/stats")
def task_stats():  
    return {"total": len(tasks)} # len(tasks) : tasks 딕셔너리의 항목 개수. 현재 1개.

@app.get("/tasks/{task_id}") 
# Path(ge=1) ensures task_id is an integer greater than or equal to 1.
def read_task(task_id: Annotated[int, Path(ge=1)]): # ge=1: greater than or equal(이상). 1은 허용하고 0, -1은 거절한다.
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found") # 404: Not Found error if task_id is not in tasks.
    return tasks[task_id]



# ==================== 여기부터 추가: 코드 + 쉬운 설명 ====================
# 위는 직접 작성하신 원본이다. 아래는 같은 코드를 쉬운 설명과 함께 다시 적은 학습용 예제다.
# 할 일 하나를 숙제 카드, tasks를 번호별 숙제 카드를 넣은 상자라고 생각해 보자.
# if False:는 아래 예제를 실행하지 않는다는 뜻이다. 서버는 위 원본 코드로 실행한다.
# 위에서 만든 app을 다시 만들거나 API를 다시 등록하지 않도록 설명판만 실행에서 제외한다.
if False:
    # Annotated: 자료형과 추가 규칙을 함께 적을 수 있도록 해주는 파이썬 도구.
    # 아래 Annotated[int, Path(ge=1)]은 "정수이며 1 이상인 경로 입력값"이라는 뜻이다.
    from typing import Annotated
    # FastAPI: 앱 생성 / HTTPException: 오류 응답 보내기 / Path: URL 경로 입력값의 조건 지정.
    # HTTPException은 모든 통신 문제를 자동 해결하는 도구가 아니라 HTTP 오류 응답을 위한 예외다.
    from fastapi import FastAPI, HTTPException, Path

    # /docs에 Lesson 03이라는 제목이 표시되는 웹 앱 객체를 만든다.
    # FastAPI는 앱을 만드는 설계도(클래스)이고, app은 그 설계도로 만든 이번 실습의 앱이다.
    app = FastAPI(title="Lesson 03")

    # 예: 번호가 1인 숙제 카드에 제목 FastAPI basics, 완료 여부 False가 적혀 있다.
    # DB 대신 파이썬 딕셔너리에 할 일 하나를 미리 담아둔다. 서버 실행 중 메모리에 있는 데이터다.
    # 바깥의 1 -> 할 일을 찾을 때 사용하는 정수 키. 예: tasks[1]. 문자열 "1"과는 다르다.
    # 안쪽의 딕셔너리 -> 그 할 일의 정보: id=번호, title=제목, done=완료 여부.
    # False는 아직 완료하지 않았다는 불리언(참/거짓) 값이다.
    # 여기서 =는 변수에 저장하는 것이며, DB에 영구 저장하는 것은 아니다.
    tasks = {1: {"id": 1, "title": "FastAPI basics", "done": False}}
    # FastAPI는 반환한 딕셔너리를 JSON 형식의 응답으로 바꿔 보낸다.
    # 단순히 str(딕셔너리)로 바꾸는 것과는 다르다. 파이썬 False는 JSON에서 false로 표현된다.
    # JSON 응답 예: {"id": 1, "title": "FastAPI basics", "done": false}

    # 고정 경로 /tasks/stats를 변수가 있는 /tasks/{task_id}보다 먼저 등록한다.
    # 요청은 등록 순서대로 경로를 찾는다. 반대 순서라면 stats가 task_id 자리로 잡힐 수 있다.
    # 그 경우 stats를 정수로 변환하지 못해 422가 생길 수 있으므로 구체적인 경로를 먼저 둔다.
    @app.get("/tasks/stats")
    def task_stats():  # 예: 전체 할 일이 몇 개인지 확인하는 요청을 처리한다.
        # len(tasks)는 바깥 딕셔너리의 항목 개수다. 현재 키가 1 하나라서 결과는 1이다.
        # 안쪽의 id/title/done 필드 개수인 3을 세는 것이 아니다.
        # GET /tasks/stats -> 200 OK, {"total": 1}
        return {"total": len(tasks)}


    # 중괄호 {task_id}는 주소의 이 부분이 요청마다 달라질 수 있다는 표시다.
    # /tasks/1의 1, /tasks/2의 2를 아래 함수의 task_id 인자로 전달한다.
    @app.get("/tasks/{task_id}")
    # int -> URL의 "1"을 파이썬 정수 1로 바꾸고, 바꿀 수 없는 "abc" 등은 거절한다.
    # Path(ge=1) -> ge는 greater than or equal(이상). 1은 허용하고 0, -1은 거절한다.
    # 이 검사는 FastAPI가 함수 실행 전에 한다. 일반 파이썬의 int 주석만으로 검사되는 것은 아니다.
    def read_task(task_id: Annotated[int, Path(ge=1)]):
        # not in은 딕셔너리에 해당 키가 없는지 확인한다.
        # 예: 1 not in tasks는 False(1번이 있음), 2 not in tasks는 True(2번이 없음)다.
        # 예: /tasks/2 -> 2는 정수이며 1 이상이므로 입력 검사 통과. 하지만 tasks에 2번은 없다.
        if task_id not in tasks:
            # raise는 예외를 발생시켜 정상 처리 흐름을 중단한다. 아래 return으로 내려가지 않는다.
            # FastAPI는 이를 HTTP 404 응답으로 바꾼다. 본문은 {"detail": "Task not found"}다.
            # detail은 요청한 쪽에 전달할 오류 설명이다.
            raise HTTPException(status_code=404, detail="Task not found")
        # 예: /tasks/1 -> task_id=1 -> tasks[1]에 들어 있는 안쪽 딕셔너리를 반환한다.
        # 상태 코드를 따로 지정하지 않았으므로 정상 응답은 200 OK다.
        return tasks[task_id]


    # 브라우저에서 직접 비교하기 (아래 경로 앞에 http://127.0.0.1:8000을 붙인다)
    # /tasks/stats -> 200: 전체 개수 {"total": 1}
    # /tasks/1     -> 200: 1번 할 일 정보
    # /tasks/2     -> 404: 번호 형식은 맞지만 해당 데이터가 없음 (우리가 작성한 if에서 검사)
    # /tasks/0     -> 422: 1 이상 조건 위반 (FastAPI가 함수 호출 전에 검사)
    # /tasks/abc   -> 422: 정수로 바꿀 수 없는 입력 (FastAPI가 함수 호출 전에 검사)
    # /            -> 404: 이 파일의 앱에는 루트 경로를 등록하지 않았음
    # 404라도 이유가 다르다. /tasks/2는 데이터 없음, /는 등록된 경로 없음이다.
    # /docs에서도 task_id에 1, 2, 0을 각각 입력해 Execute를 눌러 비교할 수 있다.


# ==================== 중요한 함수·문법 사용법 ====================
# 1. FastAPI(title="문서 제목") -> 웹 앱 객체를 만든다. 네트워크 서버를 켜는 명령은 아니다.
#    app = FastAPI(title="Lesson 03") -> 만든 앱을 app이라는 변수에 담는다.
# 2. @app.get("경로") -> 그 경로로 들어온 GET 요청을 바로 아래 함수에 연결한다.
#    예: @app.get("/tasks/stats") -> 전체 카드 개수를 알려줄 함수 등록.
# 3. def 함수이름(인자): -> 함수 정의 문법. 함수가 사용할 입력값을 괄호 안에 적는다.
#    예: read_task의 task_id에는 URL에서 받은 카드 번호가 들어온다.
# 4. Annotated[자료형, 추가규칙] -> 자료형과 추가 정보를 묶는 표기다. 함수 호출은 아니다.
#    예: Annotated[int, Path(ge=1)] -> FastAPI가 정수 변환과 1 이상 조건을 검사한다.
# 5. Path(ge=최솟값) -> 주소에서 받는 값의 규칙을 지정한다. ge=1은 1 이상이다.
#    int와 Path의 역할은 다르다. int는 정수 변환, ge=1은 숫자의 범위 검사다.
# 6. len(묶음) -> 들어 있는 항목의 개수를 구한다.
#    예: len(tasks)는 카드 개수 1이다. 카드 안의 id/title/done 칸 개수 3이 아니다.
# 7. 키 not in 딕셔너리 -> 해당 키가 없으면 True, 있으면 False다. 함수가 아니라 조건식이다.
#    예: 2 not in tasks -> 2번 카드가 없으므로 True.
# 8. HTTPException(status_code=오류번호, detail="오류 설명") -> HTTP 오류 정보를 만든다.
#    예: HTTPException(status_code=404, detail="Task not found").
# 9. raise 예외 -> 정상 실행 흐름을 멈추고 예외를 발생시키는 문법이다.
#    여기서는 FastAPI가 예외를 받아 404 응답을 보낸다. 아래 return은 실행하지 않는다.
#    서버 전체가 종료되는 것은 아니다. 다음 요청은 계속 받을 수 있다.
# 10. 딕셔너리[키] -> 그 키에 담긴 값을 꺼낸다.
#     tasks[1] -> {"id": 1, "title": "FastAPI basics", "done": False}.
# 11. return 값 -> 함수의 결과를 돌려준다. print처럼 터미널에 보여주는 명령이 아니다.
#     요청 처리 함수가 딕셔너리를 반환하면 FastAPI가 JSON 응답으로 보내 준다.

# ==================== 요청 하나를 끝까지 따라가기 ====================
# 성공 예: GET /tasks/1
# 1. 브라우저가 1번 카드 정보를 요청한다.
# 2. FastAPI가 URL의 "1"을 정수 1로 바꾸고 1 이상인지 확인한다.
# 3. read_task(task_id=1)을 호출한다.
# 4. 1번 카드가 있으므로 if 안의 오류 처리를 건너뛴다.
# 5. tasks[1]을 반환한다. 브라우저는 200과 카드 정보를 받는다.
# 없는 번호 예: GET /tasks/2
# 1. 2는 정수이고 1 이상이므로 입력 검사는 통과한다.
# 2. 함수가 실행되지만 상자에 2번 카드가 없다.
# 3. raise로 중단하고 404와 {"detail": "Task not found"}를 응답한다.
# 잘못된 입력 예: GET /tasks/0
# 1. 0은 1 이상이 아니므로 FastAPI가 422로 거절한다.
# 2. read_task 함수는 실행되지 않는다. '카드가 없다'는 검사까지 가지 않는다.
# ==================== 추가 설명 끝 ====================
