### lesson01.py : 지금 실습하는 프로그램은 무엇을 할까?
# 1. 내 Mac에서 서버를 켠다.
# 2. 브라우저 주소창에 http://127.0.0.1:8000/sports 를 입력한다.
# 3. 브라우저가 서버에 "스포츠 목록을 주세요"라는 요청을 보낸다.
# 4. 서버가 lesson01.py의 sports() 함수를 실행한다.
# 5. 브라우저에 {"sports": ["축구", "야구", "농구", "배구", "테니스"]}가 보인다.

### 함수와 웹 API: 같은 기능을 두 가지 방법으로 사용하기
# 파이썬 코드 안에서 sports()라고 쓰면 함수를 직접 호출하는 것
# 브라우저에서 /sports 주소로 요청하면 웹 API를 사용하는 것
# 브라우저는 파이썬 코드의 sports()를 직접 실행하지 않는다.
# 요청을 받은 FastAPI가 sports()를 호출해 결과를 응답으로 만든다.
# 비유: 함수는 주방의 조리 과정, 웹 API는 손님이 주문하는 창구와 주문 규칙이다.
# API는 넓은 말이다. 예를 들어 random.randint(1, 10)도 라이브러리 API 사용이다.
# 따라서 "API는 무조건 인터넷으로 호출한다"는 뜻은 아니다.

### FastAPI는 무엇을 해줄까?
# 우리가 정할 내용: "/sports로 요청하면 스포츠 목록을 보내자."
# FastAPI가 돕는 내용: 주소에 맞는 함수 찾기, 함수의 결과를 응답으로 바꾸기.
# @app.get("/sports")를 쓰면 /sports 주소와 sports 함수를 연결할 수 있다.
# 이런 기능을 처음부터 직접 만들지 않도록 기본 틀을 제공하는 것이 프레임워크다.
# FastAPI는 특히 웹 API를 만들기 위한 파이썬 프레임워크
# Django(장고)도 파이썬 웹 프레임워크
# 예를 들어 회원제 게시판을 만들 때 로그인, 관리자 화면 등의 기본 기능을 활용할 수 있다.
# FastAPI와 Django는 목적에 맞춰 고르는 도구이며, 둘 다 설치해야 하는 것은 아님

### app과 Uvicorn은 어떻게 다를까?
# app: "GET /는 root 함수, GET /sports는 sports 함수" 같은 처리 규칙을 담은 웹 앱.
# Uvicorn(유비콘): 8000번 포트에서 요청을 기다리고 app에 전달하는 서버 프로그램.
# 비유: app은 주문별로 일하는 주방, Uvicorn은 주문을 받고 음식을 전달하는 직원.
# app = FastAPI()만 적으면 웹 앱 객체가 만들어질 뿐, 요청을 기다리는 서버가 켜지지는 않는다.
# day5 폴더에서 아래 명령을 실행하면 Uvicorn이 app을 불러와 서버를 켠다.
## python -m uvicorn labs.lesson01:app --reload
# labs.lesson01 -> labs 폴더 안의 lesson01.py 파일을 찾는다.
# :app -> 그 파일에 있는 app 변수를 사용한다.
# --reload -> 파일 수정 후 저장하면 서버를 자동 재시작한다. 브라우저는 직접 새로고침한다.
# 서버를 끄려면 실행 중인 터미널에서 Ctrl + C를 누른다.
# Apache(아파치)도 웹 서버 프로그램이다. 예를 들어 HTML이나 이미지 파일을 제공할 수 있다.
# 지금 실습에서는 Uvicorn을 사용하므로 Apache를 별도로 설치할 필요는 없다.

# http://127.0.0.1:8000/sports 주소를 나누어 읽기
# http://   -> HTTP라는 방식으로 요청하고 응답
# 127.0.0.1 -> "지금 요청하는 컴퓨터 자기 자신"을 가리키는 특별한 IP 주소
# :8000     -> 그 컴퓨터에서 8000번 포트로 요청
# /sports   -> 이 앱에서 스포츠 목록을 요청하는 경로
# 비유: IP는 건물 주소, 포트는 건물의 출입구 번호, 경로는 그 안에서 찾는 업무
# 현재 lesson01의 /는 HTML 제목을 보여주고,
# /sports에 접속하면 스포츠 목록을 받는다.
# 내 Mac에서 서버를 켜고 내 Mac의 브라우저로 접속하므로 인터넷에 공개할 필요가 없다.
# *** 친구가 친구 컴퓨터에서 127.0.0.1로 접속하면 내 Mac이 아니라 친구 컴퓨터를 가리킨다. ***


### 도메인과 DNS
# 도메인은 example.com처럼 사람이 기억하기 쉬운 이름이
# DNS는 그 이름으로 접속할 때 필요한 IP 주소를 찾아주는 시스템
# 비유: 도메인은 연락처에 저장한 이름, IP는 전화번호, DNS는 번호를 찾아주는 주소록
# 도메인이 IP 숫자 자체를 바꾸는 것은 아니다.
# localhost는 보통 자기 컴퓨터를 가리키는 이름
# 이 실습에서는 http://localhost:8000/sports 로도 접속할 수 있음 


