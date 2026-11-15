# Day5 복습: FastAPI로 요청을 받고 데이터를 다루기

> 학습 순서: 실행 환경 → 요청·응답 → 주소와 메서드 → 입력 검사 → 조회·검색 → 생성·수정·삭제 → 계산기 화면 연결.
>
> `day5_FastAPI.py`의 질문 메모, `labs/lesson01.py`~`lesson07.py`의 코드·주석, `calculator/`의 Python·HTML·CSS·JavaScript·테스트를 바탕으로 정리했다. 반복 주석은 핵심 기능·문법·해석으로 압축했다. 마지막에는 이 대화에서 질문한 Git 개념을 모았다.

## 1. 먼저 전체 흐름 이해하기

웹 API는 다른 프로그램이 기능을 요청할 수 있는 창구다. 음식점으로 생각하면 주소와 요청 형식은 주문 규칙, 함수는 조리 과정이다.

```text
브라우저 또는 JavaScript가 요청
→ Uvicorn이 요청을 받음
→ FastAPI가 메서드·경로를 보고 담당 함수를 찾음
→ 입력값 검사
→ 함수 실행
→ JSON 또는 HTML 응답
→ 브라우저가 표시
```

| 이름 | 역할 | 기억할 비유 |
| --- | --- | --- |
| FastAPI | 경로 연결, 입력 검사, 응답, API 문서 작성을 돕는 프레임워크 | 주방 운영의 기본 틀 |
| `app` | 이번 프로그램의 처리 규칙을 담은 FastAPI 객체 | 실제로 운영하는 주방 |
| Uvicorn | 네트워크 요청을 받아 앱에 전달하는 서버 프로그램 | 주문과 음식을 전달하는 직원 |
| Pydantic | 입력·응답 데이터의 형식과 규칙 검사 | 신청서 검사 담당자 |

**`app = FastAPI()`만 작성하면 서버가 켜지는 것은 아니다. Uvicorn으로 실행해야 한다.** Django도 웹 프레임워크이며, Apache도 웹 서버지만 이번 실습에는 별도로 필요하지 않다. API라는 말 자체는 더 넓어서 라이브러리의 함수 사용법도 API에 해당한다.

## 2. 실행 환경: 어디서 실행하고 어떤 Python을 쓰는가?

### 2-1. 작업 폴더와 가상환경은 다른 개념

- **작업 폴더**: `requirements.txt`, `labs/lesson01.py` 같은 내 파일을 찾는 기준.
- **가상환경**: 실행할 Python과 설치 패키지를 분리해서 관리하는 환경.
- `py313`은 Conda 환경 이름, `.venv`는 venv 환경의 폴더 이름이다. 서로 설치 패키지가 자동 공유되지 않는다.
- 폴더를 `cd`로 이동해도 활성화한 환경은 유지된다. 프로그램과 문서가 다른 폴더에 있어도 문서를 열 수 있는 것과 비슷하다.

이미 프로젝트 최상위에 `.venv`가 있다는 전제로 실행한다.

```bash
cd /Users/imijeong/Downloads/AIO_4_class
source .venv/bin/activate
cd day5
python -m pip install -r requirements.txt
python -m uvicorn labs.lesson01:app --reload
```

| 문법 | 해석 |
| --- | --- |
| `cd` | change directory, 작업 폴더 이동 |
| `source .venv/bin/activate` | 활성화 스크립트를 현재 터미널에 적용 |
| `python -m pip` | 현재 Python으로 pip 모듈 실행 |
| `-r requirements.txt` | `--requirement`, 파일에 적힌 설치 목록 읽기 |
| `labs.lesson01:app` | `labs/lesson01.py`의 `app` 객체 사용 |
| `--reload` | 코드 저장 시 개발 서버 자동 재시작. 브라우저 새로고침은 별도 |
| `Ctrl + C` | 실행 중인 서버 종료 |

현재 위치가 `day5`라면 활성화 경로는 `source ../.venv/bin/activate`다. `..`는 한 단계 위를 뜻한다. 최상위에서 실습을 실행하려면 모듈 경로도 `day5.labs.lesson01:app`으로 바뀐다.

환경이 없을 때만 만드는 예시:

```bash
conda create -n py313 python=3.13
conda activate py313
# 프로젝트 최상위에서, .venv가 없을 때만 실행
python -m venv .venv
```

`-n`은 `--name`, `-m`은 Python의 모듈 실행 옵션이다. `venv`는 생성 도구이고 `.venv`는 생성할 폴더 이름이다. `py313`이라는 이름 자체가 버전을 정하지는 않는다. Conda 환경을 그대로 사용해도 되며, 두 환경을 반드시 함께 만들 필요는 없다.

