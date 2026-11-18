from typing import Annotated
from fastapi import FastAPI, Query

app = FastAPI(title="Lesson 04")
tasks = [
    {"id": 1, "title": "FastAPI basics", "done": False},
    {"id": 2, "title": "HTTP methods", "done": True},
    {"id": 3, "title": "Python review", "done": False},
]

@app.get("/tasks")
def list_tasks(
    q: str | None = None,
    done: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0, # Query(ge=0) : skip must be a non-negative integer.
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    rows = tasks
    if q is not None:
        rows = [t for t in rows if q.casefold() in t["title"].casefold()] # .casefold() : 대소문자 구분 없이 검색하기 위해 문자열을 소문자로 변환.
    if done is not None:
        rows = [t for t in rows if t["done"] == done]
    total = len(rows)
    return {"items": rows[skip:skip + limit], "total": total} # rows[skip:skip + limit] : skip부터 limit까지의 항목을 반환. total : 필터링된 전체 항목 수.


# ==================== 여기부터 추가: 코드 + 쉬운 설명 ====================
# 위는 직접 작성한 원본이다. 아래는 같은 코드를 쉬운 설명과 함께 읽는 학습용 예제다.
# 할 일 하나를 숙제 카드라고 생각하자. 카드 세 장 중 원하는 것만 골라 보여주는 실습이다.
# if False: 아래 예제는 실행하지 않는다. 위 원본으로 서버를 실행하므로 API가 중복 등록되지 않는다.
if False:
    # 자료형과 검사 규칙을 한곳에 적을 때 쓸 Annotated를 가져온다.
    from typing import Annotated
    # FastAPI는 앱을 만드는 도구, Query는 URL의 검색 조건에 규칙을 붙이는 도구다.
    from fastapi import FastAPI, Query

    # Lesson 04라는 제목의 앱을 만든다. /docs 화면에서 제목을 볼 수 있다.
    app = FastAPI(title="Lesson 04")
    # 여기서는 tasks가 리스트다. Lesson 03의 번호를 키로 쓰는 딕셔너리와 구조가 다르다.
    # 대괄호 [] 안에 카드 세 장을 넣고, 각 카드는 딕셔너리 {}로 표현한다.
    tasks = [
        # 1번 카드: FastAPI 공부, 아직 안 끝남. False는 거짓, 여기서는 미완료라는 뜻이다.
        {"id": 1, "title": "FastAPI basics", "done": False},
        # 2번 카드: HTTP 공부, 완료함. True는 참, 여기서는 완료라는 뜻이다.
        {"id": 2, "title": "HTTP methods", "done": True},
        # 3번 카드: 파이썬 복습, 아직 안 끝남.
        {"id": 3, "title": "Python review", "done": False},
    ]

    # GET /tasks 요청을 아래 list_tasks 함수에 연결한다.
    # 예: /tasks?q=python&done=false -> 제목에 python이 들어간 미완료 카드만 요청.
    # ? 뒤의 이름=값을 쿼리 매개변수라고 부른다. 여러 조건은 &로 연결한다.
    @app.get("/tasks")
    def list_tasks(
        # q는 검색할 글자다. str | None은 문자열 또는 값 없음(None)을 허용한다는 표기다.
        # = None은 q를 안 보내면 검색 조건을 적용하지 않는다는 기본값이다.
        q: str | None = None,
        # 완료 여부는 true/false로 받는다. 안 보내면 None이므로 완료 여부와 상관없이 조회한다.
        # FastAPI가 URL의 false를 파이썬 False로 바꿔 준다.
        done: bool | None = None,
        # skip은 앞에서 몇 장을 건너뛸지다. 0이면 처음부터, 1이면 첫 카드를 건너뛴다.
        # int는 정수로 변환, Query(ge=0)는 0 이상인지 검사. 생략하면 = 0을 사용한다.
        skip: Annotated[int, Query(ge=0)] = 0,
        # limit는 최대 몇 장을 보여줄지다. 1~20 사이의 정수만 받으며 생략하면 10이다.
        # ge=1은 1 이상, le=20은 20 이하. 있는 카드보다 많이 만들어 주지는 않는다.
        limit: Annotated[int, Query(ge=1, le=20)] = 10,
    ):
        # 처음에는 카드 세 장 전체를 대상으로 삼는다. 리스트를 복사하는 명령은 아니다.
        # 아래 필터는 새 리스트를 만들어 rows에 넣으므로 원래 tasks를 삭제하거나 바꾸지 않는다.
        rows = tasks
        # q가 생략되지 않았다면 제목 검색을 한다. q=None이면 이 부분을 건너뛴다.
        if q is not None:
            # casefold()는 대소문자 구분 없이 비교하기 좋게 문자열을 바꾼다.
            # 예: "PYTHON"과 "Python review" -> "python"과 "python review".
            # 문자열 A in B는 B 안에 A가 들어 있는지 확인한다. 여기서는 부분 문자열 검색이다.
            # t는 카드를 한 장씩 담는 임시 변수다. 조건을 통과한 카드만 새 리스트에 담는다.
            rows = [t for t in rows if q.casefold() in t["title"].casefold()]
        # done을 생략한 None과 미완료를 뜻하는 False는 다르다.
        # if done:이라고 쓰면 False 요청을 건너뛰므로, 반드시 None인지 구별한다.
        if done is not None:
            # 완료 여부가 요청과 같은 카드만 남긴다.
            # done=False라면 1번과 3번을 남기고, done=True라면 2번만 남긴다.
            rows = [t for t in rows if t["done"] == done]
        # 검색과 완료 조건을 적용한 전체 카드 수를 센다. 아직 skip/limit로 자르기 전이다.
        total = len(rows)
        # 리스트 위치는 0부터 센다. rows[시작:끝]은 시작 포함, 끝 제외다.
        # skip=1, limit=1이면 rows[1:2] -> 두 번째 카드 한 장만 나온다.
        # 'skip부터 limit까지'가 아니라 'skip개를 건너뛴 뒤 최대 limit개'가 정확하다.
        # items는 이번에 보여줄 카드, total은 필터 조건을 만족한 전체 개수다.
        return {"items": rows[skip:skip + limit], "total": total}

# ==================== 중요한 함수·문법 사용 형태 ====================
# 1. Query(ge=최솟값, le=최댓값): 쿼리 입력값의 범위 규칙을 지정한다.
#    예: Query(ge=1, le=20). 범위 위반이나 정수 변환 실패는 함수 실행 전 422 응답이다.
# 2. Annotated[자료형, 규칙]: 타입과 추가 정보를 묶는 표기다. 함수 호출은 아니다.
#    예: skip: Annotated[int, Query(ge=0)] = 0. 기본값은 대괄호 밖의 = 0이다.
# 3. 문자열.casefold(): 대소문자를 무시하는 비교에 사용할 문자열을 만든다.
#    예: "Python".casefold() -> "python". 일반 lower()보다 유니코드의 대소문자 차이를 더 처리한다.
# 4. len(리스트): 리스트의 항목 개수를 구한다. 예: len(tasks) -> 3.
# 5. [항목 for 항목 in 목록 if 조건]: 조건에 맞는 항목만 모아 새 리스트를 만드는 문법이다.
#    rows = [t for t in rows if t["done"] == done]은 아래와 비슷하게 생각하면 된다.
#    선택한카드 = []
#    for t in rows:
#        if t["done"] == done:
#            선택한카드.append(t)
#    rows = 선택한카드
#    리스트.append(값)은 리스트 끝에 값 하나를 추가한다.
# 6. 리스트[시작:끝]: 일부를 꺼내는 슬라이싱 문법이다. 끝 위치는 포함하지 않는다.
#    예: ["가", "나", "다"][1:2] -> ["나"]. 원본 리스트는 바뀌지 않는다.
# 7. is not None: 값이 생략된 상태(None)가 아닌지 확인한다. False나 0도 None과 다르다.
# 8. ==는 값이 같은지 비교, =는 변수에 값을 담는 문법이다.
#    t["done"] == done -> 카드의 완료 여부가 요청한 완료 여부와 같은지 비교.
# 9. return {"items": ..., "total": ...}: 두 정보를 담은 딕셔너리를 반환한다.
#    FastAPI가 JSON 응답으로 바꿔 보낸다. 파이썬 False는 JSON에서 false로 표현된다.

# ==================== 브라우저로 직접 실습하기 ====================
# day5 폴더에서: python -m uvicorn labs.lesson04:app --reload
# 다른 실습 서버가 실행 중이면 해당 터미널에서 Ctrl + C로 먼저 종료한다.
# 아래 경로 앞에 http://127.0.0.1:8000을 붙여 접속한다. 번호는 응답 items 안의 id를 말한다.
# /tasks                         -> 1, 2, 3번 카드 / total: 3 (기본 skip=0, limit=10)
# /tasks?q=PYTHON                 -> 3번 카드만 / total: 1 (대소문자 무시)
# /tasks?done=false               -> 미완료인 1, 3번 카드 / total: 2
# /tasks?done=true                -> 완료한 2번 카드 / total: 1
# /tasks?q=python&done=false      -> 두 조건에 모두 맞는 3번 카드 / total: 1
# /tasks?skip=1&limit=1           -> 2번 카드만 / total: 3
# /tasks?done=false&skip=1&limit=1 -> 미완료 [1번, 3번] 중 첫 장을 건너뛰어 3번 / total: 2
# /tasks?skip=10                  -> 보여줄 카드가 없어 items: [] / total: 3
# /tasks?q=없는제목               -> 검색 결과가 없어 items: [] / total: 0
# /tasks?skip=-1                  -> 422: skip은 0 이상이어야 함
# /tasks?limit=21                 -> 422: limit는 20 이하여야 함
# /tasks?limit=abc                -> 422: limit를 정수로 바꿀 수 없음
# total은 이번 화면의 items 개수가 아니다. 검색 조건에 맞는 전체 목록의 크기다.
# 위의 '2번 카드 한 장, total: 3' 예시가 이 차이를 보여 준다.
# /docs -> GET /tasks -> Try it out에서도 q/done/skip/limit를 입력해 시험할 수 있다.
# 위 원본의 슬라이싱 주석 'skip부터 limit까지'는 'skip개 건너뛰고 최대 limit개'로 이해하자.
# ==================== 추가 설명 끝 ====================