### 가상환경: 실습에 쓸 도구를 따로 담아둔 상자라고 생각하기
# py313과 .venv는 서로 다른 상자다. 한쪽에 설치한 FastAPI가 다른 쪽에도 설치되지는 않음 
# 터미널 앞의 (.venv)는 현재 .venv 상자의 파이썬과 패키지를 사용한다는 표시
# Conda: 상자를 만들면서 Python 3.13 같은 원하는 파이썬 버전도 설치할 수 있다.
# 예: conda create -n py313 python=3.13 -> py313 생성
#     conda activate py313 -> py313 사용 시작
# venv: 지금 실행하는 파이썬을 기반으로 별도 환경을 만든다.
# 예: Python 3.13 환경에서 python -m venv .venv -> 3.13 기반의 .venv 생성
# .venv라는 이름만 보고 버전을 알 수는 없다. python --version으로 확인 

### 현재 폴더와 가상환경은 역할이 다르다.
# AIO_4_class/.venv -> 사용할 파이썬과 패키지가 있는 곳
# AIO_4_class/day5  -> 지금 작업하고 파일을 찾는 곳
# day5에서 source ../.venv/bin/activate -> 한 단계 위(..)의 .venv 활성화
# cd labs로 이동해도 선택한 가상환경은 유지된다.
# day5에서 python -m pip install -r requirements.txt 를 실행하면:
# 1. python -m pip: 현재 환경의 파이썬으로 패키지 설치 도구를 실행한다.
# 2. -r requirements.txt: 현재 폴더에 있는 설치 목록을 읽는다.
# 3. 목록에 적힌 패키지를 현재 환경에 설치한다.
# 예: (.venv) 상태라면 day5의 목록을 읽어 .venv에 설치한다.


### Lesson 01 복습: 요청 연결과 응답 반환
# 앱 생성: app = FastAPI(title="Lesson 01")
#   -> 웹 앱 객체를 만들고 문서 제목을 지정한다.
# 요청 연결: @app.get("/sports")
#   -> GET /sports 요청을 바로 아래 함수가 처리하도록 등록한다.
# JSON 응답: return {"sports": ["축구", "야구"]}
#   -> 딕셔너리를 반환하면 FastAPI가 JSON 응답으로 보낸다.
# HTML 응답: @app.get("/", response_class=HTMLResponse)
#   -> 함수의 반환값을 HTML 응답으로 보낸다.
# HTML 내용: return "<h1>Hello FastAPI</h1>"
#   -> 브라우저가 제목으로 표시할 HTML 문자열을 반환한다.

### Lesson 02 복습: 메서드 구분과 상태 코드 지정
# 조회 등록: @app.get("/method")
#   -> GET /method 요청을 아래 함수에 연결한다.
# POST 등록: @app.post("/method", status_code=201)
#   -> POST 요청을 연결하고 정상 반환 시 상태 코드 201을 보낸다.
# 기본 응답: @app.post("/method")
#   -> 상태 코드 생략 시 정상 반환의 기본값은 200이다.
# 응답 본문: return {"method": "POST", "purpose": "create"}
#   -> 반환값을 JSON으로 보낸다. 상태 코드 지정과 본문 반환은 별개다.

### Lesson 03 복습: 경로 입력값 검사와 번호별 조회
# 개수 조회: return {"total": len(tasks)}
#   -> 딕셔너리에 저장된 항목 개수를 반환한다.
# 경로 변수: @app.get("/tasks/{task_id}")
#   -> 주소의 번호 부분을 같은 이름의 함수 인자로 받는다.
# 입력 검사: task_id: Annotated[int, Path(ge=1)]
#   -> FastAPI가 정수로 변환하고 1 이상인지 검사한다.
# 존재 검사: if task_id not in tasks:
#   -> 해당 번호 키가 없을 때만 안쪽 코드를 실행한다.
# 오류 응답: raise HTTPException(status_code=404, detail="Task not found")
#   -> 정상 흐름을 멈추고 404와 오류 설명을 전달한다.
# 항목 조회: return tasks[task_id]
#   -> 해당 번호 키에 저장된 정보를 반환한다.
# 경로 순서: /tasks/stats를 /tasks/{task_id}보다 먼저 등록
#   -> 고정 문자열 stats가 번호 자리로 인식되는 것을 방지한다.

### Lesson 04 복습: 쿼리 검색·필터·목록 자르기
# 검색 입력: q: str | None = None
#   -> 검색어를 문자열로 받고 생략하면 None을 사용한다.
# 완료 입력: done: bool | None = None
#   -> 완료 여부를 불리언으로 받고 생략하면 None을 사용한다.
# 건너뛰기: skip: Annotated[int, Query(ge=0)] = 0
#   -> 0 이상 정수이며 기본값은 0이다.
# 개수 제한: limit: Annotated[int, Query(ge=1, le=20)] = 10
#   -> 1~20 사이 정수이며 기본값은 10이다.
# 조건 적용: if q is not None: / if done is not None:
#   -> 값을 생략하지 않았을 때만 조건을 적용한다. False도 입력값으로 처리한다.
# 제목 검색: rows = [t for t in rows if q.casefold() in t["title"].casefold()]
#   -> 대소문자를 구분하지 않고 검색어가 제목에 포함된 항목만 새 리스트로 모은다.
# 완료 필터: rows = [t for t in rows if t["done"] == done]
#   -> 완료 여부가 요청값과 같은 항목만 새 리스트로 모은다.
# 전체 개수: total = len(rows)
#   -> 필터 적용 후, 목록을 자르기 전의 개수를 센다.
# 목록 자르기: rows[skip:skip + limit]
#   -> skip개를 건너뛰고 최대 limit개를 꺼낸다. 끝 위치는 제외한다.
# 결과 구성: return {"items": rows[skip:skip + limit], "total": total}
#   -> 선택한 목록과 필터 결과의 전체 개수를 함께 반환한다.

