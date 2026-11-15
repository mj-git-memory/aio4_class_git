# Day9 핵심 정리 — CRUD, 테스트, Git·PR 리뷰

`kdt_crud_pr_ai_review`의 1~8차시 `main.py`, `solution.py`, `check.py`, 통합 실습 `lesson_01_04.py`와 수업 문서를 바탕으로 정리했다. 대화에서 질문했던 개념도 함께 담았다.

## 1. 수업 전체 흐름

| 차시 | 핵심 내용 | 시작 코드의 문제 → 해결 원리 |
|---|---|---|
| 01 | GET·POST, ID 생성 | `len(tasks) + 1`은 ID 중복 가능 → 현재 최대 ID 확인 |
| 02 | 개별 조회, 404 | 없는 ID에도 `200`과 `null` → `HTTPException(404)` |
| 03 | PUT·PATCH | PATCH에서 생략한 필드까지 기본값으로 변경 → `exclude_unset=True` |
| 04 | CRUD 통합, 삭제 | ID를 리스트 인덱스로 사용 → ID를 찾아 해당 인덱스로 삭제 |
| 05 | 문자열과 불리언, 기능 브랜치 | `bool("false")`도 `True` → 문자열 값 명시적 비교 |
| 06 | 변경 요약, PR 작성 | 삭제된 파일을 변경 목록에서 누락 → 삭제도 변경으로 포함 |
| 07 | 권한 비교, AI 리뷰 검증 | `"admin" in "not-admin"`도 참 → 정확한 값 비교 |
| 08 | 데이터 통합, 충돌 해결 | 한쪽 목록만 반환 → ID별 통합과 우선순위 결정 |

1~4차시는 FastAPI를 `TestClient`로 검사한다. 5~8차시는 HTTP 요청 없이 파이썬 함수를 직접 호출한다. 각 `solution.py`는 해당 차시의 최소 정답이지, 모든 운영 환경의 요구사항까지 해결한 완성품은 아니다.

## 2. CRUD와 HTTP 상태 코드

CRUD는 생성(Create), 조회(Read), 수정(Update), 삭제(Delete)다.

| 동작 | HTTP 메서드 | 예시 | 이 실습의 정상 응답 |
|---|---|---|---|
| 생성 | POST | `/tasks` | `201 Created` |
| 전체·개별 조회 | GET | `/tasks`, `/tasks/1` | `200 OK` |
| 전체 수정 | PUT | `/tasks/1` | `200 OK` |
| 부분 수정 | PATCH | `/tasks/1` | `200 OK` |
| 삭제 | DELETE | `/tasks/1` | `204 No Content` |

주요 오류 코드:

| 코드 | 의미 | 실습 예시 |
|---|---|---|
| 400 | 요청에 문제가 있음 | 통합 실습에서 경로 ID와 본문 ID 불일치 |
| 404 | 요청한 대상 없음 | 없는 ID 조회·수정·삭제 |
| 409 | 현재 데이터와 충돌 | 통합 실습에서 같은 ID 중복 등록 |
| 422 | 요청 데이터 검증 실패 | 필수 `done` 누락, 빈 제목 전송 |
| 500 | 서버 내부 오류 | 존재하지 않는 리스트 인덱스에 `pop()` |

**주의:** `lesson_01_04.py` 상단 주석에 모든 동작이 `201`로 적혀 있지만, 실제 데코레이터와 위 표를 기준으로 기억한다. `204` 응답에는 본문이 없다.

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    ...
```

데코레이터는 요청 경로와 함수를 연결한다. `/tasks/3`에 GET 요청이 오면 `task_id`에 정수 `3`을 전달한다. 경로 등록만으로 요청 처리가 실행되는 것은 아니다.

## 3. ID 생성 — 개수, 최대값, 마지막 발급 번호는 다르다

```python
tasks = [{"id": 1}, {"id": 3}]
len(tasks) + 1  # 3: 이미 존재하는 ID와 중복
```

1차시 정답은 현재 최대 ID 다음 번호를 사용한다.

```python
max(task["id"] for task in tasks) + 1  # 4
```

하지만 다음 두 가지 한계가 있다.

- 빈 목록이면 위 `max()`는 오류가 난다. `max((t["id"] for t in tasks), default=0) + 1`로 빈 목록을 처리할 수 있다.
- 가장 큰 ID를 삭제하면 그 번호를 다시 사용할 수 있다. 빈 목록 처리만으로 재사용 문제까지 해결되지는 않는다.

### 질문: 1~5를 발급하고 2, 5를 삭제했는데 다음을 6으로 만들려면?

남은 ID `[1, 3, 4]`에서 `max() + 1`을 계산하면 `5`다. **마지막 발급 번호를 목록과 별도로 유지**해야 한다.

아래는 단일 실행 흐름에서 원리를 보여주는 간단한 예제다.

```python
last_id = 5  # 이미 5까지 발급했다고 가정

