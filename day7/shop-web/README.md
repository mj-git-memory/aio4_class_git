# 장바구니 밖의 Python

상품 상세 화면에서 재고·배송·리뷰를 조회하며 배우는 동기/비동기 앱입니다.
단순 애니메이션 대신 FastAPI와 HTTPX로 실제 로컬 HTTP 요청을 보내고 측정합니다.
기존 `main.py`, `probe.py`, `probe-web`은 수정하지 않습니다.

## 실행

`fastapi`, `uvicorn`, `httpx`가 설치된 Python 환경(예: `conda activate py313`)에서,
프로젝트 루트 `AIO_4_class`를 기준으로 실행합니다.

```bash
python -m uvicorn shop_lab:app --app-dir day7/shop-web --reload --port 8010
```

화면: http://127.0.0.1:8010

API 문서: http://127.0.0.1:8010/docs

패키지가 없다면 `python -m pip install -r day7/shop-web/requirements.txt`로 설치합니다.
`--app-dir day7/shop-web`는 옮긴 `shop_lab.py`를 찾을 폴더를 지정합니다.
`--reload`는 코드 수정 시 자동 재시작하는 옵션이며, 종료는 `Ctrl+C`입니다.

이미 `day7/shop-web` 폴더 안에 있는 터미널이라면 다음처럼 실행합니다.

```bash
python -m uvicorn shop_lab:app --reload --port 8010
```

포트 충돌 시 `--port 8011`로 바꾸고 브라우저도 해당 포트로 접속하세요.
단일 worker로 실행해야 ‘잘못된 비동기’가 다른 요청을 지연시키는 현상이 명확합니다.
정적 HTML 파일을 직접 열거나 `http.server`로 실행하면 API 실험은 작동하지 않습니다.

## 직접 해보기

1. 기본 ‘비동기 · 동시’를 실행합니다. 약 1.2초 뒤 세 정보가 표시됩니다.
2. ‘동기 · 순차’ 또는 ‘비동기 · 순차’로 바꿉니다. 약 2.7초 걸립니다.
3. 대기 배율을 2×로 바꾸고 ‘잘못된 비동기’를 실행합니다.
4. 실행 중 ‘서버 응답 확인’을 누릅니다. /api/health까지 지연되는지 확인합니다.
5. ‘동기 I/O 개선’에서 같은 실험을 반복합니다. 이벤트 루프가 응답할 수 있습니다.
6. ‘6가지 모두 비교’로 같은 배율에서 측정 기록을 모읍니다.
7. 개념 노트에서 코루틴·Task·await·gather·async with와 오류 원인을 확인합니다.

## 실행 구조와 예상값 (기본 1×)

브라우저 → `/api/run` → HTTPX → `/api/service/{stock,delivery,reviews}`.
각 API의 0.6/0.9/1.2초 대기는 외부 I/O를 흉내 낸 것입니다. 외부 인터넷 연결은 필요 없습니다.

| 모드 | 클라이언트 | 서버의 대기 | 예상 |
| --- | --- | --- | --- |
| 동기 · 순차 | 일반 def + Client, 순서대로 요청 | asyncio.sleep | 약 2.7초 |
| 비동기 · 순차 | AsyncClient, 하나씩 await | asyncio.sleep | 약 2.7초 |
| 비동기 · 동시 | AsyncClient + gather | asyncio.sleep | 약 1.2초 |
| Task · 동시 | 모두 create_task 후 await | asyncio.sleep | 약 1.2초 |
| 잘못된 비동기 | AsyncClient + gather | async def 안에서 time.sleep 직접 호출 | 약 2.7초 |
| 동기 I/O 개선 | AsyncClient + gather | to_thread로 동기 I/O 함수 실행 | 약 1.2초 |

동기 클라이언트는 실험 서버에서 `to_thread(sync_requests, ...)`로 실행합니다.
그 안의 세 요청은 동기·순차 실행이지만 서버 이벤트 루프를 막지 않습니다.
‘잘못된 비동기’는 서버 API 자체가 이벤트 루프를 막는 별도의 문제입니다.

타임라인 막대는 서버 API 처리 시작부터 종료까지의 실측 구간이며 응답 후 표시됩니다.
전체 소요 시간에는 HTTP 연결·응답 처리 시간이 포함됩니다. 프런트엔드 경과 시간은 브라우저 시계입니다.
비교 표의 ‘다른 요청’ 열은 코드에 따른 설명입니다. 실제 지연은 health 버튼의 왕복 시간을 확인하세요.
health를 작업 종료 후 누르면 blocking 모드에서도 빠를 수 있습니다.
여러 탭이나 다른 API 요청을 겹치면 측정값에 영향을 줍니다. 비교는 한 탭에서 실행하세요.
‘모두 비교’에서는 각각의 실험을 순차 실행합니다. 실험 내부의 요청 방식이 비교 대상입니다.

## 질문별 핵심

- **동기란?** 호출이 끝날 때까지 현재 스레드가 기다리는 실행 방식.
- **비동기란?** 현재 작업이 대기할 때 이벤트 루프가 다른 준비된 작업을 진행할 수 있는 방식.
- **코루틴 함수/객체?** `async def`는 정의, `fn()`은 아직 실행되지 않은 코루틴 객체 생성.
- **Task?** 이벤트 루프에 코루틴을 등록하고 실행 상태·결과를 관리하는 객체.
- **gather가 필수?** 아니다. Task들을 먼저 등록한 다음 각각 await해도 함께 진행한다.
- **await를 쓰면 동시 실행?** 아니다. A를 await한 뒤 B를 생성하면 순차 실행이다.
- **create_task를 즉시 await하면?** 등록한 작업이 끝날 때까지 기다린 뒤 다음 작업을 만들면 순차 실행이다.
  `wait01.py`의 해당 약 2초 주석과 달리, 각각 2초인 작업 두 개면 약 4초가 걸린다.
- **async with?** 비동기 자원의 진입/정리 문법. 자동 동시 실행 문법이 아니다.
- **FastAPI의 def?** 일반 def 엔드포인트는 스레드풀에서 실행된다. async def 안의 일반 함수 직접 호출은 자동으로 옮겨지지 않는다.
- **언제?** 독립적인 API·DB 등 I/O 요청의 대기를 겹칠 때. CPU 작업에는 별도 프로세스 등을 검토한다.
- **ConnectError?** 서버 연결 실패. 서버 실행 여부와 포트를 확인한다.
- **address already in use?** 포트 중복. 기존 서버를 종료하거나 포트를 바꾼다.
- **raise_for_status?** 성공 범위 밖의 HTTP 응답에 예외 발생. 상태 코드 조회는 status_code.

화면과 서버 코드는 모두 `day7/shop-web/`에 있으며, 서버 파일은 `day7/shop-web/shop_lab.py`입니다.
서버의 `WEB = Path(__file__).resolve().parent`는 서버 파일과 같은 폴더에서 HTML·CSS·JS를 찾도록 합니다.
교육용 로컬 실행을 전제로 하며 다중 worker·프록시·외부 배포 환경을 위한 앱은 아닙니다.

## 동작 검증

서버를 켜둔 뒤 다른 터미널에서 프로젝트 루트 `AIO_4_class`를 기준으로 실행합니다.
다른 실험은 동시에 실행하지 마세요.

```bash
python day7/shop-web/check.py
# 포트를 바꿨다면:
python day7/shop-web/check.py http://127.0.0.1:8011
```

정적 화면 응답, 6개 모드의 실제 API 처리 구간, health 지연, 입력 범위를 확인합니다.