### 2-2. 질문했던 환경 문제 빠르게 확인하기

```bash
pwd                                 # 현재 작업 폴더
ls -a                               # 숨김 파일·폴더까지 확인
python --version                    # 실제 Python 버전
python -c "import sys; print(sys.executable)"  # 실제 실행 중인 Python 경로
python -m pip --version              # 사용하는 pip의 위치
```

- `.venv`에서 나오기: `deactivate`. Conda에서 나오기: `conda deactivate`. 환경을 삭제하는 명령이 아니다.
- `(.venv) (base)`가 함께 보여도 패키지가 두 곳에 동시에 설치된다는 의미는 아니다. 실제 Python 경로로 확인한다.
- Mac zsh에서는 `source .../bin/activate`를 쓴다. Windows cmd용 `Scripts\activate.bat`와 다르다.
- VS Code에 파일을 열었다고 터미널도 그 폴더로 이동하지는 않는다. 설치 목록을 못 찾으면 `pwd`와 경로부터 확인한다.
- VS Code 실행 버튼의 환경은 **Python: Select Interpreter**에서도 확인한다.

## 3. Lesson 01: 주소와 함수를 연결하고 응답하기

원본: [labs/lesson01.py](labs/lesson01.py)

```python
from fastapi import FastAPI

app = FastAPI(title="Lesson 01")

@app.get("/sports")
def sports():
    return {"sports": ["축구", "야구", "농구", "배구", "테니스"]}
```

| 핵심 문법 | 해석 |
| --- | --- |
| `FastAPI(title="Lesson 01")` | 앱 생성. `title`은 `/docs`의 문서 제목 |
| `@app.get("/sports")` | GET `/sports`를 바로 아래 함수에 연결하는 데코레이터 |
| `def sports():` | 요청을 처리할 함수 정의 |
| `return {...}` | 결과를 반환하면 FastAPI가 JSON 응답으로 변환 |

`print()`는 터미널에 출력하고, `return`은 함수 결과를 돌려준다. 여기서는 그 반환값이 HTTP 응답에 사용된다.

**예제에서 한 일:** `/`는 HTML 제목, `/sports`는 스포츠 목록, `/menu`는 음식 목록을 응답한다. HTML은 `response_class=HTMLResponse`를 지정하고 HTML 문자열을 반환한다.

### 주소·엔드포인트·라우팅 구분

```text
http://127.0.0.1:8000/sports
│      │         │    └─ 경로
│      │         └────── 포트: 요청받을 출입구 번호
│      └──────────────── IP: 요청하는 컴퓨터 자신
└─────────────────────── 통신 방식
```

- **엔드포인트**: 기능에 접근하는 접점. `GET /sports`처럼 메서드와 경로를 함께 쓰면 정확하다.
- **라우팅**: 메서드와 경로에 맞는 함수를 찾아 연결하는 과정.
- **라우터**: 연결 규칙을 관리하는 도구. `APIRouter`로 기능별 API를 묶고 `app.include_router(router)`로 앱에 포함할 수도 있다. 현재 labs에서는 직접 `app`에 등록한다.
- 함수 이름을 바꿔도 데코레이터 경로가 같으면 주소는 같다.
- 친구 컴퓨터의 `127.0.0.1`은 친구 컴퓨터다. 내 서버를 뜻하지 않는다.
- 도메인은 사람이 기억하기 쉬운 이름, DNS는 도메인에 해당하는 IP 등을 찾아주는 시스템이다. `localhost`는 보통 자기 컴퓨터를 가리킨다.

Python의 `{"done": False}`는 딕셔너리이고, HTTP로 보내는 `{"done": false}`는 JSON 표현이다. 직접 `str()`로 바꾸는 것과 다르다.

## 4. Lesson 02: 같은 주소라도 메서드가 다르면 다른 기능

원본: [labs/lesson02.py](labs/lesson02.py)

```python
@app.get("/method")
def read_method():
    return {"method": "GET", "purpose": "read"}

@app.post("/method", status_code=201)
def create_method():
    return {"method": "POST", "purpose": "create"}
```

**예제에서 한 일:** GET `/method`와 POST `/method`를 서로 다른 함수에 연결하고, 기본 200과 명시한 201을 비교했다.

