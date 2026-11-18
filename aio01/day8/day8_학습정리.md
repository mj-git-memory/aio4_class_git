# Day 8 복습 — API의 약속을 문서와 테스트로 확인하기

작성일: 2026-10-29

이 문서는 `day8.py`와 1~8차시의 `main.py`, `solution.py`, `test_api.py`, 주요 README·코드 설명·프롬프트를 바탕으로 작성했습니다. **현재 학생 코드의 동작**과 **요구사항에 맞는 동작**을 구분합니다. 기존 소스는 수정하지 않았습니다.

코드 블록은 각 개념을 설명하는 발췌 예시입니다. 모든 블록을 한 파일에 이어 붙이지 말고, 실제 실행은 링크된 차시의 `main.py`와 함께 확인하세요.

뒤쪽의 Git 문답은 day8 Python 코드에 있는 내용이 아니라, **이 대화에서 직접 질문하신 내용을 연결한 복습**입니다. 제공되지 않은 다른 대화의 질문은 추측해 넣지 않았습니다.

## 읽는 순서

1. API 요청이 처리되는 전체 흐름
2. 서버 실행과 Swagger·OpenAPI
3. Path·Query·Body와 입력 검증
4. 요구사항에서 테스트와 경계값 만들기
5. 오류 응답과 응답 모델
6. 여러 요청이 이어질 때 상태 보존하기
7. AI와 검증하는 방법
8. 질문으로 정리하는 Git·GitHub·배포
9. 마지막 암기표와 확인 문제

## 1. 오늘 배운 내용을 한 문장으로

> API가 한 번 성공했다고 끝내지 말고, 입력·결과·문서·다음 요청까지 약속대로 동작하는지 확인한다.

예를 들어 예약 API가 “좌석 부족”이라고 올바르게 응답해도, 내부 좌석 수를 잘못 줄였다면 다음 예약은 실패합니다. **응답 상태만 맞는 것과 기능이 맞는 것은 다릅니다.**

수업의 전체 흐름은 다음과 같습니다.

```text
요구사항 정하기 → 요청 보내기 → 입력 검증 → 업무 처리
→ 상태 변경 → 응답 만들기 → 테스트로 기대값과 비교
```

| 차시 | 예제 | 꼭 기억할 질문 |
| --- | --- | --- |
| 01 Swagger | 인사 API | 실제로 호출되는 API가 문서에도 보이는가? |
| 02 Parameters | 상품 수량 | 생략값·최솟값·최댓값을 처리하는가? |
| 03 Body validation | 주문 | 잘못된 타입·누락·추가 필드를 거절하는가? |
| 04 AI test cases | 할인 견적 | 딱 10,000원인 경계도 검사했는가? |
| 05 Errors | 상품 조회 | 없는 상품을 성공처럼 응답하지 않는가? |
| 06 Response contract | 프로필 조회 | 공개하면 안 되는 항목을 내보내지 않는가? |
| 07 State scenarios | 작업 생성 | 두 번째 요청이 첫 번째 데이터를 덮어쓰지 않는가? |
| 08 Final verification | 좌석 예약 | 실패한 요청이 이후 정상 요청을 망가뜨리지 않는가? |

## 2. 요청을 보내면 누가 무엇을 할까?

### 2-1. API·HTTP·경로·메서드

**API는 프로그램끼리 주고받는 요청과 응답의 약속**입니다. HTTP는 이 수업에서 요청과 응답을 전달하는 방식입니다.

```text
GET http://127.0.0.1:8000/items/3?qty=2
```

| 부분 | 뜻 |
| --- | --- |
| `GET` | 조회 요청이라는 HTTP 메서드 |
| `127.0.0.1` | 내 컴퓨터를 가리키는 주소 |
| `8000` | 서버가 요청을 받는 포트 |
| `/items/3` | 어떤 기능·대상에 접근할지 나타내는 경로 |
| `?qty=2` | 수량 옵션을 전달하는 쿼리 문자열 |

이 수업에서는 GET으로 조회하고 POST로 본문을 보내 주문·작업·예약 등을 처리합니다. **엔드포인트는 메서드와 경로를 함께 보면 정확합니다.** `GET /tasks/1`과 `POST /tasks`는 다른 기능입니다.

### 2-2. FastAPI와 Uvicorn의 역할

```python
from fastapi import FastAPI

app = FastAPI(title="인사 API", version="1.0.0")

@app.get("/greet", summary="이름으로 인사")
def greet(name: str = "guest"):
    return {"message": f"Hello, {name}!"}
```

| 코드 | 역할 |
| --- | --- |
| `app = FastAPI(...)` | 웹 앱 객체를 준비 |
| `@app.get("/greet")` | GET 요청과 아래 함수를 연결하는 라우팅 등록 |
| `def greet(...)` | 요청이 들어왔을 때 수행할 처리 |
| `return {...}` | 응답으로 보낼 데이터를 반환 |

**데코레이터는 경로를 등록합니다. 그 줄을 읽는 순간 인사 함수 본문이 실행되는 것은 아닙니다.** HTTP 요청을 받으면 FastAPI가 입력을 검사하고 해당 함수를 호출합니다.

`return`은 터미널에 출력하는 `print`와 다릅니다. 위 딕셔너리를 반환하면 FastAPI가 JSON 응답으로 전달합니다.

```json
{"message": "Hello, Min!"}
```

FastAPI가 요청 처리 규칙을 제공한다면, **Uvicorn은 실제 포트에서 HTTP 요청을 받는 서버**입니다. `python main.py`만 실행해도 서버가 켜지는 코드는 이 수업 파일에 없습니다.

### 2-3. 서버 실행·중지

아래는 프로젝트 루트 `AIO_4_class`에서 시작하는 macOS 예시입니다. 현재 선택된 Python에 필요한 패키지가 설치되어 있어야 합니다.