### Lesson 05 복습: 입력·응답 모델과 새 항목 생성
# 입력 모델: class TaskInput(BaseModel):
#   -> 입력 양식을 정의하고 Pydantic의 검증 기능을 상속한다.
# 모델 설정: model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
#   -> 문자열 양끝 공백을 제거하고 정의하지 않은 필드를 거절한다.
# 제목 규칙: title: str = Field(min_length=1, max_length=80)
#   -> 필수 문자열이며 길이는 1~80자다.
# 완료 규칙: done: bool = Field(default=False, strict=True)
#   -> 생략하면 False, 입력하면 실제 불리언만 허용한다.
# 응답 모델: class TaskOut(TaskInput): 안에 id: int
#   -> 입력 모델의 필드를 물려받고 정수 id를 추가한다.
# 응답 검증: response_model=TaskOut / response_model=list[TaskOut]
#   -> 한 개 / 목록의 응답 구조와 검증 규칙을 지정한다.
# 전체 조회: return list(tasks.values())
#   -> 딕셔너리의 값들을 리스트로 만들어 반환한다.
# 공통 조회: return require_task(task_id)
#   -> 없으면 404를 발생시키는 도우미의 조회 결과를 반환한다.
# 본문 입력: def create_task(payload: TaskInput):
#   -> 요청 본문을 검증한 TaskInput 객체로 받는다.
# 번호 변경: global next_id
#   -> 함수 밖의 번호 변수를 함수 안에서 변경하겠다고 선언한다.
# 모델 변환: payload.model_dump()
#   -> 모델 객체를 파이썬 딕셔너리로 바꾼다.
# 항목 구성: task = {"id": next_id, **payload.model_dump()}
#   -> 입력 딕셔너리의 항목들을 펼쳐 새 번호와 합친다.
# 항목 저장: tasks[next_id] = task
#   -> 새 번호를 키로 사용해 딕셔너리에 항목을 저장한다.
# 번호 증가: next_id += 1
#   -> 다음에 사용할 번호를 1 늘린다.
# 생성 응답: return task
#   -> 생성한 항목을 반환한다. 데코레이터의 status_code=201이 응답 코드를 지정한다.
# 펼치기: **딕셔너리 / *리스트
#   -> 각 항목을 펼친다. {"id": 2, **입력값}, [*list_1, *list_2]처럼 합칠 때 사용한다.

### Lesson 06 복습: 전체 교체·일부 수정과 추가 검증
# 전체 교체 등록: @app.put("/tasks/{task_id}", response_model=TaskOut)
#   -> PUT 요청을 교체 함수에 연결한다.
# 전체 교체: tasks[task_id] = {"id": task_id, **payload.model_dump()}
#   -> 같은 번호의 내용을 새 입력 모델의 값으로 바꾼다. 생략한 done도 기본값 False로 바뀐다.
# 수정 모델: class TaskPatch(BaseModel):
#   -> 일부 필드만 받는 입력 양식을 정의한다.
# 생략 허용: title: str | None = Field(default=None, min_length=1, max_length=80)
#   -> 생략 시 None, 문자열 입력 시 길이 검사. 직접 입력한 null은 아래 검증 함수가 거절한다.
# 필드 검사: @field_validator("title", "done", mode="before")
#   -> 기본 필드 검사 전에 reject_null을 실행하도록 등록한다.
# 클래스 메서드: @classmethod / def reject_null(cls, value):
#   -> cls로 클래스를, value로 검사할 값을 받는다.
# null 거절: if value is None: 다음에 raise ValueError("Explicit null is not allowed")
#   -> 직접 보낸 null을 검증 오류로 거절한다.
# 전체 검사: @model_validator(mode="after")
#   -> 필드 검사 후 require_field로 모델 전체를 검사한다.
# 빈 요청 검사: if not self.model_fields_set:
#   -> 직접 보낸 필드 이름 집합이 비었는지 확인한다.
# 빈 요청 거절: raise ValueError("Provide at least one field")
#   -> 바꿀 필드가 없는 요청을 거절한다. 검증 성공 시 return self로 모델을 반환한다.
# 일부 수정 등록: @app.patch("/tasks/{task_id}", response_model=TaskOut)
#   -> PATCH 요청을 수정 함수에 연결한다.
# 기존 항목 참조: task = require_task(task_id)
#   -> 기존 딕셔너리를 참조한다. 번호가 없으면 404로 중단한다.
# 수정값 추출: payload.model_dump(exclude_unset=True)
#   -> 사용자가 직접 보낸 필드만 딕셔너리로 꺼낸다.
# 일부 수정: task.update(payload.model_dump(exclude_unset=True))
#   -> 기존 항목의 전달받은 필드만 덮어쓴다.
# 수정 응답: return task
#   -> 수정된 항목을 반환한다. 참조한 원본도 함께 바뀐다.

### Lesson 07 복습: 항목 삭제와 본문 없는 응답
# 삭제 등록: @app.delete("/tasks/{task_id}", status_code=204)
#   -> DELETE 요청을 연결하고 정상 응답 코드 204를 지정한다.
# 번호 검사: task_id: Annotated[int, Path(ge=1)]
#   -> 정수이면서 1 이상인 번호만 받는다.
# 존재 확인: require_task(task_id)
#   -> 없으면 404로 중단하고, 있으면 다음 줄로 진행한다.
# 항목 삭제: del tasks[task_id]
#   -> 해당 번호의 키와 값을 딕셔너리에서 제거한다.
# 삭제 응답: return Response(status_code=204)
#   -> 본문 없이 삭제 성공(204 No Content)을 알린다.