| 메서드 | 일반적인 의도 | 쉬운 예 |
| --- | --- | --- |
| GET | 조회 | 숙제 목록 보기 |
| POST | 생성·제출 | 새 숙제 등록 |
| PUT | 전체 교체 | 숙제 정보를 새 내용으로 교체 |
| PATCH | 일부 수정 | 완료 여부만 변경 |
| DELETE | 삭제 | 숙제 카드 제거 |

**메서드나 상태 코드만 쓰면 저장·수정이 자동으로 되는 것은 아니다. 함수 안에 실제 처리 코드를 작성해야 한다.** Lesson 02의 POST는 고정 안내만 반환하며 실제 항목을 생성하지 않는다.

| 상태 코드 | 의미 | 이번 실습 예 |
| --- | --- | --- |
| 200 OK | 정상 처리 | 조회·수정 |
| 201 Created | 생성 성공 | 새 할 일 생성 |
| 204 No Content | 성공, 응답 본문 없음 | 삭제 성공 |
| 404 Not Found | 경로 또는 데이터 없음 | 없는 할 일 번호 |
| 405 Method Not Allowed | 경로는 있지만 해당 메서드를 지원하지 않음 | GET만 있는 `/menu`에 POST |
| 422 | 요청 입력 검증 실패 | 숫자 자리에 `abc` |
| 500 | 서버 내부 문제 | 서버가 응답 모델과 맞지 않는 결과를 반환 |

브라우저 주소창은 보통 GET을 보낸다. POST·PUT·PATCH·DELETE는 `/docs`의 **Try it out → Execute**로 실습한다. `/`에 404가 나도 서버 고장은 아닐 수 있다. 실행한 앱에 `/`가 등록되어 있는지 확인한다.

## 5. Lesson 03: 경로에서 번호를 받고 검사하기

원본: [labs/lesson03.py](labs/lesson03.py)

```python
@app.get("/tasks/{task_id}")
def read_task(task_id: Annotated[int, Path(ge=1)]):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]
```

| 핵심 문법 | 해석 |
| --- | --- |
| `{task_id}` | 주소의 이 부분을 같은 이름의 함수 인자로 받음 |
| `Annotated[int, Path(ge=1)]` | 정수 타입과 경로 입력 규칙을 함께 표기 |
| `ge` | greater than or equal, 이상 |
| `task_id not in tasks` | 딕셔너리에 해당 키가 없는지 확인 |
| `raise HTTPException(...)` | 정상 흐름을 중단하고 HTTP 오류 응답 발생 |
| `tasks[task_id]` | 해당 키에 저장된 값 조회 |

`Annotated` 자체가 검사하는 것은 아니다. FastAPI가 타입과 규칙을 읽어 함수 실행 전에 검사한다. `raise`는 서버 전체를 종료하는 명령이 아니다.

**예제에서 한 일:** 1번 할 일을 조회하고 `/tasks/stats`에서 `len(tasks)`로 전체 개수를 구했다.

| 요청 | 결과 | 이유 |
| --- | --- | --- |
| `/tasks/1` | 200 | 1번 항목이 있음 |
| `/tasks/2` | 404 | 정수·범위는 맞지만 데이터가 없음 |
| `/tasks/0` | 422 | 1 이상 조건 위반 |
| `/tasks/abc` | 422 | 정수 변환 실패 |
| `/tasks/stats` | `{"total": 1}` | 등록된 항목 수 조회 |

**고정 경로 `/tasks/stats`를 가변 경로 `/tasks/{task_id}`보다 먼저 등록한다.** 반대라면 `stats`가 번호 입력으로 잡혀 422가 발생할 수 있다.

## 6. Lesson 04: 쿼리로 검색하고 목록을 나누기

원본: [labs/lesson04.py](labs/lesson04.py)

경로 변수는 **어떤 대상인지**, 쿼리는 **어떤 조건으로 볼지**라고 생각하면 쉽다.

```text
/tasks/1                           → 1번 할 일
/tasks?q=python&done=false          → python이 들어간 미완료 할 일
/tasks?skip=1&limit=1               → 한 개를 건너뛰고 최대 한 개
```

| 입력 | 문법 | 해석 |
| --- | --- | --- |
| 검색어 | `q: str \| None = None` | 문자열 또는 None. 생략하면 검색하지 않음 |
| 완료 여부 | `done: bool \| None = None` | true/false로 필터. 생략하면 전체 |
| 건너뛸 수 | `skip: Annotated[int, Query(ge=0)] = 0` | 0 이상, 기본 0 |
| 최대 개수 | `limit: Annotated[int, Query(ge=1, le=20)] = 10` | 1~20, 기본 10. `le`는 less than or equal, 이하 |