```sh
cd day8/lesson_01_swagger
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

| 실행 옵션 | 해석 |
| --- | --- |
| `python -m uvicorn` | 선택한 Python으로 Uvicorn 모듈 실행 |
| `main:app` | 현재 폴더의 `main.py`에서 `app` 객체 사용 |
| `--host 127.0.0.1` | 로컬 컴퓨터에서 접속할 주소 |
| `--port 8000` | 8000번 포트 사용 |
| `--workers 1` | 서버 프로세스 하나로 실행 |

서버를 실행한 터미널에서 **`Ctrl + C`**를 누르면 종료합니다. 위 명령에는 `--reload`가 없으므로 소스를 수정했다면 서버를 종료하고 다시 실행해야 합니다.

**서버의 현재 폴더가 중요합니다.** 각 차시에 `main.py`가 있으므로 실행한 폴더에 따라 다른 API가 뜹니다. 1차시의 `/`는 직접 만든 경로가 아니므로 404여도 이상하지 않습니다. `/docs` 또는 `/greet`로 접속하세요.

### 2-4. 가상환경은 왜 사용할까?

`day8.py`에는 Windows·Mac 가상환경 설정이 주석으로 정리돼 있습니다. 가상환경은 **프로젝트에 필요한 Python 패키지를 따로 관리하는 공간**입니다. 가상환경 생성·활성화와 서버 실행은 별개입니다.

```sh
# 각 lesson 폴더에서 새 환경을 만드는 macOS 예시
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python --version
```

수업 코드에는 Python 3.10 이상 문법이 있고 원래 교안은 3.12 환경을 사용합니다. `python3`가 가리키는 버전을 먼저 확인하세요. `day8.py`의 `python3.12` 명령은 그 버전이 설치된 경우에만 실행됩니다. 이미 적절한 가상환경이 있다면 매번 다시 만들 필요는 없습니다.

## 3. Swagger와 OpenAPI — 화면과 설명서를 구분하기

근거: [1차시 main.py](lesson_01_swagger/main.py), [1차시 테스트](lesson_01_swagger/test_api.py).

| 주소 | 역할 |
| --- | --- |
| `/greet?name=Min` | 실제 기능 요청 |
| `/docs` | 사람이 API를 살펴보고 실행하는 Swagger UI 화면 |
| `/openapi.json` | 경로·입력·응답 구조를 기계가 읽는 API 명세 |

카페로 비유하면 **실제 API는 주문 처리**, **OpenAPI는 메뉴 정보**, **Swagger UI는 그 정보를 보여 주고 주문도 해 보는 메뉴판**입니다.

Swagger에서는 `GET /greet` → **Try it out** → 이름 입력 → **Execute** 순서로 실행합니다. 화면의 `Example Value`는 예시이고, 실제 실행 결과는 Execute 후의 **Server response**에서 확인합니다.

### 주석의 “include_in_schema=False면 에러”는 무슨 뜻일까?

현재 `main.py`에는 다음 비교가 남아 있습니다.

```python
# include_in_schema=False  # -> 에러 발생
include_in_schema=True    # -> 수정 시 에러 안남
```

정확한 의미는 다음과 같습니다.

| 설정 | 실제 `/greet` 호출 | OpenAPI·Swagger 목록 |
| --- | --- | --- |
| `False` | 여전히 가능 | 목록에서 제외 |
| `True` | 가능 | 목록에 포함 |

**False 자체가 문법 오류나 서버 실행 오류를 만드는 것은 아닙니다.** 이 수업은 “공개 문서에 `/greet`가 있어야 한다”는 계약을 검사하므로 False일 때 문서 테스트가 실패합니다. 현재 코드는 True로 수정된 상태입니다.

문서에서 숨기는 것은 인증이나 접근 차단이 아닙니다. `/docs`가 200으로 열리는 것만 확인하지 말고 `/openapi.json`에 필요한 경로가 있는지도 확인해야 합니다. Swagger의 외부 CSS·JS가 로딩되지 않는 문제와 API 자체의 문제도 구분합니다.

## 4. 입력은 어디에서 오는가? — Path·Query·Body

### 4-1. Path와 Query

근거: [2차시 main.py](lesson_02_parameters/main.py).

```python
from typing import Annotated
from fastapi import Path, Query

@app.get("/items/{item_id}")
def read_item(
    item_id: Annotated[int, Path(ge=1)],
    qty: Annotated[int, Query(ge=1, le=5)] = 1,
):
    return {"item_id": item_id, "qty": qty, "total": qty * 1000}
```

```text
/items/3?qty=2
       ↑     ↑
     Path   Query
```

`item_id`는 경로에 들어 있는 대상 번호이고 `qty`는 `?` 뒤에 붙는 수량 옵션입니다. `qty`를 생략하면 기본값 1을 사용합니다. **생략과 0 입력은 다릅니다.** 0을 보내면 기본값으로 바꾸지 않고 범위 위반으로 거절합니다.

| 요청 | 기대 결과 |
| --- | --- |
| `/items/3` | 200, `qty=1`, `total=1000` |
| `/items/3?qty=2` | 200, `qty=2`, `total=2000` |
| `/items/3?qty=5` | 200, 허용 최댓값 |
| `/items/3?qty=6` | 422, 수량 범위 위반 |
| `/items/0` | 422, 번호 범위 위반 |
| `/items/abc` | 422, 정수로 해석할 수 없음 |

이 차시는 실제 상품 DB를 조회하지 않습니다. 따라서 양수 번호가 검증을 통과했다고 “해당 상품이 실제로 있다”는 뜻은 아닙니다.

### 4-2. Annotated는 무엇을 붙이는 문법일까?

주석의 “Annotated: 형식을 제한”은 다음처럼 나누어 이해하면 정확합니다.

```python
Annotated[int, Query(ge=1, le=5)]
#         타입  + 추가 검증 정보
```

`Annotated`는 **타입에 추가 정보를 붙이는 틀**이고, 실제 수량 범위는 `Query(ge=1, le=5)`에 적습니다. FastAPI가 이 정보를 읽어 검증합니다.

| 표현 | 의미 |
| --- | --- |
| `ge=1` | 1 이상, 경계 포함 |
| `le=5` | 5 이하, 경계 포함 |
| `gt=1` | 1 초과 |
| `lt=5` | 5 미만 |
| `= 1` | 값을 생략했을 때 쓸 기본값 |

`qty` 기본값을 2로 바꾸면 값을 생략했을 때의 응답과 문서도 달라집니다. 현재 테스트는 기본값 1을 계약으로 검사하므로, 단순한 숫자 변경이어도 테스트 결과에 영향을 줍니다.

### 4-3. Body와 Pydantic 모델

근거: [3차시 main.py](lesson_03_body_validation/main.py).

여러 값을 묶어 보내는 POST 요청은 JSON 본문으로 전달합니다. `BaseModel`은 그 본문의 모양과 검사 규칙을 정의하는 데 사용합니다.

```python
from pydantic import BaseModel, ConfigDict, Field

class OrderIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=20)
    quantity: int = Field(ge=1, le=5, strict=True)

@app.post("/orders", status_code=201)
def create_order(order: OrderIn):
    return {
        "name": order.name,
        "quantity": order.quantity,
        "total": order.quantity * 3000,
    }
```

```json
{"name": "tea", "quantity": 2}
```

위 본문은 검증을 통과하고 201과 다음 응답을 돌려줍니다.

```json
{"name": "tea", "quantity": 2, "total": 6000}
```

| 규칙 | 쉽게 해석하면 |
| --- | --- |
| `name: str` | 이름은 문자열 |
| `min_length=1, max_length=20` | 이름 길이는 1~20 |
| `quantity: int` | 수량은 정수 |
| `strict=True` | 문자열 숫자 등을 정수로 바꿔 받지 않음 |
| `extra="forbid"` | 모델에 없는 추가 항목은 거절 |
| 필드에 기본값 없음 | 요청에 반드시 있어야 함 |

| 본문 예 | 결과·이유 |
| --- | --- |
| `{"name":"tea","quantity":0}` | 422, 수량 범위 위반 |
| `{"name":"tea","quantity":"2"}` | 422, 숫자 2와 문자열 "2"는 다름 |
| `{"name":"tea","quantity":true}` | 422, 엄격한 정수 검사에서 불리언 거절 |
| `{"name":"tea","quantity":null}` | 422, 정수 필드에 null 불가 |
| `{"name":"tea"}` | 422, 필수 수량 누락 |
| `{"name":"tea","quantity":1,"admin":true}` | 422, 추가 필드 금지 |

**실제 파일의 주석에 있는 `ge=0`은 수량 0을 허용합니다.** 계약은 1~5이므로 현재 적용된 `ge=1`이 맞습니다.

주의할 차이도 있습니다. URL의 `qty=2`는 원래 텍스트지만 2차시에서는 FastAPI가 정수로 해석합니다. 3차시 JSON의 `"quantity":"2"`는 `strict=True` 때문에 거절합니다. 입력 위치와 검증 설정을 함께 봐야 합니다.

또한 현재 `name`은 길이만 검사합니다. `"   "`처럼 공백만 있는 문자열을 자동으로 지우거나 거절하는 규칙은 없습니다. **길이 검사와 공백 정리는 별개의 기능**입니다.

### 4-4. 검증이 실패하면 함수는 실행될까?

```text
요청 도착 → FastAPI·Pydantic의 입력 검증
           ├─ 실패: 422 응답, 경로 함수 본문 실행 안 함
           └─ 성공: 경로 함수 → 업무 처리 → 응답
```

이것은 FastAPI를 거쳐 요청할 때의 흐름입니다. 일반 Python 함수에 타입 힌트만 붙였다고 모든 직접 호출에 같은 검증이 생기는 것은 아닙니다.

## 5. 테스트는 현재 코드가 아니라 요구사항에서 만든다

근거: [4차시 main.py](lesson_04_ai_test_cases/main.py), [solution.py](lesson_04_ai_test_cases/solution.py), [test_seed.py](lesson_04_ai_test_cases/test_seed.py), [test_api.py](lesson_04_ai_test_cases/test_api.py).

### 5-1. 업무 계약이란?

여기서 계약은 “이 입력에는 이 결과를 내야 한다”는 요구사항입니다. 할인 API의 계약은 **10,000원 이상이면 1,000원 할인**입니다.

현재 학생 코드에는 다음 결함이 있습니다.

```python
return 1000 if amount > 10000 else 0
```

`>`는 10,000원을 포함하지 않습니다. 요구사항에 맞는 `solution.py`는 다음과 같습니다.

```python
return 1000 if amount >= 10000 else 0
```

| 금액 | 계약상 할인 | 결제액 | 현재 main.py |
| --- | --- | --- | --- |
| 5,000 | 0 | 5,000 | 정상 |
| 9,999 | 0 | 9,999 | 정상 |
| **10,000** | **1,000** | **9,000** | **할인 0으로 잘못 처리** |
| 10,001 | 1,000 | 9,001 | 정상 |
| 20,000 | 1,000 | 19,000 | 정상 |

`test_seed.py`는 5,000원·20,000원만 검사하므로 이 오류를 놓칩니다. **양쪽의 일반값만 통과해도 경계값이 틀릴 수 있습니다.**

### 5-2. 경계값을 고르는 방법

“10,000원 이상”이라는 조건이 있다면 **바로 아래 9,999 / 경계 10,000 / 바로 위 10,001**을 확인합니다. 입력 허용 범위 1~100,000도 별도로 검사합니다.

| 검사 분류 | 예시 |
| --- | --- |
| 정상 일반값 | 5,000 / 20,000 |
| 할인 조건의 경계 | 9,999 / 10,000 / 10,001 |
| 입력 허용 끝값 | 1 / 100,000 |
| 입력 범위 밖 | 0 / 100,001 |
| 잘못된 타입 | `"10000"` |
| 필수값 누락 | `{}` |

**현재 코드의 잘못된 결과를 기대값으로 복사하면 테스트도 함께 틀립니다.** 기대값은 요구사항을 읽고 먼저 정합니다.

### 5-3. TestClient와 assert

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_discount_boundary():
    response = client.post("/quotes", json={"amount": 10000})
    assert response.status_code == 200
    assert response.json() == {
        "amount": 10000,
        "discount": 1000,
        "payable": 9000,
    }
```

이 설명용 테스트는 현재 4차시 `main.py`에서는 실패하고 올바른 구현에서는 통과해야 합니다.

