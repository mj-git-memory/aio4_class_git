# day23 CoT와 ReAct 소스코드 학습 정리

`CoT_ReAct_KDT_8Sessions`는 같은 수학 문제를 서로 다른 프롬프트로 풀고, 계산 도구를 연결한 뒤 정답과 실행 과정을 비교하는 실습 프로젝트다. 이 문서는 소스 분석, 주요 함수의 문법과 반환값, 예제 데이터의 결과, 복습할 개념을 정리한다.

예시의 계산·데모·정답 비교 결과는 로컬 실행으로 확인했다. 실제 LLM API의 응답은 실행 시 사용하는 모델에 따라 달라진다.

## 1 전체 구조와 파일별 기능

```text
JSON 문제 읽기
    ↓
지시문과 질문으로 메시지 만들기
    ↓
데모 또는 실제 LLM에 전달
    ↓
일반 답변 또는 계산 도구를 이용한 답변 생성
    ↓
기준 정답과 비교
    ↓
JSON 기록과 HTML 보고서 저장
```

| 파일 | 구현 기능 | 주요 함수와 클래스 |
| --- | --- | --- |
| [lesson.py](CoT_ReAct_KDT_8Sessions/lesson.py) | CoT와 ReAct 실행, 계산, 기록 저장 | prompt, calculate, react, demo, save, main |
| [providers.py](CoT_ReAct_KDT_8Sessions/providers.py) | 외부 LLM API 연결 | RemoteChat, CallLimit |
| [s02.py](CoT_ReAct_KDT_8Sessions/s02.py) | 동일 질문에 두 지시문 결합 | records, variants |
| [s03.py](CoT_ReAct_KDT_8Sessions/s03.py) | 두 지시문으로 응답 받기 | ask, scripted, egg_demo, sprint_demo |
| [s04.py](CoT_ReAct_KDT_8Sessions/s04.py) | JSON 계산 요청을 검사하고 실행 | execute |
| [s05.py](CoT_ReAct_KDT_8Sessions/s05.py) | ReAct 대화와 도구 실행 추적 | trace |
| [s06.py](CoT_ReAct_KDT_8Sessions/s06.py) | direct·CoT·ReAct 정답 비교 | answer_numbers, display_number, compare |
| [s07.py](CoT_ReAct_KDT_8Sessions/s07.py) | 잘못된 응답과 반복 종료 재현 | replay |
| [s08.py](CoT_ReAct_KDT_8Sessions/s08.py) | 비교 기록을 HTML로 변환 | numeric_values, report |

`CoT_ReAct_KDT_8Sessions/mission/`은 도넛 대시보드 설계 문서와 프롬프트를 담은 폴더다. 실행 가능한 대시보드 코드는 아니다.

## 2 실제 예제 데이터

| 파일 | 사용하는 코드 | 문제와 정답 |
| --- | --- | --- |
| [problem.json](CoT_ReAct_KDT_8Sessions/data/problem.json) | lesson.py | 재닛의 오리알 판매액: 18달러 |
| [problems.json](CoT_ReAct_KDT_8Sessions/data/problems.json) | s02부터 이어지는 실습 | 오리알 판매: 108달러·24개, 달리기: 540미터 |

`problem.json`은 문제 딕셔너리 하나이고, `problems.json`은 문제 딕셔너리들이 담긴 리스트다.

달리기 문제의 주요 실제 값은 다음과 같다.

```python
{
    "id": "gsm8k-main-test-0003",
    "dataset_id": "D04",
    "config": "main",
    "split": "test",
    "row_index": 3,
    "question": "제임스는 일주일에 3번씩 달리기 훈련을 하며, 한 번 훈련할 때마다 전력 질주를 3회 합니다. 전력 질주 한 번의 거리는 60미터입니다. 제임스가 일주일 동안 달리는 총거리는 몇 미터입니까?",
    "answer": "제임스는 일주일 동안 전력 질주를 3 * 3 = <<3*3=9>>9회 합니다.\n따라서 일주일 동안 달리는 총거리는 9 * 60 = <<9*60=540>>540미터입니다.\n#### 540"
}
```