```python
if q is not None:
    rows = [t for t in rows if q.casefold() in t["title"].casefold()]
if done is not None:
    rows = [t for t in rows if t["done"] == done]
total = len(rows)
return {"items": rows[skip:skip + limit], "total": total}
```

- `casefold()`: 대소문자 차이를 줄여 비교. `PYTHON`으로도 `Python review`를 찾는다.
- `[t for t in rows if 조건]`: 조건을 만족하는 항목만 모아 새 리스트 생성.
- **`if done:` 대신 `if done is not None:`**: `False`도 사용자가 보낸 유효한 값이기 때문이다.
- `rows[시작:끝]`: 시작 포함, 끝 제외. `skip=1, limit=1`이면 `[1:2]`다.
- **필터 → total 계산 → 슬라이싱** 순서다. total은 현재 페이지의 개수가 아니다.

**예제에서 한 일:** 세 할 일을 제목·완료 여부로 필터링하고, skip/limit로 나눠 반환했다. `/tasks?done=false&skip=1&limit=1`이면 미완료 1·3번 중 3번만 나오며 `total`은 2다. 원본 tasks 목록을 지우는 작업은 아니다.

## 7. Lesson 05: 요청 양식을 검사하고 새 할 일 만들기

원본: [labs/lesson05.py](labs/lesson05.py)

### 7-1. 입력 모델과 응답 모델

```python
class TaskInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=80)
    done: bool = Field(default=False, strict=True)

class TaskOut(TaskInput):
    id: int
```

모델은 제목·완료 칸이 있는 신청서에 비유할 수 있다. **BaseModel을 상속하므로 단순 변수 묶음이 아니라 검증 기능도 가진다. DB 테이블을 만드는 코드는 아니다.**

| 문법 | 해석 |
| --- | --- |
| `str_strip_whitespace=True` | 문자열 양끝 공백 제거. 중간 공백은 유지 |
| `extra="forbid"` | 정의하지 않은 필드 거절 |
| `Field(min_length=1, max_length=80)` | 제목은 필수, 1~80자 |
| `Field(default=False, strict=True)` | done 생략 시 False. 입력했다면 실제 bool만 허용 |
| `class TaskOut(TaskInput)` | title·done을 상속하고 id 추가 |
| `response_model=TaskOut` | 한 항목의 응답 검증·변환·문서화 |
| `response_model=list[TaskOut]` | 항목 여러 개가 담긴 리스트 응답 |

요청 예: `{"title": "  수학 숙제  "}` → title은 `수학 숙제`, done은 기본 `false`가 된다. 빈 제목, 공백만 있는 제목, `"done": "false"`, 정의하지 않은 `price`는 이 모델에서 422다. JSON 불리언은 따옴표 없는 `false`다.

### 7-2. 생성 과정과 핵심 Python 문법

```python
@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskInput):
    global next_id
    task = {"id": next_id, **payload.model_dump()}
    tasks[next_id] = task
    next_id += 1
    return task
```

1. `payload: TaskInput`: JSON 본문을 검사한 모델 객체를 받는다. payload는 변수 이름이다.
2. `model_dump()`: 모델을 Python 딕셔너리로 바꾼다. JSON 문자열 변환은 아니다.
3. `**딕셔너리`: 항목을 펼쳐 id와 합친다.
4. `tasks[next_id] = task`: 메모리에 실제 저장한다.
5. `next_id += 1`: 다음 번호 준비. `global`은 바깥 번호 변수를 함수에서 다시 대입하기 위한 선언이다.
6. `return task`: 생성 결과를 반환하고 설정한 201로 응답한다.

추가 문법: `[*[1, 2], *[3, 4]]`는 `[1, 2, 3, 4]`다. 리스트 펼치기는 `*`, 딕셔너리 펼치기는 `**`를 썼다. `list(tasks.values())`는 번호 키를 빼고 값들만 목록으로 만든다.

**예제에서 한 일:** 전체 조회 `list_tasks()`, 한 개 조회 `read_task()`, 공통 존재 확인 `require_task()`, 새 항목 생성 `create_task()`를 구현했다. 처음 POST하면 id 2가 생성되며 GET으로 확인할 수 있다. 두 항목을 만들려면 JSON 하나씩 두 번 요청한다.

## 8. Lesson 06: PUT은 교체, PATCH는 보낸 칸만 수정

원본: [labs/lesson06.py](labs/lesson06.py)

기존 값이 `{"title": "수학 숙제", "done": true}`라고 가정한다.