# 딕셔너리와 JSON: 파이썬 안의 값과 HTTP로 주고받는 표현 구분하기
# 파이썬 안: {"done": False} -> 딕셔너리이며 False는 파이썬의 거짓 값.
# HTTP 응답 본문: {"done": false} -> JSON 형식이며 거짓은 소문자 false로 표기.
# FastAPI가 응답으로 변환하므로 이 예제에서는 직접 문자열로 바꿀 필요가 없다.
# tasks 딕셔너리는 DB가 아니다. 서버 재시작 시 파일의 초기 값으로 다시 만들어진다.
# 따라서 이 실습에서 메모리 값만 바꿔도 영구 저장되는 것은 아니다.

# 파일별로 실행해서 관찰하기 (현재 폴더: day5)
# lesson01: python -m uvicorn labs.lesson01:app --reload -> /, /sports, /menu 확인
# lesson02: python -m uvicorn labs.lesson02:app --reload -> /docs에서 GET/POST 비교
# lesson03: python -m uvicorn labs.lesson03:app --reload -> /tasks/1, /tasks/2, /tasks/0 비교
# lesson04: python -m uvicorn labs.lesson04:app --reload -> /tasks?q=python 등 검색 조건 비교
# lesson05: python -m uvicorn labs.lesson05:app --reload -> /docs에서 POST 추가 후 GET으로 확인
# lesson06: python -m uvicorn labs.lesson06:app --reload -> /docs에서 PUT과 PATCH의 결과 비교
# lesson07: python -m uvicorn labs.lesson07:app --reload -> /docs에서 DELETE 후 GET으로 확인
# 각 파일은 별도 앱이다. lesson03을 실행했다고 lesson01의 /menu까지 생기지는 않는다.
# 실습을 바꿀 때는 기존 서버를 Ctrl + C로 종료한 뒤 다음 명령을 실행한다.
# 어느 앱을 실행했는지 헷갈리면 /docs의 Lesson 01~07 제목을 확인한다.



# ==================== 추가 정리 시작: 명령어 · 가상환경 · 라우팅 ====================
# 아래는 질문·답변과 가상환경 명령을 추가로 정리한 부분입니다.

# 질문 정리: 명령어의 옵션과 가상환경 위치
# Q. conda create -n py313 python=3.13에서 -n은?
# A. name(이름)을 지정하는 옵션이며 --name과 같다.
#    conda create -> 환경 생성 / -n py313 -> 이름 지정 / python=3.13 -> 설치할 버전 지정.
#    py313이라는 이름만 붙였다고 3.13이 되는 것은 아니다. 버전은 python=3.13이 정한다.

# Q. python -m venv .venv에서 venv와 .venv는?
# A. venv는 파이썬에 포함된 가상환경 생성 모듈이고, .venv는 생성할 폴더 경로다.
#    -m은 현재 파이썬으로 모듈을 찾아 실행하라는 옵션이다.
#    AIO_4_class에서 실행하면 AIO_4_class/.venv에 생성한다.
#    python -m venv myenv라면 myenv 폴더에 생성한다. 이름은 바꿀 수 있다.
#    Python 3.13으로 이 명령을 실행해야 3.13 기반 환경이 만들어진다.

# Q. 파이썬은 AIO_4_class/.venv에 있는데 왜 day5에서 사용할 수 있을까?
# A. '작업할 파일을 찾는 위치'와 '실행할 프로그램이 있는 위치'가 달라도 되기 때문이다.
#    비유: Word 프로그램과 내가 작성한 문서가 서로 다른 폴더에 있어도 문서를 열 수 있다.
#    가상환경 활성화는 현재 터미널의 PATH(명령어 검색 경로)에 .venv/bin을 먼저 넣는다.
#    그래서 day5에서 python이라고 입력해도 .venv/bin/python을 찾아 실행한다.
#    그 파이썬은 자기 환경의 패키지 폴더에서 FastAPI, Uvicorn 등을 찾는다.
#    내 소스코드를 .venv 안에 넣거나 라이브러리를 day5에 복사할 필요는 없다.
#    day5에서 python -m uvicorn labs.lesson03:app --reload를 실행하는 예:
#    - 파이썬: AIO_4_class/.venv/bin/python
#    - Uvicorn과 FastAPI: .venv 안에 설치된 패키지
#    - 내 코드: 현재 위치 기준 labs/lesson03.py
#    단, 파일 경로는 현재 위치에 영향을 받는다. labs 폴더로 이동하면 실행 경로도 달라진다.

# Q. (.venv) (base) ... day5 % 표시는?
# A. (.venv)는 venv 환경 활성화, (base)는 Conda 기본 환경 활성화, day5는 현재 폴더다.
#    Conda base 위에 .venv를 활성화하면 둘 다 표시될 수 있다.
#    라이브러리가 두 환경에 동시에 설치된다는 의미는 아니다.
#    실제 사용하는 파이썬은 표시 이름보다 아래 명령의 결과로 확인하는 것이 정확하다.
#    python -c "import sys; print(sys.executable)"
#    -> 이 실습에서는 /Users/imijeong/Downloads/AIO_4_class/.venv/bin/python이 예상된다.
#    python --version -> 현재 파이썬 버전 확인.
#    python -m pip --version -> 현재 pip와 패키지 설치 환경의 경로 확인.