`row_index=3`은 문제에 붙은 번호다. 현재 파일의 리스트에서는 두 번째 항목이다. `####`는 풀이와 최종 기준 정답을 구분하는 표시다.

## 3 패키지와 기본 모듈

외부 패키지는 `requirements.txt`의 다음 두 가지다.

| 패키지 | 사용 기능 |
| --- | --- |
| langchain-core | 지시문과 질문을 메시지 템플릿으로 구성 |
| python-dotenv | .env 설정을 환경변수로 불러오기 |

이 프로젝트는 LangChain 에이전트 클래스를 사용하지 않는다. LangChain은 프롬프트 생성에 사용하고, ReAct 반복은 직접 만든 `react()`가 수행한다.

| 파이썬 기본 모듈 | 함수와 클래스 | 기능 |
| --- | --- | --- |
| pathlib | Path | 파일과 폴더 경로 처리 |
| json | loads, dumps, load | JSON 변환과 읽기 |
| argparse | ArgumentParser | 명령줄 옵션 처리 |
| urllib.request | Request, urlopen | HTTP 요청 생성과 실행 |
| urllib.error | HTTPError, URLError | API와 연결 오류 처리 |
| os | getenv | 환경변수 읽기 |
| re | compile, findall, finditer | 정규표현식으로 숫자와 답 표시 찾기 |
| math | isfinite | 무한대와 NaN 등 비정상 숫자 검사 |
| time | perf_counter | 소요 시간 측정 |
| datetime | datetime.now | 결과 파일명에 사용할 현재 시각 |
| html | escape | 문자열을 HTML에 문자로 표시하도록 변환 |

## 4 경로 생성과 데이터 읽기

### ROOT의 생성 위치와 값

`ROOT`는 `lesson.py`에서 정의한 변수다.

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parent
```

| 표현 | 의미 |
| --- | --- |
| __file__ | 현재 모듈 파일의 경로 |
| Path(__file__) | 해당 경로를 다루는 객체 생성 |
| .resolve() | 절대 경로로 정리하고 심볼릭 링크 해석 |
| .parent | 경로의 상위 폴더 반환 |

`lesson.py` 안에서 다음 코드를 사용하면:

```python
print(Path(__file__).resolve())
```

출력은 파일까지 포함한 경로다.

```text
/Users/imijeong/Downloads/AIO_4_class/aio02/day23/CoT_ReAct_KDT_8Sessions/lesson.py
```

반면 `print(ROOT)`는 폴더 경로를 출력한다.

```text
/Users/imijeong/Downloads/AIO_4_class/aio02/day23/CoT_ReAct_KDT_8Sessions
```

`ROOT`는 경로 객체를 가리키는 변수다. 대문자는 상수처럼 사용한다는 관례이며 변경 자체가 금지되는 것은 아니다.

절대 경로는 최상위 폴더부터 시작하는 전체 주소다. 상대 경로는 기준 위치에서부터 적은 주소다. `ROOT`에 데이터 경로를 연결하면 터미널의 현재 위치 대신 `lesson.py` 폴더를 기준으로 파일을 찾는다.

### records의 실행 과정

`records()`는 `s02.py`에 정의한 함수다.

```python
def records():
    return json.loads(
        (ROOT / "data/problems.json").read_text(encoding="utf-8")
    )
```

이를 풀면 다음과 같다.

```python
path = ROOT / "data/problems.json"       # 경로 연결
text = path.read_text(encoding="utf-8")  # 파일 → 문자열
rows = json.loads(text)                 # JSON 문자열 → 파이썬 리스트
```

`/`는 이 경우 경로 연결 연산자다. `read_text()`는 `Path` 객체의 메서드이며 파일 전체를 문자열로 반환한다. `json.loads()`는 문자열을 파이썬 데이터로 변환하는 함수다.

```python
json.loads('[1, 2, 3]')       # [1, 2, 3]
json.loads('{"count": 10}')   # {"count": 10}