| 요청 | 본문 | 이 예제의 결과 |
| --- | --- | --- |
| PUT `/tasks/1` | `{"title": "영어 숙제"}` | 제목 교체, done은 기본 false로 바뀜 |
| PATCH `/tasks/1` | `{"title": "영어 숙제"}` | 제목만 변경, done은 true 유지 |
| PATCH `/tasks/1` | `{"done": false}` | 제목 유지, done은 false로 변경 |

```python
# PUT: 입력 모델 결과로 새 딕셔너리를 만들어 교체
tasks[task_id] = {"id": task_id, **payload.model_dump()}

# PATCH: 기존 딕셔너리에 직접 보낸 필드만 반영
task = require_task(task_id)
task.update(payload.model_dump(exclude_unset=True))
```

**`exclude_unset=True`는 False를 제외하는 옵션이 아니다. 보내지 않은 필드만 제외한다.** `update()`는 원본 딕셔너리를 직접 바꾸고 반환값은 None이다. `task = task.update(...)`라고 쓰면 안 된다. 이 코드의 `task`는 저장된 딕셔너리의 복사본이 아니라 같은 객체를 가리킨다.

### PATCH는 생략·null·빈 요청을 구분한다

`TaskPatch`는 title·done에 `None` 기본값을 두어 생략을 허용하고, 추가 검사로 직접 보낸 null과 빈 요청을 막는다.

| 문법 | 역할 |
| --- | --- |
| `@field_validator("title", "done", mode="before")` | 필드 타입 검사 전에 `reject_null()` 실행 |
| `@classmethod` / `cls` | 객체 대신 클래스를 첫 인자로 받는 메서드 |
| `raise ValueError(...)` | 이 모델 검증 중 잘못된 값으로 처리. API 입력 오류 422로 이어짐 |
| `@model_validator(mode="after")` | 필드 검사 후 모델 전체를 `require_field()`로 검사 |
| `self.model_fields_set` | 사용자가 직접 보낸 필드 이름의 집합 |
| `return self` | 전체 검사를 통과한 모델 객체 반환 |

- `{"done": true}`: title을 생략했으므로 제목 유지.
- `{"done": false}`: False도 직접 보낸 값이므로 반영.
- `{"title": null}`: 명시적 null이므로 422.
- `{}`: 바꿀 필드가 하나도 없으므로 422.
- 없는 번호에 유효한 수정 요청: 공통 존재 검사에서 404.

**예제에서 한 일:** Lesson 05의 조회·생성에 `replace_task()`와 `update_task()`를 추가했다. 메서드 이름만으로 동작이 생기는 것이 아니라 교체·update 코드가 차이를 만든다.

## 9. Lesson 07: 삭제하고 본문 없이 성공 알리기

원본: [labs/lesson07.py](labs/lesson07.py)

```python
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: Annotated[int, Path(ge=1)]):
    require_task(task_id)
    del tasks[task_id]
    return Response(status_code=204)
```

번호 검사 → 항목 존재 확인 → `del`로 삭제 → 본문 없는 204 응답 순서다. 삭제한 번호를 다시 GET하면 404가 된다.

**예제에서 한 일:** 조회·생성·전체 교체·일부 수정에 삭제까지 더해 CRUD를 완성했다. CRUD는 Create(생성), Read(조회), Update(수정), Delete(삭제)의 약자다.

**공통 주의:** 각 Lesson은 별도의 앱이다. Lesson 05에서 추가한 항목이 Lesson 06으로 이어지지 않는다. tasks는 DB가 아니라 메모리이므로 서버를 재시작하면 추가·수정·삭제가 초기화된다. 간단한 `next_id` 역시 DB의 자동 번호 기능이 아니다.

## 10. 계산기: 프론트엔드와 백엔드를 연결한 종합 예제

### 10-1. 파일마다 한 일

| 파일 | 구현한 내용 |
| --- | --- |
| [calculator/main.py](calculator/main.py) | 입력 검사, Decimal 사칙연산, HTML·정적 파일 제공 |
| [calculator/static/index.html](calculator/static/index.html) | 숫자 입력 폼, 계산·초기화 버튼, 결과 카드 |
| [calculator/static/style.css](calculator/static/style.css) | 색상·배치·카드 디자인과 작은 화면 대응 |
| [calculator/static/app.js](calculator/static/app.js) | 이벤트 처리, API 요청, 결과·오류 표시 |
| [calculator/test_main.py](calculator/test_main.py) | 정상 계산·오류·페이지 제공의 자동 검증 |
| [calculator/readme.md](calculator/readme.md) | 실행 방법, 계산 규칙, API 사용 예 |
| `requirements.txt` | 패키지 설치 목록. `==`는 버전 지정 |