| 표현 | 역할 |
| --- | --- |
| `client.get(..., params={...})` | 쿼리 값을 넣어 조회 요청 |
| `client.post(..., json={...})` | JSON 본문을 넣어 POST 요청 |
| `response.status_code` | 실제 상태 코드 |
| `response.json()` | 응답 JSON을 Python 딕셔너리·리스트 등으로 읽기 |
| `assert 조건` | 참이면 통과, 거짓이면 테스트 실패 |

**보내는 `json=`과 읽는 `.json()`을 구분하세요.**

TestClient는 8000번 포트의 서버로 접속하지 않습니다. 테스트 프로세스 안에서 앱에 요청하므로 **pytest를 실행하려고 Uvicorn을 먼저 켤 필요가 없습니다.** 별도로 실행한 Swagger 서버의 메모리 데이터와 테스트의 데이터도 같지 않습니다.

### 5-4. parametrize는 같은 검사를 여러 입력으로 실행한다

```python
import pytest

@pytest.mark.parametrize("amount, discount", [
    (9999, 0),
    (10000, 1000),
    (10001, 1000),
])
def test_discount(amount, discount):
    response = client.post("/quotes", json={"amount": amount})
    assert response.json()["discount"] == discount
```

한 함수를 입력 세 묶음으로 실행하므로 테스트 세 건입니다. 반복문을 함수 안에 길게 쓰는 대신 어떤 입력에서 실패했는지 구분하기 쉽습니다.

### 5-5. 테스트 실행 위치와 실패 메시지

각 lesson은 같은 이름의 `main.py`를 독립적으로 사용합니다. **차시 폴더 안에서 파일을 지정해 실행**하세요.

```sh
# 프로젝트 루트에서 시작
cd day8/lesson_04_ai_test_cases
python -m pytest -q test_api.py
```

특정 검사만 실행하려면:

```sh
python -m pytest -q test_api.py::test_quote
```

현재 `test_seed.py`까지 확인하려면 `python -m pytest -q test_seed.py test_api.py`처럼 두 파일을 명시할 수 있습니다. 과정 전체 폴더에서 무작정 pytest를 실행하면 같은 테스트 파일·모듈 이름이 충돌할 수 있습니다.

실패 메시지의 `assert 0 == 1000`은 “실제 할인 0이 기대 할인 1000과 다르다”는 뜻입니다. 실패 자체를 없애려고 테스트를 지우기보다 **입력·기대값·실제값·계약**을 비교하세요.

## 6. 상태 코드로 성공과 실패를 구분하기

근거: [5차시 main.py](lesson_05_errors/main.py), [solution.py](lesson_05_errors/solution.py).

| 코드 | 수업에서의 의미 | 예 |
| --- | --- | --- |
| 200 | 요청 처리 성공 | 인사·상품 조회·견적 |
| 201 | 새 항목 생성 성공 | 주문·작업·예약 처리의 계약 |
| 404 | 요청한 자원 없음 | 양수 상품 번호지만 저장소에 없음 |
| 409 | 현재 상태와 충돌 | 남은 좌석보다 많은 예약 요청 |
| 422 | 입력 검증 실패 | 숫자 자리에 문자, 범위 위반, 필수값 누락 |

POST가 항상 201인 것은 아닙니다. `/quotes`는 `status_code`를 따로 지정하지 않아 정상 응답이 200입니다. 또한 201을 지정했다고 데이터가 DB에 자동 저장되는 것도 아닙니다. 저장은 별도 코드가 해야 합니다.

### 6-1. 404와 422가 헷갈릴 때

```text
/products/abc → 번호 형식이 잘못됨 → 422
/products/0   → 1 이상 규칙 위반 → 422
/products/99  → 번호 형식은 맞지만 상품 없음 → 404
```

없는 URL 자체의 404와, 존재하는 조회 API 안에서 없는 자원에 대해 반환한 404도 원인을 구분해서 봅니다.

### 6-2. raise와 return

```python
def find_product(product_id: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]
```

`return`은 정상 결과를 반환합니다. `raise HTTPException(...)`은 정상 흐름을 중단하고 FastAPI가 지정한 오류 응답을 만들게 합니다.

```json
{"detail": "Product not found"}
```

현재 학생 코드는 이 예외를 아래처럼 잡아 버립니다.

```python
try:
    return find_product(product_id)
except Exception:
    return {"id": product_id, "name": "unknown"}
```

`HTTPException`도 `Exception`에 잡히므로, 없는 상품이 `200 + unknown`이라는 성공처럼 바뀝니다. 이 수업의 수정은 **넓게 잡는 try/except를 없애고 `return find_product(product_id)`로 오류를 그대로 전달**하는 것입니다. 예외처리를 무조건 많이 넣는다고 안전해지지 않습니다.

### 6-3. 문서 선언과 실제 동작은 다르다

```python
@app.get("/products/{product_id}", responses={404: {"description": "상품 없음"}})
```

`responses={404: ...}`는 OpenAPI 문서에 404를 설명합니다. **없는 상품을 자동으로 찾아 404로 응답시키는 코드가 아닙니다.** 실제 조건 검사와 `raise`가 필요합니다.

입력 오류 응답의 `detail`은 보통 오류 목록입니다. 테스트의 다음 코드는 첫 오류가 어디에서 생겼는지 확인합니다.

```python
assert response.json()["detail"][0]["loc"] == ["body", "quantity"]
```

`["path", "product_id"]`라면 경로 변수, `["query", "qty"]`라면 쿼리 변수 문제입니다. 입력이 여러 군데 틀리면 오류도 여러 개일 수 있습니다.

## 7. 응답 모델 — 저장된 모든 정보를 공개하지 않기

근거: [6차시 main.py](lesson_06_response_contract/main.py), [solution.py](lesson_06_response_contract/solution.py).

서버 내부에 다음 정보가 있다고 가정합니다.

```python
record = {"id": 1, "name": "Min", "internal_note": "staff only"}
```

밖으로는 id와 name만 내보내기로 했다면 **응답 전용 모델**을 정의합니다.

```python
class ProfileOut(BaseModel):
    id: int
    name: str

@app.get("/profiles/{profile_id}", response_model=ProfileOut)
def read_profile(profile_id: Annotated[int, Path(ge=1)]):
    # 실제 파일에는 존재 여부 검사도 있다.
    return profiles[profile_id]
```