rows = records()
len(rows)                    # 2
rows[1]["row_index"]          # 3
```

`json.loads()`는 문자열을 읽고, `json.load()`는 열린 파일이나 응답 스트림을 읽는다는 차이가 있다.

## 5 실행 옵션과 문제 선택

다음 명령을 기준으로 설명한다.

```bash
python s02.py --row 3
```

### 실행 시작 순서

파일은 맨 위부터 실행한다. import, 변수 대입, 함수 정의를 마친 다음 아래 조건에 도착한다.

```python
if __name__ == "__main__":
```

직접 실행한 `s02.py`의 `__name__`은 `"__main__"`이다. 다른 파일에서 `import s02`로 가져올 때는 `"s02"`이므로 이 블록을 실행하지 않는다. 함수 정의는 호출될 때까지 함수 본문을 실행하지 않는다.

### ArgumentParser와 메서드

```python
parser = argparse.ArgumentParser()
parser.add_argument("--row", choices=[0, 3], type=int, default=0)
args = parser.parse_args()
```

`ArgumentParser`는 클래스다. `ArgumentParser()`는 파서 객체를 생성하는 클래스 호출이며 `parser`는 그 객체를 가리킨다.

`add_argument()`는 옵션 규칙을 등록하는 메서드다.

| 입력 | 의미 |
| --- | --- |
| --row | 옵션 이름 |
| choices=[0, 3] | 허용하는 값은 0과 3 |
| type=int | 입력 문자열을 정수로 변환 |
| default=0 | 옵션을 생략하면 0 사용 |

`add_argument()`는 옵션 설정을 나타내는 Action 객체를 반환하지만 현재 코드는 그 반환값을 저장하지 않는다. 핵심 효과는 parser에 규칙이 등록되는 것이다.

`parse_args()`는 실제 명령줄 옵션을 읽고 Namespace 객체를 반환한다.

```python
# python s02.py --row 3
args          # Namespace(row=3)
args.row      # 3

# python s02.py
args          # Namespace(row=0)
args.row      # 0
```

`args.row`는 객체의 속성에 접근하는 문법이다. 옵션 생략 시 첫 번째 문제를 선택하더라도 저장된 값은 1이 아니라 0이다.

### next와 제너레이터 표현식

```python
row = next(r for r in records() if r["row_index"] == args.row)
```

| 표현 | 역할 |
| --- | --- |
| records() | 문제 리스트 읽기 |
| for r in records() | 문제를 하나씩 r에 담기 |
| if r["row_index"] == args.row | 번호가 같은 문제만 통과 |
| 맨 앞의 r | 조건을 통과한 문제 자체를 내놓기 |
| next(...) | 나온 값 중 첫 번째 하나를 반환 |

`next()`는 파이썬 내장 함수다. 조건 검사는 if가 수행한다. 현재 데이터와 `args.row=3`이면 첫 번째 오리알 문제는 건너뛰고 두 번째 달리기 문제 딕셔너리를 `row`에 저장한다. 해당 문제가 없으면 StopIteration 오류가 난다.

```python
row["row_index"]  # 3
row["question"]   # 제임스의 달리기 문제 문자열
```

## 6 프롬프트 생성과 두 방식 비교

### lesson.prompt

문법은 `prompt(system, question)`이며 반환값은 메시지 딕셔너리 리스트다.

```python
def prompt(system, question):
    template = ChatPromptTemplate.from_messages([
        ("system", "{instruction}"), ("human", "{question}")
    ])
    value = template.invoke({"instruction": system, "question": question})
    instruction, problem = value.to_messages()
    return [{"role": "system", "content": instruction.content},
            {"role": "user", "content": problem.content}]