# Q. python -m pip install -r requirements.txt에서 -r은?
# A. requirements(설치 요구 목록) 파일을 지정하는 옵션이며 --requirement와 같다.
#    python -m pip -> 현재 파이썬으로 pip 실행 / install -> 설치 / -r -> 파일에서 목록 읽기.
#    requirements.txt에 fastapi와 uvicorn이 적혀 있다면 그 두 패키지를 설치한다.
#    fastapi==특정버전처럼 적혀 있으면 해당 버전을 지정해서 설치한다.
#    -r은 '지금 파일에 적힌 목록을 읽어라'이지 파일을 실행하라는 의미가 아니다.
#    day5에서 실행하면 day5/requirements.txt를 읽고, 활성화된 .venv 환경에 설치한다.
#    AIO_4_class에서 실행하려면 python -m pip install -r day5/requirements.txt로 경로 지정.
#    -r 없이 pip install requirements.txt라고 쓰면 파일 속 목록을 읽지 않는다.

# Mac에서 사용한 명령어 정리: 생성과 활성화는 다르다.
# 생성은 환경이 없을 때 하는 작업이고, 활성화는 현재 터미널에서 사용할 환경을 고르는 작업이다.
# 아래 명령들은 복습용이다. 기존 .venv가 있으면 새로 생성하지 말고 활성화 단계만 사용한다.

# 1. Conda 환경 py313 생성과 사용 (현재 폴더와 관계없이 이름으로 선택)
# conda create -n py313 python=3.13  -> 없을 때 한 번 생성
# conda activate py313              -> 사용 시작. 터미널 앞에 (py313)
# python --version                  -> Python 3.13.x인지 확인
# where python                      -> Mac zsh에서 python 명령을 찾는 위치 확인
# conda deactivate                  -> Conda 환경에서 빠져나옴. 이전 환경에 따라 (base)가 남을 수 있음

# 2. .venv를 처음 만들었던 흐름 (AIO_4_class 폴더에서, py313 활성화 후)
# conda activate py313
# python -m venv .venv              -> py313의 파이썬을 기반으로 프로젝트의 .venv 생성
# 이미 만들었다면 이 생성 명령을 반복할 필요는 없다.

# 3. 이미 있는 .venv 활성화 (현재 위치에 맞는 명령 하나만 사용)
# AIO_4_class에서:      source .venv/bin/activate
# AIO_4_class/day5에서: source ../.venv/bin/activate
# ../는 한 단계 위 폴더를 뜻한다. 명령을 입력해도 현재 작업 폴더 자체는 바뀌지 않는다.
# source는 활성화 스크립트를 현재 터미널에 적용한다. 새 환경을 만드는 명령은 아니다.
# Windows cmd의 .venv\Scripts\activate.bat는 Mac zsh에서 사용하는 명령이 아니다.

# 4. py313에서 .venv로 바꿀 때 (현재 위치: day5)
# conda deactivate
# source ../.venv/bin/activate
# python --version
# python -c "import sys; print(sys.executable)"
# python -m pip install -r requirements.txt  -> .venv에 필요한 패키지 설치
# python -m uvicorn labs.lesson03:app --reload
# 서버 종료는 Ctrl + C. 서버 실행 중인 터미널에서는 종료 후 다른 명령을 입력한다.

# 5. .venv 사용을 끝내거나 py313으로 돌아갈 때
# deactivate                       -> venv 비활성화. .venv 폴더나 설치 패키지는 삭제하지 않음
# conda activate py313              -> 다시 py313 선택
# venv는 deactivate, Conda는 conda deactivate라는 차이가 있다.
# 새 터미널에서는 활성화 상태가 다를 수 있으므로 프롬프트와 실제 파이썬 경로를 확인한다.
# VS Code의 실행 버튼도 같은 환경을 쓰려면 Python: Select Interpreter에서 .venv/bin/python 선택.

# 질문 정리: '메서드와 경로를 함수에 연결한다'는 라우팅이란?
# 예: 안내 직원이 방문 목적과 창구 번호를 보고 담당자를 찾아주는 것과 비슷하다.
# 웹 요청에는 '요청 방식(GET/POST 등)'과 '경로(/method 등)'가 들어 있다.
# FastAPI에 아래처럼 담당 함수를 미리 등록해 둔다. 아래 코드는 설명용 주석이다.
#
# @app.get("/method")
# def read_method():
#     return {"method": "GET", "purpose": "read"}
#
# @app.post("/method", status_code=201)
# def create_method():
#     return {"method": "POST", "purpose": "create"}
#
# 위 코드가 만드는 연결표:
# 요청 방식 | 경로    | 실행할 함수
# GET       | /method | read_method
# POST      | /method | create_method
#
# 브라우저 주소창에 http://127.0.0.1:8000/method 입력:
# 1. 브라우저가 GET /method 요청을 보낸다.
# 2. FastAPI가 연결표에서 GET과 /method가 일치하는 항목을 찾는다. 이 과정이 라우팅이다.
# 3. 연결된 read_method 함수를 실행하고 그 결과를 응답한다.
# /docs에서 POST /method를 골라 Execute:
# 1. 이번에는 POST /method 요청을 보낸다.
# 2. 경로는 같아도 방식이 POST이므로 create_method로 연결한다.
# 3. create_method의 결과와 설정한 201 상태 코드를 응답한다.
# 함수 이름이 read_method여서 GET이 되는 것이 아니다. @app.get이 연결 규칙을 등록한다.
# status_code=201은 함수 선택 기준이 아니라 처리 후 보내는 응답 코드 설정이다.
# 등록된 경로가 없으면 보통 404, 경로는 있지만 지원하지 않는 메서드로 요청하면 보통 405다.
# lesson02에 GET/POST /method만 있다면 GET /unknown은 404, DELETE /method는 405다.