이때 응답은 다음처럼 공개 모델에 맞춰 나갑니다.

```json
{"id": 1, "name": "Min"}
```

현재 학생 `main.py`는 `ProfileOut`에 `internal_note`도 넣어 두었으므로 내부 메모가 노출됩니다. `solution.py`는 **저장소의 메모는 유지하고 공개 모델에서만 제외**합니다.

| 구분 | 담당 |
| --- | --- |
| 입력 모델 `OrderIn` | 사용자가 보내도 되는 값 |
| 내부 저장 데이터 | 서버가 업무를 위해 보관하는 값 |
| 출력 모델 `ProfileOut` | 외부에 공개해도 되는 값 |

이름의 `In`·`Out`은 역할을 알리는 관례입니다. 이름만 붙여 자동으로 보안 처리가 되는 것은 아닙니다. 특히 응답 필터링은 `response_model=ProfileOut`으로 실제 연결해야 합니다. **잘못 설계한 공개 모델도 그대로 적용될 수 있으므로 응답의 정확한 키까지 테스트**합니다.

## 8. 한 번의 요청에서 여러 요청의 흐름으로

### 8-1. app.state는 서버가 기억하는 임시 메모리

근거: [7차시 main.py](lesson_07_state_scenarios/main.py), [solution.py](lesson_07_state_scenarios/solution.py).

```python
app.state.tasks = {}
```

`app.state`는 앱 객체에 공유 상태를 보관하는 공간입니다. 이 예제의 `tasks`는 **Python 딕셔너리이며 DB가 아닙니다.** 같은 프로세스에서 이어지는 요청은 값을 공유하지만, 서버 재시작 시 초기화되고 worker가 여러 개면 프로세스마다 별도 상태를 가집니다.

현재 학생 코드는 항상 같은 ID를 사용합니다.

```python
task_id = 1
app.state.tasks[task_id] = task
```

딕셔너리의 같은 키에 다시 대입하면 추가가 아니라 덮어쓰기가 됩니다.

```python
tasks = {}
tasks[1] = {"id": 1, "title": "read"}
tasks[1] = {"id": 1, "title": "write"}
# read가 사라지고 1번에는 write만 남는다.
```

정답에서는 다음과 같이 다음 ID를 만듭니다.

```python
task_id = max(app.state.tasks, default=0) + 1
```

| 상태 | 계산 | 새 ID |
| --- | --- | --- |
| 빈 딕셔너리 | 기본값 0 + 1 | 1 |
| 키가 1 | 최대 키 1 + 1 | 2 |
| 키가 1, 2 | 최대 키 2 + 1 | 3 |

`max(딕셔너리)`는 여기서 키의 최댓값을 구합니다. `default=0`은 데이터가 비어 있을 때 사용합니다. 이 방식은 단일 프로세스 수업 예제이며 동시 요청·영구 ID 발급을 해결하는 운영 DB 방식은 아닙니다.

### 8-2. 생성만 하지 말고 다시 조회하기

```text
첫 번째 작업 생성 → 첫 번째 ID 저장
두 번째 작업 생성 → 두 번째 ID 저장
첫 번째 ID 조회 → 첫 번째 제목이 그대로인가?
두 번째 ID 조회 → 두 번째 제목이 맞는가?
두 ID가 서로 다른가?
```

두 생성 요청이 모두 201이어도 기존 데이터를 덮어썼을 수 있습니다. **만들었다고 응답한 데이터가 나중에도 맞게 조회되는지 확인**해야 합니다. 제목이 같아도 서로 다른 두 생성 요청에는 별도 ID가 필요합니다.

### 8-3. 테스트는 서로 독립적이어야 한다

```python
@pytest.fixture(autouse=True)
def clean_tasks():
    app.state.tasks.clear()
    yield
    app.state.tasks.clear()
```

`fixture`는 테스트 준비·정리를 담당합니다. 이 예제에서 `yield` 앞은 테스트 전, 뒤는 테스트 후에 실행됩니다. `autouse=True`라 테스트 함수가 직접 요청하지 않아도 해당 범위의 테스트에 적용됩니다.

테스트 A가 만든 작업이 테스트 B의 기대 ID를 바꾸지 않게 **테스트 사이의 상태를 초기화**합니다. 다만 “한 테스트 안의 여러 요청”은 시나리오를 확인하려고 상태를 유지합니다.

## 9. 종합 핵심 — 실패한 요청은 상태를 망가뜨리면 안 된다

근거: [8차시 main.py](lesson_08_final_verification/main.py), [solution.py](lesson_08_final_verification/solution.py), [테스트](lesson_08_final_verification/test_api.py).

전체 좌석은 4석입니다. 계약은 다음과 같습니다.

- `name`: 1~20자, `seats`: 엄격한 정수 1~4.
- 성공하면 201, 예약 저장과 잔여 좌석 감소.
- 잔여 좌석이 부족하면 409, **예약과 잔여 좌석은 그대로**.
- 예약 조회 성공은 200, 없는 예약은 404.

### 9-1. 잘못된 처리 순서

```python
app.state.remaining -= body.seats
if app.state.remaining < 0:
    raise HTTPException(status_code=409, detail="Not enough seats")
```

먼저 차감한 뒤 거절하면 이미 메모리가 바뀌어 있습니다. **HTTPException을 발생시켜도 딕셔너리나 숫자 변경이 자동으로 원복되지 않습니다.**

| 요청 순서 | 올바른 상태 | 현재 학생 코드의 상태 |
| --- | --- | --- |
| 시작 | 잔여 4 | 잔여 4 |
| A가 3석 예약 | 201, 잔여 1 | 201, 잔여 1 |
| B가 2석 요청 | 409, **잔여 1 유지** | 409지만 **잔여 -1** |
| C가 1석 요청 | 201, 잔여 0 | 잘못된 상태 때문에 다시 409 |

B의 상태 코드만 보면 오류를 놓칩니다. B 이후의 C까지 확인해야 원인을 볼 수 있습니다.

### 9-2. 올바른 처리 순서