```

`ChatPromptTemplate`은 다음 외부 패키지 클래스다.

```python
from langchain_core.prompts import ChatPromptTemplate
```

| 호출 | 기능 | 반환 형태 |
| --- | --- | --- |
| ChatPromptTemplate.from_messages(...) | 빈칸이 있는 메시지 템플릿 생성 | ChatPromptTemplate 객체 |
| template.invoke({...}) | 빈칸에 실제 값 대입 | ChatPromptValue 객체 |
| value.to_messages() | 메시지 객체 리스트로 변환 | SystemMessage와 HumanMessage 리스트 |
| message.content | 메시지 본문 속성 접근 | 문자열 |

`from_messages()`는 클래스 메서드, `invoke()`와 `to_messages()`는 객체의 메서드다. `.content`는 속성이므로 호출 괄호가 없다.

`system`, `human`은 인식되는 역할 이름이다. 사용자 역할에는 `user`도 사용할 수 있다. 반면 `{instruction}`, `{question}`은 직접 정하는 빈칸 이름이며 invoke에 전달하는 키와 일치해야 한다.

달리기 문제에 지시문을 넣으면:

```python
messages = prompt("한국어로 답하세요.", row["question"])
```

다음 구조를 반환한다.

```python
[
    {"role": "system", "content": "한국어로 답하세요."},
    {"role": "user", "content": row["question"]}
]
```

두 번째 content의 값은 앞에서 읽은 실제 제임스 문제 문자열이다. `template.invoke()`는 프롬프트 완성이며 LLM 호출이 아니다.

### s02.variants

```python
def variants(row):
    return {name: prompt(instruction, row["question"])
            for name, instruction in [("direct", DIRECT), ("cot", WORKED)]}
```

딕셔너리 컴프리헨션을 일반 반복문으로 풀면 다음과 같다.

```python
def variants(row):
    result = {}
    for name, instruction in [("direct", DIRECT), ("cot", WORKED)]:
        result[name] = prompt(instruction, row["question"])
    return result
```

첫 반복은 `name="direct"`, `instruction=DIRECT`이고, 두 번째는 `name="cot"`, `instruction=WORKED`다. 최종 구조는 다음과 같다.

```python
{
    "direct": prompt(DIRECT, row["question"]),
    "cot": prompt(WORKED, row["question"])
}
```

현재 DIRECT도 간단한 계산 설명을 요청한다. WORKED에는 연필 문제와 풀이 예시가 추가된다.

### 화면에 출력하는 반복문

```python
for name, messages in variants(row).items():
    print(name); print('---')
    for message in messages:
        print(message["role"], message["content"], sep="\n")
        print()
```

`.items()`는 딕셔너리의 키와 값 쌍을 순회하는 뷰 객체를 반환한다. 첫 번째 반복의 name은 direct, messages는 해당 메시지 리스트다. 두 번째는 cot와 그 메시지 리스트다.

`print(name); print('---')`의 세미콜론은 두 문장을 같은 줄에 적은 것이다. `sep="\n"`은 두 출력값 사이를 줄바꿈으로 구분하고, 인자 없는 `print()`는 빈 줄을 만든다.

아래는 첫 번째 방식의 실제 출력이다.

```text
direct
---
system
문제의 조건을 순서대로 계산하고 한국어로 간단히 설명한다.
마지막 줄은 '답: 숫자와 단위' 형식으로 쓴다. 답이 여러 개면 질문 순서대로 쉼표로 구분한다.

user
제임스는 일주일에 3번씩 달리기 훈련을 하며, 한 번 훈련할 때마다 전력 질주를 3회 합니다. 전력 질주 한 번의 거리는 60미터입니다. 제임스가 일주일 동안 달리는 총거리는 몇 미터입니까?
```

그다음 cot 방식의 풀이 예시 지시문과 같은 질문을 출력한다. s02는 메시지를 만들고 보여주며 정답을 계산하거나 LLM에 요청하지 않는다.

## 7 데모 응답과 실제 API 연결

### s03.ask와 데모 함수

```python
def ask(row, method, messages, remote):
    if remote is None:
        return scripted(row, method, messages)
    return remote(messages)
```

remote가 None이면 준비된 대본을 반환하고, API 객체이면 실제 요청을 보낸다. 둘 다 최종 반환값은 문자열이다.

```python
ask(row, "direct", variants(row)["direct"], None)
# '답: 540미터'

