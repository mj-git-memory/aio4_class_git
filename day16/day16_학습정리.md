# Day 16 학습 정리 — Streamlit에서 대화 서비스까지

작성 기준: 2026-11-07의 `day16` 소스 코드와 이 대화의 학습 질문·답변.

오류 해결 질문과 그 답변은 제외했다. 소스 코드를 수정하지 않고, 현재 구현된 기능을 기준으로 설명했다. 실행 결과를 검증한 보고서가 아니라 코드를 읽고 정리한 학습 자료다.

## 1. 이 폴더에서 무엇을 만드는가?

전체 주제는 **사용자와 대화하는 웹 화면을 만들고, AI 서버 또는 대화 저장 서버와 연결하는 것**이다.

| 파일 | 만드는 기능 | 실제 AI 답변 | 기록 보관 위치 |
|---|---|---|---|
| `main1.py` | 이름·질문 입력과 대화 미리보기 | 없음. 정해진 안내 문구 출력 | 별도 보관 없음 |
| `main2.py` | 로컬 AI 서버에 질문하고 답변 표시 | 있음. llama 서버 호출 | 앱에서 대화 이력을 보관하지 않음 |
| `main3.py` | 사이드바·두 열로 구성한 대화 화면 시제품 | 없음. 문자열로 모의 답변 생성 | 별도 보관 없음 |
| `main4.py` | 현재 Streamlit 세션에서 대화 이력 유지 | 없음. 모의 답변 | `st.session_state` |
| `main5.py` | 대화방 생성·연결, 사용자 메시지 저장·조회 | 현재 AI 호출 없음 | Supabase PostgreSQL |
| `backend.py` | 대화방·메시지·세션 관리 API | AI 호출 없음 | PostgreSQL과 Redis |

`main1.py`부터 `main5.py`까지는 각각 별도로 실행하는 Streamlit 앱이다. 파일 번호가 올라간다고 앞 파일을 자동으로 실행하거나 기능을 모두 상속하지는 않는다. 특히 `main5.py`는 `main2.py`의 AI 호출 기능을 포함하지 않는다.

학습 흐름은 다음처럼 볼 수 있다.

```text
main1: 입력과 미리보기
   ├─ main2: 실제 AI 서버 호출
   └─ main3: 화면 배치 → main4: 세션에 이력 유지
                          → main5 + backend: DB에 기록 저장
```

## 2. 먼저 알아둘 개념

### Streamlit과 UI

**Streamlit**은 Python으로 입력창·버튼·표·그래프 등이 있는 웹 앱을 만드는 오픈소스 프레임워크다. **UI(User Interface)**는 사용자가 보고 조작하는 화면과 요소를 말한다.

`print('안녕하세요')`가 서버의 터미널에 출력한다면, `st.text('안녕하세요')`는 웹 화면에 표시한다. 이 폴더에서는 데이터 분석 화면보다 대화용 UI를 만드는 데 사용한다.

| 코드 | 역할 |
|---|---|
| `st.title()`, `st.header()`, `st.subheader()` | 제목 표시 |
| `st.caption()` | 작은 보조 설명 표시 |
| `st.text_input()` | 한 줄 입력 |
| `st.text_area()` | 여러 줄 입력 |
| `st.button()` | 클릭 동작 받기 |
| `st.checkbox()`, `st.selectbox()` | 켜기·끄기 또는 항목 선택 |
| `st.chat_message()` | 사용자·도우미 말풍선 영역 만들기 |
| `st.chat_input()` | 채팅 메시지 입력 |
| `st.spinner()` | 처리 중임을 표시 |
| `st.sidebar`, `st.columns()` | 사이드바와 열로 화면 배치 |

`st.chat_message('assistant')`를 쓴다고 AI가 실행되는 것은 아니다. 말풍선 모양을 만드는 기능이며, 실제 답변 생성은 별도 코드가 담당한다.

### 재실행과 상태

