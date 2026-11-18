# 03. 버전별 실행 방법

모든 명령은 터미널에서 실행합니다. Python 소스 안에 붙여 넣는 명령이 아닙니다. 기존 모델이 있다는 전제로 다운로드는 실행하지 않습니다. 아래는 현재 코드에서 확인한 실행 구성으로, 이 문서 작성 중 실제 서버를 띄워 검증한 기록은 아닙니다.

## 1. 공통 준비

새 터미널을 열었다면 폴더와 환경을 먼저 선택하세요.

```bash
cd /Users/imijeong/Downloads/AIO_4_class/day17
conda activate py313_arm
```

필요한 패키지를 준비하는 명령입니다. 이미 조건에 맞게 설치되어 있으면 그대로 사용합니다.

```bash
python -m pip install torch==2.8.0
python -m pip install -r requirements.txt -r backend/requirements.txt
python -m pip install requests
```

`-m`은 선택한 Python 환경의 모듈을 실행합니다. `pip`은 설치 도구, `-r 파일`은 그 파일의 패키지 목록을 읽으라는 뜻입니다. 현재 requirements에 명시되지 않은 `torch`와 `requests`는 따로 적었습니다.

프로젝트 루트의 기존 `.env`에 필요한 키를 설정합니다. 다른 설정을 지우거나 파일 전체를 덮어쓰지 마세요.

```dotenv
HF_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
MODEL_DIR=/Users/imijeong/Downloads/AIO_4_class/day17/models/qwen2.5-0.5b-instruct
BACKEND_URL=http://127.0.0.1:8000
```

위 `MODEL_DIR`는 이 작업공간의 기존 모델을 가리키는 **예시 절대 경로**입니다. 이번 노트는 실제 `.env`를 읽거나 수정하지 않았습니다. 환경변수에 같은 키가 이미 설정되어 있으면 코드의 `override=False` 때문에 그 값이 우선할 수 있습니다.

### 왜 절대 경로를 예시로 쓰나요?

현재 코드별 상대 경로의 기준이 다르기 때문입니다.

| 코드 | 상대 `MODEL_DIR`의 기준 폴더 |
|---|---|
| `main1.py` | `day17` |
| `backend/backend.py` | `day17` |
| `stream_backend/backend.py` | `day17/stream_backend` |
| `dig_context_backend/backend.py` | `day17/dig_context_backend` |

공통 절대 경로를 사용하면 소스를 변경하거나 모델을 복사하지 않고 같은 모델 파일을 사용합니다. 상대 경로를 유지하려면 앞의 두 코드는 `models/qwen2.5-0.5b-instruct`, 뒤의 두 코드는 `../models/qwen2.5-0.5b-instruct`가 맞습니다. 하나의 공통 `.env`에 서로 다른 상대 값을 동시에 지정할 수 없으므로 여기서는 절대 경로로 통일하는 방법을 안내합니다.

## 2. 독립 채팅 앱

터미널 한 개에서 실행합니다.

```bash
python -m streamlit run main1.py
```

브라우저: http://localhost:8501

화면과 모델 실행을 이 앱이 모두 담당합니다. Uvicorn 서버는 필요하지 않습니다. 질문을 보내면 완성된 답변이 표시됩니다.

## 3. 화면·서버 분리 앱: `backend/`

터미널 1에서 서버를 실행합니다.

```bash
python -m uvicorn backend.backend:app --reload
```

터미널 2에서도 `day17`로 이동하고 `py313_arm`을 활성화한 뒤 화면을 실행합니다.

```bash
python -m streamlit run backend/main.py
```

- 채팅 화면: http://localhost:8501
- API 테스트 문서: http://127.0.0.1:8000/docs
- 실제 질문 API: `POST /chat`

`backend.backend:app`에서 앞의 `backend`는 폴더, 뒤의 `backend`는 `backend.py`, `app`은 파일 안의 FastAPI 객체 이름입니다. `--reload`는 개발 중 파일 변경 시 서버를 다시 불러오는 옵션입니다.

## 4. 스트리밍 앱: `stream_backend/`

다른 버전의 서버·화면을 실행 중이면 각각 `Ctrl + C`로 종료한 뒤 같은 포트를 사용하세요.

터미널 1:

```bash
python -m uvicorn stream_backend.backend:app --reload
```

터미널 2:

```bash
python -m streamlit run stream_backend/main.py
```

화면 주소는 http://localhost:8501 입니다. 답변이 생성되는 동안 조각이 이어서 표시됩니다. 실제 질문 API는 `POST /chat/stream`이고 요청 본문은 `{"prompt":"질문"}` 형태입니다.

## 5. 대화 이력 앱: `dig_context_backend/`

터미널 1:

```bash
python -m uvicorn dig_context_backend.backend:app --reload
```

터미널 2:

```bash
python -m streamlit run dig_context_backend/main.py
```

화면 주소는 http://localhost:8501 입니다. 앞 질문과 답변을 함께 전달합니다. “광합성이 뭐야?”를 물은 뒤 “그럼 밤에도 가능해?”로 후속 질문을 해보세요. “새 대화” 버튼은 현재 이력을 비웁니다.

이 버전도 `POST /chat/stream`을 쓰지만 본문은 `{"messages":[...]}`입니다. 스트리밍 단일 질문 버전의 `{"prompt":...}`와 다릅니다. **서버와 화면은 반드시 같은 폴더의 쌍을 사용하세요.**

## 6. `yield` 원리만 실험

```bash
python main_yield.py
```

브라우저와 모델은 필요 없습니다. 터미널에서 리스트 반환과 값별 전달의 차이를 확인합니다. 대기 코드 때문에 전체 예제는 대략 6초가 걸립니다.

## 7. 명령 선택표

| 원하는 일 | 선택 |
|---|---|
| 가장 간단한 채팅 화면 | `main1.py` 단독 |
| API와 화면의 역할 실습 | `backend/` 두 파일 |
| 생성 중 답변 읽기 | `stream_backend/` 두 파일 |
| 앞 대화를 참고하는 채팅 | `dig_context_backend/` 두 파일 |
| `yield` 실행 순서 관찰 | `main_yield.py` |

분리 앱은 화면만 실행하면 AI 서버가 준비되지 않습니다. 서버의 `Application startup complete`를 확인한 뒤 질문하세요. 패키지 설치는 모델 다운로드와 별개이며, 모델 파일을 공유해도 각 서버는 실행 시 메모리에 모델을 로딩합니다.
