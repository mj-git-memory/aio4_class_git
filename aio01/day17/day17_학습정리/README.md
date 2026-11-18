# day17 학습 노트: 내 컴퓨터에서 동작하는 AI 대화 앱

작성 기준: 2026-11-07에 저장된 day17 소스코드와 이 채팅의 학습 질문.

이 자료는 프로그래밍을 처음 배우는 분을 위해 작성했습니다. 실행 에러에 관한 과거 질문과 답변은 제외했습니다. 과거 설명 중 파일 변경으로 달라진 내용은 현재 코드 기준으로 바로잡았습니다. 실제 `.env` 값이나 비밀키는 복사하지 않았습니다.

## 읽는 순서

1. [01 — 무엇을 만드는 코드인가? 개념과 활용 예시](01_concepts.md)
2. [02 — 패키지와 주요 함수 문법](02_packages_and_syntax.md)
3. [03 — 버전별 실행 방법](03_run_guide.md)
4. [04 — 이전 학습 질문과 답변](04_learning_qa.md)

## 전체 지도

| 파일 | 만들려는 기능 | 답변 표시 | 이전 대화 전달 |
|---|---|---|---|
| `../main1.py` | 화면과 모델 실행을 한 앱에서 처리 | 완성 후 한꺼번에 | 없음 |
| `../main_yield.py` | `return`과 `yield`의 차이를 숫자로 실험 | 터미널 출력 | 해당 없음 |
| `../backend/main.py` | API에 질문을 보내는 화면 | 완성 후 한꺼번에 | 없음 |
| `../backend/backend.py` | 단일 질문을 처리하는 AI 서버 | JSON 한 개 반환 | 없음 |
| `../stream_backend/main.py` | 생성 중인 답변을 받아 표시하는 화면 | 조각이 도착할 때마다 | 없음 |
| `../stream_backend/backend.py` | 생성 중인 답변을 전송하는 AI 서버 | 줄 단위 JSON 스트림 | 없음 |
| `../dig_context_backend/main.py` | 이전 대화를 저장하고 함께 보내는 화면 | 조각이 도착할 때마다 | 있음 |
| `../dig_context_backend/backend.py` | 대화 이력을 입력받는 AI 서버 | 줄 단위 JSON 스트림 | 요청에 담긴 이력을 사용 |

아래 그림의 각 줄은 하나의 실행 방식입니다. 세 방식을 동시에 실행할 필요는 없습니다.

```text
독립 앱:       브라우저 ↔ main1.py ↔ 로컬 모델
분리 앱:       브라우저 ↔ backend/main.py ↔ backend/backend.py ↔ 로컬 모델
스트리밍 앱:   브라우저 ↔ stream_backend/main.py ↔ stream_backend/backend.py ↔ 로컬 모델
대화 이력 앱:  브라우저 ↔ dig_context_backend/main.py ↔ dig_context_backend/backend.py ↔ 로컬 모델
```

`main.py`라는 이름 자체가 화면을 뜻하지는 않습니다. 현재 세 하위 폴더의 `main.py`는 Streamlit 화면이고, `backend.py`는 FastAPI 서버입니다.

이 노트는 코드 동작을 읽고 설명한 자료입니다. 모델을 실제로 실행하거나 응답 품질·처리 속도를 측정한 결과는 아닙니다.
