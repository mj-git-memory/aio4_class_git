# 02. 패키지와 주요 함수 문법

아래 코드는 문법을 이해하기 위한 짧은 발췌·축약 예시입니다. 각 조각을 따로 실행하려면 import와 변수 준비가 필요합니다. 실제 전체 실행은 [실행 안내](03_run_guide.md)를 따르세요.

## 1. 패키지 지도

**패키지**는 가져다 쓸 수 있는 기능 묶음입니다. `pip`은 이를 설치하는 도구이고, `import`는 설치된 기능을 코드에서 불러오는 문법입니다. 설치 이름과 import 이름이 다를 수 있습니다.

| 설치 이름 | 코드에서 불러오는 이름 | 하는 일 | 필요한 코드 |
|---|---|---|---|
| `torch` | `torch` | 텐서와 AI 계산 | `main1.py`, 모든 `backend.py` |
| `transformers` | `AutoTokenizer`, `AutoModelForCausalLM` | 모델 로딩·문장 변환·답변 생성 | 모델 실행 코드 |
| 같은 `transformers` | `TextIteratorStreamer` | 생성 중인 텍스트 전달 | 스트리밍 백엔드 두 개 |
| `huggingface-hub` | `huggingface_hub` | 모델 파일 다운로드 | `main1.py`, 모든 `backend.py` |
| `python-dotenv` | `dotenv` | `.env` 설정 읽기 | 모든 채팅 화면·백엔드 |
| `streamlit` | `streamlit as st` | 브라우저 화면·세션 상태 | `main1.py`, 각 폴더의 `main.py` |
| `requests` | `requests` | 백엔드로 HTTP 요청 | 각 폴더의 `main.py` |
| `fastapi` | `FastAPI`, `HTTPException`, `StreamingResponse` | API 경로·응답 정의 | 모든 `backend.py` |
| `pydantic` | `BaseModel`, `Field`, `ConfigDict`, `model_validator` | 데이터 조건 검사 | 모든 `backend.py` |
| `uvicorn` | 명령 `python -m uvicorn` | API 서버 실행 | 분리형 앱 실행 시 |

`os`, `pathlib`, `argparse`, `contextlib`, `threading`, `queue`, `json`, `typing`, `urllib.parse`, `time`은 Python 기본 제공 모듈입니다. `main_yield.py`는 기본 모듈 `time`만 사용합니다.

현재 requirements 파일에 적힌 버전은 `transformers==4.57.1`, `huggingface-hub==0.36.0`, `streamlit==1.50.0`, `python-dotenv==1.1.1`, `fastapi==0.118.0`, `pydantic==2.12.3`, `uvicorn==0.37.0`입니다. `torch`와 `requests`는 두 requirements 파일에 명시돼 있지 않으므로 실행 안내에서 따로 다룹니다. 이 목록은 최신 버전 추천이 아니라 현재 수업 파일의 기록입니다.

## 2. Python 기본 문법부터 읽기

```python
def greet(name):
    return f"안녕하세요, {name}님"

message = greet("민지")
```

- `def 함수이름(매개변수):`는 재사용할 작업을 정의합니다. 정의하는 것과 호출하는 것은 달라요.
- `greet("민지")`처럼 괄호와 값을 적으면 호출합니다.
- `return 값`은 호출한 곳에 결과를 돌려줍니다. 값 없는 `return`은 그 함수 실행을 끝냅니다.
- `f"...{변수}..."`는 문자열에 값을 끼워 넣습니다.
- `#` 뒤는 설명용 주석입니다. 실행하지 않습니다.

day17에서 자주 보이는 자료형:

```python
prompt = "안녕"                              # 문자열 str
message = {"role": "user", "content": prompt}  # 이름과 값을 묶는 딕셔너리 dict
messages = [message]                           # 순서 있는 목록 list
content = messages[0]["content"]               # 첫 메시지의 content
```

`len(prompt)`는 글자 수, `len(messages)`는 목록 항목 수입니다. `None`은 아직 값이 없다는 뜻입니다. `if prompt is None: return`은 입력이 없으면 처리를 끝내는 문법입니다.

## 3. 설정과 경로

```python
load_dotenv(override=False, interpolate=False)
value = os.getenv("MODEL_DIR")
model_dir = Path(value).expanduser()
if not model_dir.is_absolute():
    model_dir = Path(__file__).resolve().parent / model_dir
```