HTML은 화면 뼈대, CSS는 모양, JavaScript는 화면 동작, Python은 실제 계산을 맡는다. 파일을 직접 여는 대신 서버의 `/`로 접속해야 한다.

### 10-2. 클릭부터 결과 표시까지

```text
12와 4 입력 → submit 이벤트
→ JavaScript 입력 검사
→ POST /api/calculate, 본문 {"a": "12", "b": "4"}
→ Pydantic이 Decimal로 변환·검사
→ Python에서 계산
→ JSON 응답
→ JavaScript가 결과 카드에 16, 8, 48, 3 표시
```

```javascript
const response = await fetch('/api/calculate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({a, b})
});
const result = await response.json();
```

| 문법 | 해석 |
| --- | --- |
| `querySelector('#calculator')` | id가 calculator인 화면 요소 선택 |
| `addEventListener('submit', 함수)` | 폼 제출 시 실행할 이벤트 처리 함수 등록 |
| `event.preventDefault()` | 기본 폼 제출로 페이지가 이동하는 동작 방지 |
| `async` / `await` | 비동기 작업을 다루고 요청·본문 처리 결과를 기다림 |
| `fetch()` | HTTP 요청 전송. Git의 fetch와는 다른 기능 |
| `JSON.stringify({a, b})` | JavaScript 객체를 JSON 문자열로 변환 |
| `response.ok` | HTTP 상태가 성공 범위인지 확인. 422가 자동으로 catch에 잡히는 것은 아님 |
| `response.json()` | 응답의 JSON 본문을 JavaScript 값으로 읽음 |
| `textContent` | 화면 요소의 글자 내용을 변경 |
| `try` / `catch` / `finally` | 정상 처리·오류 처리·마무리 처리 |

콜백은 다른 코드에 맡겨 두었다가 호출되는 함수다. 이벤트 처리 함수는 클릭·입력 같은 일이 생겼을 때 실행하는 함수다. `함수이름`은 함수 자체를 전달하고, `함수이름()`은 지금 실행한다. FastAPI의 요청 처리 함수도 등록해 두면 프레임워크가 요청 시 호출한다.

이 계산기는 input/reset 때 결과를 비운다. `requestVersion`을 비교해 이전 입력의 늦은 응답이 새 화면을 덮지 않게 하고, 요청 중 버튼을 비활성화한다. 화면 검사와 별도로 서버도 반드시 입력을 검사한다.

### 10-3. Python 계산 코드의 핵심

| 문법 | 해석 |
| --- | --- |
| `Path(__file__).resolve().parent` | 현재 Python 파일의 폴더를 기준 경로로 구함 |
| `app.mount("/static", StaticFiles(...))` | CSS·JS 같은 정적 파일 제공 |
| `FileResponse(... / "index.html")` | HTML 파일을 응답 |
| `include_in_schema=False` | 이 경로를 자동 API 문서에서 숨김. 접속 차단은 아님 |
| `a: Decimal = Field(...)` | 입력을 십진수로 검사·변환 |
| `with localcontext() as context:` | 이번 계산에 쓸 Decimal 설정 범위를 만듦 |
| `context.prec = 80` | 연산 정밀도를 유효 숫자 80자리로 설정 |
| `quantize(..., rounding=ROUND_HALF_UP)` | 나눗셈을 소수점 아래 10자리까지 반올림 |
| `display(number)` | 뒤의 불필요한 소수 0을 제거하고 음수 0도 `0`으로 표시 |

숫자를 문자열 `"0.1"`로 보내고 `Decimal`로 계산해 일반적인 float의 표현 오차를 피한다. 응답 숫자도 문자열이다. 입력은 유효 숫자 최대 30자리, 소수점 아래 최대 10자리이며 이 Field 제약에서 정수 부분은 최대 20자리다. NaN·무한대·잘못된 입력은 거절한다.

| 입력 | 동작 |
| --- | --- |
| `"0.1"`, `"0.2"` | 더하기 `"0.3"` |
| `"1"`, `"3"` | 나누기 `"0.3333333333"` |
| `"7"`, `"0"` | 다른 세 연산은 계산, division은 null, 나누기 오류 문구 표시. 전체 응답은 200 |
| `"abc"`, `"2"` | 입력 자체가 잘못되어 422 |

0으로 나누기는 서버를 중단시키지 않고 해당 결과만 안내하도록 설계했다. DB나 입력·결과 저장 기능은 없다.

### 10-4. 테스트 파일은 무엇을 확인했나?