def next_id() -> int:
    global last_id
    last_id += 1
    return last_id

print(next_id())  # 6
```

삭제할 때 `last_id`를 줄이지 않는다. 6도 이미 발급했다가 삭제했다면 다음은 7이어야 한다.

`itertools.count()`로도 카운터를 만들 수 있다.

```python
from itertools import count

id_counter = count(6)
next(id_counter)  # 6
next(id_counter)  # 7
```

메모리 카운터는 재시작 시 유지되지 않고 여러 서버 프로세스가 공유하지도 않는다. 동시 요청에서 직접 작성한 증가 연산을 안전하다고 가정해서도 안 된다. 운영 서비스에서는 마지막 발급 이력을 영속적으로 보관하는 DB의 ID 발급 방식을 사용하고, 사용하는 DB의 재사용 정책을 확인해야 한다.

## 4. 딕셔너리의 get()과 없는 데이터 처리

```python
tasks = {1: {"id": 1, "title": "Git 준비"}}

tasks.get(1)  # {"id": 1, "title": "Git 준비"}
tasks.get(2)  # None
```

`get()`은 파이썬 딕셔너리가 제공하는 메서드라 직접 정의할 필요가 없다.

- `get_task(1)`: 직접 정의한 함수 호출
- `tasks.get(1)`: 딕셔너리 메서드 호출
- `tasks.get_task(1)`: 딕셔너리에 없는 메서드이므로 오류
- `tasks[2]`: 없는 키에 직접 접근하므로 `KeyError`

FastAPI에서 `None`을 그대로 반환하면 이 실습에서는 `200`과 JSON `null`이 나온다. 데이터가 없다는 의미를 전달하려면 직접 404를 지정한다.

```python
task = tasks.get(task_id)
if task is None:
    raise HTTPException(status_code=404, detail="Task not found")
return task
```

`HTTPException`은 HTTP 오류 응답에 사용할 예외 클래스다. `raise`는 예외를 발생시키고 현재 함수의 정상 실행을 중단한다. FastAPI는 이 예외를 처리해 `404`와 `{"detail": "Task not found"}`를 응답한다. 서버 전체가 종료되는 것은 아니다.

**`return`도 함수를 끝낸다.** 현재 2차시 `main.py`는 첫 줄의 `return tasks.get(task_id)` 때문에 아래의 404 처리까지 도달하지 않는다. 또한 정상 데이터의 `return task` 자체가 404를 만드는 것은 아니다.

## 5. payload, Pydantic, PUT·PATCH

```python
class TaskPut(BaseModel):
    title: str = Field(min_length=1)
    done: bool

def replace_task(payload: TaskPut):
    ...
```

`payload`는 **매개변수 이름**이다. `data` 같은 다른 이름으로 바꿔도 된다. FastAPI는 요청 본문을 Pydantic 모델로 검사한 뒤 함수에 전달한다.

- `payload.title`: 모델의 제목 값
- `payload.model_dump()`: 모델 데이터를 딕셔너리로 변환
- `Field(min_length=1)`: 문자열은 최소 한 글자
- `Field(ge=1)`: 통합 실습의 ID가 1 이상이어야 함
- 일반 함수의 타입 표시는 그 자체로 자동 검증을 수행하지 않는다. 이 요청 검증은 FastAPI와 Pydantic이 수행한다.

### PUT: 수정할 필드를 모두 받기

`TaskPut`의 `title`, `done`은 기본값이 없어 모두 필수다. `{"title": "누락"}`만 보내면 `422`다. 실습에서는 ID를 유지하고 수정 가능한 필드들을 모두 갱신한다.

### PATCH: 요청에 포함된 필드만 수정하기

```python
class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    done: bool = False
```

둘 다 기본값이 있어 생략할 수 있다. 제목만 보내면:

```python
payload = TaskPatch(title="제목만")