| 문법 | 의미 | 왜 쓰나 |
|---|---|---|
| `os.getenv("키")` | 환경변수 값 읽기 | 코드 밖에서 경로·주소 변경 |
| `override=False` | 이미 존재하는 환경변수 우선 | 실행 시 지정한 설정 유지 |
| `interpolate=False` | `${...}` 형태의 문자열 치환 끄기 | 설정값을 치환 없이 읽기 |
| `.strip()` | 문자열 양끝 공백 제거 | 입력·설정 정리. 내부 공백은 남음 |
| `.rstrip("/")` | 끝의 `/` 제거 | URL 경로 결합을 단순화 |
| `Path(__file__)` | 현재 소스 파일 경로 | 터미널 위치와 독립된 기준 사용 |
| `.parent` | 한 단계 위 폴더 | 파일이 있는 폴더 선택 |
| `.resolve()` | 절대 경로로 정리 | 실제로 어디를 가리키는지 명확히 함 |
| `폴더 / "파일명"` | 경로 결합 | 운영체제에 맞는 경로 구성 |
| `urlparse(url)` | URL을 scheme·netloc 등으로 나누기 | `http://...` 형식 검사 |

## 4. 모델 다운로드와 로딩

```python
snapshot_download(
    repo_id="Qwen/Qwen2.5-0.5B-Instruct",
    local_dir=str(model_dir),
    allow_patterns=["config.json", "tokenizer*.json", "*.safetensors"],
)
```

`이름=값`은 **키워드 인자**입니다. 각 설정을 이름으로 전달합니다. `repo_id`는 저장소 이름, `local_dir`는 저장 위치, `allow_patterns`는 받을 파일 이름 규칙입니다. `*`는 여러 이름과 맞는 패턴입니다. 위 예시는 축약 목록이고 실제 코드에는 더 많은 패턴이 있습니다.

```python
tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    str(model_dir), dtype=torch.float32, local_files_only=True
)
model.to("cpu")
model.eval()
```

`Auto...`는 설정을 읽고 알맞은 모델·토크나이저 클래스를 선택합니다. `CausalLM`은 앞에 있는 글을 바탕으로 다음 토큰을 생성하는 언어 모델 종류입니다. `dtype=torch.float32`는 계산용 수치를 32비트 실수로 준비한다는 뜻이며 양자화가 아닙니다. `.to("cpu")`는 CPU 사용, `.eval()`은 학습 때 사용하는 일부 동작을 평가용으로 바꾸는 설정입니다. `.eval()`만으로 연산 기록을 끄는 것은 아닙니다.

## 5. 질문을 모델에 넣고 답변 꺼내기

```python
messages = [
    {"role": "system", "content": "한국어로 짧게 답하세요."},
    {"role": "user", "content": prompt},
]
inputs = tokenizer.apply_chat_template(
    messages, tokenize=True, add_generation_prompt=True,
    return_dict=True, return_tensors="pt",
)
```

`tokenize=True`는 숫자로 변환, `add_generation_prompt=True`는 모델이 답변을 이어갈 시작 표시 추가, `return_dict=True`는 이름 붙은 자료 묶음 반환을 뜻합니다. `input_ids`는 토큰 번호, `attention_mask`는 모델이 처리할 위치를 표시하는 정보입니다.

```python
with torch.inference_mode():
    outputs = model.generate(**inputs, max_new_tokens=96, do_sample=False)
input_length = inputs["input_ids"].shape[1]
answer = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
```

- `with`는 해당 범위의 준비·정리를 관리합니다. `inference_mode()`는 답변 생성 시 학습용 연산 기록 등을 줄입니다.
- `**inputs`는 딕셔너리의 키와 값을 함수 인자로 펼칩니다. `{"x": 1}`을 `**`로 전달하면 `x=1`처럼 전달하는 원리입니다.
- `max_new_tokens=96`은 새 답변 토큰의 상한입니다. 정확히 96개를 생성하라는 뜻은 아닙니다.
- `do_sample=False`는 무작위 추출 대신 점수가 높은 토큰을 선택하는 설정입니다.
- `.shape[1]`은 이 입력 텐서에서 문장 길이 차원의 크기를 읽습니다.
- `outputs[0][input_length:]`는 첫 결과에서 입력 부분을 제외하고 새 답변 부분을 자릅니다. `[시작:]`은 해당 위치부터 끝까지의 슬라이싱입니다.
- `skip_special_tokens=True`는 대화 제어용 특수 토큰을 출력에서 빼줍니다.