# ==================== 추가 정리 끝: 명령어 · 가상환경 · 라우팅 ====================


# ==================== 추가 시작: 지금까지 질문한 내용과 답변 모음 ====================
# 앞의 Lesson별 정리는 실습 순서대로, 아래는 내가 궁금했던 질문 순서대로 복습하는 부분이다.
# 아래 예제 코드도 모두 주석이므로 이 파일을 실행해도 서버가 켜지거나 환경이 바뀌지 않는다.

### 질문 01. Python 3.13으로 바꾸려면? VS Code에서만 쓸 수 있나?
# 답: Python 3.13 환경을 만들고 그 환경의 파이썬을 선택한다. VS Code 밖의 Mac 터미널에서도 쓴다.
# conda create -n py313 python=3.13 -> 이름이 py313인 환경에 Python 3.13 설치.
# conda activate py313 -> 현재 터미널에서 그 환경 사용.
# python --version -> 실제 버전 확인. 환경 이름만으로 버전을 보장하는 것은 아니다.
# VS Code: Cmd + Shift + P -> Python: Select Interpreter -> 사용할 환경 선택.
# VS Code의 실행 버튼과 터미널이 같은 환경을 쓰는지 각각 확인하면 혼동을 줄일 수 있다.
# Mac에 원래 있던 파이썬이나 기존 base 환경을 지울 필요는 없다.

### 질문 02. 가상환경은 무엇이고, py313과 .venv는 어떻게 다른가?
# 답: 실습에 사용할 파이썬과 라이브러리를 따로 관리하는 도구 상자라고 생각하면 된다.
# py313은 Conda로 만든 환경 이름이고, .venv는 venv로 만든 환경 폴더 이름이다.
# 둘 다 가상환경이지만 서로 별개다. py313에 설치한 FastAPI가 .venv에 자동으로 설치되지는 않는다.
# py313의 위치 예: /Users/imijeong/anaconda3/envs/py313
# .venv의 위치 예: /Users/imijeong/Downloads/AIO_4_class/.venv
# 생성은 상자를 만드는 일, 활성화는 이번 터미널에서 사용할 상자를 고르는 일이다.
# python -m venv .venv는 실행한 위치에 폴더를 만든다. .으로 시작하므로 Mac에서는 숨김 폴더다.
# ls -a로 숨김 폴더까지 볼 수 있다. day5에서 안 보인다면 상위 폴더에 있을 수 있다.

### 질문 03. source .venv/bin/activate와 .venv\Scripts\activate.bat는?
# 답: 둘 다 만들어 둔 venv 환경을 활성화하는 스크립트지만 사용하는 터미널이 다르다.
# Mac zsh/bash: source .venv/bin/activate (프로젝트 최상위에서)
# Mac zsh/bash: source ../.venv/bin/activate (day5에서. ..는 상위 폴더)
# Windows cmd: .venv\Scripts\activate.bat (그 위치 아래에 .venv가 있을 때)
# source는 스크립트 내용을 현재 터미널에 적용하라는 명령이다. 환경 생성 명령은 아니다.
# Conda의 py313을 쓰고 있다면 venv 활성화를 추가로 할 필요 없이 그대로 실습할 수 있다.
# py313에서 .venv로 전환할 때는 conda deactivate 후 위치에 맞는 source 명령을 사용했다.
# .venv에서 나올 때는 deactivate, Conda 환경에서 나올 때는 conda deactivate를 쓴다.
# 비활성화는 환경 폴더를 삭제하는 일이 아니다. 나중에 다시 활성화할 수 있다.

### 질문 04. .venv는 상위에 있는데 왜 day5의 코드에서 라이브러리를 쓰나?
# 답: 프로그램이 설치된 위치와 내가 작성한 파일 위치는 달라도 된다. Word와 문서가 다른 곳인 것과 같다.
# 활성화하면 python 명령이 .venv/bin/python을 먼저 찾게 된다.
# 그 파이썬은 자기 환경에 설치된 FastAPI 등의 패키지를 찾아 사용한다.
# 현재 폴더 day5는 requirements.txt나 labs/lesson01.py 같은 작업 파일을 찾는 기준이다.
# cd로 작업 폴더를 바꿔도 활성화한 환경이 자동으로 바뀌지는 않는다.
# (.venv) (base) ... day5 %는 venv와 Conda base 활성화 표시, 그리고 현재 폴더를 보여준다.
# 어느 파이썬인지 확실히 알려면 python -c "import sys; print(sys.executable)"로 경로를 확인한다.

### 질문 05. 명령어의 -n, -m, -r은 무엇인가?
# 답: 각각 뒤에 오는 값의 역할을 알려주는 옵션이다. 같은 글자라도 다른 도구에서는 뜻이 다를 수 있다.
# conda create -n py313 python=3.13의 -n은 --name: 환경 이름을 지정한다.
# python -m venv .venv의 -m은 모듈(module) 실행 옵션: venv 모듈로 .venv 폴더에 환경 생성.
# python -m uvicorn ...도 현재 파이썬으로 uvicorn 모듈을 실행한다는 뜻이다.
# python lesson03.py는 파일 경로로 실행, python -m uvicorn은 모듈 이름으로 실행한다.
# python -m pip install -r requirements.txt의 -r은 --requirement: 파일에서 설치 목록 읽기.
# 예: 파일에 fastapi, uvicorn이 적혀 있다면 두 패키지를 현재 파이썬 환경에 설치한다.
# (.venv) 상태의 day5에서 실행 -> day5/requirements.txt를 읽고 .venv 환경에 설치.
# -r 없이 pip install requirements.txt라고 쓰면 파일 속 목록을 읽는 동작이 아니다.