```python
if body.seats > app.state.remaining:
    raise HTTPException(status_code=409, detail="Not enough seats")

app.state.remaining -= body.seats
# 이 뒤에서 예약 ID를 만들고 예약 데이터를 저장한다.
```

> 바꿔도 되는지 먼저 확인하고, 성공할 요청에 대해서만 상태를 바꾼다.

`Field(le=4)`와 잔여 좌석 검사도 다릅니다. 2석은 입력 허용 범위 1~4 안이라 422 대상이 아닙니다. 하지만 잔여가 1석이면 업무 상태상 불가능하므로 409입니다.

이 코드는 수업의 순차 요청을 바로잡은 예제입니다. 여러 worker나 동시 예약을 안전하게 처리하는 DB 트랜잭션까지 구현한 것은 아닙니다.

### 9-3. 생성 응답과 조회 응답의 차이

생성 응답에는 생성 당시의 잔여 좌석 `remaining`이 포함됩니다.

```json
{"id": 1, "name": "A", "seats": 3, "remaining": 1}
```

조회 응답에는 저장된 예약 정보만 있습니다.

```json
{"id": 1, "name": "A", "seats": 3}
```

같은 예약이라도 요청 종류별 계약이 다를 수 있습니다. “항상 모든 필드를 반환하겠지”라고 가정하지 말고 응답 구조를 확인합니다.

## 10. AI에게 물어볼 때도 검증의 순서가 있다

근거: [4차시 CODEX_PROMPTS.md](lesson_04_ai_test_cases/CODEX_PROMPTS.md), 각 차시의 같은 이름 파일.

```text
요구사항으로 테스트표 작성 → 현재 동작 재현 → 원인 분석
→ 최소 수정 → 같은 테스트 재실행 → 실제 결과와 한계 기록
```

AI에게 “고쳐줘”만 말하기보다 다음 정보를 함께 줍니다.

```text
day8/lesson_04_ai_test_cases의 README, main.py, test_api.py를 읽어줘.
계약은 10,000원 이상이면 1,000원 할인이고, 현재 10,000원에서 실패해.
먼저 원인을 설명하고, 기대값은 현재 코드가 아니라 계약에서 구해줘.
정상값·경계값·잘못된 타입·누락을 테스트표로 정리해줘.
새 라이브러리나 API는 추가하지 말고 최소 수정해줘.
수정 후 같은 테스트를 실행하고, 실제 결과와 미검증 항목을 구분해줘.
```

**초록색 테스트도 기대값이 틀리면 근거가 약합니다.** `test_seed.py`처럼 범위가 부족할 수도 있습니다. 테스트 통과는 검사한 사례의 근거이며, 모든 버그가 없다는 보장은 아닙니다.

수업의 `VERIFICATION.md`는 제작자가 기록한 과거 실행 결과입니다. 현재 내 `main.py`를 실행한 결과와는 구분해야 합니다. README가 “시작 코드가 실패한다”고 해도 내가 이미 수정했다면 통과할 수 있습니다.

## 11. 이 대화에서 질문했던 Git 개념 복습

아래는 직접 질문했던 흐름에 맞춘 설명입니다. 명령은 개념 복습용 예시이며, 현재 브랜치·커밋 상태를 확인하지 않고 한꺼번에 실행하는 절차가 아닙니다.

### 11-1. 저장·add·commit·push는 서로 다르다

```text
파일 편집·저장 → git add → git commit → git push
  작업 폴더       스테이징    로컬 이력      GitHub 반영
```

| 질문 | 답 |
| --- | --- |
| `git status --short`에서 `?? day8/`은? | 아직 Git이 추적하지 않는 새 파일·폴더가 있다는 뜻 |
| `git add day8`은? | day8 폴더의 변경을 다음 커밋 후보인 스테이징 영역에 반영 |
| add만 하면 GitHub에 올라가나? | 아니요. commit 후 push해야 함 |
| `git diff --cached --name-status`는? | 마지막 커밋과 비교해 지금 스테이징한 변경의 종류·경로를 표시 |
| 목록 앞의 A·M·D는? | 추가 Added·수정 Modified·삭제 Deleted |
| 긴 목록 아래 `:`가 나오면? | 보통 pager 화면. 영문 `q`로 종료. 변경 내용은 유지 |

```sh
# pager 없이 다음 커밋에 들어갈 파일 목록 확인
git --no-pager diff --cached --name-status
```

**`git add day1-day8`은 day1~day8 전체를 의미하지 않습니다.** 이름이 정확히 `day1-day8`인 폴더만 대상으로 합니다. 다른 변경을 이미 스테이징했다면 그것이 자동으로 취소되는 것도 아닙니다. 커밋 전 전체 스테이징 목록을 확인하세요.

### 11-2. 왜 study/day8에도 기존 day1~day7이 보였을까?

브랜치는 특정 커밋을 가리키는 이름표입니다. 기존 main에서 브랜치를 만들면 그 커밋의 파일과 이력을 이어받으므로 수업 폴더들이 함께 보입니다. **브랜치 이름이 study/day8이라고 day8 폴더만 들어가는 것은 아닙니다.**

이것은 기존 커밋을 공유하는 것이므로 브랜치 수만큼 모든 파일을 각각 복사해 저장하지 않습니다. 수정·새 파일의 커밋에는 추가 데이터가 필요하지만, 브랜치 생성 자체의 정보는 작습니다.

“로컬 파일에서 가져왔나, GitHub main에서 가져왔나?”는 시작한 커밋에 달렸습니다. 로컬 main에서 만들었다면 로컬 main의 커밋을 기준으로 합니다. 그 main이 GitHub와 동기화돼 있었다면 내용도 같은 것입니다.

### 11-3. 다른 폴더의 로컬 수정도 push될까?

**커밋하지 않은 로컬 수정은 push되지 않습니다.** day1~day7을 편집했어도 스테이징·커밋하지 않았다면 GitHub 브랜치에는 기존 커밋의 내용이 보입니다. 단, 이전에 해당 변경을 커밋했다면 그 커밋도 브랜치 이력에 포함될 수 있습니다.

Push는 “지금 선택한 폴더”를 전송하는 명령이 아니라 브랜치의 커밋을 원격으로 반영하는 명령입니다.