payload.model_dump()
# {"title": "제목만", "done": False}

payload.model_dump(exclude_unset=True)
# {"title": "제목만"}
```

따라서 부분 수정은 다음과 같이 작성한다.

```python
item.update(payload.model_dump(exclude_unset=True))
return item
```

**`exclude_unset=True`는 보내지 않은 필드를 제외한다.** 명시적으로 보낸 `False`나 `None`을 무조건 제외하는 옵션은 아니다. 현재 모델은 `"title": null`도 허용하므로, 이를 보내면 제목이 `None`으로 바뀐다. PATCH 데코레이터만 붙인다고 자동으로 부분 수정이 되는 것도 아니다.

`return item`을 빼면 수정은 되어도 함수 반환값은 `None`이라 이 설정에서는 응답 본문이 `null`이 된다.

## 6. 원본 수정과 ID·인덱스 구별

### 질문: task를 바꾸면 왜 tasks도 바뀔까?

```python
tasks = [{"id": 1, "title": "첫째"}]
task = tasks[0]
task["title"] = "변경"

print(tasks)  # [{"id": 1, "title": "변경"}]
```

`task`와 `tasks[0]`은 같은 딕셔너리를 가리킨다. `task`가 별도 복사본이 아니므로 내용 변경이 원본에 반영된다. `return` 때문에 바뀌는 것이 아니다.

단, `task = {"id": 9}`처럼 변수에 새 딕셔너리를 대입하는 것은 원본 리스트의 항목을 바꾸는 것과 다르다.

### ID로 찾아 수정하기

```python
for task in tasks:
    if task["id"] == task_id:
        task["title"] = payload.title
        return task
raise HTTPException(status_code=404, detail="Task not found")
```

ID가 일치하면 그 항목의 제목만 바꾼다. 일치하는 항목이 없으면 변경하지 않고 404를 응답한다.

### ID는 리스트 위치가 아니다

```python
tasks = [{"id": 1}, {"id": 3}]
# 인덱스:     0            1
```

`tasks.pop(1)`은 ID 1이 아니라 **인덱스 1에 있는 ID 3을 삭제**한다.

```python
for index, task in enumerate(tasks):
    if task["id"] == task_id:
        tasks.pop(index)
        return