### 질문 06. command not found나 requirements.txt를 못 찾는 오류는 왜 났나?
# 답: Mac에서 Windows 명령을 쓰거나, 현재 폴더에 없는 파일 경로를 지정했기 때문이다.
# dir 대신 Mac에서는 ls를 사용한다. pwd는 현재 폴더의 전체 경로를 보여준다.
# Windows용 .venv\Scripts\activate.bat 대신 Mac용 source 명령을 사용한다.
# AIO_4_class에서 설치: python -m pip install -r day5/requirements.txt
# day5에서 설치: python -m pip install -r requirements.txt
# VS Code에서 파일을 열었다고 터미널이 그 파일의 폴더로 자동 이동하는 것은 아니다.
# Successfully installed는 설치 성공이다. pip 업데이트 notice는 설치 실패가 아니라 안내다.

### 질문 07. 프레임워크, Django, FastAPI, Uvicorn, Apache는?
# 답: 프레임워크는 자주 필요한 기능과 작성 구조를 제공하는 기본 틀이다.
# 예: 주소마다 함수를 찾아 실행하는 기능을 매번 직접 만들지 않고 @app.get으로 등록할 수 있다.
# Django(장고), FastAPI, Flask는 파이썬 웹 프레임워크다. 장고만 있는 것이 아니다.
# Django는 회원제 게시판을 만들 때 쓸 로그인·관리자 화면 등의 기본 기능을 폭넓게 제공한다.
# FastAPI는 웹 API를 만들 때 주소 연결, 입력 검사, 응답 생성, API 문서 등을 돕는다.
# Uvicorn(유비콘)은 네트워크 요청을 받아 FastAPI 앱에 전달하고 응답을 돌려주는 서버 프로그램이다.
# 비유: FastAPI 앱은 주문을 처리하는 주방, Uvicorn은 주문과 결과를 전달하는 직원이다.
# app = FastAPI()만으로 네트워크 서버가 켜지지 않는다. Uvicorn으로 app을 실행한다.
# Apache HTTP Server도 웹 서버 프로그램이다. 현재 실습은 Apache 없이 Uvicorn으로 실행한다.
# PastAPI, uicon은 대화에서 나온 오타이고 여기서 사용하는 정확한 이름은 FastAPI, Uvicorn이다.

### 질문 08. --reload는 왜 넣나? main:app은 어디에서 실행하나?
# 답: --reload는 코드 수정·저장 시 개발 서버를 자동 재시작해서 변경 사항을 적용하는 옵션이다.
# 옵션을 빼도 실행되지만 수정 후 직접 재시작해야 한다. 브라우저 새로고침은 별도로 해야 한다.
# day5에서 실습 실행: python -m uvicorn labs.lesson03:app --reload
# labs.lesson03:app은 labs/lesson03.py 파일의 app 객체를 사용한다는 뜻이다.
# day5에서 계산기 실행: python -m uvicorn calculator.main:app --reload
# calculator에서 실행: python -m uvicorn main:app --reload
# 파일 경로 표기는 calculator/main.py지만 모듈 이름 표기는 calculator.main이다. 여기서는 / 대신 . 사용.
# day5에서 main:app만 쓰면 그 위치에서 main 모듈을 못 찾아 Could not import module 오류가 날 수 있다.
# Application startup complete가 나오면 앱 시작 완료. http://127.0.0.1:8000으로 접속한다.
# 서버 종료는 Ctrl + C. --reload는 개발용이며 실제 운영에서는 일반적으로 사용하지 않는다.

### 질문 09. 메서드·엔드포인트·라우팅·라우터는 어떻게 다른가?
# 답: 음식점에 비유하면 요청 방식, 주문 창구, 담당자에게 보내는 과정, 그 연결을 관리하는 도구다.
# 메서드: GET은 조회, POST는 제출/생성 등 요청 의도를 구분한다. 실제 작업 코드는 별도로 작성한다.
# 엔드포인트: 기능에 접근하는 접점. GET /menu처럼 메서드와 경로를 함께 적으면 정확하다.
# 라우팅: GET /menu 요청을 menu() 함수로 연결하는 과정.
# 라우터: 이런 연결 규칙을 관리하고 알맞은 함수로 보내는 도구. FastAPI 앱 내부에도 있다.
# 기능이 많아지면 APIRouter로 회원 API, 주문 API처럼 묶어 관리할 수 있다.
# 예시 코드:
# from fastapi import APIRouter
# router = APIRouter()
# @router.get("/menu")
# def menu():
#     return {"menu": ["짜장면", "짬뽕"]}
# app.include_router(router) -> router에 등록한 API들을 app에 포함한다.
# APIRouter 자체가 별도의 Uvicorn 서버인 것은 아니다.

