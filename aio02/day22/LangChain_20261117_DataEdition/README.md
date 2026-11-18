# 상품 데이터로 배우는 LangChain·프롬프트·LCEL

**2026-11-17 · 단일 에이전트 추론 및 AI 오케스트레이션 · U2-01**

상품 설명에서 근거를 찾아 고객 문의에 대한 한국어 안내 초안을 만드는 서비스다. 가방의 노트북 수납 여부처럼 설명에서 답할 수 있는 내용과 재고·배송일처럼 추가 확인이 필요한 내용을 구별한다. Python의 dict·함수·파일 처리를 메시지 템플릿과 LCEL 연결에 적용한다.

차시당 50분·총 400분은 설계 가정이며 휴식은 별도다. 각 차시에 이론, 데이터 흐름 도식, 실행 코드, 결과 해설, 화면 캡처 방법을 담았다. HTML은 차시 이동·코드 복사·프롬프트 미리보기를 제공하고, PDF는 인쇄용이다. `course/01_README.md`~`08_README.md`는 코드를 만들기 위한 차시별 이론서다.

| 차시 | 핵심 이론 | 실습 결과 |
|---|---|---|
| 1 | 환경·JSON·데이터 출처 | 상품 20개 읽기, 원문 화면 저장 |
| 2 | 메시지 역할·템플릿 변수 | 상품 설명을 메시지로 렌더링 |
| 3 | Role·Instruction·Context | 같은 상품 맥락의 프롬프트 3종 |
| 4 | Runnable·자료형·순차 합성 | 수동 실행과 LCEL 실행 |
| 5 | 검증·정규화·책임 경계 | RunnableLambda 전처리 |
| 6 | invoke·batch·stream | 일괄 처리, 스트리밍, Groq 선택 |
| 7 | 조건 통제·응답 해석 | 상품·질문·모델을 고정한 비교 |
| 8 | CSV 계약·오류 분리·저장 | 문의 CSV → 초안 JSONL → 증빙 화면 |

## 실행환경과 설치

Python 3.11 이상을 가정하며 제작 환경은 Python 3.12다. ZIP 압축을 풀고 `app`, `sessions`, `requirements.txt`가 있는 프로젝트 루트에서 실행한다. 실습 파일의 경로는 압축 해제 위치를 기준으로 계산한다.

Windows CMD:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m sessions.s01
```

PowerShell에서 활성화가 제한되면 위처럼 가상환경 Python을 직접 호출한다. 이후 명령의 `python`을 `.\.venv\Scripts\python.exe`로 바꾸면 된다. 설치된 Python 버전이 3.11이라면 `py -3.11`로 환경을 만든다.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## API 설정과 비용 범위

`.env`의 `OPENAI_API_KEY`, `OPENAI_MODEL`을 제공받은 계정의 키와 사용 가능한 모델 ID로 바꾼다. `LLM_PROVIDER=openai`가 기본이다. `LLM_TEMPERATURE`는 미설정일 때 전달하지 않으며 해당 파라미터를 지원하는 모델에서만 지정한다. 키는 코드나 결과 화면에 표시하지 않는다.

Groq 선택 실습은 `python -m pip install -r requirements-groq.txt` 후 `LLM_PROVIDER=groq`, `GROQ_API_KEY`, `GROQ_MODEL`을 지정한다. 무료 플랜에도 모델별·조직별 한도가 있다. 두 공급자의 모델 지원·가격·한도는 수업 전 공식 콘솔에서 확인한다. 공급자 전환은 자동으로 일어나지 않는다.

1~3차시는 모델 요청이 없다. 4~5차시는 기본 명령당 1회, 6차시 batch는 3회·stream은 1회, 7차시는 기본 9회(최대 27회), 8차시는 기본 최대 3회다. 정상 경로 기본 실행을 한 번씩 하면 총 17회이며 수동·스트리밍·재실행·선택 실습은 추가다. 출력 상한은 요청당 500토큰 설정이며 모델별 지원은 별도로 확인한다. 자동 재시도는 0회다. 429가 나면 계정 한도를 확인하고 대기 후 수동으로 재실행한다. `batch`는 입력당 호출이 발생하며 공급자의 할인 Batch API와 다르다.

## 데이터 준비와 실행

포함 데이터는 **Fake Store API 유래 공개 가공 표본** 20개다. 제작 환경에서 원본 API가 차단되어 직접 수집하지 못했다. 가격·통화는 검증하지 못해 모델 맥락에서 제외했다. 각 결과 화면에 데이터 출처·파일 해시·취득 방식과 모델 실행 방식을 표시한다. 기관에서 원본 직접 수집 결과를 요구하면 다음 명령으로 학생 환경에서 취득한 뒤 해당 파일을 사용한다.

```bash
python -m app.fetch_products
python -m sessions.s01 --data data/products_live.json
```

직접 수집이 안 되면 브라우저에서 정상 저장한 JSON을 `python -m app.fetch_products --import-file 저장한파일.json`으로 가져온다. 이 방식은 출처를 독립 검증한 직접 수집과 구별된다. 데이터 파일을 바꾸면 8차시 CSV의 id도 실제 목록의 `api-1` 등으로 맞춘다.

모델 키 없이 구조를 확인할 때:

```bash
python -m sessions.s01
python -m sessions.s02
python -m sessions.s03
python -m sessions.s04 --mock
python -m sessions.s05 --mock
python -m sessions.s06 --mock
python -m sessions.s07 --mock
python -m sessions.s08 --mock --input data/requests.csv
```

모의 모드는 실제 LangChain 템플릿·체인을 실행하고 모델만 고정 응답으로 대체한다. 모든 질문에 같은 문장이 나오므로 의미 품질 비교에 사용할 수 없다. 실제 API 실행은 `--mock`을 빼고 수행한다. 모델 응답은 검토용 초안이다.

## 결과 화면과 캡처

실행하면 `reports/s01_report.html`~`s08_report.html`과 JSON 기록을 저장한다. 파일을 브라우저에서 열면 상품 원문·질문·처리 결과를 나란히 볼 수 있다. Windows CMD에서는 `start reports\s08_report.html`, PowerShell에서는 `Start-Process .\reports\s08_report.html`을 실행한다. 실행할 때 같은 차시 보고서는 덮어쓰므로 보관할 결과는 먼저 복사한다.

데이터 출처, 추적 id, 질문과 결과, 실행 모드가 읽히도록 캡처해 `evidence/U2-01_s08_D01_result.png`로 저장한다. 파일명은 제안이며 기관의 공식 양식이 아니다. 포함된 예시 PNG는 공개 가공본·모의 모델 실행 결과 HTML의 인쇄 렌더링이다. 학생의 원본 API·원격 모델 실행 증빙을 대신하지 않는다.

## 코드 검증과 후속 연결

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

입력·상품 스키마·메시지·LCEL·일괄·스트리밍·보고서의 소프트웨어 검사다. 11월 18일에는 GSM8K와 추론 전략 비교로 이어진다. 이번에는 CoT·Structured Output·Tool Calling·LangGraph 구현을 추가하지 않는다.