## 6. Streamlit 화면과 캐시

```python
st.title("학습 도우미")
prompt = st.chat_input("질문을 입력하세요")
if prompt is None:
    return
with st.chat_message("user"):
    st.write(prompt)
```

`st.chat_input()`은 제출된 질문을 받습니다. `st.chat_message("user")` 블록은 사용자 말풍선 영역, `st.write()`는 내용 표시입니다. `st.spinner("...")`는 작업 중 안내, `st.warning()`과 `st.info()`는 안내 메시지, `st.error()`는 처리 실패 표시입니다. `st.stop()`은 현재 화면 코드 실행을 멈춥니다.

```python
@st.cache_resource
def load_local_model(model_dir):
    ...
```

`@...`는 **데코레이터**입니다. 함수에 추가 동작을 붙이는 문법입니다. 여기서는 모델 로딩 함수에 자원 재사용 기능을 붙입니다. Streamlit의 캐시된 모델은 같은 프로세스의 세션들 사이에서 공유될 수 있어 모델 호출을 제어하는 락도 사용합니다.

## 7. API와 데이터 양식

```python
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    prompt: str = Field(min_length=1, max_length=500, strict=True)

app = FastAPI(lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    ...
```

`class`는 자료와 동작의 틀을 정의합니다. `(BaseModel)`은 Pydantic의 데이터 검증 기능을 이어받는다는 뜻입니다. `prompt: str`는 문자열 필드라는 **타입 표시**입니다. 일반 Python 타입 표시 자체가 모든 값을 검사하는 것은 아니고, 여기서는 Pydantic과 FastAPI가 이를 읽어 검증합니다.

`Field()`는 길이 등의 조건, `strict=True`는 문자열이 아닌 값을 임의 변환하지 않도록 하는 설정, `extra="forbid"`는 정하지 않은 추가 항목 금지입니다. `response_model`은 반환 데이터의 양식을 지정합니다. `@app.post()`는 해당 주소의 POST 요청을 아래 함수와 연결합니다.

`raise HTTPException(status_code=..., detail=...)`은 API 응답 상태와 설명을 지정합니다. 코드의 주요 상태는 입력 조건 위반 422, 모델 사용 중 503, 내부 생성 실패 500 등입니다. 이는 요청 처리 개념 설명이며 과거 에러 질문을 옮긴 것은 아닙니다.

## 8. 서버 시작·종료와 자원 공유

```python
@asynccontextmanager
async def lifespan(app):
    app.state.model = load_model()  # 개념 예시: 실제 코드는 from_pretrained 사용
    yield
    del app.state.model
```

`async def`는 비동기 함수 정의 문법입니다. 이 예시에서는 프레임워크의 시작·종료 절차에 맞춰 동작합니다. `yield` 앞이 준비, 뒤가 정상 종료 정리입니다. `app.state`는 앱이 유지할 자원을 넣는 공간이고, `del`은 해당 참조를 제거합니다. `async`라고 적었다고 CPU 모델 계산이 자동으로 병렬화되지는 않습니다.

## 9. 일반 HTTP 요청

```python
with requests.post(
    f"{backend_url}/chat", json={"prompt": prompt}, timeout=(5, 180)
) as response:
    response.raise_for_status()
    data = response.json()
return data["answer"]
```

`json=`은 데이터를 JSON 본문으로 보내는 옵션입니다. `timeout=(5, 180)`은 연결 대기 5초, 응답 읽기 대기 180초를 구분합니다. 전체 작업이 무조건 180초 이내 끝난다는 뜻은 아닙니다. `raise_for_status()`는 실패 상태를 정상 답변과 구분합니다. `with` 범위를 나가면 응답 연결 자원을 정리합니다.

## 10. `yield`와 스트리밍 주요 문법

```python
def pieces():
    yield "안녕"
    yield "하세요"

answer = st.write_stream(pieces())
```

함수 호출만으로 문자열 전체가 반환되는 대신 반복해서 꺼낼 객체를 만듭니다. `st.write_stream()`이 값을 차례로 소비해 표시합니다. 이 코드처럼 텍스트만 나오면 완성된 문자열도 반환하므로 대화 이력에 저장할 수 있습니다. [공식 반환값 설명](https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream)

```python
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True,
                               skip_special_tokens=True, timeout=180.0)
worker = Thread(target=run_generation, daemon=True)
worker.start()
```