### 질문 10. 200과 201을 왜 구분하나? 201을 쓰면 저장되나?
# 답: 코드 종류가 아니라 이번 요청을 처리한 결과를 알려주는 공통 약속이다.
# 200 OK: 처리 성공. 예: 주문 목록 조회 성공.
# 201 Created: 새 데이터 생성 성공. 예: 새 주문 저장 성공.
# 204 No Content: 처리 성공, 응답 본문 없음. 예: Lesson 07의 삭제 성공.
# @app.post("/method")는 정상 반환 시 기본 200, status_code=201을 붙이면 정상 반환 시 201이다.
# 두 경우 return이 같다면 응답 본문은 같고 상태 코드만 다르다. POST라고 자동으로 201이 되지 않는다.
# 201은 '생성 버튼'이 아니라 '생성 완료 표시'다. 배송 완료 표시만 바꾼다고 실제 배달이 되지 않는 것과 같다.
# 실제 순서: DB에 새 주문 저장 -> 성공 확인 -> 201과 주문 정보 응답.
# 저장 코드가 있어도 저장에 실패하면 201을 보내면 안 된다. 오류 원인에 맞는 응답이 필요하다.
# 클라이언트는 서버 내부 코드를 읽을 수 없어도 201을 통해 생성에 성공했음을 알 수 있다.
# lesson02는 상태 코드 실습이라 딕셔너리를 반환할 뿐 실제 주문이나 DB 데이터를 생성하지 않는다.

### 질문 11. 콜백 함수와 이벤트 처리 함수는?
# 답: 콜백은 다른 코드에 맡겨 두었다가 그 코드가 필요한 때 호출하는 함수다.
# def say_hello():
#     print("안녕하세요!")
# def run_callback(callback):
#     callback()
# run_callback(say_hello) -> 함수 자체를 전달. run_callback이 받아서 호출한다.
# say_hello는 함수 자체, say_hello()는 지금 실행하는 표현이다.
# 이벤트 처리 함수는 버튼 클릭이나 키 입력 같은 일이 발생했을 때 실행되는 담당 함수다.
# 버튼 클릭 담당 함수를 등록해 두었다가 프로그램이 호출하면 콜백 역할도 한다.
# FastAPI에서도 @app.get으로 함수를 등록해 두면 요청이 올 때 프레임워크가 호출한다.
# 호출을 맡긴다는 점은 비슷하며, FastAPI에서는 보통 요청 처리 함수라고 부르면 된다.
# 예: GET /tasks/1 -> 입력 검사 -> 등록한 read_task(task_id=1) 호출.

### 질문 12. Annotated와 raise는 무엇인가?
# 답: Annotated는 자료형과 추가 규칙을 함께 적는 표기이고 raise는 예외를 발생시키는 문법이다.
# task_id: Annotated[int, Path(ge=1)] -> 번호는 정수로 변환하고 1 이상이어야 한다는 정보.
# Annotated 자체가 검사하지는 않는다. FastAPI가 정보를 읽고 함수 호출 전에 검사한다.
# /tasks/0은 조건 위반, /tasks/abc는 정수 변환 실패 -> 422, 함수는 실행되지 않는다.
# if task_id not in tasks: -> 이 번호가 딕셔너리의 키에 없는지 확인한다.
# raise HTTPException(status_code=404, detail="Task not found") -> 예외를 발생시켜 404 응답으로 처리.
# raise는 함수 안의 정상 흐름을 중단하므로 아래 return tasks[task_id]를 실행하지 않는다.
# 서버 전체를 종료하는 것이 아니다. 다음 요청은 계속 받을 수 있다.
# return은 정상 결과 반환, raise는 예외 발생이라는 차이가 있다.

### 질문 13. response_model=list[TaskOut]은 응답을 검사한다는 뜻인가?
# 답: 맞다. 응답이 리스트이고 각 항목이 TaskOut의 구조와 규칙에 맞는지 검사한다.
# TaskOut은 id, title, done이 있는 양식이므로 [{"id": 1, "title": "숙제", "done": False}] 형태다.
# TaskInput은 받은 데이터의 양식, response_model에 지정한 TaskOut은 보낼 데이터의 양식이다.
# FastAPI는 응답을 모델에 맞게 검증·변환하고 /docs 문서에도 반영한다.
# 서버가 id가 빠진 항목을 반환하면 응답 검증 실패다. 기본적으로 서버 문제인 500 오류다.
# 클라이언트가 잘못된 입력을 보내 발생하는 422와 구분한다. 모델이 DB를 만드는 것도 아니다.

### 질문 14. if False: 아래에 코드를 적은 이유는?
# 답: 조건이 참일 때만 안쪽을 실행하는 if 문에 항상 거짓인 False를 넣어 실행하지 않게 했다.
# if False:
#     print("실행하지 않아요")
# print("여기는 if 바깥이므로 실행해요")
# 들여쓴 부분만 if의 범위다. 실행하지 않더라도 파이썬 문법은 올바르게 작성해야 한다.
# 실습 파일 위쪽에는 내가 쓴 원본, 아래쪽에는 같은 코드와 자세한 설명을 두기 위해 사용했다.
# 아래까지 실행하면 app을 다시 만들거나 API를 중복 등록할 수 있어 설명용 영역만 제외한 것이다.
# FastAPI 앱에 필수인 문법은 아니다. 원본 코드만 있는 파일에는 이 장치가 필요 없다.

### 질문 15. 수정된 파일 내용이 VS Code에 안 보인 이유는?
# 답: 편집 중인 미저장 내용과 디스크의 파일 내용이 다를 수 있다. 탭의 흰 점은 미저장 표시다.
# VS Code의 File: Compare Active File with Saved로 현재 편집본과 저장본의 차이를 비교할 수 있다.
# File: Revert File은 미저장 편집 내용을 버리고 저장본을 다시 읽는다. 필요한 수정은 먼저 보관한다.
# 내용이 다를 때 무조건 저장하거나 되돌리기보다 먼저 비교해서 직접 작성한 내용을 보호한다.
# 추가한 부분은 이 파일에서 '추가 시작: 지금까지 질문한 내용과 답변 모음'을 검색해 찾는다.
# ==================== 추가 끝: 지금까지 질문한 내용과 답변 모음 ====================