raise HTTPException(status_code=404, detail="Task not found")
```

`enumerate()`는 `(인덱스, 데이터)`를 함께 제공한다. 일치하는 ID의 위치를 찾아 삭제하고 바로 반환한다.

## 7. TestClient, JSON, 서버 오류

```python
client = TestClient(app, raise_server_exceptions=False)
response = client.get("/tasks/1")
print(response.status_code)
print(response.json())
```

`TestClient`는 서버를 별도 실행하지 않고 앱에 테스트 요청을 보낸다. 실행 중인 Uvicorn 서버의 메모리 데이터를 그대로 조회하는 것이 아니라, 테스트가 불러온 앱을 사용한다.

`.json()`은 **응답 본문의 JSON을 파이썬 값으로 변환하는 메서드**다.

| JSON | 파이썬 |
|---|---|
| 객체 `{...}` | `dict` |
| 배열 `[...]` | `list` |
| `true`, `false` | `True`, `False` |
| `null` | `None` |

FastAPI는 이 실습의 딕셔너리·리스트 반환값을 JSON 응답으로 만든다. 모든 웹 응답이 JSON인 것은 아니다. HTML, 이미지, 빈 본문도 있으므로 JSON이 아닌 응답에 `.json()`을 호출하면 오류가 난다. 특히 204에는 `.json()`을 사용하지 않는다.

### 질문: raise_server_exceptions=False여도 404가 나올까?

**그렇다. 이 옵션이 모든 오류를 500으로 바꾸지는 않는다.**

| API 내부 상황 | 기본값 `True` | `False` |
|---|---|---|
| `raise HTTPException(404, ...)` | 404 응답 | 404 응답 |
| 처리하지 않은 `IndexError` 등 | 테스트 호출에 예외 전달 | 일반적인 이 실습에서는 500 응답 |

현재 4차시 시작 코드에서 등록 후 ID는 `[1, 3, 4]`지만 인덱스는 `[0, 1, 2]`다. `pop(3)`은 범위를 벗어나 500이 된다. 정답처럼 ID를 찾아 처리하면 `/tasks/3` 삭제는 204, 없는 `/tasks/999`는 404다.

## 8. assert — 출력이 아니라 검증

```python
assert response.status_code == 404
```

**“404를 반환하라”가 아니라 “실제 응답이 404인지 확인하라”**는 뜻이다.

- 조건이 참이면 아무것도 출력하지 않고 다음 줄로 간다.
- 거짓이면 `AssertionError`를 발생시킨다.
- 이 실습처럼 예외를 잡지 않으면 뒤의 테스트와 `print("PASS")`는 실행되지 않는다.

```python
assert found.status_code == 200 and found.json()["id"] == 1
assert missing.status_code == 404
assert missing.json()["detail"] == "Task not found"
```

각각 성공 코드·데이터 ID, 없는 대상의 상태 코드, 오류 설명을 확인한다. `and`는 두 조건 모두 참이어야 한다. 오류 설명은 문자열이 정확히 같아야 한다.

```python
assert removed.status_code == 204, "ID를 인덱스로 사용했을 수 있습니다"
```

쉼표 뒤 문자열은 실패 시 표시할 설명이다. 응답을 확인하고 싶다면 검사 앞에 출력한다.

```python
print("DELETE:", removed.status_code)
assert removed.status_code == 204
```

중복 검사는 다음과 같다.

```python
ids = [1, 3, 3]
len(ids) == len(set(ids))  # 3 == 2 → False
```

`set()`이 중복을 제거하므로 길이가 달라지면 중복 ID가 있다는 뜻이다. `assert`는 함수가 아닌 문법이며, `python -O`에서는 생략될 수 있으므로 실제 API 입력 검증이나 권한 검사를 대신하는 용도로 쓰지 않는다.

## 9. sys.argv, importlib, 함수 자체와 호출

### 질문: sys.argv에는 무엇이 들어 있을까?

```bash
python check.py solution
```

```python
sys.argv     # ["check.py", "solution"]
sys.argv[0]  # 실행한 파일 이름
sys.argv[1]  # "solution"
len(sys.argv)  # 2
```

`python`은 이 리스트에 포함되지 않는다. `sys.argv[1]`은 값을 가져오는 표현이며, 화면에 보려면 `print(sys.argv[1])`을 쓴다. **`sys.arvg`는 오타**라 `AttributeError`가 난다.

```python
name = sys.argv[1] if len(sys.argv) == 2 else "main"
```

풀어 쓰면:

```python
if len(sys.argv) == 2:
    name = sys.argv[1]
else:
    name = "main"
```

인자가 없으면 `main`이다. `aaa`를 넣으면 우선 `name`은 `aaa`가 되지만 다음 허용 목록 검사에서 종료한다.

```python
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
```

안내 문구의 `|`는 “또는”이라는 뜻이다. 이 문구를 명령으로 그대로 입력하라는 뜻은 아니다. 또한 현재 조건은 인자가 너무 많아도 `main`을 선택한다는 점을 알아둔다.

### 선택한 모듈에서 객체 가져오기

```python
module = importlib.import_module(name)
client = TestClient(module.app)
```

`name`이 `solution`이면 `solution.py`의 `app` 객체를 가져와 전달한다. 각 차시 디렉터리에서 실행해야 같은 이름의 파일을 의도대로 선택하기 쉽다.

```python
f = module.summarize_changes  # 함수 자체를 가져오기
result = f(sample)           # 괄호를 붙여 실제 호출하기
```

`payload`, `f`, `ready`, `combine`, `result`는 개발자가 정한 이름이다. `f` 문자열의 접두사와 변수명 `f`도 별개의 용법이다.

```python
print(f"file name: {name}.py")  # {name} 자리에 값 삽입
```

### 직접 실행과 import 구별

```python
if __name__ == "__main__":
    print(is_ready("false"))