ask(row, "cot", variants(row)["cot"], None)
# '주당 3 × 3 = 9회\n9 × 60 = 540미터\n답: 540미터'
```

`scripted()`는 문제 ID와 질문이 등록된 대본과 같은지 검사한다. `egg_demo()`와 `sprint_demo()`는 대화에 쌓인 Observation 등을 보고 다음 계산 요청 또는 최종 응답을 JSON 문자열로 반환한다. 임의의 새 문제를 풀어 주는 모델이 아니다.

### providers.RemoteChat

```python
remote = RemoteChat("gemini", max_calls=8, max_tokens=800)
reply = remote(messages)
```

| 메서드 | 역할 | 반환값 |
| --- | --- | --- |
| __init__ | 설정·키·모델·호출 상한 초기화 | 초기화 메서드 자체는 None |
| prepare(messages) | API 주소·헤더·요청 본문 구성 | (url, headers, payload) 튜플 |
| extract(data) | 응답 본문과 사용량 추출 | (text, usage) 튜플 |
| __call__(messages) | HTTP 요청, 응답 추출, 오류 처리 | 응답 문자열 |

`RemoteChat(...)`은 초기화된 객체를 생성한다. 객체에 `__call__()`이 있어서 `remote(messages)`처럼 함수 형태로 호출할 수 있다.

설정 읽기:

```python
load_dotenv(find_dotenv(), override=False)
model = os.getenv("GEMINI_MODEL", "").strip()
```

`find_dotenv()`는 .env 경로 문자열을 반환한다. `load_dotenv()`는 그 설정을 환경변수에 반영한다. override=False이므로 기존 환경변수가 우선한다. `os.getenv()`는 환경변수 값을 읽고 없으면 기본값을 반환한다. `.strip()`은 문자열 양 끝 공백을 제거한다.

요청과 응답:

```python
req = request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

with request.urlopen(req, timeout=45) as response:
    data = json.load(response)
```

Request는 HTTP 요청 객체를 만든다. `json.dumps()`는 딕셔너리를 JSON 문자열로, `.encode()`는 문자열을 전송용 바이트로 변환한다. `urlopen()`이 요청을 보내며 `json.load(response)`가 응답 JSON을 파이썬 객체로 읽는다.

API 응답 예시를 설명하기 위한 최소 데이터는 다음과 같다. 실제 모델 응답을 실행한 결과는 아니다.

```python
data = {
    "choices": [{
        "finish_reason": "stop",
        "message": {"content": "답: 540미터"}
    }],
    "usage": {"total_tokens": 100}
}

# remote.extract(data)의 반환 형태
("답: 540미터", {"total_tokens": 100})
```

`CallLimit`은 RuntimeError를 상속한 사용자 정의 예외 클래스다. API 요청 상한에 도달하면 발생한다. 실패한 요청도 호출 횟수에 포함하며 자동 재시도는 하지 않는다.

## 8 JSON 계산 요청과 계산 도구

`s04.execute(reply)`는 JSON 문자열을 읽어 action, a, b 필드가 정확한지 검사한 뒤 `lesson.calculate()`를 호출한다.

```python
execute('{"action":"subtract","a":16,"b":3}')
# 13
```

내부 흐름:

```python
step = json.loads(reply)
# {"action": "subtract", "a": 16, "b": 3}

calculate(step["action"], step["a"], step["b"])
# calculate("subtract", 16, 3)
```

`calculate(action, a, b)`의 지원 연산:

```python
calculate("add", 12, 12)          # 24
calculate("subtract", 16, 3)      # 13
calculate("multiply", 3, 60)      # 180
calculate("percent_of", 60, 20)   # 12
```

`percent_of`는 a의 b%를 구한다. 입력은 유한한 정수 또는 실수여야 하고 bool은 제외한다. `isinstance()`로 자료형을, `math.isfinite()`로 실수의 정상 범위를 검사한다. bool은 파이썬에서 int의 하위 클래스이므로 별도로 제외한다.

```python
calculate("subtract", "16", 3)
# ValueError: a와 b에는 유한한 숫자를 입력한다.
```

CLI 예:

```bash
python s04.py --action percent_of --a 60 --b 20
```

출력:

```text
{"action": "percent_of", "a": 60, "b": 20}
Observation: 12
```

`vars(args)`는 Namespace의 속성을 딕셔너리로 가져온다. 이를 `json.dumps()`로 문자열로 만들어 execute에 전달한다.

## 9 ReAct 반복과 실행 추적

### lesson.react

```python
react(messages, chat, events)
```

- messages: 모델에 전달할 대화 리스트
- chat: 대화를 받아 문자열을 반환하는 함수 또는 호출 가능한 객체
- events: 사람이 확인할 실행 기록 리스트

```text
모델 응답 받기 → JSON 해석
                   ├─ final이면 종료
                   └─ action이면 계산 → Observation 전달 → 다음 응답
