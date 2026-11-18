# Day21 핵심 학습 정리

분석 대상: `lesson01~08/main.py`와 각 차시의 교안·패키지 목록.
**배운 것: 개인화 여행 챗봇을 만들고 → 평가를 수집·저장하고 → 실패에 대응하고 → 배포 후 개선하는 흐름.**

## 1. 차시별 배운 내용

| 소스 | 학습 내용 | 핵심 함수·도구 |
| --- | --- | --- |
| lesson01 | 여행 취향을 프롬프트에 반영하고 답변을 실시간 표시 | `build_input()`, `st.session_state`, `batch_text()` |
| lesson02 | 답변마다 ID를 붙여 평가와 이유 연결 | `uuid4()`, `show_feedback()`, 딕셔너리 |
| lesson03 | 저장 동의를 받고 필요한 평가 정보만 JSONL로 내보내기 | `make_record()`, `json.dumps()`, `st.download_button()` |
| lesson04 | Supabase의 PostgreSQL에 평가 영구 저장 | `psycopg.connect()`, `conn.execute()`, SQL |
| lesson05 | 실패한 평가를 보관하고 같은 ID로 재시도 | `pending_feedback`, `persist_record()`, UPSERT |
| lesson06 | 질문 길이·호출 간격·세션별 요청 횟수 제한 | `len()`, `time.monotonic()`, `request_error()` |
| lesson07 | 배포용 표시와 환경설정, Streamlit Cloud 배포 절차 | `release_label()`, Secrets, GitHub |
| lesson08 | 개선 이유 집계와 프롬프트 버전별 평가 | `show_feedback_summary()`, `improvement_policy()` |

## 2. 꼭 기억할 개념과 정의

- **세션 상태**: 현재 브라우저 연결에서 유지하는 임시 데이터. Streamlit은 상호작용 시 스크립트를 다시 실행하므로 `st.session_state`로 대화·프로필을 유지한다. 새 연결이나 앱 재시작을 넘는 보관은 DB가 맡는다.
- **프롬프트**: AI에게 전달하는 지침과 입력. 이 코드는 기본 지침 + 프로필 + 여행 규칙 + 개선 지침을 만들고, 이전 대화와 현재 질문을 함께 보낸다.
- **스트리밍·제너레이터**: 답변 조각을 도착하는 대로 처리하는 방식. `yield`는 값을 하나 전달하고 실행을 잠시 멈춘다. `batch_text()`는 조각을 모아 화면 갱신 횟수를 줄이고 공백·줄바꿈을 보존한다.
- **상태 전이**: 요청을 대기 → 성공 또는 실패로 관리하는 것. 정상 완료한 답변만 `history`에 추가하고, 실패 시 부분 답변을 `pending`에 남겨 재시도한다.
- **깊은 복사**: `deepcopy()`로 중첩 딕셔너리까지 복사한다. 이후 프로필을 바꿔도 요청·답변 생성 당시의 조건을 유지한다.
- **멱등성·UPSERT**: 같은 평가를 재전송해도 행이 중복되지 않게 하는 것. `message_id` 기본키와 `ON CONFLICT ... DO UPDATE`로 같은 답변의 평가를 갱신한다.
- **최소 수집·버전 기록**: 동의한 평가와 선택형 프로필·버전 등을 저장한다. 질문·답변 전문은 피드백 DB에 저장하지 않으며, 나중에 평가해도 답변 생성 당시 버전을 사용한다.

## 3. 기능을 구현할 때 무엇을 사용할까?

| 구현할 기능 | 패키지·기본 사용법 |
| --- | --- |
| 채팅 입력·답변 표시 | `streamlit`: `st.chat_input()`, `with st.chat_message("assistant"):` |
| 선택값을 한 번에 적용 | `with st.form("profile_form"):` + `st.form_submit_button()` |
| 화면 재실행 후 값 유지 | `st.session_state.setdefault("history", [])`; `st.rerun()`은 즉시 재실행 |
| AI 호출 | `openai`의 `OpenAI(api_key=..., base_url=...)` → `client.responses.create(..., stream=True)` |
| 환경변수 읽기 | `python-dotenv`의 `load_dotenv(override=False, interpolate=False)` + `os.getenv("GROQ_API_KEY")` |
| DB 연결·저장 | `psycopg`: `with psycopg.connect(...) as conn:` → `conn.execute(sql, params)` |
| 프로필을 DB JSONB로 전달 | `from psycopg.types.json import Jsonb` → `Jsonb(profile)` |
| ID·저장 시각·소요 시간 | `str(uuid4())`, `datetime.now(timezone.utc).isoformat()`, `time.perf_counter()` |
| JSONL 다운로드 | `"\n".join(json.dumps(r, ensure_ascii=False) for r in records)` → 다운로드 버튼 |