```

이 블록은 파일을 직접 실행했을 때만 실행된다. `check.py`가 모듈을 import할 때는 실행되지 않는다. 다만 블록 밖의 최상위 코드는 import 시에도 실행된다.

## 10. 5~8차시에서 기억할 파이썬 개념

### 5차시: bool("false")는 True

```python
bool("true")   # True
bool("false")  # True
bool("")       # False
```

문자열의 뜻이 아니라 비어 있는지 검사하기 때문이다. 실습 정답은 다음과 같다.

```python
def is_ready(value: str) -> bool:
    return value.lower() == "true"
```

`"TRUE"`도 참, `"false"`는 거짓이다. 이 구현은 `" true "`의 공백을 제거하지 않으며, `"yes"` 같은 다른 문자열도 거짓으로 처리한다.

### 6차시: 리스트 컴프리헨션과 조건 필터

```python
sample = [
    {"path": "main.py", "status": "modified"},
    {"path": "old.py", "status": "deleted"},
]

[c["path"] for c in sample if c["status"] != "deleted"]
# ["main.py"]

[c["path"] for c in sample]
# ["main.py", "old.py"]
```

일반형은 `[모을 값 for 변수 in 목록 if 조건]`이다. 조건을 빼면 모든 항목을 대상으로 한다. 삭제도 변경이므로 PR 변경 요약에서는 삭제된 파일을 빠뜨리면 안 된다.

### 7차시: 포함 여부와 정확한 일치는 다르다

```python
"admin" in "not-admin"  # True: 부분 문자열 포함
"not-admin" == "admin"  # False: 전체 문자열 비교
```

실습의 권한 정책은 `role == "admin"`일 때만 허용한다. 정상 관리자뿐 아니라 `not-admin`, `viewer`가 거부되는지도 테스트해야 한다.

### 8차시: 딕셔너리로 ID별 통합하기

```python
def combine_tasks(main_tasks: list[dict], feature_tasks: list[dict]) -> list[dict]:
    by_id = {task["id"]: task for task in main_tasks}
    for task in feature_tasks:
        by_id[task["id"]] = task
    return [by_id[key] for key in sorted(by_id)]
```

1. `{task["id"]: task for task in main_tasks}`로 ID를 키로 쓰는 딕셔너리를 만든다.
2. 기능 쪽 데이터를 넣는다. 같은 ID라면 기존 데이터 전체를 기능 쪽 데이터로 교체한다.
3. `sorted(by_id)`로 키를 정렬하고, 그 순서대로 값을 꺼내 리스트로 만든다.

```python
combine_tasks([{"id": 1}], [{"id": 2}])
# [{"id": 1}, {"id": 2}]