```

달리기 문제의 실제 데모 실행:

```text
모델: {"action":"multiply","a":3,"b":3}
도구: Observation: 9

모델: {"action":"multiply","a":9,"b":60}
도구: Observation: 540

모델: {"final":"540미터"}
```

최대 반복은 `MAX_REACT_TURNS=8`이다. 계산 실행뿐 아니라 최종 응답도 모델 응답 횟수에 포함된다. `react()`는 정상 종료 시 None을 반환하며, 전달받은 messages와 events 리스트에 내용을 추가한다.

### s05.trace

```python
events = []
messages = trace(row, None, events)
len(messages)  # 달리기 문제에서는 7
```

trace는 초기 프롬프트를 만들고 react를 실행한 뒤 전체 대화 리스트를 반환한다.

```text
초기 system·user 2개 + 모델 응답 3개 + Observation 2개 = 7개
```

내부 함수 chat은 바깥 trace의 row와 remote를 사용한다.

```python
def chat(history):
    return ask(row, "react", history, remote)
```

이처럼 내부 함수가 바깥 함수의 변수를 사용하는 구조를 클로저라고 한다.

## 10 정답 추출과 세 방식 비교

### s06.answer_numbers와 display_number

```python
answer_numbers("답: 판매 수익 108달러, 판매하지 않은 달걀 24개")
# [108.0, 24.0]

answer_numbers("답: 540미터")
# [540.0]

display_number([])             # None
display_number([540.0])        # 540.0
display_number([108.0, 24.0])   # [108.0, 24.0]
```

answer_numbers는 정규표현식으로 마지막 정답 표시 이후의 숫자를 추출한다. 정답 표시가 없으면 마지막 줄을 사용한다. display_number는 숫자가 하나면 단일 값, 여러 개면 리스트로 표시한다.

### s06.compare

```python
cases = compare(row, None, "demo")
```

direct, cot, react의 실행 결과를 각각 딕셔너리로 만들고 리스트로 반환한다. 데모 실행으로 확인한 결과는 다음과 같다.

| 문제 | 방식 | 추출 정답 | 도구 실행 | API 요청 |
| --- | --- | --- | --- | --- |
| 오리알 | direct | [108.0, 24.0] | 0 | 0 |
| 오리알 | cot | [108.0, 24.0] | 0 | 0 |
| 오리알 | react | [108.0, 24.0] | 7 | 0 |
| 달리기 | direct | 540.0 | 0 | 0 |
| 달리기 | cot | 540.0 | 0 | 0 |
| 달리기 | react | 540.0 | 2 | 0 |

모두 기준 답의 숫자와 순서가 일치했다. 다만 이 검사는 단위나 설명의 의미까지 검증하지 않는다. 540달러도 숫자만 보면 540미터와 일치할 수 있다.

직접 실행하면 JSON 파일을 저장한다.

```bash
python s06.py
```

```text
results/compare_실행날짜_실행시간.json
```

데모 결과는 미리 작성한 응답이므로 실제 LLM의 성능 평가로 해석하지 않는다.

## 11 오류 처리 실습

`s07.replay(reply, question)`는 모델 대신 고정된 응답을 반복해서 반환하게 만든다.

```python
lambda history: reply
```

이는 다음 함수와 같은 역할이다.

```python
def fixed_reply(history):
    return reply
```

replay는 상태 문자열과 Observation 목록을 튜플로 반환한다.

```python
replay('{"final":"18달러"}', question)
# ("종료", [])
```

| 입력 | 결과 |
| --- | --- |
| 계산하겠습니다. | 올바른 JSON이 아니어서 오류 |
| action이 minus인 요청 | 지원하지 않는 연산 오류 |
| a가 문자열 "16"인 요청 | 숫자 자료형 오류 |
| 계산 요청만 계속 반환 | 8회 이후 반복 상한 오류 |
| final 필드의 문자열 응답 | 즉시 종료 |

final 응답의 종료 성공은 형식이 맞다는 의미다. 해당 문제의 정답 여부까지 검사한 것은 아니다.

## 12 저장과 HTML 보고서

### lesson.save

```python
path = save(events, mode, row)
```

실행 기록을 HTML로 저장하고 생성한 파일의 Path 객체를 반환한다.

```python
directory.mkdir(exist_ok=True)  # 폴더 생성, 이미 있어도 허용
path.write_text(text, encoding="utf-8")  # 문자열을 파일로 저장
```

### s08.numeric_values와 report

```python
numeric_values("108달러, 24개")
# [108.0, 24.0]