- `TestClient(app)`: 별도 Uvicorn 서버를 띄우지 않고 API 요청을 흉내 낸다.
- `client.post(..., json=...)`: JSON 요청을 보내고 `response.status_code`, `response.json()`으로 확인한다.
- `assert`: 예상 결과가 맞는지 검사한다.
- `@pytest.mark.parametrize`: 같은 테스트를 여러 입력 조합으로 반복한다.
- 현재 코드에는 정상 연산 6건, 잘못된 입력 9건, 0 나눗셈·큰 수 곱셈·페이지 제공 각 1건으로 총 18개 테스트 사례가 정의되어 있다. 이는 코드 구성 설명이며 이번 문서 작성 중 실행 결과는 아니다.

## 11. 실행하며 복습하기: 무엇을 확인할까?

먼저 `day5` 폴더에서 가상환경을 활성화하고 필요한 패키지를 설치한다. **한 서버를 종료한 뒤 다음 서버를 실행**한다.

| 실행 명령 | 확인할 내용 |
| --- | --- |
| `python -m uvicorn labs.lesson01:app --reload` | `/`, `/sports`, `/menu`: HTML과 JSON |
| `python -m uvicorn labs.lesson02:app --reload` | `/docs`: GET 200과 POST 201 |
| `python -m uvicorn labs.lesson03:app --reload` | `/tasks/1`, `/tasks/2`, `/tasks/0`: 200·404·422 |
| `python -m uvicorn labs.lesson04:app --reload` | `/tasks?done=false&skip=1&limit=1`: 필터·페이지·total |
| `python -m uvicorn labs.lesson05:app --reload` | POST로 생성 후 GET으로 확인 |
| `python -m uvicorn labs.lesson06:app --reload` | PATCH로 done=true → PUT에서 title만 보내 done=false 확인 |
| `python -m uvicorn labs.lesson07:app --reload` | DELETE 204 → 같은 번호 GET 404 |

계산기는 별도 폴더로 이동해서 실행한다.

```bash
# 현재 위치: day5
cd calculator
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

접속 주소는 `http://127.0.0.1:8000`, API 문서는 `/docs`다. 테스트는 계산기 폴더에서 `python -m pytest -q`로 실행하며 pytest·httpx 설치가 필요하다.

### 자주 헷갈렸던 부분

- `Could not import module`: 실행 위치와 `labs.lesson01:app` 같은 모듈 경로 확인.
- `Address already in use`: 기존 서버 종료 또는 `--port 8001` 사용. 접속 포트도 변경.
- 앱 혼동: `/docs`의 Lesson 제목 확인. 다른 파일의 app은 별개다.
- `if False:` 안의 코드는 설명용 중복 예제를 실행하지 않기 위한 장치다. 필수 FastAPI 문법은 아니다.
- 응답 모델 오류는 서버 쪽 문제이며, 잘못된 요청 입력의 422와 구분한다.
- VS Code 미저장 내용과 디스크 내용이 다르면 먼저 **File: Compare Active File with Saved**로 비교한다. **Revert File**은 미저장 변경을 버릴 수 있다.

## 12. 대화에서 질문한 Git 개념 함께 복습

FastAPI 코드와 별도로 질문했던 내용이다. 아래 경로 예시는 프로젝트 최상위 `AIO_4_class` 기준이다.

### 12-1. 파일 선택과 업로드는 다른 단계

```text
작업 파일 수정 → add(선택) → commit(로컬 기록) → push(GitHub 전송)
```

| 명령 | 뜻 |
| --- | --- |
| `git status` | 현재 브랜치와 변경·스테이징 상태 확인 |
| `git add -A` | `--all`: 저장소 전체의 추가·수정·삭제 스테이징 |
| `git add .` | 현재 폴더와 그 아래 변경 스테이징. 최상위라면 위와 같은 범위 |
| `git add -A -- day5/` | day5 아래 변경만 선택 |
| `git commit -m "day5 학습 정리"` | `--message`: 선택된 변경을 메시지와 함께 로컬 기록 |
| `git push origin main` | 로컬 main의 커밋들을 원격 origin의 main으로 전송 |

스테이징은 다음 커밋에 넣을 변경을 골라 두는 단계다. push 자체에서 파일을 선택하는 것이 아니다. 다른 미전송 커밋이 있으면 함께 올라갈 수 있다. `.gitignore`는 미추적 파일 제외 규칙이며 이미 추적 중인 파일을 자동으로 추적 해제하지 않는다. `*.pdf`를 주석 처리하면 다른 제외 규칙에 걸리지 않는 새 PDF도 추가할 수 있다.