Streamlit은 기본적으로 입력 반영이나 버튼 클릭이 발생하면 스크립트를 위에서 아래로 다시 실행해 화면을 갱신한다. 일반 변수는 실행할 때 다시 만들어지므로, 이전 실행의 기록을 유지하려면 별도 저장 공간이 필요하다. [공식 실행 원리](https://docs.streamlit.io/get-started/fundamentals/summary)

**상태(state)**는 앱이 현재 기억하는 값이다. 예를 들어 선택한 대화방 ID와 지금까지 입력한 메시지 목록이 상태다.

**`st.session_state`**는 현재 Streamlit 세션에서 재실행 사이에 값을 보관하는 공간이다. 브라우저 연결에 묶인 임시 보관함으로 생각하면 된다. 새로고침이나 연결 재생성 시 유지가 보장되는 영구 저장소는 아니다. [공식 Session State 설명](https://docs.streamlit.io/develop/concepts/architecture/session-state)

### 프런트엔드·백엔드·API

- **프런트엔드:** 사용자가 조작하는 화면 쪽. 여기서는 Streamlit 앱이 담당한다.
- **백엔드:** 데이터 처리와 저장 등 요청을 처리하는 서버 쪽. 여기서는 FastAPI가 담당한다.
- **API:** 프로그램끼리 요청과 응답을 주고받는 약속이다. 예를 들어 `POST /messages`는 “이 메시지를 저장해 주세요”라는 요청이다.
- **HTTP:** API 요청을 전달하는 통신 방식이다. `GET`은 조회, `POST`는 생성·처리 요청, `DELETE`는 삭제 등에 사용한다.
- **JSON:** 통신할 데이터를 키와 값으로 표현하는 텍스트 형식이다. Python 딕셔너리와 닮았지만 Python 객체 자체는 아니다.

비유하면 Streamlit은 주문 화면, API는 주문 양식, FastAPI는 주문 접수 담당, DB는 주문 장부다. Streamlit 코드도 Python 서버에서 실행되지만, 이 실습에서는 역할을 설명하기 위해 화면 쪽이라고 부른다.

## 3. `main1.py` — 이름과 질문을 입력받는 미리보기

### 실행 흐름

1. 제목과 안내 문구를 표시한다.
2. 이름과 질문을 입력받는다.
3. 체크박스를 선택하면 설명을 표시한다.
4. 미리보기 버튼을 클릭하면 양끝 공백을 제거한다.
5. 둘 중 하나라도 비어 있으면 입력 안내를 표시한다.
6. 모두 입력되어 있으면 사용자 말풍선과 정해진 확인 문구를 표시한다.

예를 들어 이름이 `민수`, 질문이 `Streamlit은 무엇인가요?`라면 다음과 같은 화면을 만든다.

```text
사용자: 민수 : Streamlit은 무엇인가요?
도우미: 민수님 질문을 확인했습니다. 이 화면은 미리보기 입니다.
```

실제 질문의 답을 생성하는 기능은 없다. 입력 검사와 말풍선 표시를 연습하는 코드다.

### `.strip()`의 의미

문자열 양끝의 공백·탭·줄바꿈을 제거하고 새 문자열을 반환하는 메서드다. 중간의 공백은 유지한다.

```python
name = '  홍 길동  '
clean_name = name.strip()  # '홍 길동'
# name 자체는 여전히 '  홍 길동  '이다.
```

빈 문자열 `''`은 조건식에서 거짓으로 취급한다. 따라서 다음은 “이름이나 질문 중 하나라도 비어 있으면”이라는 뜻이다.

```python
if not clean_name or not clean_question:
    st.warning('이름과 질문을 모두 입력하세요.')
```

### 버튼과 `else`의 의미

```python
if st.button('대화 미리보기'):
    # 클릭으로 발생한 이번 실행에서 수행
else:
    # 버튼을 클릭한 실행이 아닐 때 수행
```

| 상황 | 버튼 반환값 | 이 코드의 결과 |
|---|---|---|
| 처음 접속 | `False` | 입력 안내 캡션 |
| 입력값 변경을 반영해 재실행 | `False` | 입력 안내 캡션 |
| 미리보기 버튼 클릭 | `True` | 입력 검사 후 미리보기 |
| 이후 다른 위젯으로 재실행 | `False` | 다시 입력 안내 캡션 |

버튼은 클릭한 뒤 계속 켜져 있는 스위치가 아니다. 미리보기 결과를 계속 보관하는 코드도 없으므로 다른 조작으로 재실행되면 미리보기가 사라질 수 있다.

## 4. `main2.py` — 로컬 AI 서버에 질문하기

### 무엇을 하는가?

질문을 llama 서버로 보내고, 서버가 생성한 답변을 받아 말풍선에 표시한다.

```text
브라우저에서 질문 입력
  → Streamlit Python 코드
  → HTTP POST /v1/chat/completions
  → llama 서버가 Qwen 모델로 답변 생성
  → JSON 응답
  → Streamlit 화면에 답변 표시
```

**모델 추론(inference)**은 학습된 모델로 입력에 대한 결과를 계산하는 과정이다. 이 코드는 모델을 새로 학습시키지 않고 이미 학습된 모델을 사용한다.

### 설정 읽기

```python
load_dotenv()
base_url = os.getenv('LLAMA_BASE_URL', '').strip()
model = os.getenv('LLAMA_MODEL', '').strip()
timeout_text = os.getenv('LLMA_TIMEOUT_SECONDS', '180').strip()
timeout_seconds = int(timeout_text)
```

**환경변수**는 프로그램 밖에서 제공하는 설정 값이다. `.env`는 로컬 개발에서 그 값을 적어 두는 파일이고, `load_dotenv()`는 찾아낸 `.env`의 값을 환경변수로 읽어들인다. `os.getenv()`는 해당 이름의 값을 조회한다.

예를 들어 서버 주소는 어디로 요청할지, 모델 이름은 어느 모델을 사용할지 정한다. 현재 코드는 시간 제한 설정 이름으로 `LLMA_TIMEOUT_SECONDS`를 사용하므로 설명에서도 그 이름을 그대로 사용한다. 실제 `.env`의 비밀 값은 이 문서에 복사하지 않았다.

### 요청 데이터의 의미

| 항목 | 현재 값 또는 역할 |
|---|---|
| `model` | 서버에서 지정한 모델 별칭 |
| `messages` | 모델에게 전달할 지시와 질문 목록 |
| `role: system` | “한국어로 핵심만 2~3문장” 같은 동작 지시 |
| `role: user` | 사용자의 현재 질문 |
| `temperature: 0.7` | 다음 토큰 선택의 무작위성 조절 |
| `chat_template_kwargs` | 모델의 대화 형식에 추가 설정 전달 |
| `enable_thinking: False` | 별도 thinking 모드를 끄도록 지정 |
| `max_tokens: 128` | 생성 토큰 수 상한 |
| `stream: False` | 전체 응답을 받은 뒤 표시 |

**토큰**은 모델이 처리하는 텍스트 조각이다. 한 글자나 한 단어와 정확히 같지 않으므로 128토큰이 128글자라는 뜻은 아니다. 길이 상한에 도달하면 문장이 중간에 끝날 수 있다.

`timeout=(5, timeout_seconds)`는 연결 수립 대기와 응답 읽기 대기의 제한이다. 값을 낮춘다고 모델 계산이 빨라지는 것은 아니며, 전체 작업의 정확한 총시간 제한과도 다르다.

`response.json()`은 JSON 응답을 Python 딕셔너리·리스트 등으로 바꾸고, 다음 코드는 첫 번째 답변 후보의 본문을 가져온다.

```python
choice = data['choices'][0]
answer = choice['message']['content']
```

### 현재 구현의 범위

이름은 사용자 말풍선에만 표시하고 AI 요청에는 질문만 보낸다. 이전 질문·답변을 `messages`에 추가하지 않으므로 **이 코드는 이전 대화를 전달하는 다회차 챗봇이 아니라 한 번씩 질문하는 화면**이다. `stream=False`라서 생성 중 문장이 조금씩 나타나지도 않는다.

Qwen3.5-0.8B는 공식 설명상 non-thinking이 기본이다. 별도 thinking을 끄는 설정은 명시했지만, 일반 답변 생성 계산까지 없어지는 것은 아니다. [Qwen 모델 설명](https://huggingface.co/Qwen/Qwen3.5-0.8B), [llama.cpp 요청 설정](https://github.com/ggml-org/llama.cpp/tree/master/tools/server#post-v1chatcompletions-openai-compatible-chat-completions-api)

## 5. `main3.py` — 대화 화면의 배치 시제품

**프로토타입**은 완성 서비스 전에 화면과 사용 흐름을 확인하는 시제품이다. 이 파일은 실제 AI나 DB 없이 화면 구성에 집중한다.

1. 사이드바에서 대화 제목과 `간단히`·`단계별` 형식을 선택한다.
2. `st.columns([1, 2])`로 왼쪽 입력 영역과 오른쪽 미리보기 영역을 만든다. 숫자는 상대적인 너비 비율이다.
3. `st.text_area()`에서 여러 줄 메시지를 입력받는다.
4. 버튼을 클릭하면 선택한 형식에 따라 문자열을 만들어 표시한다.

예를 들어 `대화 이력을 왜 저장해?`를 입력하고 `단계별`을 고르면 다음처럼 정해진 틀을 채운다.

```text
1.메세지 확인: 대화 이력을 왜 저장해?
2. 실제 답변 생성 전 입니다.
```

질문 내용을 이해해 답한 것이 아니라 f-string으로 문자열을 조합한 것이다. 제목이 공백이면 `title.strip() or '제목없음'`에 의해 대체 제목을 사용한다. `clean_title`은 계산하지만 이후 사용하지 않는다.

## 6. `main4.py` — 현재 세션에서 대화 이력 유지

### 핵심 개념

```python
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
```

처음 한 번만 빈 목록을 만든다. 재실행할 때마다 빈 목록으로 덮어쓰지 않기 위해 존재 여부를 검사한다.

대화 한 건은 다음과 같은 딕셔너리로 표현한다.

```python
{'role': 'user', 'content': '안녕하세요'}
{'role': 'assistant', 'content': '모의답변: 안녕하세요 ...'}
```

목록을 반복하며 기존 기록을 먼저 그리고, `st.chat_input()`으로 새 입력을 받는다. `role`은 누구의 말인지, `content`는 말의 내용을 나타낸다.

예를 들어 `단계별`로 메시지 두 개를 보내면 사용자 메시지 두 개와 모의 답변 두 개가 목록에 쌓인다. 같은 연결에서 설정을 바꿔 재실행해도 저장된 목록을 다시 표시할 수 있다.

### 현재 코드에서 구분할 동작

현재 들여쓰기에서는 **메시지 추가와 새 말풍선 출력이 `else`, 즉 `단계별` 분기 안에만 있다.** 따라서 `간단히`에서는 답변 문자열만 만들고 새 메시지를 이력에 추가하거나 표시하지 않는다. “모든 형식에서 이력을 저장한다”라고 읽으면 실제 코드와 다르다.

또한 `title`과 `title_clean`을 읽지만 본문 제목이나 대화방 저장에 사용하지 않는다. DB·AI 연결은 없고, 이력은 현재 Streamlit 세션의 값이다.

## 7. `main5.py` — 대화방과 사용자 메시지의 실제 저장

### 만드는 서비스

여러 대화방 중 하나에 연결하고, 사용자 메시지를 DB에 저장했다가 다시 조회하는 웹 화면이다. 이 파일의 하이브리드는 **PostgreSQL에 기록을 두고 Redis에 만료되는 세션을 두는 조합**으로 이해하면 된다.

```text
브라우저 ↔ Streamlit(main5.py) ↔ FastAPI(backend.py)
                                  ├─ PostgreSQL: 대화방·메시지
                                  └─ Redis: 세션 ID → 대화방 ID
```

주석과 범용 함수에는 모델 서버 관련 표현도 있지만, 현재 실제 호출 경로에는 LLM 요청이 없다. 저장되는 메시지에도 `role` 열이 없고 화면에서는 모두 `user` 말풍선으로 출력한다.

### 함수와 사용자 동작

| 코드/동작 | 역할 |
|---|---|
| `request_json()` | HTTP 요청을 보내고 JSON 응답을 읽는 공통 함수 |
| `api()` | `API_BASE_URL`과 API 경로를 합쳐 요청 |
| `GET /conversations` | 저장된 대화방 목록 조회 |
| 새 대화 만들기 | 대화방 생성 → 그 방의 세션 발급 |
| 선택한 대화 연결 | 기존 방에 새 세션 발급 |
| `GET /messages` | 현재 세션이 가리키는 방의 메시지 조회 |
| 채팅 입력 제출 | `request_id`와 내용을 보내 저장 |
| `st.rerun()` | 저장 이후 DB를 다시 조회하도록 재실행 |

`request_json()`은 세션 ID가 있으면 `X-Session-Id` 헤더를 붙인다. **헤더**는 본문과 별도로 전달하는 요청의 부가 정보다. 서버는 이 값을 보고 Redis에서 대화방을 찾는다. 이 공통 함수에는 Bearer API 키를 넣는 기능도 있지만, 현재 `api()` 호출에서는 그 기능을 사용하지 않는다.

`room_id`, `session_id`, 조회 결과인 `rows`는 `st.session_state`에 보관한다. 메시지의 원본은 DB에 있고 `rows`는 화면에 보여 주기 위해 읽어 온 사본이다. 서버 저장 후 로컬 목록에만 추가하지 않고 DB에서 다시 읽는 점이 `main4.py`와 다르다.

예를 들어 `파이썬 공부`라는 방을 만들고 `오늘은 리스트를 배웠다`를 보내면 DB에 저장한다. 나중에 같은 방에 다시 연결하면 DB 기록을 읽어 표시한다. 이것은 AI의 응답 생성이나 모델 학습을 뜻하지 않는다.

현재 UI는 세션 연장·종료·최근 이력 복원 전용 API를 직접 호출하지 않는다. 기존 방 선택 시에는 `/sessions`로 세션을 발급한 뒤 `/messages`로 이력을 조회한다.

## 8. `backend.py` — 대화 저장과 세션 관리 서버

### 주요 기술

| 기술 | 정의와 이 코드에서의 역할 |
|---|---|
| FastAPI | HTTP 요청을 Python 함수에 연결하는 웹 프레임워크 |
| Pydantic | 요청 데이터의 형식·길이·필수 여부 검사 |
| PostgreSQL | 관계형 DB. 대화방과 메시지를 테이블에 저장 |
| Supabase | 이 실습에서 PostgreSQL을 제공하는 서비스 |
| psycopg | Python에서 PostgreSQL에 접속하고 SQL을 실행하는 드라이버 |
| Redis | 키·값 저장소. 여기서는 만료 시간이 있는 세션 보관 |
| UUID | ID로 사용하는 식별자. 대화방·세션·요청에 사용 |

`@app.post('/conversations')`는 해당 경로의 POST 요청을 함수와 연결한다. 데코레이터를 읽었다고 즉시 대화방이 생성되는 것은 아니다. `BaseModel`로 정의한 자료형은 요청 본문을 검사하는 데 쓰인다. [FastAPI 요청 본문 설명](https://fastapi.tiangolo.com/tutorial/body/)

### DB 구조

`kdt_hybrid`라는 스키마에 다음 테이블을 만든다. **스키마**는 DB 안에서 테이블을 묶는 이름 공간이다.

| 테이블 | 주요 필드 | 의미 |
|---|---|---|
| `conversations` | `id`, `title`, `created_at` | 대화방 |
| `messages` | `id`, `conversation_id`, `content`, `created_at`, `request_id` | 그 방에 속하는 메시지 |

**기본키**는 한 행을 구별하는 값이다. **외래키**인 `messages.conversation_id`는 메시지가 어느 대화방에 속하는지 연결한다. 예를 들어 대화방 A에 속한 메시지만 조회하려면 `WHERE conversation_id = ...` 조건을 사용한다.

`with connect_db() as conn:`은 정상 종료 시 변경을 확정(commit)하고 예외 시 해당 트랜잭션을 되돌린다(rollback). **트랜잭션**은 함께 처리할 DB 작업의 단위다. DB 작업과 Redis 작업 전체를 하나의 원자적 트랜잭션으로 묶은 코드는 아니다.

SQL의 `%s`에는 값을 따로 전달한다. 사용자가 입력한 문자열을 SQL 문장에 직접 이어 붙이지 않는 방식이다.

### 요청 데이터 검사

- `ConversationCreate`: 제목 양끝 공백 제거 후 1~100자.
- `MessageCreate`: UUID 형태의 `request_id`, 공백 제거 후 1~1000자의 내용.
- `SessionCreate`: 대화방 ID를 UUID로 받음.
- `extra='forbid'`: 정의하지 않은 필드는 받지 않음.

`main5.py`의 입력 길이는 1~500자이므로, 현재 화면 쪽이 백엔드보다 짧게 제한한다.

### API 전체 지도

| 메서드·경로 | 처리 함수 | 기능 |
|---|---|---|
| `POST /conversations` | `create_conversation()` | 대화방 생성 |
| `GET /conversations` | `list_conversations()` | 대화방 목록 |
| `POST /sessions` | `create_session()` | 존재하는 대화방에 세션 발급 |
| `POST /messages` | `create_message()` | 세션의 대화방에 메시지 저장 |
| `GET /messages` | `list_messages()` | 세션의 대화방 메시지 조회 |
| `GET /session` | `session_status()` | 대화방 ID와 남은 세션 시간 조회 |
| `POST /session/renew` | `renew_session()` | 세션 만료 시간을 현재 시점 기준으로 재설정 |
| `DELETE /session` | `end_session()` | Redis 세션 삭제. DB 기록 유지 |
| `POST /conversations/{conversation_id}/resume` | `resume_conversation()` | 새 세션 발급과 최근 메시지 조회 |

`connect_db()`와 `connect_redis()`는 각 저장소의 연결을 만들고, `resolve_conversation()`은 헤더의 세션 ID를 확인해 Redis에 저장된 대화방 ID를 찾는다.

### 세션과 TTL — 이용권 비유

**백엔드 세션**은 요청을 특정 대화방과 연결해 주는 서버 측 정보다. Streamlit의 `st.session_state`와 이름은 비슷하지만 별개다.

```text
Redis 키:   kdt:hybrid:l08:session:<세션 ID>
Redis 값:   <대화방 ID>
만료 시간:  SESSION_TTL_SECONDS
```

**TTL(Time To Live)**은 남은 유효 시간이다. 세션을 “대화방에 들어가는 임시 이용권”이라고 생각하면 쉽다. 예를 들어 300초로 설정했다면 발급 시점부터 유효 시간이 흐른다. 이 코드에서는 메시지를 읽거나 저장해도 시간이 자동 연장되지 않고, 별도의 연장 요청이 필요하다. [Redis 만료 기능](https://redis.io/docs/latest/commands/expire/)

이용권이 만료되거나 삭제되어도 PostgreSQL의 대화방·메시지는 삭제하지 않는다. 같은 대화방에 새 세션을 발급하면 기록을 다시 읽을 수 있다.

이 실습에는 사용자 로그인과 대화방 소유자 확인이 구현되어 있지 않다. 따라서 이 세션 ID를 곧바로 사용자 계정 인증 체계와 같은 것으로 이해하면 안 된다.

### 중복 저장 방지 — 멱등성

**멱등성(idempotency)**은 같은 논리 요청을 여러 번 보내도 결과가 중복 적용되지 않도록 하는 성질이다. 이 코드는 `(conversation_id, request_id)` 조합에 고유 인덱스를 둔다.

예를 들어 같은 방에 `request_id=A, 내용='안녕하세요'`를 두 번 보내면 메시지를 두 개 만들지 않고 기존 행을 돌려준다. 첫 저장은 `replayed=False`, 재전송은 `replayed=True`로 구별한다. [PostgreSQL ON CONFLICT 설명](https://www.postgresql.org/docs/current/sql-insert.html)

중요한 조건은 **재전송할 때 같은 요청 ID를 유지해야 한다는 것**이다. 현재 `main5.py`는 제출할 때 `uuid4()`로 새 ID를 만들고, 미처리 요청을 보관해 같은 ID로 재시도하는 UI까지는 구현하지 않았다. 같은 내용을 새 ID로 보내면 별개의 메시지다.

### 초기화와 검증용 함수

- `init_db()`: 스키마·테이블·중복 방지 인덱스를 준비한다.
- `verify_http()`: 실제 HTTP 요청으로 생성·저장·재전송·세션 만료·복원을 확인하는 검증용 클라이언트다. 실행하면 실제 검증용 대화방과 메시지를 DB에 만든다.
- `if __name__ == '__main__'`: 직접 실행했을 때 `init` 또는 `verify` 명령을 처리한다. Uvicorn이 앱을 가져올 때 초기화를 자동 실행하지 않는다.

검증 함수의 존재를 확인한 것이며, 이번 문서 작성에서는 DB를 변경하거나 검증 함수를 실행하지 않았다.

## 9. 이 대화에서 배운 질문과 답변

아래는 오류 해결을 제외한 질문을 학습 주제별로 다시 정리한 것이다.

### Q1. Streamlit은 무엇이고 어떤 기능이 있나?

Python으로 웹 화면과 상호작용을 만드는 도구다. 입력 위젯, 표·차트, 파일 업로드, 레이아웃, 세션 상태, 캐싱 등을 제공한다. 이 폴더에서는 입력·말풍선·상태 관리·서버 연동을 배운다.

**캐싱**은 이미 계산한 결과를 재사용해 같은 일을 반복하지 않는 방식이다. 다만 현재 소스에는 `st.cache_data`나 `st.cache_resource`가 실제 사용되지는 않는다.

### Q2. `.strip()`과 버튼의 참·거짓은?

`.strip()`은 문자열 양끝의 공백을 제거한다. 버튼은 클릭해서 발생한 실행에서만 `True`이며 계속 켜져 있지 않다. 그래서 `else`의 캡션은 처음 접속하거나 다른 위젯으로 재실행한 경우에도 표시된다. 자세한 예시는 3절에 있다.

### Q3. llama 명령어의 각 부분은 무엇인가?

```bash
llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF --alias local-chat
```

| 부분 | 뜻 |
|---|---|
| `llama` | 모델을 실행하는 프로그램 |
| `serve` | 요청을 받아 답변하는 서버 실행 |
| `-hf` | Hugging Face의 모델 저장소 지정 |
| `ggml-org` | 저장소를 제공하는 조직 |
| `Qwen3.5-0.8B-GGUF` | 모델 파일 저장소 |
| `--alias local-chat` | API에 표시할 모델 별칭 지정 |

Python 함수들을 호출한 문장이 아니라 터미널 프로그램에 명령과 옵션을 전달한 것이다. 필요한 모델은 다운로드해 캐시에 두고 재사용한다. [llama 서버 문서](https://llama.app/docs/serve)

`llama`는 실행 도구 이름이고, 여기서 실행하는 모델은 Qwen이다. 실행 도구와 모델을 구분하면 이해하기 쉽다.

### Q4. Qwen3.5-0.8B는 모델 이름인가? 용량은?

그렇다. Qwen은 모델 계열, 3.5는 버전, 0.8B는 약 8억 개 파라미터 규모를 뜻한다. **파라미터**는 학습 과정에서 조정된 숫자 값이다. 0.8B가 파일 크기 0.8GB라는 뜻은 아니다. GGUF는 모델 저장 형식이다.

**양자화**는 모델 숫자의 정밀도를 낮춰 저장 공간과 메모리 부담을 줄이는 기술이다. 품질에 영향을 줄 수 있으며 속도 효과는 하드웨어와 구현에 따라 달라진다.

| 해당 저장소 파일 | 파일 크기 |
|---|---:|
| `Q4_0` | 약 563MB |
| `Q8_0` | 약 834MB |
| `BF16` | 약 1.56GB |

출처: [모델 파일 목록](https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF/tree/main). 실행 도구와 기타 파일의 용량은 별도다.

**이전 대화에서 사용자 Mac을 직접 확인한 결과**는 `Qwen3.5-0.8B-Q8_0.gguf`, 정확히 **833,592,096바이트**였다. 약 834MB이며 이진 단위로 약 795MiB다. 이는 그때 내려받은 파일에 대한 확인 결과이고, 옵션 생략 시 언제나 같은 종류가 선택된다는 보편 규칙은 아니다.

종류를 확실히 지정하려면 저장소 이름 뒤에 `:Q8_0` 또는 `:Q4_0`처럼 붙인다.

### Q5. RAM과 디스크는 서버 종료 후 어떻게 되나?

| 구분 | 쉬운 비유 | 서버 종료 후 |
|---|---|---|
| RAM | 작업하는 책상 | 종료된 프로세스가 사용하던 메모리 회수 |
| 디스크 | 책을 보관하는 책장 | 다운로드한 모델 파일이 남음 |

`Ctrl+C`는 실행을 멈출 뿐 모델 파일을 삭제하지 않는다. 모델을 다시 실행할 때는 저장된 파일을 재사용한다. 다른 앱과 운영체제 캐시도 있으므로 RAM 전체 사용량이 실행 전 숫자와 정확히 같아지는 것은 아니다.

### Q6. 별도 추론을 끄거나 답변을 짧게 만들 수 있나?

현재 코드는 `enable_thinking=False`와 `max_tokens=128`을 사용하고 “2~3문장”을 요청한다. 별도 thinking을 줄이는 것과 생성 답변을 짧게 만드는 것은 다른 조절이다. 후자는 생성할 양을 줄여 총 대기시간을 줄일 수 있지만, 고정된 응답시간을 보장하지는 않는다.

`stream=False`는 완성 후 표시한다. 스트리밍을 사용하면 생성된 조각을 먼저 보여 줄 수 있어 체감 대기시간을 줄일 수 있지만, 계산 전체가 그만큼 빨라지는 의미는 아니다.

### Q7. temperature의 ‘무작위성’은 무슨 뜻인가?

모델이 다음 토큰을 고를 때 후보들의 선택 확률을 조절한다. 낮으면 가능성 높은 후보에 선택이 집중되고, 높으면 덜 유력한 후보도 선택될 여지가 커진다. 값의 범위는 서버 구현에 따라 다르므로 무조건 0~1만 가능하다는 의미는 아니다.

가령 `비가 오면 챙길 것은 ____`에서 후보가 우산·우비·장화라면 낮은 값에서는 우산 쪽으로 더 몰리고, 높은 값에서는 다른 후보의 선택 가능성도 커진다고 생각하면 된다. 설명용 예시이지 실제 모델의 확률을 측정한 것은 아니다.

카페 이름을 지을 때도 낮은 값은 무난한 이름을 반복할 경향, 높은 값은 더 다양한 표현을 고를 경향이 있다. 그러나 특정 결과를 보장하거나 정확도를 보장하지 않는다. **temperature는 생각의 깊이나 추론 시간 제한이 아니다.**

### Q8. GitHub 푸시 후 Streamlit 배포는 어떻게 진행하나?

이미 같은 저장소·브랜치·파일을 배포했다면 GitHub 변경을 감지해 업데이트한다. 새 앱을 배포한다면 다음 순서다.

1. Streamlit Cloud 로그인 → `Create app`.
2. GitHub 저장소와 실제 푸시한 브랜치 선택.
3. Main file path에 실행할 파일 입력. 예: `day16/main2.py`.
4. Advanced settings의 Secrets에 필요한 설정 등록.
5. Deploy를 눌러 배포하고 앱 화면 확인.

Secrets는 TOML 형식이며 문자열 값을 따옴표로 감싼다. 로컬 `.env`가 자동으로 Cloud 설정이 되는 것은 아니다. 배포 환경은 별도이므로 실행 파일 위치 또는 저장소 루트의 의존성 파일에 필요한 패키지를 선언한다. 이는 일반 배포 개념으로 정리한 것이며 오류 해결 과정은 포함하지 않았다. [공식 배포 절차](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [의존성 선언](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

### Q9. `127.0.0.1`이면 Cloud에서 내 Mac으로 연결되는가?

아니다. `127.0.0.1`은 **요청을 보내는 프로그램이 실행 중인 컴퓨터 자기 자신**을 뜻하는 루프백 주소다. `9931`은 그 안에서 서버가 듣는 포트 번호다.

| 요청 코드 실행 위치 | `http://127.0.0.1:9931`의 의미 |
|---|---|
| 내 Mac의 Streamlit | 내 Mac의 llama 서버 |
| Streamlit Cloud | Cloud 서버 내부의 9931번 포트 |

브라우저를 내 Mac에서 열었다고 Streamlit의 Python 요청도 내 Mac에서 나가는 것은 아니다. Cloud에 배포한 Python 코드는 Cloud에서 실행된다. Cloud 앱이 모델을 사용하려면 Cloud에서 접근 가능한 모델 서버 주소가 필요하다.

## 10. 파일들을 직접 실행하며 비교하기

프로젝트 최상위 폴더 `AIO_4_class`에서 실행하는 예시다. 필요한 패키지와 각 외부 서비스 설정은 준비되어 있다고 가정한다.

```bash
# 화면·입력·미리보기
python -m streamlit run day16/main1.py

# AI 서버는 별도 터미널에서 계속 실행
llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF:Q8_0 --alias local-chat

# AI 질문 화면은 다른 터미널에서 실행
python -m streamlit run day16/main2.py

# 화면 배치 시제품 또는 세션 기록 실습: 하나씩 선택해 실행
python -m streamlit run day16/main3.py
python -m streamlit run day16/main4.py
```

DB 저장 실습은 PostgreSQL·Redis가 준비된 상태에서 진행한다. 아래 초기화 명령은 실제 DB 구조를 생성하거나 기존 테이블에 필요한 열·인덱스를 추가한다.

```bash
# DB 구조 준비
python day16/backend.py init

# 백엔드 실행: 별도 터미널에서 유지
python -m uvicorn backend:app --app-dir day16 --reload

# 화면 실행: 다른 터미널
python -m streamlit run day16/main5.py
```

`main5.py`의 `API_BASE_URL`은 위 FastAPI 서버 주소를 가리켜야 한다. `LLAMA_BASE_URL`은 별개의 AI 서버 주소다. 이번 문서 작성에서는 서버나 DB 초기화를 실행하지 않았다.

## 11. 복습용 확인 질문

1. `st.chat_message('assistant')`만 사용하면 실제 AI가 답하는가? → 아니다. 말풍선 영역만 만든다.
2. `main2.py`는 이전 질문을 기억하는가? → 이전 이력을 요청에 보내지 않는다.
3. `main4.py`와 `main5.py`는 기록을 어디에 두는가? → 현재 세션 / PostgreSQL.
4. Redis 세션 만료가 DB 메시지 삭제를 뜻하는가? → 아니다.
5. 같은 내용을 같은 방에 보내면 항상 중복 방지되는가? → 같은 요청 ID를 유지한 재전송이어야 한다.
6. `main5.py`는 Qwen을 호출하는가? → 현재 구현에서는 호출하지 않는다.
7. temperature를 낮추면 별도 추론이 꺼지는가? → 아니다. 서로 다른 설정이다.
8. Cloud의 localhost는 내 Mac인가? → 아니다. Cloud 서버 자신이다.

## 12. 기능 구현에 필요한 Python 함수 기본 문법

이 절의 짧은 예시는 문법 학습용이다. 실제 서버에 요청하거나 DB에 저장하는 완성 코드는 앞 절의 소스 파일에서 확인한다.

### 12-1. 함수란? — 작업에 이름 붙이기

**함수(function)**는 특정 작업을 수행하는 코드를 이름으로 묶은 것이다. 같은 작업을 여러 곳에서 사용하거나 복잡한 작업을 작은 단위로 나눌 때 쓴다.

```python
def greet():
    return '안녕하세요!'

message = greet()
print(message)  # 안녕하세요!
```

- `def`: 함수를 정의하는 키워드.
- `greet`: 함수 이름. 동작을 드러내는 이름을 붙이면 읽기 쉽다.
- `()`: 매개변수를 적는 자리. 받을 값이 없어도 괄호를 쓴다.
- `:`와 들여쓰기: 함수의 본문을 구분한다. 보통 공백 4칸을 사용한다.
- `return`: 함수 실행을 끝내고 결과를 호출한 곳에 돌려준다.
- `greet()`: 함수를 실제로 호출한다.

`def`로 정의하면 함수 본문을 바로 실행하는 것이 아니라 호출할 준비를 한다. `greet`는 함수 객체를 가리키고, `greet()`는 그 함수를 실행한다.

이 폴더의 `connect_db()`는 DB 연결 만들기, `list_messages()`는 메시지 목록 조회처럼 작업별로 이름을 붙인 함수다.

### 12-2. 매개변수와 인수 — 함수에 재료 전달하기

```python
def make_preview(name, question):
    return f'{name} : {question}'

text = make_preview('민수', 'Streamlit은 무엇인가요?')
print(text)  # 민수 : Streamlit은 무엇인가요?
```

**매개변수(parameter)**는 함수를 정의할 때 값을 받을 이름인 `name`, `question`이다. **인수(argument)**는 호출할 때 실제로 전달한 `'민수'`, `'Streamlit은 무엇인가요?'`다.

함수를 요리법이라고 생각하면 매개변수는 재료를 놓을 자리, 인수는 실제 재료다. `main1.py`의 입력값을 받아 미리보기 문장을 만드는 기능을 이렇게 함수로 분리할 수 있다.

### 12-3. 위치 인수와 키워드 인수

```python
# 위치 인수: 순서로 전달
make_preview('민수', '파이썬이란?')

# 키워드 인수: 매개변수 이름으로 전달
make_preview(name='민수', question='파이썬이란?')

# 이름을 지정하면 순서를 바꿔도 된다.
make_preview(question='파이썬이란?', name='민수')
```

일반적인 호출에서는 위치 인수를 먼저, 키워드 인수를 뒤에 쓴다.

```python
make_preview('민수', question='파이썬이란?')
```

`main5.py`의 다음 호출도 같은 원리다.

```python
api('GET', '/messages', session_id=sid)
```

`'GET'`과 `'/messages'`는 위치 인수이고, `session_id=sid`는 키워드 인수다.

### 12-4. 기본값 — 생략했을 때 사용할 값

```python
def make_answer(content, style='간단히'):
    if style == '간단히':
        return f'확인했습니다: {content}'
    return f'1. 메시지 확인: {content}\n2. 다음 단계 준비'

print(make_answer('안녕하세요'))  # 기본값 '간단히' 사용
print(make_answer('안녕하세요', style='단계별'))
```

기본값이 없는 일반 매개변수는 기본값이 있는 매개변수보다 먼저 적는다. 실제 `main5.py`의 함수도 같은 구조다.

```python
def request_json(method, url, payload=None, session_id=None,
                 read_timeout=15, api_key=''):
    # 실제 파일에서는 HTTP 요청을 보낸다.
    pass
```

`method`, `url`은 반드시 전달하고, 나머지는 생략하면 기본값을 사용한다. `None`은 “값이 없음”을 나타내며 빈 문자열 `''`이나 빈 목록 `[]`과는 다른 값이다. `pass`는 이 예시에서 본문을 비워 두기 위한 문장이다.

목록처럼 변경 가능한 값을 기본값으로 직접 두면 호출끼리 같은 객체를 공유할 수 있다. 새 목록이 필요하면 다음처럼 만든다.

```python
def add_message(content, messages=None):
    if messages is None:
        messages = []
    messages.append(content)
    return messages
```

### 12-5. `return`과 `print()`의 차이

```python
def clean_text(text):
    return text.strip()

def show_text(text):
    print(text.strip())

a = clean_text('  안녕  ')  # a는 '안녕'
b = show_text('  안녕  ')   # 터미널에 출력하지만 b는 None
```

`return`은 결과를 다른 코드에서 사용하도록 돌려주고, `print()`는 터미널에 출력한다. 함수에서 `return`을 쓰지 않고 끝나면 `None`을 반환한다. `st.text()`는 웹 화면에 표시하는 역할이다.

```python
cleaned = clean_text(question)
st.text(cleaned)
```

`main2.py`에서 `response.json()`이 돌려준 값을 `data`에 저장하는 것도 반환값을 받아 사용하는 예다.

### 12-6. 함수 안에서 조건을 검사하고 일찍 반환하기

```python
def make_user_message(name, question):
    clean_name = name.strip()
    clean_question = question.strip()

    if not clean_name or not clean_question:
        return None

    return f'{clean_name} : {clean_question}'

preview = make_user_message('  민수 ', ' 파이썬이란? ')
if preview is None:
    print('이름과 질문을 입력하세요.')
else:
    print(preview)
```

`return`이 실행되면 그 호출의 함수 실행은 끝난다. 조건에 맞지 않으면 먼저 반환하는 방식은 나머지 코드를 덜 깊게 들여쓸 수 있게 해 준다.

`if`는 조건 실행, `not`은 참·거짓 뒤집기, `or`는 이 코드에서 “둘 중 하나라도”를 표현한다. 들여쓰기가 달라지면 실행 범위도 달라진다. `main4.py`에서 저장 코드가 `else` 안에 있는 점이 실제 동작을 결정하는 이유다.

### 12-7. 딕셔너리와 리스트를 받아서 반환하기

채팅 기록은 여러 메시지를 순서대로 담기 때문에 리스트를 쓰고, 메시지 한 개의 속성은 딕셔너리로 묶는다.

```python
def make_message(role, content):
    return {'role': role, 'content': content.strip()}

messages = []
messages.append(make_message('user', ' 안녕하세요 '))
messages.append(make_message('assistant', ' 반갑습니다 '))

for message in messages:
    print(message['role'], message['content'])
```

- `[]`: 리스트. 순서대로 여러 값을 보관한다.
- `{키: 값}`: 딕셔너리. 이름으로 값을 조회한다.
- `.append()`: 리스트 끝에 항목을 추가한다. 반환값은 `None`이다.
- `for ... in ...`: 각 항목을 하나씩 꺼내 반복한다.
- `message['content']`: 딕셔너리에서 내용 조회.

이 구조가 `main4.py`의 대화 이력과 `main2.py`의 AI 요청 `messages`에 사용된다.

### 12-8. 일반 함수·메서드·라이브러리 함수 구분

| 표현 | 종류 | 의미 |
|---|---|---|
| `len(messages)` | Python 내장 함수 | 항목 개수 |
| `make_message('user', '안녕')` | 직접 정의한 함수 | 메시지 딕셔너리 생성 |
| `question.strip()` | 문자열 객체의 메서드 | 양끝 공백 제거 |
| `messages.append(item)` | 리스트 객체의 메서드 | 항목 추가 |
| `st.text('안녕')` | Streamlit 모듈의 함수 | 웹 화면에 텍스트 표시 |
| `requests.post(url, json=payload)` | requests 모듈의 함수 | HTTP POST 요청 |
| `response.json()` | 응답 객체의 메서드 | JSON 응답을 Python 자료형으로 변환 |

점(`.`)은 객체나 모듈 안의 이름에 접근하는 문법이다. 점이 붙었다고 모두 같은 종류는 아니다. `st.session_state`는 속성 접근이고, `st.session_state['messages']`는 그 안의 키로 값에 접근하는 형태다.

### 12-9. 타입 힌트 — 어떤 값을 기대하는지 적기

```python
def make_message(role: str, content: str) -> dict:
    return {'role': role, 'content': content.strip()}
```

`role: str`은 문자열을 기대한다는 표시이고, `-> dict`는 딕셔너리를 반환한다는 표시다. **일반 Python 함수의 타입 힌트만으로 실행 중 값이 자동 검사되지는 않는다.** IDE나 검사 도구가 코드를 이해하는 데 도움을 준다.

반면 FastAPI와 Pydantic은 선언된 타입을 요청 검사에 실제 활용한다.

```python
class SessionCreate(BaseModel):
    conversation_id: UUID

@app.post('/sessions', status_code=201)
def create_session(body: SessionCreate):
    # 실제 코드에서는 DB를 확인하고 Redis에 세션을 만든다.
    ...
```

`class`는 자료와 동작의 구조를 정의한다. 여기서는 `BaseModel`을 바탕으로 요청 본문의 형태를 정한다. `body.conversation_id`처럼 속성으로 읽는다. 위 예시의 `...`은 생략한 구현을 나타낸다.

실제 코드의 `str | None`은 “문자열 또는 None”이라는 타입 표현이다.

### 12-10. 데코레이터 — 함수에 역할 연결하기

```python
@app.get('/conversations')
def list_conversations():
    # 실제 파일에서는 DB 조회 결과를 반환한다.
    return []
```

`@...`는 데코레이터 문법이다. 함수 정의 시 함수 객체를 데코레이터에 전달해 등록하거나 동작을 감쌀 수 있다. 위 FastAPI 예시에서는 GET 요청 경로와 함수를 연결한다.

사용자가 목록 API를 호출하면 FastAPI가 `list_conversations()`를 실행한다. **경로 등록 시점과 요청 처리 시점은 다르다.** `status_code=201` 같은 값은 이 경우 경로 등록에 전달한 키워드 인수다.

### 12-11. `with ... as ...` — 시작·종료를 관리하는 구문

```python
with requests.post(url, json=payload, timeout=(5, 30)) as response:
    response.raise_for_status()
    data = response.json()
```

`with`는 함수 정의 문법이 아니라 **컨텍스트 관리자**를 사용하는 구문이다. 블록에 들어가고 나올 때 필요한 처리를 객체에 맡긴다. 위에서는 요청 응답 자원을 사용한 뒤 정리한다. `as response`는 블록에서 사용할 객체에 이름을 붙인다.

```python
with st.chat_message('user'):
    st.text('안녕하세요')
```

Streamlit에서는 블록 안에 그리는 요소를 해당 말풍선 영역에 배치한다. 같은 `with` 문법이지만 구체적인 시작·종료 동작은 대상 객체에 따라 다르다.

### 12-12. 지역변수와 바깥 변수

```python
API_BASE_URL = 'http://127.0.0.1:8000'

def make_url(path):
    url = API_BASE_URL + path
    return url

print(make_url('/messages'))
```

`API_BASE_URL`은 모듈 수준에서 정의한 변수이고, `url`과 `path`는 해당 함수 호출 안에서 사용하는 지역 이름이다. 함수 밖에서 `url`을 그대로 사용할 수는 없으므로 필요한 결과를 `return`으로 받는다.

`main5.py`의 `api()`는 바깥의 `API_BASE_URL`을 읽어 URL을 만든다. 함수에서 바깥 값을 읽는 것과 그 변수에 새 값을 대입하는 것은 구분해야 한다.

### 12-13. 함수를 조합해서 기능 만들기

큰 기능은 보통 작은 함수 여러 개를 연결해서 만든다.

```python
def clean_text(text):
    return text.strip()

def make_payload(question, model='local-chat'):
    return {
        'model': model,
        'messages': [
            {'role': 'system', 'content': '한국어로 짧게 답하세요.'},
            {'role': 'user', 'content': clean_text(question)},
        ],
        'max_tokens': 128,
        'stream': False,
    }

payload = make_payload('  파이썬 함수란?  ')
print(payload['messages'][1]['content'])  # 파이썬 함수란?
```

이 예시는 요청 데이터를 만들기만 하므로 실제 AI 답변은 생성하지 않는다. `main2.py`에서는 이런 딕셔너리를 `requests.post(..., json=payload)`로 보내고, `main5.py`에서는 `api()`가 `request_json()`을 호출해 공통 통신 작업을 맡긴다.

### 12-14. 직접 실행과 import 구분

```python
def main():
    print('시작합니다.')

if __name__ == '__main__':
    main()
```

`python 파일명.py`로 직접 실행하면 조건이 참이 되어 `main()`을 호출한다. 다른 파일에서 `import`하면 이 조건 안의 호출은 실행하지 않는다. 다만 모듈 최상위의 다른 코드까지 전부 실행하지 않는다는 뜻은 아니다.

`backend.py`는 이 문법으로 DB 초기화·검증용 명령과 서버용 import를 구분한다.

### 12-15. 기본 문법을 실제 기능과 연결해 복습하기

| 만들 기능 | 관련 문법 | 실제 코드 |
|---|---|---|
| 입력 정리 | 메서드 호출, 변수 대입 | `name.strip()` |
| 입력 검사 | `if`, `not`, `or` | `main1.py` |
| 대화 문자열 만들기 | f-string | `f'{name} : {question}'` |
| 메시지 표현 | 딕셔너리·리스트 | `{'role': ..., 'content': ...}` |
| 이력 쌓기·출력 | `.append()`, `for` | `main4.py` |
| 공통 통신 묶기 | `def`, 기본값, 반환값 | `request_json()`, `api()` |
| 서버 요청 처리 | 데코레이터, 타입 힌트 | `backend.py` API 함수 |
| 응답·연결 정리 | `with ... as ...` | HTTP 응답과 DB 연결 |
| 초기화 명령 분리 | `__name__` 조건 | `backend.py` 실행 진입점 |

연습할 때는 “무엇을 입력받는가 → 무슨 처리를 하는가 → 무엇을 반환하는가”를 한 문장으로 적고 함수로 옮겨 보자. 예를 들어 `clean_text()`는 “문자열을 받아 양끝 공백을 제거한 문자열을 반환한다”라고 설명할 수 있다.