```sh
git push -u origin study/day8
```

| 부분 | 뜻 |
| --- | --- |
| `origin` | 원격 저장소에 붙인 이름 |
| `study/day8` | 전송할 로컬 브랜치 |
| `-u` | 로컬 브랜치의 upstream 연결을 기억 |

일반적인 설정에서 이후 해당 브랜치의 `git push`만으로 같은 원격 브랜치에 올릴 수 있습니다. 이 명령이 main에 merge하는 것은 아닙니다.

### 11-4. fetch를 했는데 아무것도 출력되지 않으면?

```sh
git fetch origin
```

원격 커밋과 브랜치 정보를 가져와 `origin/main` 같은 원격 추적 정보를 갱신합니다. **현재 작업 파일이나 로컬 main에 자동으로 합치지는 않습니다.**

새로 가져올 정보가 없으면 아무 출력 없이 정상 종료될 수 있습니다. 출력이 궁금하면 `git fetch origin --verbose`를 사용합니다. 오류 메시지가 있다면 별도로 확인합니다.

```sh
git diff --name-status origin/main...study/day8
```

이 비교는 **두 커밋의 공통 조상부터 로컬 study/day8까지의 커밋된 변경**을 봅니다. `A day1-day8/main.py`만 나온다면 해당 파일이 그 분기 이후 새로 추가됐다는 뜻입니다. `...`는 main의 최신 파일과 단순히 일대일 비교하는 `..` 방식과 구분합니다. 커밋하지 않은 작업 파일은 이 비교에 포함되지 않습니다.

### 11-5. merge한 다음에도 push해야 할까?

네. 로컬 merge와 GitHub 반영은 별개입니다. 작업이 커밋돼 있고 main을 최신화할 수 있는 상태라는 전제의 예시입니다.

```sh
git switch main
git pull --ff-only origin main
git merge study/day8
git push origin main
```

| 명령 | 뜻 |
| --- | --- |
| `switch main` | 합칠 대상인 main으로 이동 |
| `pull --ff-only origin main` | 원격 main을 가져와 fast-forward 가능한 경우에만 현재 브랜치 갱신 |
| `merge study/day8` | 현재 브랜치 main에 작업 브랜치의 변경을 합침 |
| `push origin main` | 합친 로컬 main을 GitHub main에도 반영 |

`Already up to date.`는 현재 브랜치가 가져온 내용을 이미 포함한다는 뜻입니다. **내가 main에 있는지까지 그 메시지가 확인해 주는 것은 아니므로** `git branch --show-current`로 함께 봅니다. `--ff-only`가 중단되거나 충돌이 나면 다음 명령을 계속 실행하지 말고 원인을 확인합니다.

### 11-6. 브랜치에서 day1~day7을 지우면 main에는 어떻게 될까?

삭제를 커밋하고 merge하면 **그 삭제도 main에 반영될 수 있습니다.** main에서 같은 파일을 수정했다면 수정·삭제 충돌이 날 수도 있습니다.

방명록 폴더만 추가하고 싶다면 기존 수업 폴더를 지울 필요가 없습니다. main과 공유하던 폴더를 건드리지 않고 새 폴더의 변경만 커밋했다면, merge 시 기존 자료는 유지되고 새 변경만 반영됩니다. merge는 폴더 선택 도구가 아니라 커밋 이력을 합치는 동작입니다.

### 11-7. 작업 브랜치를 삭제해도 main의 파일은 남을까?

main에 제대로 합쳐졌다면 남습니다. 브랜치 이름표를 없애는 것과 main이 참조하는 커밋·파일을 삭제하는 것은 다릅니다.

```sh
git switch main
git branch -d study/day8
git push origin --delete study/day8
```

두 번째는 로컬 브랜치, 세 번째는 원격 브랜치 삭제입니다. 현재 사용 중인 브랜치는 삭제할 수 없습니다. `-d`가 병합되지 않았다고 거절하면 이유를 확인하고, 바로 강제 삭제하지 않습니다. 배포 서비스가 아직 그 브랜치를 사용한다면 먼저 배포 대상도 바꿔야 합니다.

### 11-8. main.py·main 브랜치·배포 폴더는 서로 다르다

| 이름 | 의미 |
| --- | --- |
| `main.py` | Python 소스 파일 이름 |
| Git의 `main` | 커밋을 가리키는 브랜치 이름 |
| `main:app` | main 모듈의 app 객체를 서버에서 실행하라는 지정 |
| 배포의 Branch | 어떤 Git 브랜치의 코드를 받을지 |
| 배포의 Root Directory | 그 저장소 안에서 어떤 폴더를 앱 기준으로 삼을지 |

이 대화의 방명록 예에서는 **Branch가 main, Root Directory는 day1-day8**이었습니다. 브랜치를 main으로 바꾼다고 폴더 경로까지 main으로 바꾸는 것이 아닙니다. day8의 개별 학습 API와 방명록 앱도 서로 다른 앱입니다.

로컬 파일 수정 → Commit → Push → 호스팅의 새 버전 배포 → 브라우저 확인 순서가 모두 연결돼야 공개 화면이 바뀝니다. “로컬에 최신 코드가 있다”, “GitHub에 올라갔다”, “그 커밋이 실제 Live로 배포됐다”는 각각 다른 확인입니다.

## 12. 꼭 기억할 내용 12개

| 기억할 것 | 한 줄 설명 |
| --- | --- |
| API의 정답은 계약 | 현재 구현의 결과를 무조건 정답으로 쓰지 않기 |
| 문서와 실행은 별개 | Swagger·OpenAPI·실제 HTTP 응답을 구분 |
| include_in_schema는 문서 표시 | 접근 권한 설정이 아님 |
| 입력 위치 구분 | Path는 경로, Query는 ? 뒤, Body는 본문 |
| 타입·범위·필수 여부는 각각 규칙 | `int`, `ge/le`, 기본값 유무를 따로 읽기 |
| strict=True | 편리한 타입 변환을 제한해 잘못된 입력 거절 |
| 경계값 | 기준 바로 아래·기준·바로 위를 검사 |
| 상태 코드와 본문 모두 검사 | 200이어도 업무 결과가 틀릴 수 있음 |
| 예외를 성공으로 숨기지 않기 | 넓은 except가 HTTPException도 잡을 수 있음 |
| 공개 모델 최소화 | 내부 데이터와 외부 응답을 분리 |
| 검사 후 상태 변경 | 실패 요청이 데이터를 망가뜨리지 않게 하기 |
| add·commit·push·merge 구분 | 스테이징·로컬 이력·원격 반영·이력 합치기는 다른 동작 |