이름 변경 예:

```bash
git add -A -- day4/day4.py day4/day4_git.py
```

기존 파일 삭제와 새 파일 추가를 함께 선택한다. 두 경로 순서는 상관없고, `--`는 뒤가 옵션이 아닌 경로라는 표시다. 내용을 비교해 Git이 이름 변경으로 인식할 수 있다.

### 12-2. 브랜치와 origin, upstream

```bash
git switch -c study/day5
git add -A -- day5/
git commit -m "day5 복습 정리"
git push -u origin study/day5
```

- `switch -c`: 현재 커밋에서 브랜치 생성 후 이동. 브랜치 이름은 작업할 폴더를 제한하지 않는다.
- `origin`: 연결한 원격 저장소 주소의 별명. 저장소마다 다른 주소일 수 있다.
- `-u`: `--set-upstream`. 로컬 브랜치의 기본 연결 대상을 `origin/study/day5`로 설정한다.
- 설정 후 해당 브랜치에서는 보통 `git push`, `git pull`만 사용한다. 실제 대상은 연결·Git 설정에 따른다.
- GitHub에서 base=`main`, compare=`study/day5`인 Pull Request를 만들어 검토·병합한다. 이후 로컬 main도 pull해 갱신한다.
- 원격에만 있는 브랜치도 정상이다. 로컬에서 쓰려면 fetch 후 `git switch --track origin/브랜치이름`으로 만들 수 있다.
- Active branches는 최근 활동에 따른 분류이며 별도 복사본이 아니다.

### 12-3. clone·fetch·pull의 차이와 선생님 자료 받기

| 명령 | 역할 |
| --- | --- |
| `clone` | 저장소를 처음 복제. 대상 폴더도 자동 생성 |
| `fetch` | 원격 변경을 받되 현재 작업 파일과 브랜치에는 합치지 않음 |
| `pull` | 원격 변경을 받아 현재 브랜치에 통합 |
| `--ff-only` | fast-forward 방식으로 이동할 수 있을 때만 통합. 폴더 선택 옵션이 아님 |

**push와 pull은 커밋을 주고받는다. add로 받을 파일을 골라 pull하는 기능은 없다.** 로컬 파일을 유지한 채 무조건 새 파일만 추가하는 것도 아니다. pull은 커밋의 수정·삭제도 반영하며 로컬 변경과 겹치면 중단되거나 병합 충돌이 날 수 있다.

선생님 저장소를 별도 `AIO_4_class_teacher` 폴더에 clone하고 필요한 자료만 내 프로젝트로 복사하면 구분하기 쉽다. 그 폴더의 origin은 선생님 저장소이고, 내 프로젝트의 origin은 내 GitHub다. 저장소 안의 `.git`은 Git 기록이므로 일반 학습 파일과 구분한다.

Day8만 작업 파일에 반영하는 예시(선생님 저장소 폴더에서):

```bash
git fetch origin
git restore --source=origin/main --worktree -- Day8
```

`--source`는 원본 버전, `--worktree`는 실제 작업 폴더에 적용한다는 뜻이다. 최신 커밋이 Day1 수정이어도 그 버전에 Day8이 남아 있다면 Day8 내용을 꺼낼 수 있다. 다른 작업 파일은 그대로지만 다운로드 범위 자체를 Day8로 제한하지는 않는다. 로컬 브랜치도 이동하지 않아 파일은 로컬 변경으로 보일 수 있고, 해당 경로의 기존 수정은 덮어쓸 수 있다.

## 13. 꼭 기억할 10가지

1. FastAPI 앱 생성과 Uvicorn 서버 실행은 별도다.
2. API는 **HTTP 메서드 + 경로**로 구분한다. 함수 이름이 주소를 정하지 않는다.
3. Path는 대상 번호, Query는 검색·목록 조건, Body 모델은 제출할 내용을 다룬다.
4. 타입·규칙 검사는 FastAPI/Pydantic이 수행한다. 존재 여부는 내가 확인한다.
5. 422는 입력 규칙 위반, 404는 경로나 데이터 없음, 응답 모델 실패는 서버 문제다.
6. 상태 코드 201만 적는다고 저장되는 것은 아니다.
7. PUT은 이 예제에서 전체 교체, PATCH는 직접 보낸 필드만 수정한다.
8. False·None·생략·null은 서로 구별해야 한다.
9. 메모리 딕셔너리는 DB가 아니다. 재시작하면 값이 초기화된다.
10. 계산기는 화면 → API 요청 → 서버 계산 → JSON → 화면 갱신의 연결을 보여 준다.