combine_tasks(
    [{"id": 1, "title": "기존"}],
    [{"id": 1, "title": "기능 우선"}],
)
# [{"id": 1, "title": "기능 우선"}]
```

이것은 **리스트 데이터를 합치는 정책**을 보여주는 함수다. Git 브랜치 자체를 병합하는 명령은 아니다. `return feature_tasks`만 쓰면 두 매개변수를 모두 받더라도 반환은 기능 쪽 목록만 하게 된다.

## 11. 통합 실습 lesson_01_04.py의 추가 개념

이 파일은 앞 차시와 달리 클라이언트가 `id`, `name`, `message`를 보낸다. 자동 ID 발급 방식과 혼동하지 않는다.

- `find_task(task_id)`: ID 검색과 404 처리를 공통 함수로 모음
- POST: 기존 ID와 중복이면 `409`
- PUT: 경로 ID와 본문 ID가 다르면 `400`
- `task.clear()` 후 `task.update(...)`: 같은 딕셔너리 객체의 내용을 비우고 다시 채움
- PATCH: `exclude_unset=True`로 전송된 필드만 갱신
- DELETE: 찾은 딕셔너리를 `tasks.remove(task)`로 제거

`pop(index)`는 위치로, `remove(value)`는 같은 값을 가진 첫 항목을 찾아 제거한다.

## 12. Git·PR·AI 리뷰 핵심

수업 문서의 협업 흐름은 **기능 브랜치 → 수정과 테스트 → 커밋·push → PR → 리뷰 반영 → 재검증 → 병합**이다. 아래 명령은 복습 예시이며, 이번 정리 작업에서 Git 작업을 수행한 것은 아니다.

```bash
git status
git switch -c feature/task-fix
# 코드 수정 후 해당 차시 디렉터리에서 검사
python check.py main
git diff
git add main.py
git commit -m "fix: correct task behavior"
git push -u origin feature/task-fix
```

- 브랜치: 기능 작업을 위한 분리된 변경 흐름
- 커밋: 의미 있는 변경 기록
- push: 로컬 커밋을 원격 저장소에 올림
- PR: 변경을 검토하고 병합하기 위한 요청. PR 생성 자체가 병합은 아님
- base: 변경을 받아들일 대상 브랜치, compare: 변경을 제안하는 브랜치
- 리뷰 반영: 같은 기능 브랜치에 수정 커밋을 push하면 해당 PR에 반영됨
- 충돌 해결: `<<<<<<<`, `=======`, `>>>>>>>` 양쪽 내용을 읽고 의도에 맞게 수정한 뒤 테스트

PR 본문에는 **변경 이유, 변경 범위, 버그 재현 방법, 수정 후 검사 결과**를 적는다. AI의 지적은 입력·실제 결과·기대 결과로 확인한다.

예: “`can_edit('not-admin')`이 True라 잘못 허용된다. `== 'admin'`으로 수정하고 admin 허용·not-admin 거부·viewer 거부를 검사했다.”

## 13. 복습 실행과 최종 확인

각 차시 폴더에서 실행한다. 예를 들어 프로젝트 루트 기준:

```bash
cd day9/kdt_crud_pr_ai_review/lesson_04
python check.py main
python check.py solution
```

시작 코드의 실패는 버그를 재현하는 학습 과정이다. 수정 후에는 `main` 검사도 통과시키는 것이 목표다. 1~4차시를 브라우저로 확인하려면 해당 차시에서 `python -m uvicorn main:app`을 실행하고 `/docs`를 연다. `check.py` 실행에는 별도의 웹 서버가 필요 없다.

### 기억할 문장 10개

1. 목록 길이, ID, 인덱스는 서로 다른 개념이다.
2. 삭제된 ID 재사용을 막으려면 현재 최대값 이상의 발급 이력이 필요하다.
3. `dict.get()`은 없는 키에 `None`을 반환하고, 자동으로 404를 만들지는 않는다.
4. `return`은 함수를 끝내고, `raise`는 예외를 발생시킨다.
5. PATCH는 보내지 않은 필드를 유지해야 하므로 `exclude_unset=True`를 기억한다.
6. 같은 딕셔너리를 가리키는 변수로 내용을 바꾸면 원본에도 반영된다.
7. `assert`는 검사이고 `print()`는 출력이다. 기대값을 쓴다고 실제 응답이 바뀌지 않는다.
8. `raise_server_exceptions=False`는 의도한 404 응답을 500으로 바꾸지 않는다.
9. `bool("false")`와 `"admin" in "not-admin"`은 둘 다 True다.
10. AI 리뷰와 병합 결과는 정상 입력뿐 아니라 누락·없는 ID·거부 대상·충돌 사례로 검증한다.

### 원본 찾아보기

- [전체 과정 개요](kdt_crud_pr_ai_review/COURSE_OVERVIEW.md)
- [1차시: ID 생성](kdt_crud_pr_ai_review/lesson_01/solution.py)
- [2차시: 404 처리](kdt_crud_pr_ai_review/lesson_02/solution.py)
- [3차시: PATCH](kdt_crud_pr_ai_review/lesson_03/solution.py)
- [4차시: CRUD와 삭제](kdt_crud_pr_ai_review/lesson_04/solution.py)
- [5차시: 문자열 불리언](kdt_crud_pr_ai_review/lesson_05/solution.py)
- [6차시: 변경 요약](kdt_crud_pr_ai_review/lesson_06/solution.py)
- [7차시: 권한 비교](kdt_crud_pr_ai_review/lesson_07/solution.py)
- [8차시: 데이터 통합](kdt_crud_pr_ai_review/lesson_08/solution.py)
- [통합 CRUD 실습](kdt_crud_pr_ai_review/lesson_01_04.py)