## 13. 스스로 확인하기

먼저 답을 가리고 설명해 보세요.

1. `include_in_schema=False`로 바꾸면 `/greet` 호출도 막힐까요?
2. `qty=0`을 보내면 기본값 1을 쓰나요?
3. `quantity: int`에 `strict=True`가 있을 때 JSON의 `"2"`를 받아도 될까요?
4. 없는 상품 99와 잘못된 번호 abc는 왜 다른 상태 코드일까요?
5. 5,000원과 20,000원 테스트만으로 할인 기능 검증이 충분할까요?
6. `responses={404: ...}`만 쓰면 없는 상품을 자동으로 처리할까요?
7. 서버 내부 딕셔너리에 `internal_note`가 있으면 반드시 응답에도 나와야 할까요?
8. 생성 요청 두 번이 모두 201이면 기존 데이터 보존도 증명될까요?
9. 좌석을 차감한 뒤 HTTPException을 발생시키면 차감도 취소될까요?
10. `git add day8` 후 push만 하면 방금 변경이 전송될까요?

<details>
<summary>답과 이유 보기</summary>

1. 아닙니다. 문서에서만 제외합니다.
2. 아닙니다. 생략한 경우만 기본값을 쓰고 0은 범위 위반으로 422입니다.
3. 안 됩니다. 문자열 숫자는 엄격한 정수가 아닙니다.
4. 99는 유효한 번호 형식이지만 자원이 없어 404, abc는 입력 형식이 틀려 422입니다.
5. 부족합니다. 10,000원과 그 앞뒤 경계값을 검사해야 합니다.
6. 아닙니다. 실제 검사·raise와 별개의 문서 설명입니다.
7. 아닙니다. 공개 모델에 없는 필드는 응답 모델을 통해 제외할 수 있습니다.
8. 아닙니다. ID가 다르고 각 ID 조회 결과가 올바른지도 확인합니다.
9. 아닙니다. 메모리 변경은 자동으로 되돌아가지 않습니다.
10. 아닙니다. 변경 내용을 커밋해야 push할 수 있습니다.

</details>

## 14. 현재 파일을 직접 확인한 결과

2026-10-29에 각 차시를 **별도 임시 폴더**로 복사하고 `main.py + test_api.py`를 실행했습니다. 정답 검증은 다른 임시 폴더에서 `solution.py`를 `main.py`라는 이름으로 복사해 같은 테스트를 실행했습니다. 원본 소스·주석·테스트는 수정하지 않았습니다.

환경: Python 3.11.4, FastAPI 0.115.12, Pydantic 2.11.5, httpx 0.28.1, pytest 8.3.5. 기존 Anaconda Python 환경을 사용했으며 패키지를 새로 설치하지 않았습니다. 이전 작업 때 사용한 프로젝트 루트 `.venv`는 이번 확인 시 없었으므로 그 환경에서 실행했다고 기록하지 않았습니다.

| 차시 | 현재 main.py | solution.py를 적용한 임시 복사본 | 핵심 차이 |
| --- | --- | --- | --- |
| 01 | 4 통과 | 4 통과 | 현재 main은 이미 문서 포함 True |
| 02 | 9 통과 | 9 통과 | 현재 기본 수량 1 |
| 03 | 13 통과 | 13 통과 | 현재 최소 수량 1 |
| 04 | 10 통과·1 실패 | 11 통과 | 10,000원에서 `>`와 `>=` 차이 |
| 05 | 6 통과·1 실패 | 7 통과 | 넓은 except가 404를 200으로 변경 |
| 06 | 2 통과·2 실패 | 4 통과 | 내부 메모가 응답·명세에 포함 |
| 07 | 7 통과·2 실패 | 9 통과 | 작업 ID가 항상 1 |
| 08 | 13 통과·2 실패 | 15 통과 | 실패 요청이 좌석 수를 변경 |

`test_api.py` 기준으로 현재 코드에는 총 **64 통과·8 실패**, 정답 복사본은 **72 통과**입니다. 4차시의 `test_seed.py`는 이번 실행 수에 포함하지 않았습니다. 4~8차시의 실패는 문서에서 설명한 실습용 결함을 확인한 결과이며, 이번 요청에서 이를 수정한 것은 아닙니다.

각 실행에 기존 Starlette/AnyIO의 `BlockingPortal` 관련 폐기 예정 경고가 1건씩 있었고 위 assertion 실패와는 별개입니다. 검증은 TestClient 기준이며, 이번에는 Uvicorn 실제 네트워크 서버·Swagger 브라우저 클릭·원격 배포·동시 요청은 검증하지 않았습니다.

### 원본으로 돌아가서 더 보기

| 더 보고 싶은 내용 | 파일 |
| --- | --- |
| 운영체제별 환경·서버 명령 주석 | [day8.py](day8.py) |
| API 문서와 실제 호출 | [1차시 README](lesson_01_swagger/README.md) |
| 입력 위치·기본값·범위 | [2차시 코드](lesson_02_parameters/main.py) |
| 본문 모델과 엄격한 검증 | [3차시 테스트](lesson_03_body_validation/test_api.py) |
| 경계값과 AI 검토 요청 예시 | [4차시 프롬프트](lesson_04_ai_test_cases/CODEX_PROMPTS.md) |
| 오류를 숨기는 코드와 수정 비교 | [5차시 정답](lesson_05_errors/solution.py) |
| 출력 필드 제한 | [6차시 정답](lesson_06_response_contract/solution.py) |
| 두 번 생성·두 번 조회 | [7차시 테스트](lesson_07_state_scenarios/test_api.py) |
| 실패 후 다시 성공하는 예약 | [8차시 테스트](lesson_08_final_verification/test_api.py) |