target = report(path)
```

report는 s06의 비교 JSON을 읽고 문제, 프롬프트, 응답, 도구 결과, 수치 일치 여부를 HTML로 저장한다. 반환값은 HTML 경로 객체다.

```text
입력: results/compare_20261118_151318_810226.json
출력: results/compare_20261118_151318_810226.html
```

```python
path.with_suffix(".html")  # 확장자를 바꾼 새 경로 객체
escape("<계산 결과>")     # '&lt;계산 결과&gt;'
```

html.escape는 본문이 태그로 해석되지 않도록 변환한다. s08은 입력 경로를 생략하면 results 폴더의 compare JSON 파일명을 정렬해 마지막 파일을 사용한다.

## 13 실행 명령 모음

아래 명령은 CoT_ReAct_KDT_8Sessions 폴더에서 실행한다. lesson, s06, s08은 결과 파일을 생성한다.

```bash
python lesson.py
python s02.py --row 3
python s03.py --provider demo
python s04.py --action percent_of --a 60 --b 20
python s05.py --row 3 --provider demo
python s06.py --provider demo
python s07.py
python s08.py
```

실제 API 모드 예시는 다음과 같다. 선택한 공급자의 키와 모델 설정, 사용 가능 여부를 확인해야 한다.

```bash
python s03.py --provider gemini
```

## 14 꼭 기억할 개념

| 개념 | 정의와 적용 |
| --- | --- |
| 클래스와 객체 | 클래스는 생성 규칙, 객체는 실제 생성된 값. ArgumentParser()가 객체를 만들고 parser가 가리킨다. |
| 함수와 메서드 | records()는 함수, parser.parse_args()는 객체의 메서드다. |
| 속성 | args.row와 message.content처럼 객체가 가진 값에 접근한다. |
| 반환과 출력 | return은 호출한 곳으로 값 전달, print는 화면 표시다. |
| 프롬프트와 모델 호출 | template.invoke는 프롬프트 완성이다. 실제 요청은 remote(messages)에서 수행한다. |
| CoT | 단계별 계산과 풀이를 요청하는 방식이다. 풀이가 있어도 정답을 보장하지 않는다. |
| ReAct | 응답, 도구 실행, 관찰 결과, 다음 응답을 반복하는 구조다. |
| JSON과 딕셔너리 | JSON은 데이터 표현 형식이다. loads로 파이썬 객체, dumps로 JSON 문자열을 만든다. |
| 대화와 로그 | messages는 모델에 전달할 대화, events는 사람이 확인할 실행 기록이다. |
| 가변 객체 | 전달한 리스트에 append하면 호출한 쪽에서도 추가된 내용이 보인다. |
| 제너레이터와 next | 조건에 맞는 값을 차례로 내놓고 next가 다음 값 하나를 가져온다. |
| 언패킹 | name, instruction처럼 여러 값을 변수에 순서대로 나누어 받는다. |
| 데모와 실제 모델 | 데모는 미리 준비된 응답이며 임의의 새 문제를 해결하는 모델이 아니다. |
| 종료 조건 | 최종 답과 반복 상한을 확인해 끝없는 반복을 막는다. |
| API 호출 수와 도구 실행 수 | 모델 요청과 파이썬 계산은 다른 작업이며 횟수도 따로 센다. |
| 형식 검사와 정답 검사 | JSON 형식이 맞는 것과 정답인 것은 별개의 검사다. |
| 데이터 변경 | 질문 변경 시 데모 대본, 정답 추출, 단위와 비교 방식도 함께 검토한다. |

복습은 s02 → s03 → s04 → s05 → s06 → s07 → s08 순서로 진행하면서 각 파일이 가져오는 lesson.py와 providers.py의 정의를 함께 확인하면 된다.
