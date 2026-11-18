# Day 7 — 동기·비동기와 FastAPI 핵심 정리

> **비동기는 기다림을 없애는 기술이 아니라, 기다리는 동안 다른 작업을 진행하는 방식이다.**
>
> 학습 흐름: 서버와 클라이언트 → 동기·비동기 → 코루틴과 await → 여러 작업 실행 → FastAPI 적용 → 외부 API와 오류 처리 → 결과 순서 → 실행 방법.

현재 `day7`의 소스코드·주석과 수업 중 질문을 기준으로 정리했다. 코드와 주석이 다른 부분은 실제 동작을 기준으로 설명한다. 아래 시간은 별도 표시가 없으면 **코드에 따른 예상값**이며, 이번 정리에서 서버를 새로 실행해 측정한 값은 아니다.

## 1. 먼저 구분하기: 서버와 클라이언트

| 역할 | 하는 일 | 수업 파일 |
| --- | --- | --- |
| 서버 | 요청을 받아 처리하고 응답 | `01/main.py`, `02/main.py`, `03/main.py` |
| 클라이언트 | 서버로 요청을 전송 | `01/probe.py`, `02/fetch01.py`, 브라우저 |
| 외부 API 역할의 모의 서버 | 테스트에 필요한 응답·지연·오류 제공 | `03/mock_api.py` |

`02/main.py`는 서버이면서 외부 API에 대해서는 클라이언트이기도 하다.

```text
사용자 브라우저
    → 내 FastAPI 서버의 /todos/1
        → HTTPX로 외부 API에 요청
        ← 외부 API의 할 일 데이터
    ← 필요한 정보를 정리한 응답
```

**비동기로 호출해도 외부 API 결과가 필요한 요청은 결과를 받은 뒤 사용자에게 응답한다.** 달라지는 것은 기다리는 동안 다른 사용자 요청을 처리할 수 있다는 점이다.

## 2. 동기와 비동기: 무엇이 다를까?

관련 파일: [01/wait01.py](01/wait01.py)

| 구분 | 동기 | 비동기 |
| --- | --- | --- |
| 기본 흐름 | 호출이 끝나야 다음 줄 실행 | 대기 지점에서 멈췄다가 나중에 이어서 실행 가능 |
| 기다리는 동안 | 현재 스레드가 기다림 | 이벤트 루프가 다른 준비된 작업을 진행할 수 있음 |
| 대표 예 | `time.sleep(2)` | `await asyncio.sleep(2)` |
| 적합한 상황 | 동기 라이브러리 사용 등 | API·DB 등 I/O 응답 대기가 많은 작업 |

**스레드**는 코드를 실행하는 일꾼, **이벤트 루프**는 실행 가능한 비동기 작업을 번갈아 진행하는 관리자라고 생각하면 된다. **프로세스**는 실행 중인 프로그램의 단위다.

카페로 비유하면, 비동기는 커피가 내려오는 동안 다른 주문을 받는 방식이다. 커피 자체가 더 빨리 내려오는 것은 아니다.

### 꼭 구분할 두 가지

- **동기/비동기:** 기다리는 동안 실행 흐름을 어떻게 다루는가?
- **순차/동시 진행:** 여러 작업을 하나씩 시작하는가, 함께 진행하도록 등록하는가?

비동기 함수도 순차 실행할 수 있다. 동시 진행은 여러 CPU에서 계산하는 **병렬 처리**와도 다르다. 이 수업의 asyncio 예제는 주로 I/O 대기를 겹치는 동시성이다.

## 3. 코루틴 함수 → 코루틴 객체 → 실행

```python
import asyncio

async def make_drink(name):        # 코루틴 함수: 작업 정의
    await asyncio.sleep(2)
    return name

async def main():
    work = make_drink('커피')      # 코루틴 객체 생성: 본문은 아직 실행 안 됨
    result = await work           # 작업 실행 및 완료 대기
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
```

| 용어·문법 | 기억할 의미 |
| --- | --- |
| 코루틴 | 중간에 실행을 양보하고 나중에 이어갈 수 있는 작업 |
| 코루틴 함수 | `async def`로 정의한 함수 |
| 코루틴 객체 | 코루틴 함수를 호출해 만든 실행 대상 |
| `await` | 현재 작업에서 완료를 기다림. 미완료 작업을 기다릴 때 다른 작업에 실행 기회를 줄 수 있음 |
| Task | 코루틴을 이벤트 루프에 등록하고 상태·결과를 관리하는 객체 |
| `asyncio.run(main())` | 일반 스크립트에서 이벤트 루프를 시작해 `main()`을 실행하고 정리 |

