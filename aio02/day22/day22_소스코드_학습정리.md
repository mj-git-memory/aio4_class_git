# day22 LangChain 소스코드 학습 정리

`LangChain_20261117_DataEdition`은 상품 정보를 근거로 고객 문의에 답하는 AI 프로그램을 단계별로 만드는 프로젝트다. 상품 JSON을 읽고, 입력을 검증하고, 프롬프트와 모델을 연결한 뒤, 여러 요청의 처리 결과를 파일로 저장한다.

분석 기준일: 2026년 11월 22일. 아래 설명은 당시 작업 폴더의 코드를 기준으로 한다. 긴 상품 설명은 일부 생략하며, 단순화한 데이터와 가상의 실제 모델 답변은 예시임을 표시한다.

## 목차

1. [패키지 모듈 함수 클래스 객체](#1-패키지-모듈-함수-클래스-객체)
2. [프로젝트 구조와 차시별 역할](#2-프로젝트-구조와-차시별-역할)
3. [주요 패키지와 표준 라이브러리](#3-주요-패키지와-표준-라이브러리)
4. [예시 데이터와 전체 자료형 흐름](#4-예시-데이터와-전체-자료형-흐름)
5. [catalog 상품 데이터 처리](#5-catalog-상품-데이터-처리)
6. [cli 명령줄 옵션](#6-cli-명령줄-옵션)
7. [config 환경변수와 Settings](#7-config-환경변수와-settings)
8. [prompts 채팅 프롬프트](#8-prompts-채팅-프롬프트)
9. [providers 모델 생성과 오류 안내](#9-providers-모델-생성과-오류-안내)
10. [pipeline 전처리와 체인](#10-pipeline-전처리와-체인)
11. [invoke batch stream](#11-invoke-batch-stream)
12. [s01부터 s06까지](#12-s01부터-s06까지)
13. [s07 프롬프트 비교](#13-s07-프롬프트-비교)
14. [s08 CSV 문의와 JSONL](#14-s08-csv-문의와-jsonl)
15. [report 보고서 저장](#15-report-보고서-저장)
16. [fetch_products 상품 수집](#16-fetch_products-상품-수집)
17. [주요 파이썬 문법](#17-주요-파이썬-문법)
18. [기억할 개념과 재사용 예제](#18-기억할-개념과-재사용-예제)
19. [검증 범위](#19-검증-범위)

## 1 패키지 모듈 함수 클래스 객체

| 용어 | 정의 | 이 프로젝트의 예 |
|---|---|---|
| 패키지 | 여러 모듈을 묶은 단위 | `app`, `sessions`, `langchain_core` |
| 모듈 | 파이썬 코드 파일 | `catalog.py`, `pipeline.py` |
| 함수 | 특정 작업을 수행하는 코드 묶음 | `read_catalog()` |
| 클래스 | 객체의 데이터와 동작을 정의하는 틀 | `Settings`, `ChatPromptTemplate` |
| 객체 또는 인스턴스 | 클래스로 만든 실제 값 | `settings`, `prompt`, `model` |
| 메서드 | 클래스나 객체에 속한 함수 | `prompt.invoke()`, `path.read_text()` |

```python
from app.catalog import read_catalog

records = read_catalog()
```

`app` 패키지의 `catalog` 모듈에서 `read_catalog` 함수를 가져와 실행하고, 반환값을 `records`에 저장한다.

```python
settings = Settings(provider="mock", model="local-fixture")
```

`Settings`는 클래스이고, `settings`는 그 클래스로 만든 객체다.

### 반환과 화면 출력

```python
def add(a, b):
    return a + b

result = add(2, 3)
```

`result`는 `5`지만 화면에는 아무것도 나오지 않는다. `print(result)`를 해야 화면에 `5`가 표시된다. 이 문서에서 함수의 출력 형태는 주로 **반환값**을 뜻한다.

### 모듈 실행

프로젝트 폴더에서 실행한다.

```bash
python -m sessions.s02
```

`-m` 뒤에는 파일 경로가 아니라 모듈 이름을 쓴다. `/`, `:`, `.py` 대신 `sessions.s02`처럼 점으로 구분한다.

```python
if __name__ == "__main__":
    main()
```

직접 실행되는 시작 모듈이면 `main()`을 호출하고, 다른 모듈에서 import할 때는 이 조건 아래의 코드를 실행하지 않는다.

## 2 프로젝트 구조와 차시별 역할

```text
LangChain_20261117_DataEdition/
├── app/
│   ├── catalog.py         상품 파일 읽기·검증·조회
│   ├── cli.py             공통 실행 옵션
│   ├── config.py          환경변수·모델 설정
│   ├── prompts.py         프롬프트 템플릿
│   ├── providers.py       모델 생성·오류 안내
│   ├── pipeline.py        입력 준비·체인 구성
│   ├── report.py          JSON·HTML 보고서
│   └── fetch_products.py  상품 데이터 수집·가져오기
├── sessions/
│   └── s01.py ~ s08.py    차시별 실행 프로그램
├── data/
│   ├── products_public_derived.json
│   ├── dataset_source.json
│   ├── requests.csv
│   └── requests_with_error.csv
├── tests/
│   └── test_project.py
├── reports/              실행 보고서
└── requirements.txt      외부 패키지 목록
```

`app`은 재사용할 기능을 제공하고, `sessions`는 그 기능을 조합해 실행한다.

| 파일 | 구현 내용 | 결과 |
|---|---|---|
| `s01.py` | 환경·상품 데이터 확인 | 상품 목록·출처 |
| `s02.py` | 메시지 템플릿 | system·human 메시지 |
| `s03.py` | 프롬프트 3종 | weak·role·designed 메시지 |
| `s04.py` | 수동 실행과 LCEL | 모델 답변 |
| `s05.py` | 전처리·입력 검증 | 성공·오류 결과 |
| `s06.py` | 배치·스트리밍 | 여러 답변 또는 답변 조각 |
| `s07.py` | 비교 조건과 실행 기록 | 버전·해시·시간 |
| `s08.py` | CSV 문의 처리 | JSONL·보고서 |

## 3 주요 패키지와 표준 라이브러리

| 구분 | 패키지 또는 모듈 | 사용하는 기능 |
|---|---|---|
| 외부 | `langchain-core` | 프롬프트·Runnable·체인·출력 파서 |
| 외부 | `langchain-openai` | `ChatOpenAI` |
| 외부 | `langchain-groq` | `ChatGroq`, 선택 공급자 |
| 외부 | `python-dotenv` | `.env` 읽기 |
| 외부 | `pytest` | 테스트 |
| 표준 | `pathlib` | 파일·폴더 경로 |
| 표준 | `json` | JSON 변환 |
| 표준 | `csv` | CSV 읽기 |
| 표준 | `argparse` | 명령줄 옵션 |
| 표준 | `dataclasses` | 데이터 보관용 클래스 |
| 표준 | `os` | 환경변수 조회 |
| 표준 | `hashlib` | SHA-256 해시 |
| 표준 | `time` | 경과 시간 측정 |
| 표준 | `datetime` | 실행 시각 |
| 표준 | `html` | HTML 문자 이스케이프 |
| 표준 | `urllib.request` | HTTP 요청 |
| 표준 | `importlib.metadata` | 설치된 패키지 버전 |

`requirements.txt`에 지정된 버전:

```text
langchain-core==1.8.1
langchain-openai==1.8.0
python-dotenv==1.2.4
```

설치 이름과 import 이름은 다를 수 있다.

```bash
python -m pip install python-dotenv
```

```python
from dotenv import load_dotenv
```

소스에서는 `langchain_core`, 설치 목록에서는 `langchain-core`를 사용한다.

## 4 예시 데이터와 전체 자료형 흐름

포함된 상품 파일에는 상품 20개가 있다. 실제 첫 상품은 15인치 노트북 수납 설명이 있는 Fjallraven 가방이다. 다음은 구조를 설명하기 위해 단순화한 상품이다.

```python
raw_product = {
    "title": "노트북 가방",
    "price": 1090,
    "description": "최대 15인치 노트북을 수납할 수 있습니다.",
    "category": "가방",
    "image": "https://example.com/bag.jpg"
}
```

고객 요청은 다음과 같다.

```python
request = {
    "record_id": "row-001",
    "question": "15인치 노트북을 넣을 수 있나요? 반품도 가능한가요?"
}
```

체인을 통과하는 자료형:

```text
request: dict
  {record_id, question}
        ↓ prepare_input
values: dict
  {context: str, question: str}
        ↓ ChatPromptTemplate
ChatPromptValue
        ↓ 모델의 일반 호출
AIMessage
        ↓ StrOutputParser
answer: str
```

## 5 catalog 상품 데이터 처리

소스: [catalog.py](LangChain_20261117_DataEdition/app/catalog.py)

| 함수 | 기능 | 반환 형태 |
|---|---|---|
| `read_catalog()` | 읽기·검증·정리 | `list[dict]` |
| `find_product()` | ID로 상품 조회 | `dict` |
| `product_context()` | 프롬프트용 상품 정보 구성 | `str` |
| `data_info()` | 출처·파일명·해시 | `dict` |

### read_catalog

핵심 코드:

```python
path = Path(path)
data = json.loads(path.read_text(encoding="utf-8-sig"))
```

`read_text()`는 파일을 문자열로 읽는다. `utf-8-sig`는 UTF-8 BOM이 있는 파일도 처리한다. `json.loads()`는 JSON 문자열을 파이썬 자료형으로 바꾼다.

```python
text = '[{"title": "가방"}]'
data = json.loads(text)
# [{"title": "가방"}]
```

함수는 다음을 검사한다.

- 전체 데이터가 비어 있지 않은 리스트인지
- 상품 수가 1,000개 이하인지
- 각 상품이 딕셔너리인지
- `title`, `category`, `description`이 비어 있지 않은 문자열인지
- 생성된 상품 ID가 중복되지 않는지

상품을 정리하는 코드:

```python
for index, row in enumerate(data, 1):
    record_id = (
        "api-" + str(row["id"])
        if "id" in row
        else f"row-{index:03d}"
    )

    records.append({
        "record_id": record_id,
        "source_row": index,
        "raw": row,
        "title": row["title"].strip(),
        "category": row["category"].strip(),
        "description": row["description"].strip()
    })
```

단순화한 상품을 읽은 반환값:

```python
records = [
    {
        "record_id": "row-001",
        "source_row": 1,
        "raw": raw_product,
        "title": "노트북 가방",
        "category": "가방",
        "description": "최대 15인치 노트북을 수납할 수 있습니다."
    }
]
```

`raw`는 원본을 보관한다. 바깥의 문자열은 앞뒤 공백을 제거한 값이다.

```python
records[0]                 # 첫 상품 딕셔너리
records[0]["record_id"]    # "row-001"
records[0]["raw"]["price"] # 1090
```

주요 문법:

```python
for index, value in enumerate(["가방", "재킷"], 1):
    print(index, value)
```

출력:

```text
1 가방
2 재킷
```

```python
f"row-{1:03d}"        # "row-001"
"  가방  ".strip()    # "가방"
```

원본에 `id`가 있으면 `api-3` 같은 ID를 사용하고, 없으면 원본 순서에 따라 `row-003`을 사용한다. 데이터 파일을 바꾸면 ID 체계도 달라질 수 있다.

중복 검사:

```python
ids = [x["record_id"] for x in records]
if len(ids) != len(set(ids)):
    raise ValueError("record_id가 중복됩니다.")
```

`set()`이 중복을 제거하므로 원본 개수와 집합 개수가 다르면 중복이 있다는 뜻이다.

### find_product

```python
def find_product(records, record_id):
    for row in records:
        if row["record_id"] == record_id:
            return row
    raise ValueError("상품을 찾지 못했습니다: " + str(record_id))
```

```python
product = find_product(records, "row-001")
# 해당 상품 dict

find_product(records, "row-999")
# ValueError: 상품을 찾지 못했습니다: row-999
```

### product_context

```python
def product_context(product):
    fields = {
        k: product[k]
        for k in ("record_id", "title", "category", "description")
    }
    return json.dumps(fields, ensure_ascii=False, indent=2)
```

딕셔너리 컴프리헨션으로 필요한 네 필드만 고른다. `json.dumps()`는 이를 JSON 형식의 문자열로 만든다.

```python
context = product_context(product)
print(context)
```

단순화한 예시 출력:

```json
{
  "record_id": "row-001",
  "title": "노트북 가방",
  "category": "가방",
  "description": "최대 15인치 노트북을 수납할 수 있습니다."
}
```

위 모양으로 출력돼도 `context`는 딕셔너리가 아니라 문자열이다.

```python
isinstance(context, str)  # True
```

- `ensure_ascii=False`: 한글을 그대로 표현한다.
- `indent=2`: 두 칸 들여쓰기를 적용한다.
- `price`, `image`는 모델 맥락에서 제외한다.

```python
json.loads('{"title": "가방"}')
# 문자열 → dict

json.dumps({"title": "가방"}, ensure_ascii=False)
# dict → 문자열
```

### data_info

기본 데이터는 `data/dataset_source.json`을 읽는다. 다른 데이터 파일은 `.source.json` 확장자의 대응 파일을 확인한다. 메타데이터가 없으면 미확인 로컬 파일로 표시한다.

```python
Path("products.json").with_suffix(".source.json")
# Path("products.source.json")
```

반환값은 출처 정보에 파일명과 해시를 합친 딕셔너리다.

```python
{
    "acquisition": "public_derived_file",
    # 그 밖의 출처 정보
    "file": "products_public_derived.json",
    "sha256": "64자리 해시 문자열"
}
```

해시 생성:

```python
hashlib.sha256(path.read_bytes()).hexdigest()
```

파일 바이트로 SHA-256 해시를 만든다. 같은 데이터를 사용했는지 추적하는 용도이며, 데이터의 정확성을 판정하는 점수는 아니다.

## 6 cli 명령줄 옵션

소스: [cli.py](LangChain_20261117_DataEdition/app/cli.py)

```python
def parser():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    p.add_argument("--mock", action="store_true")
    return p
```

`parser()`는 옵션을 정의한 파서 객체를 반환한다. 실제 명령줄을 읽는 메서드는 `parse_args()`다.

```python
args = parser().parse_args()
```

```bash
python -m sessions.s05 --mock --data data/products_public_derived.json
```

개념적인 파싱 결과:

```python
Namespace(
    data=Path("data/products_public_derived.json"),
    mock=True
)
```

`args`는 딕셔너리가 아니라 Namespace 객체이므로 `args.data`, `args.mock`으로 접근한다.

| 문법 | 의미 |
|---|---|
| `type=Path` | 경로 객체로 변환 |
| `type=int` | 정수로 변환 |
| `default=3` | 생략 시 기본값 |
| `action="store_true"` | 옵션이 있으면 True, 없으면 False |
| `choices=[1, 2, 3]` | 허용값 제한 |
| `parse_args()` | 실제 명령줄 해석 |

차시별로 공통 옵션에 새 옵션을 추가한다.

```python
p = parser()
p.add_argument("--question")
args = p.parse_args()
```

## 7 config 환경변수와 Settings

소스: [config.py](LangChain_20261117_DataEdition/app/config.py)

### 경로와 dotenv

```python
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(find_dotenv(), override=False)
```

```text
__file__                 현재 config.py 경로
Path(...).resolve()      절대 경로로 정리
.parents[0]              app 폴더
.parents[1]              프로젝트 폴더
```

일반적인 파이썬 파일 실행에서 `find_dotenv()`는 호출 파일 위치부터 상위로 `.env`를 찾는다. `load_dotenv()`는 파일의 값을 환경변수로 읽는다. `override=False`이면 이미 설정된 환경변수는 덮어쓰지 않는다.

`load_dotenv(".env")`처럼 경로를 직접 쓰면 현재 작업 폴더의 파일을 지정한다. `find_dotenv()`로 검색하는 것과 구분해야 한다.

### Settings 클래스

```python
@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    max_output: int = 500
    temperature: float | None = None
```

```python
settings = Settings("mock", "local-fixture")

settings.provider     # "mock"
settings.model        # "local-fixture"
settings.max_output   # 500
settings.temperature  # None
```

- `@dataclass`: 데이터 보관용 생성자 등을 자동으로 만든다.
- `frozen=True`: 일반적인 필드 재할당을 금지한다.
- `provider: str`: 문자열을 사용한다는 타입 힌트다.
- `float | None`: 실수 또는 값 없음이라는 타입 표시다.
- 타입 힌트 자체가 실행 중 값을 자동 검증하지는 않는다.

### Settings.read

```python
settings = Settings.read(args.mock)
```

주요 처리:

```python
provider = "mock" if mock else os.getenv("LLM_PROVIDER", "openai").lower()
prefix = provider.upper()
model = (
    "local-fixture"
    if provider == "mock"
    else os.getenv(prefix + "_MODEL", "").strip()
)
```

`mock=True`이면 공급자는 `mock`, 모델은 `local-fixture`다. 그 외에는 환경변수에서 읽고 공급자·모델·키·temperature를 검사한다.

```python
os.getenv("LLM_PROVIDER", "openai")
# 환경변수가 없으면 "openai"

"OpenAI".lower()  # "openai"
"openai".upper()  # "OPENAI"
"OPENAI" + "_MODEL"  # "OPENAI_MODEL"
float("0.5")      # 0.5
```

`read()`는 `@classmethod`다. 객체를 먼저 만들지 않고 `Settings.read()`로 호출한다. `cls`는 호출 대상 클래스이고 다음 문장은 Settings 객체를 만들어 반환한다.

```python
return cls(provider, model, temperature=temperature)
```

## 8 prompts 채팅 프롬프트

소스: [prompts.py](LangChain_20261117_DataEdition/app/prompts.py)

### ChatPromptTemplate

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role}입니다. 상품 정보: {context}"),
    ("human", "{question}")
])
```

`from_messages()`는 역할과 메시지 본문으로 채팅 템플릿을 만든다.

```python
values = {
    "role": "상품 안내 도우미",
    "context": "최대 15인치 노트북 수납 가능",
    "question": "15인치 노트북을 넣을 수 있나요?"
}

prompt_value = prompt.invoke(values)
messages = prompt_value.to_messages()
```

반환 형태:

```python
[
    SystemMessage(
        content="당신은 상품 안내 도우미입니다. 상품 정보: 최대 15인치 노트북 수납 가능"
    ),
    HumanMessage(content="15인치 노트북을 넣을 수 있나요?")
]
```

| 역할 | 용도 | 메시지 type |
|---|---|---|
| system | 역할·규칙·조건 | `"system"` |
| human | 사용자 입력 | `"human"` |
| ai | 모델 응답 | `"ai"` |

`prompt.invoke()`는 프롬프트를 완성할 뿐, 모델을 호출하지 않는다. `invoke()`의 동작은 호출 대상에 따라 다르다.

### 필수 변수와 중괄호

```python
sorted(prompt.input_variables)
# ["context", "question", "role"]

prompt.invoke({"question": "문의"})
# KeyError: role과 context가 빠져 있음
```

입력값 안의 중괄호는 다시 템플릿 변수로 해석하지 않는다.

```python
values["question"] = "주문 {order_id}도 조회해 주세요."
```

완성된 human 메시지에도 `{order_id}`가 그대로 남는다. 템플릿의 `{question}`을 치환한 후, 그 안의 내용을 다시 치환하지 않기 때문이다.

### 세 프롬프트와 get_prompt

| 버전 | 구성 |
|---|---|
| weak | 상품 정보와 질문 |
| role | 상담원 역할 + 상품 정보와 질문 |
| designed | 근거 범위·추측 금지·말투·길이·답변 순서 |

```python
def get_prompt(version="designed"):
    if version not in PROMPTS:
        raise ValueError("version은 weak/role/designed 중 하나입니다.")
    return PROMPTS[version]
```

```python
get_prompt()        # designed 템플릿 객체
get_prompt("weak")  # weak 템플릿 객체
```

designed는 상품 설명에 없는 재고·현재 판매가·통화·배송일·보증·반품 정책을 추측하지 않도록 지시한다. 프롬프트 지시가 정확성을 자동 보장하는 것은 아니다.

## 9 providers 모델 생성과 오류 안내

소스: [providers.py](LangChain_20261117_DataEdition/app/providers.py)

### make_model

```python
if settings.provider == "mock":
    return FakeListChatModel(responses=[MOCK_TEXT])

common = dict(
    model=settings.model,
    max_tokens=settings.max_output,
    timeout=30,
    max_retries=0
)
```

공급자에 따라 `ChatOpenAI(**common)` 또는 `ChatGroq(**common)` 객체를 반환한다. temperature가 설정돼 있으면 인수에 추가한다.

```python
common = dict(model="모델 ID", timeout=30)
# {"model": "모델 ID", "timeout": 30}

ChatOpenAI(**common)
# ChatOpenAI(model="모델 ID", timeout=30)과 같은 인수 전달
```

`**common`은 딕셔너리를 이름 있는 인수로 펼친다.

```python
model = make_model(settings)   # 모델 객체 생성
message = model.invoke(...)   # 모델 요청 실행
```

`max_tokens=500`은 500글자 제한이 아니다. 토큰 수와 문자 수를 구분해야 한다.

모의 모델의 고정 응답:

```text
[모의 응답] 안녕하세요. 상품 설명과 질문을 연결하는 형식을 확인했습니다. 재고·배송·반품 정책은 별도 확인이 필요합니다. 문의별 실제 답변을 생성한 결과는 아닙니다.
```

모의 모델은 체인의 구조 확인용이다. 상품별 답변 품질을 비교하는 용도로 쓰면 안 된다.

### friendly_error

입력은 예외 객체, 반환값은 안내 문자열이다.

```python
status = getattr(error, "status_code", None)
```

`status_code` 속성이 있으면 읽고 없으면 `None`을 사용한다.

| 상태 코드 | 안내 내용 |
|---|---|
| 400 | 요청 설정·파라미터 확인 |
| 401 | API 키 확인 |
| 403 | 프로젝트·모델 권한 확인 |
| 404 | 모델 ID·주소 확인 |
| 429 | 호출·토큰·크레딧 한도 확인 |

```python
friendly_error(ValueError("질문이 비어 있습니다."))
# "질문이 비어 있습니다."

type(ValueError("문제")).__name__
# "ValueError"
```

입력 오류는 `str(error)`로 바꾸고, 그 밖의 오류는 예외 종류와 일반적인 연결 안내로 표현한다.

## 10 pipeline 전처리와 체인

소스: [pipeline.py](LangChain_20261117_DataEdition/app/pipeline.py)

### sample_requests

상품이 9개 이상이면 인덱스 `[0, 2, 8]`을 선택한다. 실제 데이터에서는 가방·재킷·외장 하드다.

```python
inputs = [
    {
        "record_id": "row-001",
        "question": "15인치 노트북을 넣을 수 있나요? 반품이 가능한가요?"
    },
    {
        "record_id": "row-003",
        "question": "어떤 활동에 적합한 상품인가요? 현재 재고가 있나요?"
    },
    {
        "record_id": "row-009",
        "question": "지원하는 운영체제는 무엇인가요? 배송일은 언제인가요?"
    }
]
```

생성 코드:

```python
return [
    {"record_id": records[j]["record_id"], "question": questions[i]}
    for i, j in enumerate(indices)
]
```

`enumerate([0, 2, 8])`은 `(0, 0)`, `(1, 2)`, `(2, 8)`을 제공한다. `i`는 질문 번호, `j`는 상품 인덱스다.

상품이 적으면 다음으로 존재하는 상품 중 최대 세 개를 고른다.

```python
list(range(min(3, len(records))))

# 상품 2개 → [0, 1]
# 상품 5개 → [0, 1, 2]
```

### prepare_input

```python
def prepare_input(request, records):
    if not isinstance(request, dict):
        raise TypeError("요청은 dict여야 합니다.")

    question = request.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question은 공백이 아닌 문자열이어야 합니다.")

    question = question.strip()
    if len(question) > 500:
        raise ValueError("질문은 500자 이내로 입력하세요.")

    record_id = request.get("record_id")
    if not isinstance(record_id, str):
        raise ValueError("record_id가 필요합니다.")

    product = find_product(records, record_id)
    return {"context": product_context(product), "question": question}
```

입력:

```python
{
    "record_id": "row-001",
    "question": "  노트북을 넣을 수 있나요?  ",
    "context": "고객이 임의로 적은 상품 정보"
}
```

반환값:

```python
{
    "context": "카탈로그에서 직접 만든 상품 JSON 문자열",
    "question": "노트북을 넣을 수 있나요?"
}
```

고객이 보낸 `context`는 사용하지 않는다. 상품 ID로 카탈로그에서 정보를 직접 가져온다.

```python
{}.get("question")  # None
```

`get()`은 키가 없을 때 기본값을 반환하지만 `request["question"]`은 키가 없으면 KeyError다.

빈 질문은 다음 오류를 만든다.

```text
ValueError: question은 공백이 아닌 문자열이어야 합니다.
```

### build_chain

```python
def build_chain(model, records, version="designed"):
    prepare = RunnableLambda(
        lambda request: prepare_input(request, records)
    )
    return prepare | get_prompt(version) | model | StrOutputParser()
```

`lambda`는 익명 함수다.

```python
lambda request: prepare_input(request, records)
```

는 다음과 비슷하다.

```python
def prepare_one(request):
    return prepare_input(request, records)
```

미리 읽은 `records`를 사용하면서, 실행할 때마다 다른 요청을 받는다.

`RunnableLambda`는 파이썬 함수를 LangChain 실행 단계로 감싼다. `|`는 앞 단계의 반환값을 다음 단계의 입력으로 연결한다. 이런 연결을 LCEL이라고 한다.

```text
prepare → prompt → model → output_parser
```

체인을 만드는 순간에는 모델을 호출하지 않는다. `invoke()`, `batch()`, `stream()`으로 실행할 때 처리한다.

### StrOutputParser

```python
message = AIMessage(content="노트북 수납이 가능합니다.")
answer = StrOutputParser().invoke(message)
# "노트북 수납이 가능합니다."
```

메시지에서 텍스트를 추출한다. 사실 검증기는 아니다. `현재 재고는 100개입니다.`라는 근거 없는 응답을 넣어도 그 문장을 추출한다.

분석에 사용한 설치 환경에서는 반환값의 구체적인 클래스 이름이 `TextAccessor`로 표시되기도 했다. 이는 `str`의 하위 타입으로 `isinstance(answer, str)`는 참이다.

## 11 invoke batch stream

| 메서드 | 입력 | 반환 형태 | 용도 |
|---|---|---|---|
| `invoke()` | 요청 하나 | 완성된 결과 하나 | 단일 문의 |
| `batch()` | 요청 리스트 | 결과 리스트 | 여러 문의 |
| `stream()` | 요청 하나 | 결과 조각 이터레이터 | 점진적 표시 |

### invoke

```python
answer = chain.invoke(request)
# "완성된 답변 문자열"
```

### batch

```python
outputs = chain.batch(
    inputs,
    config={"max_concurrency": 1},
    return_exceptions=True
)
```

입력 순서에 대응하는 결과 리스트가 나온다. 아래 답변은 설명용 예시다.

```python
[
    "첫 번째 답변",
    ValueError("question은 공백이 아닌 문자열이어야 합니다."),
    "세 번째 답변"
]
```

- `max_concurrency=1`: 동시 처리를 하나로 제한한다.
- `return_exceptions=True`: 개별 요청 오류도 결과 항목으로 받는다.
- 한 프롬프트에 여러 질문을 합치는 것이 아니라 각 입력에 체인을 실행한다.
- 공급자의 별도 할인 Batch API와 구분한다.

요청과 결과를 연결할 때 `zip()`을 쓴다.

```python
for request, output in zip(inputs, outputs):
    if isinstance(output, Exception):
        result = {"status": "error", "error": friendly_error(output)}
    else:
        result = {"status": "ok", "answer": output}

    row = {**request, **result, "execution": "batch"}
```

```python
list(zip(["질문1", "질문2"], ["답변1", "답변2"]))
# [("질문1", "답변1"), ("질문2", "답변2")]
```

`zip()`은 두 목록의 길이가 다르면 짧은 쪽까지만 묶는다.

### stream

```python
chunks = []
for chunk in chain.stream(request):
    print(chunk, end="", flush=True)
    chunks.append(chunk)

answer = "".join(chunks)
```

예를 들어 다음 조각을 받았다면:

```python
["안녕하세요.", " 노트북을", " 수납할 수 있습니다."]
```

결합 결과는 다음과 같다.

```text
안녕하세요. 노트북을 수납할 수 있습니다.
```

실제 조각 경계는 모델 구현에 따라 달라진다.

- `end=""`: 출력 뒤에 줄바꿈을 붙이지 않는다.
- `flush=True`: 출력 버퍼를 즉시 비운다.
- `chunks.append(chunk)`: 조각을 보관한다.
- `"".join(chunks)`: 조각 사이에 구분자를 넣지 않고 합친다.

## 12 s01부터 s06까지

### s01 데이터 확인

```python
records = read_catalog(args.data)
print("langchain-core", version("langchain-core"))
print("상품 수:", len(records))
```

현재 데이터와 분석 환경의 핵심 출력:

```text
langchain-core 1.8.1
상품 수: 20
```

실제 파일은 args, 상품 전체 목록, 데이터 취득 방식, 첫 상품도 출력한다. `list(first["raw"])`는 원본 딕셔너리의 키 목록을 만든다.

```python
["title", "price", "description", "category", "image"]
```

모델 호출은 없다.

### s02 메시지 템플릿

첫 상품을 읽고 role·context·question을 채운다. 완성된 system·human 메시지를 출력한다. 필수 변수를 빠뜨린 KeyError를 의도적으로 재현하고 처리한다. 모델 호출은 없다.

### s03 프롬프트 세 종류

```python
for version in ("weak", "role", "designed"):
    value = get_prompt(version).invoke(values)
```

같은 상품·같은 질문에 대해 지시문만 바꾼 메시지를 만든다. 보고서에는 세 항목을 저장한다. 모델 호출은 없다.

### s04 수동 실행과 LCEL

수동 실행:

```python
prompt_value = prompt.invoke(values)
message = model.invoke(prompt_value)
answer = output_parser.invoke(message)
```

LCEL:

```python
chain = prompt | model | output_parser
answer = chain.invoke(values)
```

동일한 순서를 직접 나열하거나 체인으로 연결한다. 이 체인은 전처리 단계가 없으므로 `{context, question}` 형태의 `values`를 받는다. `build_chain()`의 체인은 전처리가 포함돼 `{record_id, question}` 요청을 받는다는 차이가 있다.

**현재 s04.py에는 중간 확인용 실행 코드가 있어 정상 실행 시 모델을 총 세 번 호출한다.** 직접 `model.invoke()`, 확인용 `chain.invoke()`, 마지막 분기에서 각각 한 번이다. README의 원래 호출 수 설명과 현재 코드가 다르다.

### s05 질문 검증

```bash
python -m sessions.s05 --mock --question ""
```

예시 결과:

```python
{
    "record_id": "row-001",
    "question": "",
    "error": "question은 공백이 아닌 문자열이어야 합니다.",
    "status": "error"
}
```

검증 실패는 전처리에서 발생하므로 해당 요청은 모델 단계까지 진행하지 않는다.

### s06 배치와 스트리밍

```bash
python -m sessions.s06 --mock
```

요청 세 개를 배치로 처리한다. 답변은 보고서에 저장하며, 배치 분기에는 각 답변을 터미널에 출력하는 코드가 없다.

```bash
python -m sessions.s06 --mock --stream
```

`inputs[0]`을 사용하므로 첫 요청 하나만 스트리밍한다. 보고서에도 항목 하나를 저장한다. 스트리밍 도중 오류가 나면 현재 코드는 부분 답변을 보고서로 저장하지 않고 바깥 예외 처리로 이동한다.

## 13 s07 프롬프트 비교

소스: [s07.py](LangChain_20261117_DataEdition/sessions/s07.py)

같은 상품·질문·모델을 유지하고 프롬프트 버전을 바꾸어 실행한다.

```text
질문 3개 × 프롬프트 3개 × 반복 횟수
```

기본 반복 한 번이면 정상 완료 시 9개 기록이다.

```bash
python -m sessions.s07 --mock --repeats 2
```

정상 완료 시 18개 기록을 만든다. 반복은 1·2·3 중 선택한다.

### 실행 순서 회전

```python
versions = ["weak", "role", "designed"]
versions = versions[repeat:] + versions[:repeat]
```

```text
repeat=0 → weak, role, designed
repeat=1 → role, designed, weak
repeat=2 → designed, weak, role
```

`items[a:b]`는 a부터 b 직전까지 자른다.

### 해시

```python
hashlib.sha256(values["context"].encode()).hexdigest()[:12]
```

문자열을 `encode()`로 바이트로 바꾸고, SHA-256 해시의 16진수 표현 앞 12자리를 저장한다. 맥락·질문·완성 프롬프트의 해시를 기록해 비교 입력을 추적한다.

### 시간

```python
started = time.perf_counter()
# 처리
elapsed = round(time.perf_counter() - started, 4)
```

`perf_counter()`는 경과 시간 측정에 사용하고, `round(..., 4)`는 소수점 넷째 자리까지 반올림한다.

### 현재 답변 저장 코드의 상태

성공 답변을 추출하고 기록하는 부분이 주석 처리돼 있다.

```python
# answer = StrOutputParser().invoke(message)
# row.update(status="ok", answer=answer, characters=len(answer),
#            within_500_chars=len(answer)<=500, usage=message.usage_metadata)
```

따라서 현재 코드는 모델 메시지를 터미널에 출력하지만 성공 답변 본문·문자 수·사용량을 보고서에 넣지 않는다. 성공 기록은 다음 형태다.

```python
{
    "record_id": "row-001",
    "question": "...",
    "version": "designed",
    "repeat": 1,
    "context_hash": "12자리 해시",
    "question_hash": "12자리 해시",
    "prompt_hash": "12자리 해시",
    "elapsed_seconds": 0.1234
}
```

실패 시에는 `row.update(status="error", error=...)`로 오류 정보를 추가한다. 429이면 중첩 반복문을 차례로 중단한다. 문자 수·응답 시간만으로 답변의 정확성을 평가할 수는 없다.

## 14 s08 CSV 문의와 JSONL

소스: [s08.py](LangChain_20261117_DataEdition/sessions/s08.py)

```text
CSV → 행별 요청 dict → 체인 → 성공·오류 결과 → JSONL·보고서
```

```bash
python -m sessions.s08 --mock --input data/requests_with_error.csv
```

입력:

```csv
record_id,question
row-001,노트북을 넣을 수 있나요?
row-003,
row-009,지원 운영체제를 알려주세요.
```

### CSV 읽기

```python
with args.input.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
```

`with`는 블록 종료 시 파일을 닫는다. `newline=""`는 CSV 모듈이 줄바꿈을 처리하도록 한다. DictReader는 헤더를 키로 사용한다.

```python
{"record_id": "row-001", "question": "노트북을 넣을 수 있나요?"}
{"record_id": "row-003", "question": ""}
```

빈 칸은 여기서 빈 문자열로 읽힌다.

헤더 검사:

```python
{"record_id", "question"} <= set(reader.fieldnames)
```

집합의 `<=`는 부분집합 관계다. 추가 열이 있어도 필수 두 열을 포함하면 된다.

```python
{"record_id", "question"} <= {"record_id", "question", "customer"}
# True
```

`--limit`은 1부터 5까지 지정할 수 있고 기본값은 3이다. CSV 입력이 없으면 예시 요청 목록을 사용하므로 원래 예시 개수인 세 개보다 늘어나지는 않는다.

### 행별 오류 처리

```python
try:
    row = {**request, "answer": chain.invoke(request), "status": "ok"}
except Exception as error:
    row = {**request, "error": friendly_error(error), "status": "error"}
```

예시 결과:

```python
[
    {"record_id": "row-001", "question": "노트북을 넣을 수 있나요?",
     "answer": "[모의 응답] ...", "status": "ok"},
    {"record_id": "row-003", "question": "",
     "error": "question은 공백이 아닌 문자열이어야 합니다.", "status": "error"},
    {"record_id": "row-009", "question": "지원 운영체제를 알려주세요.",
     "answer": "[모의 응답] ...", "status": "ok"}
]
```

일반적인 개별 오류는 기록하고 다음 행으로 진행한다. 상태 코드가 429이면 중단한다.

### JSONL 저장

```python
out.write_text(
    "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
    encoding="utf-8"
)
```

출력 경로는 `outputs/drafts.jsonl`이다. JSONL은 한 줄에 JSON 값 하나를 저장한다.

```jsonl
{"record_id":"row-001","status":"ok","answer":"..."}
{"record_id":"row-003","status":"error","error":"..."}
{"record_id":"row-009","status":"ok","answer":"..."}
```

파일 전체를 대괄호로 감싸는 일반 JSON 배열과 구분한다.

성공 개수:

```python
sum(x["status"] == "ok" for x in rows)
```

합산할 때 True는 1, False는 0으로 계산된다.

```python
sum([True, False, True])  # 2
```

위 오류 포함 CSV를 모의 모델로 처리한 출력:

```text
성공 2 / 오류 1
```

## 15 report 보고서 저장

소스: [report.py](LangChain_20261117_DataEdition/app/report.py)

```python
save_report(session, records, result_rows, data_path, settings=None, notes=None)
```

```python
path = save_report(6, records, rows, args.data, settings)
```

JSON과 HTML을 저장하고 HTML 파일의 Path 객체를 반환한다.

```text
reports/s06_report.json
reports/s06_report.html
```

JSON은 데이터 처리용이고 HTML은 브라우저 확인용이다. 같은 차시의 파일은 다시 실행하면 덮어쓴다.

JSON에는 차시·UTC 실행 시각·출처·파일 해시·공급자·모델·설정·결과 rows가 들어간다.

```python
{
    "topic_id": "U2-01",
    "session": 6,
    "created_at": "UTC 실행 시각",
    "data": {"file": "products_public_derived.json", "sha256": "..."},
    "provider": "mock",
    "model": "local-fixture",
    "model_mode": "모의 모델 · 실제 추론 아님",
    "temperature": None,
    "max_output": 500,
    "notes": [],
    "rows": rows
    # 실제 기록에는 dataset_mode 등도 포함
}
```

주요 문법:

```python
folder.mkdir(exist_ok=True)              # 이미 폴더가 있으면 그대로 사용
f"s{6:02d}_report"                      # "s06_report"
datetime.now(timezone.utc).isoformat()    # UTC 시각 문자열
```

HTML에 값을 넣을 때는 문자를 이스케이프한다.

```python
html.escape("<script>")
# "&lt;script&gt;"
```

입력 문자열이 HTML 태그가 아니라 글자로 표시되게 한다.

상품 원문을 찾는 코드:

```python
product = next(
    (p for p in records if p["record_id"] == row.get("record_id")),
    None
)
```

조건에 맞는 첫 항목을 가져오고 없으면 None을 사용한다.

```python
next((x for x in [1, 2, 3] if x > 1), None)  # 2
next((x for x in [1, 2, 3] if x > 9), None)  # None
```

## 16 fetch_products 상품 수집

소스: [fetch_products.py](LangChain_20261117_DataEdition/app/fetch_products.py)

API 요청:

```bash
python -m app.fetch_products
```

저장된 파일 가져오기:

```bash
python -m app.fetch_products --import-file saved_products.json
```

주요 코드:

```python
with urllib.request.urlopen(origin, timeout=20) as response:
    content = response.read(2_000_001)
```

응답을 제한된 크기까지 읽고, 2,000,000바이트를 넘으면 오류 처리한다. JSON으로 해석한 뒤 임시 파일을 만들고 `read_catalog(temp)`로 형식을 검증한다.

```python
temp.replace(target)
```

검증한 임시 파일을 최종 경로로 옮긴다.

```text
data/products_live.json
data/products_live.source.json
```

첫 파일은 상품 데이터, 두 번째는 출처·취득 방식·시각·상품 수다. 파일 가져오기와 직접 API 수집은 취득 방식으로 구분해 기록한다.

원본 id가 있는 데이터로 바꾸면 CSV의 record_id도 `api-1` 같은 실제 ID에 맞춰야 한다.

## 17 주요 파이썬 문법

| 문법 | 기능 | 예시 |
|---|---|---|
| `isinstance(x, str)` | 자료형 확인 | `isinstance("가방", str)` → True |
| `len(x)` | 개수·길이 | `len([1, 2])` → 2 |
| `dict.get()` | 키 조회와 기본값 | `{}.get("x")` → None |
| `str.strip()` | 양 끝 공백 제거 | `" A ".strip()` → `"A"` |
| `enumerate()` | 번호와 값 순회 | `(0, 값), (1, 값)` |
| `zip()` | 같은 위치끼리 묶기 | 질문·답변 연결 |
| `set()` | 중복 없는 집합 | `set([1, 1, 2])` → `{1, 2}` |
| `range(3)` | 정수 순회 | 0, 1, 2 |
| `min(3, 2)` | 작은 값 선택 | 2 |
| `getattr(x, "a", None)` | 속성 조회 | 없으면 None |
| `round(1.23456, 4)` | 반올림 | 1.2346 |
| `"".join(parts)` | 문자열 결합 | `["A", "B"]` → `"AB"` |
| `sum(조건 for x in 목록)` | 조건 만족 개수 | 성공 수 |
| `raise ValueError(...)` | 예외 발생 | 호출한 쪽으로 전달 |
| `try / except` | 예외 처리 | 실패 결과 저장 |
| `with ... as f` | 자원 사용 후 정리 | 파일 자동 닫기 |

리스트 컴프리헨션:

```python
[x * 2 for x in [1, 2, 3]]
# [2, 4, 6]
```

딕셔너리 컴프리헨션:

```python
{k: product[k] for k in ("title", "description")}
```

조건 표현식:

```python
"ok" if success else "error"
```

딕셔너리 항목 펼치기:

```python
new_row = {**request, "status": "ok"}
```

함수 인수 펼치기:

```python
ChatOpenAI(**common)
```

딕셔너리 갱신:

```python
row = {"record_id": "row-001"}
row.update(status="ok", answer="예시 답변")
# row에 status와 answer가 추가됨
```

예외 처리와 프로그램 종료:

```python
if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(friendly_error(error))
```

처리하지 못한 일반 예외를 안내 문자열로 바꿔 종료한다. 배치의 `return_exceptions=True`는 개별 체인 실행에 관한 설정이며, 앞선 파일 읽기·설정 오류까지 모두 결과 목록으로 만드는 것은 아니다.

## 18 기억할 개념과 재사용 예제

| 개념 | 기억할 정의 또는 원칙 |
|---|---|
| 모듈 실행 | 프로젝트 폴더에서 `python -m sessions.s02` |
| 경로 기준 | 상대 경로는 보통 작업 폴더, `__file__`은 코드 파일 위치 |
| JSON | 저장 형식과 파이썬 dict를 구분 |
| loads와 dumps | 문자열을 데이터로 / 데이터를 문자열로 |
| 입력 계약 | 필요한 키·자료형·제약을 명확히 정의 |
| 전처리 | 검증·정규화·상품 조회를 모델 호출 전에 수행 |
| 프롬프트 | 역할·지시·근거·질문을 구성한 입력 |
| 템플릿 | 변수를 실제 값으로 채우는 틀 |
| Runnable | invoke·batch·stream 등으로 실행 가능한 처리 단위 |
| LCEL | `|`로 Runnable을 연결하는 표현 방식 |
| 자료형 연결 | 앞 단계 결과를 다음 단계가 받을 수 있어야 함 |
| 출력 파서 | 응답 형태를 정리하며 사실을 검증하지 않음 |
| 토큰 | 모델 처리 단위이며 글자 수와 다름 |
| 모의 모델 | 처리 구조 확인용, 답변 품질 검증용이 아님 |
| 오류 경계 | 개별 요청 실패와 프로그램 전체 실패를 구분 |
| 추적 | 원본·상품 ID·출처·해시를 보관 |
| JSONL | 한 줄마다 독립적인 JSON 값 하나 |
| 비교 실험 | 상품·질문·모델을 고정하고 비교 대상만 변경 |

### 재사용할 최소 코드

프로젝트 폴더에서 실행하는 코드 예시다.

```python
from app.catalog import read_catalog
from app.config import Settings
from app.providers import make_model
from app.pipeline import build_chain

records = read_catalog()
settings = Settings.read(mock=True)
model = make_model(settings)
chain = build_chain(model, records)

request = {
    "record_id": records[0]["record_id"],
    "question": "15인치 노트북을 넣을 수 있나요?"
}

answer = chain.invoke(request)
print(answer)
```

모의 모델이므로 고정 모의 응답을 출력한다. 여러 요청은 `batch()`, 점진적 출력은 `stream()`, CSV 입력은 `csv.DictReader`, 보고서는 `save_report()`를 연결한다.

### 복습 질문

1. `product_context()`의 반환값이 dict가 아니라 str인 이유는 무엇인가?
2. `prompt.invoke()`와 `model.invoke()`는 각각 무엇을 하는가?
3. `prompt | model | parser`와 `build_chain()`이 받는 입력은 어떻게 다른가?
4. 고객이 보낸 context를 그대로 사용하지 않는 이유는 무엇인가?
5. `return_exceptions=True`가 없을 때와 있을 때 결과 처리는 어떻게 달라지는가?
6. 출력 파서가 문자열을 반환했다고 답변의 사실성이 보장되는가?
7. 배치 처리와 공급자의 별도 Batch API는 같은 기능인가?
8. JSON 배열 파일과 JSONL 파일은 어떻게 구분하는가?
9. 모의 응답으로 프롬프트의 의미 품질을 비교할 수 있는가?
10. 현재 s07 코드에는 성공 답변 본문이 보고서에 저장되는가?

## 19 검증 범위

모의 모델로 다음 동작을 확인했다.

- 상품 20개 읽기와 첫 ID `row-001`
- 체인의 응답이 문자열로 사용 가능함
- 배치의 정상 응답과 ValueError 개별 보존
- 스트리밍 조각을 결합하면 일반 호출의 모의 응답과 일치
- 오류 포함 CSV 처리 시 성공 2건·오류 1건
- SHA-256 해시 길이 64자리
- 임시 폴더에서 HTML·JSON 보고서 생성
- 누락된 템플릿 변수의 KeyError
- 질문 값 안의 `{order_id}`가 그대로 보존됨

`tests/test_project.py`에는 데이터 검증·전처리·템플릿·체인·배치·스트리밍·보고서 이스케이프 검사 등이 있다. 분석 당시 Python 환경에 pytest가 없어 전체 pytest 테스트는 실행하지 않았다.

기존 소스와 실행 보고서는 수정하지 않았다. 검증용 보고서는 임시 폴더에서 생성·확인했다.