`target=run_generation`은 실행할 함수를 **전달**합니다. `run_generation()`처럼 바로 호출한 결과를 넣는 것과 다릅니다. `skip_prompt=True`는 입력 질문이 답변 출력에 섞이지 않도록 합니다. 실제 생성 스레드 안의 `model.generate(streamer=streamer, ...)`가 조각을 공급합니다.

```python
yield json.dumps({"type": "delta", "text": text}, ensure_ascii=False) + "\n"
return StreamingResponse(events, media_type="application/x-ndjson")
```

`json.dumps()`는 Python 자료를 JSON 글로 바꾸고, `ensure_ascii=False`는 한국어를 그대로 읽을 수 있게 표현합니다. `json.loads()`는 역방향 변환입니다. 끝의 `"\n"`은 한 줄 경계입니다. `events`는 여기서 조각을 만드는 반복자를 뜻하는 설명용 이름이며 실제 코드는 `stream_events(...)`를 전달합니다.

화면 쪽의 `requests.post(..., stream=True)`는 응답을 점진적으로 읽도록 하고, `response.iter_lines(chunk_size=1, decode_unicode=True)`는 데이터를 줄별로 모아 문자열로 제공합니다. `chunk_size=1`은 읽기 버퍼 단위이며 모델의 토큰 단위가 아닙니다. `event.get("type")`으로 사건 종류를 읽고 `delta`의 텍스트만 다시 `yield`합니다.

## 11. 잠금과 작업 완료

```python
if not lock.acquire(blocking=False):
    # 사용 중이라는 응답 처리
    ...
try:
    ...  # 공유 모델 사용
finally:
    lock.release()
```

`blocking=False`는 잠금을 바로 얻을 수 없으면 기다리지 않는다는 뜻입니다. `try / except / finally`에서 `except`는 문제 발생 시 처리, `finally`는 성공·실패와 관계없는 정리 작업입니다. 실제 스트리밍 코드는 생성 스레드의 `finally`에서 락을 해제합니다. 생성 시작 후에는 응답 전송 함수가 아니라 생성 작업이 끝나는 시점에 해제합니다.

## 12. 대화 이력 문법

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

candidate = st.session_state.messages + [{"role": "user", "content": prompt}]
answer = st.write_stream(request_stream(backend_url, candidate))
st.session_state.messages = candidate + [{"role": "assistant", "content": answer}]
```

`not in`은 항목이 없는지 검사합니다. 목록의 `+`는 두 목록을 이어 새 목록을 만듭니다. 실제 코드는 완료된 `answer`가 있을 때만 마지막 대입을 합니다.

```python
role: Literal["user", "assistant"]
messages: list[Message] = Field(min_length=1, max_length=9)

@model_validator(mode="after")
def check_order(self):
    ...
    return self
```

`Literal`은 허용할 역할 값을 지정하고, `list[Message]`는 메시지 양식 객체들의 목록이라는 뜻입니다. `@model_validator(mode="after")`는 각 필드 검증 뒤 여러 항목을 함께 검사합니다. 실제 `check_order()`는 `enumerate()`로 위치와 메시지를 함께 순회하고, `% 2`로 질문·답변 순서를 확인합니다. `message.model_dump()`는 검증된 메시지 객체를 딕셔너리로 바꿉니다.

`st.button("새 대화")`를 누르면 목록을 비우고 `st.rerun()`으로 화면 코드를 다시 실행합니다. `st.chat_input(..., disabled=조건)`은 질문 횟수가 한도에 도달하면 입력을 비활성화합니다.

## 13. 명령 해석과 시작점

```python
parser = argparse.ArgumentParser()
parser.add_argument("command", nargs="?", default="app",
                    choices=["download", "app"])
args = parser.parse_args()

if __name__ == "__main__":
    main()
```

`argparse`는 터미널 명령 뒤의 인자를 읽는 기본 도구입니다. `nargs="?"`는 생략 가능, `default`는 생략 시 값, `choices`는 허용 값입니다. `args.command`를 조건문에서 사용해 실제 함수를 호출해야 동작이 선택됩니다.

`if __name__ == "__main__":`는 파일을 프로그램의 시작점으로 실행했을 때만 아래 함수를 호출하는 관용 문법입니다. Uvicorn이 `backend.py`를 import할 때는 다운로드용 `main()`을 호출하지 않고 `app`을 사용합니다.