**`await`는 “기다리지 않는다”는 뜻이 아니다. 현재 코루틴은 기다리지만, 이벤트 루프는 다른 일을 할 수 있다는 뜻이다.** 다른 작업이 없다면 그냥 기다리게 된다.

- `await`는 `async def` 안에서 사용한다.
- 코루틴 객체를 만들기만 하고 await하거나 등록하지 않으면 본문이 실행되지 않는다.
- 완료된 코루틴 객체를 다시 await해 재실행할 수는 없다. 새 작업은 함수를 다시 호출해 만든다.
- FastAPI는 비동기 라우터를 직접 실행하므로 라우터 안에서 `asyncio.run()`을 쓰지 않는다.
- `if __name__ == '__main__':`는 이 파일을 직접 실행했을 때만 아래 코드를 실행하라는 뜻이다.

공식 확인: [Python 코루틴과 Task](https://docs.python.org/3.13/library/asyncio-task.html).

## 4. 여러 작업: gather()가 항상 필요할까?

아래 조각들은 앞의 `make_drink()`를 사용하며, `async def main()` 안에 넣는 코드다.

### ① 하나씩 await하면 순차 실행 — 약 4초

```python
await make_drink('커피')
await make_drink('차')
```

커피가 끝난 뒤 차를 시작한다. **비동기 코드이지만 두 음료의 대기는 겹치지 않는다.**

### ② gather()로 함께 진행 — 약 2초

```python
results = await asyncio.gather(
    make_drink('커피'),
    make_drink('차'),
)
# ['커피', '차']
```

두 작업을 함께 진행하고 모두 끝나면 결과를 모은다. **결과는 완료 순서가 아니라 전달한 순서**다.

### ③ Task를 먼저 모두 등록해도 동시 진행 — 약 2초

```python
coffee_task = asyncio.create_task(make_drink('커피'))
tea_task = asyncio.create_task(make_drink('차'))

coffee = await coffee_task
tea = await tea_task
```

두 작업을 먼저 등록했기 때문에 커피를 기다리는 동안 차 작업도 진행된다. **gather()는 필수가 아니다.**

### 주의: 만들자마자 await하면 다시 순차 실행 — 약 4초

```python
coffee = await asyncio.create_task(make_drink('커피'))
tea = await asyncio.create_task(make_drink('차'))
```

`01/wait01.py`의 5번 예제는 실제로 이 형태다. 주석에는 약 2초라고 되어 있지만, 각 작업을 바로 기다리므로 해당 부분은 **약 4초**가 맞다. 이때 `coffee`와 `tea`에는 Task가 아니라 완료 결과가 들어간다.

이 파일은 여러 예제를 한 파일에 모으면서 `main()`을 여러 번 재정의하고 중간에도 실행한다. 파일 전체 실행 시간과 개별 예제의 시간을 혼동하지 말자.

## 5. FastAPI에서 /bad와 /good은 왜 다를까?

관련 파일: [01/main.py](01/main.py), [01/probe.py](01/probe.py)

```python
# 좋지 않은 예: 이벤트 루프 스레드를 막는다.
@app.get('/bad')
async def bad():
    time.sleep(3)
    return {'status': 'ok'}

# 비동기 대기: 기다리는 동안 다른 요청 처리 가능.
@app.get('/good')
async def good():
    await asyncio.sleep(3)
    return {'status': 'ok'}
```

`probe.py`는 `gather()`로 요청 세 개를 함께 보낸다. 단일 worker·다른 부하가 없는 조건에서 예상은 다음과 같다.

| 확인할 것 | `/bad` | `/good` |
| --- | --- | --- |
| 요청 하나 | 약 3초 | 약 3초 |
| 요청 세 개 전체 | 약 9초 | 약 3초 |
| 실행 중 `/health` 요청 | 같은 이벤트 루프가 막혀 지연 | 빠르게 처리 가능 |

**클라이언트가 요청을 함께 보내도, 서버가 이벤트 루프를 막으면 동시 처리 효과가 사라진다.** HTTP 200은 성공 여부일 뿐 빠르게 처리했다는 뜻이 아니다.

`01/프롬프트A.md`의 6초·2초 수치는 기대 예시다. 현재 코드의 3초 대기 기준 예상은 위 표이며, 실제 측정 시 연결·처리 비용 등으로 조금 달라진다.

### 기존 동기 I/O 함수를 써야 한다면

```python
def legacy_lookup():
    time.sleep(3)
    return {'name': '학습자'}

@app.get('/fixed')
async def fixed():
    user = await asyncio.to_thread(legacy_lookup)
    return {'user': user}
```

`to_thread()`는 동기 함수를 별도 스레드에 맡긴다. **`legacy_lookup()`로 먼저 실행한 결과가 아니라 `legacy_lookup` 함수 자체를 전달한다.** 이는 기존 동기 I/O 코드에 유용하며, CPU 계산을 자동으로 빠르게 만드는 방법은 아니다.

## 6. 라우터는 언제 def, 언제 async def일까?

**GET·POST·PUT·DELETE라는 메서드 이름보다 함수 안에서 하는 일과 라이브러리를 기준으로 고른다.**

| 대표 작업 | 선택 | 이유 |
| --- | --- | --- |
| `httpx.AsyncClient`로 외부 API 호출 | `async def` + `await` | 네트워크 대기 동안 다른 요청 처리 |
| 비동기 DB 드라이버로 조회·수정·삭제 | `async def` + `await` | DB 대기를 양보할 수 있음 |
| `requests`, `httpx.Client`, 동기 DB 라이브러리 사용 | 일반 `def` 라우터 | FastAPI가 스레드풀에서 실행 |
| 비동기 처리 중 기존 동기 I/O 일부 사용 | `async def` + `to_thread()` 검토 | 동기 부분만 스레드로 분리 |
| 짧은 계산·간단한 값 반환 | `async def` 사용 가능 | 오래 실행을 막는 작업이 없음 |
| 대량 계산·무거운 이미지 처리 | 별도 프로세스·작업 큐 검토 | 비동기 문법만으로 CPU 작업이 빨라지지 않음 |

**대부분의 라우터를 비동기로 만들어도 될까?** API·DB 등 주요 I/O가 비동기를 지원하고, 이벤트 루프를 오래 막는 코드를 분리했다면 가능하다. 전부 같은 문법으로 통일할 필요는 없다.

일반 `def` 라우터를 쓴다고 서버 전체가 요청을 하나씩만 처리하는 것은 아니다. FastAPI가 스레드풀에서 실행한다. 반대로 **`async def` 안에서 직접 호출한 일반 함수는 자동으로 스레드풀로 이동하지 않는다.** 스레드 자원도 무한하지 않다.

현재 [02/main.py](02/main.py)는 외부 API 응답을 기다리고 HTTPX가 비동기를 지원하므로 `async def`가 적합하다. 요청 하나라서 `gather()`는 필요 없다.

공식 확인: [FastAPI의 동기·비동기 선택](https://fastapi.tiangolo.com/async/).

## 7. HTTPX로 외부 API를 호출하는 기본 흐름

관련 파일: [02/fetch01.py](02/fetch01.py), [02/main.py](02/main.py)

```python
async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
    response = await client.get('/todos/1')
    response.raise_for_status()
    data = response.json()
```

| 코드 | 의미 |
| --- | --- |
| `async with` | 비동기 자원에 진입하고 블록 종료 시 연결 자원 정리 |
| `AsyncClient` | HTTP 요청을 보내는 클라이언트 객체. 브라우저 자체는 아님 |
| `base_url` | 요청 주소 앞에 공통으로 붙일 기본 주소 |
| `await client.get(...)` | GET 응답 기다리기 |
| `response.status_code` | 상태 코드 확인: 200, 404, 503 등 |
| `response.raise_for_status()` | 비성공 상태에 `HTTPStatusError` 발생시킴 |
| `response.json()` | 응답 JSON을 Python 값으로 변환. 항상 dict인 것은 아님 |
| `data.get('title', '제목 없음')` | dict에서 키가 없을 때 기본값 사용. 타입 검증은 아님 |
| `timeout` | 연결·읽기 등 네트워크 대기에 시간 제한. 전체 작업의 고정 마감 시간과는 다름 |
| `trust_env=False` | 환경변수의 프록시 등 HTTPX 환경 설정을 사용하지 않도록 함 |

**`async with` 자체가 여러 요청을 동시에 실행해 주지는 않는다.** 동시에 진행할지는 내부의 `await`, `gather()`, Task 등록 방식이 결정한다.

`response.json()`은 역직렬화(JSON → Python 값)다. Python dict를 JSON으로 변환하는 것은 직렬화이며, FastAPI는 일반적으로 반환한 dict를 JSON 응답으로 만들어 준다.

공식 확인: [HTTPX 응답·상태·JSON 처리](https://www.python-httpx.org/quickstart/).

## 8. 외부 API 오류는 단계별로 나눠 생각하기

| 발생 단계·증상 | 의미 | 확인·대응 |
| --- | --- | --- |
| `ConnectError` | 서버에 연결하지 못함 | 서버 실행 여부, 주소·포트·네트워크 확인 |
| `TimeoutException` | 네트워크 작업이 제한 시간 안에 진행되지 못함 | 외부 응답 지연 확인, 오류 응답 처리 |
| `HTTPStatusError` | HTTP 응답은 왔지만 비성공 상태 | `raise_for_status()` 호출 후 상태에 맞게 처리 |
| `response.json()` 실패 | HTML·잘못된 JSON 등 | JSON 형식 확인 |
| JSON인데 필드 누락·타입 오류 | 응답 구조가 예상과 다름 | dict 여부·필드·타입 검증, 필요하면 Pydantic 사용 |

예를 들어 `{"completed": "false"}`의 `"false"`는 문자열이다. Python의 `False`와 다르며 `bool("false")`는 오히려 `True`다. 문자열을 무조건 `bool()`로 바꾸면 안 된다.

### 현재 02/main.py에서 주의할 부분

1. `raise_for_status()`가 없어 404·503을 받아도 현재의 `except HTTPStatusError`로 잡히지 않는다.
2. 예외를 잡고 출력만 하면 `data`가 없는 상태에서 다음 코드가 실행될 수 있다.
3. 연결 실패·타임아웃·JSON 형식 오류는 HTTP 상태 오류와 별개다.

다음은 **HTTP 상태·연결·타임아웃 처리의 개선 예시**다. 원본을 수정한 코드는 아니다.

```python
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

@app.get('/todos/{todo_id}')
async def read_todo(todo_id: int):
    try:
        async with httpx.AsyncClient(
            base_url='https://jsonplaceholder.typicode.com', timeout=10.0
        ) as client:
            response = await client.get(f'/todos/{todo_id}')
            response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail='외부 API 응답 시간 초과')
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            raise HTTPException(status_code=404, detail='할 일을 찾을 수 없습니다')
        raise HTTPException(status_code=502, detail='외부 API 응답 오류')
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail='외부 API 연결 실패')

    # JSON 형식과 필드·타입 검증은 추가로 필요하다.
    return response.json()
```

## 9. 결과 순서: gather()와 as_completed()

관련 파일: [03/main.py](03/main.py), [03/mock_api.py](03/mock_api.py)

모의 API는 ID 1에 0.6초, ID 2에 0.1초, ID 3에 0.3초 대기를 넣는다.

| 방식 | 결과를 받는 순서 | 예상 전체 대기 |
| --- | --- | --- |
| `for` 안에서 하나씩 `await fetch(...)` | 요청 순서 1 → 2 → 3 | 약 1.0초 |
| `await gather(fetch(1), fetch(2), fetch(3))` | 입력 순서 1 → 2 → 3 | 약 0.6초 |
| `for ... in as_completed(...)` | 완료 순서. 이 예제는 대략 2 → 3 → 1 | 약 0.6초 |

완료 순서는 네트워크와 실행 상황에 따라 달라질 수 있다. `/summary`는 비동기 **순차** 실행이고, `/labels`는 비동기 **동시** 진행이다. 주석의 ‘병렬’은 이 예제에서는 ‘동시 진행’으로 이해하자.

### 현재 /labels의 함정: 요청 ID와 데이터가 섞임

```python
# 완료 순서 데이터에 원래 요청 순서를 다시 붙이면 잘못된 짝이 생긴다.
for item_id, data in zip(ids, completed):
    ...
```

`ids`가 `[1, 2, 3]`, 완료된 데이터의 ID가 `[2, 3, 1]`이면 요청 ID 1에 데이터 2를 붙이게 된다. **완료 순서로 받을 때는 요청의 식별자도 함께 반환해야 한다.**

아래는 `03/main.py`의 `/labels`를 바꾼다면 사용할 수 있는 개선 예시다. 같은 파일의 `fetch`, `BASE_URL`, `app`을 사용한다.

```python
@app.get('/labels')
async def labels():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=3) as client:
        async def fetch_labeled(item_id):
            data = await fetch(client, item_id)
            return {'requested_id': item_id, 'data': data}

        jobs = [fetch_labeled(item_id) for item_id in [1, 2, 3]]
        completed = []
        for job in asyncio.as_completed(jobs):
            completed.append(await job)
        return completed
```

원래 요청 순서로 결과만 모으면 되는 상황이라면 `gather()`가 더 간단하다. 완료된 것부터 처리하고 싶으면 `as_completed()`를 선택한다. 여기서 예외를 별도로 처리하지 않았으므로 작업 하나가 실패하면 정상 결과 목록 대신 예외가 전달될 수 있다.

## 10. 모의 API가 준비해 둔 추가 실습

`03/mock_api.py`에는 다음 상황이 준비되어 있다. **현재 `03/main.py`가 이 모든 상황을 처리하는 것은 아니다.** 동시 요청 제한·재시도·부분 실패 대응을 확장 연습할 수 있는 서버다.

| 경로 | 재현하는 상황 | 배울 점 |
| --- | --- | --- |
| `/cases/slow` | 느린 응답 | 타임아웃 |
| `/cases/missing`, `/cases/wrong_bool`, `/cases/list` | 필드 누락·타입·형태 차이 | JSON 파싱 뒤 데이터 검증 |
| `/cases/html`, `/cases/broken_json` | HTML 또는 깨진 JSON | 형식 오류 처리 |
| `/cases/not_found`, `/cases/server_error` | 404·503 | HTTP 상태 처리 |
| `/limited/{id}` | 동시 처리 2개 초과 시 429 | Semaphore 등으로 동시 요청 수 제한 |
| `/metrics` | 현재·최대 동시 처리 수 | 요청 제한 효과 확인 |
| `/flaky/{id}` | 같은 요청 식별자·ID로 처음 두 번 503 | 제한된 횟수의 재시도와 대기 간격 |
| `/tools/{name}` | `scenario=partial` 또는 `all_fail` | 느린 도구·부분 실패·전체 실패 구분 |

`/limited`는 `finally`에서 사용 중인 자리 수를 돌려놓는다. 성공뿐 아니라 예외·취소가 발생해도 자원을 정리하는 것이 중요하다. 모의 서버의 상태는 메모리에 있으며 재시작하면 초기화된다.

## 11. 쇼핑몰 앱으로 개념 연결하기

관련 파일: [shop-web/shop_lab.py](shop-web/shop_lab.py), [실행 안내](shop-web/README.md)

재고 0.6초 + 배송 0.9초 + 리뷰 1.2초를 조회하는 실험이다. HTTP 요청은 실제 로컬 요청이고, 외부 쇼핑몰의 대기만 sleep으로 흉내 낸다.

| 모드 | 핵심 | 기본 배율 예상 |
| --- | --- | --- |
| 동기·순차 | `Client`로 하나씩 호출. 실험 서버에서는 동기 함수 전체를 스레드에 맡김 | 약 2.7초 |
| 비동기·순차 | `AsyncClient`를 사용하지만 하나씩 await | 약 2.7초 |
| 비동기·동시 | `gather()`로 함께 진행 | 약 1.2초 |
| Task·동시 | 모두 등록한 뒤 await | 약 1.2초 |
| 잘못된 비동기 | 클라이언트는 동시 요청, 서버가 `time.sleep()`으로 이벤트 루프 차단 | 약 2.7초 |
| 동기 I/O 개선 | 서버의 동기 대기를 `to_thread()`로 분리 | 약 1.2초 |

**같이 느려도 이유는 다를 수 있다.** 순차 요청은 전체 시간이 길어도 다른 사용자 요청을 처리할 수 있다. 이벤트 루프 차단은 다른 요청까지 지연시킨다. 실행 중 ‘서버 응답 확인’을 눌러 구분하자.

## 12. 실행 명령과 자주 만난 오류

모든 명령은 프로젝트 루트 `AIO_4_class` 기준이다. 여러 실습을 동시에 할 때 같은 포트의 서버를 중복 실행하지 않는다.

### 실습별 실행

```bash
# 01: 서버를 켜둔 뒤 다른 터미널에서 probe 실행
python -m uvicorn main:app --app-dir day7/01 --reload --port 8000
python day7/01/probe.py

# 02: 외부 API 호출 스크립트 또는 FastAPI 서버
python day7/02/fetch01.py
python -m uvicorn main:app --app-dir day7/02 --reload --port 8000

# 03: 두 서버를 각각 별도 터미널에서 실행
python -m uvicorn mock_api:app --app-dir day7/03 --reload --port 9000
python -m uvicorn main:app --app-dir day7/03 --reload --port 8000

# 쇼핑몰 실험 앱
python -m uvicorn shop_lab:app --app-dir day7/shop-web --reload --port 8010
```

- 02 확인: `http://127.0.0.1:8000/todos/1`
- 03 확인: `http://127.0.0.1:8000/summary`, `http://127.0.0.1:8000/labels`
- 쇼핑몰: `http://127.0.0.1:8010`

### python -m을 붙이는 이유

| 명령 | 실행 파일을 찾는 기준 |
| --- | --- |
| `uvicorn ...` | 터미널 PATH에서 찾은 uvicorn 실행 파일 |
| `python -m uvicorn ...` | 현재 python 환경에 설치된 uvicorn 모듈 |

가상환경과 실행 파일이 일치하면 사실상 같은 서버를 실행한다. 환경이 여러 개면 `python -m uvicorn`이 어떤 Python을 사용하는지 명확하게 해준다. `--app-dir`는 모듈을 찾을 폴더, `--reload`는 수정 시 자동 재시작, `--port`는 포트 번호다.

`패키지.모듈:app`에서 `:app`은 파일 안의 `app = FastAPI()` 객체를 뜻한다. 숫자 폴더나 하이픈 폴더는 일반 Python import 문법에 제약이 있으므로 이 정리에서는 `--app-dir` 방식을 사용했다.

현재 디스크에서 확인한 쇼핑몰 폴더 이름은 **`shop-web`**이다. 실제 이름을 `shop_web`으로 변경하면 루트에서 `python -m uvicorn day7.shop_web.shop_lab:app --reload --port 8010`처럼 쓸 수 있다. 대화 당시 경로보다 현재 파일 위치를 기준으로 실행하자.

### 오류를 보면 이 순서로 확인

| 오류·증상 | 먼저 확인할 것 |
| --- | --- |
| `await`에 문법 오류 | 해당 함수가 `async def`인가? |
| `coroutine was never awaited` | 코루틴을 만들기만 하고 실행하지 않았는가? |
| `address already in use` | 포트 중복. 기존 서버를 `Ctrl+C`로 종료하거나 포트 변경 |
| `ConnectError: All connection attempts failed` | 서버가 켜져 있는가? 클라이언트와 서버의 포트가 같은가? |
| 200인데 느림 | 성공 여부와 별개로 순차 실행·이벤트 루프 차단 확인 |
| 요청 ID와 응답 ID가 다름 | 완료 순서 결과를 원래 순서와 zip하지 않았는가? |

포트를 확인하려면 macOS에서 `lsof -nP -iTCP:8000 -sTCP:LISTEN`을 사용한다. 포트를 바꾸면 브라우저 주소와 `probe.py`의 `base_url`도 맞춰야 한다. `probe.py`만 실행한다고 서버가 자동으로 켜지지는 않는다.

## 13. 꼭 기억할 8문장

1. **비동기는 기다리는 동안 다른 작업을 진행할 기회를 준다.**
2. **async def만 붙여도 자동으로 비동기 I/O나 동시 실행이 되지는 않는다.**
3. **하나씩 await하면 순차 실행, 대기를 겹치려면 작업들을 먼저 함께 등록한다.**
4. **gather는 입력 순서, as_completed는 완료 순서다.**
5. **async def 안에서 직접 실행한 동기 함수는 이벤트 루프를 막을 수 있다.**
6. **라우터의 def/async def는 HTTP 메서드가 아니라 사용하는 작업·라이브러리로 결정한다.**
7. **연결 성공 → HTTP 성공 → JSON 파싱 → 데이터 검증은 서로 다른 단계다.**
8. **사용자에게 필요한 결과를 기다린 뒤 응답한다는 점은 동기·비동기 모두 같다.**