`os`, `time`, `copy`, `uuid`, `datetime`, `json`은 파이썬 표준 라이브러리라 별도 설치하지 않는다.
`openai`는 이 코드에서 **Groq의 OpenAI 호환 API를 호출하는 SDK**로 사용한다.

## 4. 소스에서 반복되는 기본 파이썬 문법

```python
# 함수·조건문·반환: 조건이 맞으면 True, 아니면 False
def requires_reason(rating):
    return rating == 0

# 딕셔너리: 키로 저장·조회, get()은 키가 없을 때 기본값 사용
record = {"rating": 0, "reason": "조건 미반영"}
reason = record.get("reason", "선택 없음")

# 리스트 컴프리헨션: 조건에 맞는 평가만 새 리스트로 만들기
negative = [r for r in records if r["rating"] == 0]

# 반복문·집계: 이유별 개수를 1씩 늘리기
counts = {}
for r in negative:
    counts[r["reason"]] = counts.get(r["reason"], 0) + 1

# 다중 반환·언패킹: 반환한 두 값을 각각 받기
version, improvement = improvement_policy()

# 슬라이싱·문자열 포맷: 최근 40개 메시지, 소수점 둘째 자리
recent = history[-40:]
label = f"응답 시간: {elapsed:.2f}초"
```

추가로 `try`는 실행, `except`는 실패 처리, `else`는 성공 처리, `finally`는 성공·실패와 관계없는 정리에 쓴다. `raise`는 오류를 발생시키거나 다시 전달한다. `with`는 자원 정리 또는 Streamlit UI 영역 지정에 사용한다. `if __name__ == "__main__":`는 파일을 직접 실행할 때만 `main()`을 호출한다.

## 5. 실제 코드 기준 주의점

- 방문지는 현재 모든 차시에서 하루 **4곳 이내**라는 지침이다. 여유로운 스타일만 2곳으로 바꾸는 것은 교안의 수정 과제이며, 프롬프트는 출력의 강제 검증 장치가 아니다.
- 부정 평가 이유는 **lesson02만 필수**(`rating == 0`)이고 lesson03~08은 `requires_reason()`이 `False`를 반환한다. 피드백 재시도 횟수 제한도 현재 `retry_allowed()`가 항상 `True`여서 없다.
- lesson06~08은 **질문 1,000자·호출 간격 3초·연결당 30회**로 제한한다. 실패한 API 시도도 횟수에 포함되며 새 연결에서는 초기화된다.
- DB SQL 값은 문자열에 끼워 넣지 않고 **`%s` 자리표시자 + 매개변수 튜플**로 전달한다. RLS는 행 접근 제어이며 코드에서는 공개 역할의 권한도 회수한다.
- lesson08 화면의 집계·다운로드는 **현재 연결에서 저장한 평가만** 다룬다. 전체 DB 집계는 별도 SQL로 확인하며, 도움 비율은 `도움 평가 수 / 평가된 답변 수 × 100`이다. 미평가 답변은 분모에서 제외한다.
- 피드백은 모델을 자동 학습시키지 않는다. 사람이 원인을 보고 `improvement_policy()`의 지침·버전을 수정한다. API 키·DB 주소는 `.env` 또는 배포 Secrets에 두고 Git에 올리지 않는다.

## 6. 실행 명령

프로젝트 루트에서 마지막 차시를 실행하는 예:

```bash
python -m pip install -r day21/lesson08/requirements.txt
python -m streamlit run day21/lesson08/main.py
```

필수 설정은 `GROQ_API_KEY`, `DATABASE_URL`. 새 DB는 테이블 준비가 필요하며, 관련 절차는 [BACKEND_GUIDE.md](BACKEND_GUIDE.md), 배포는 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)를 참고한다.
