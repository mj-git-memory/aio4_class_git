# day1~day8 분석과 적용

## 분석 범위

요청 폴더 `day1-day8`에는 처음에 `codex.md`만 있었습니다. 따라서 학습 소스는 상위 폴더의 `day1`~`day8`을 확인했습니다. Python 파일의 함수·클래스·import·라우트를 조사하고, 아래 대표 코드와 복습 문서, requirements 및 테스트를 읽어 구현 범위를 정했습니다. 모든 수업 파일을 실행하거나 PDF·이미지 교재 전체를 분석한 것은 아닙니다.

| 수업 | 확인한 자료와 핵심 문법·처리 | 방명록 적용 |
| --- | --- | --- |
| day1 | `day1.py`, 파일 구조와 함수 목록: 변수, 연산, 문자열, 리스트, 조건·반복, 숫자 맞히기 함수 | 문자열과 개수 처리, 간단한 함수 구성 |
| day2 | `day2_복습.md`, `day2-8.py`, 함수 목록: 조건 분기, 딕셔너리, 반복, 필터링, 정렬, 금지어 처리, pytest | 잘못된 입력 거절, 딕셔너리 폼 처리, 목록 반복, 경계값 테스트 |
| day3 | `day3-1.py`, `day3_복습.md`: 클래스, 속성, 상속, 데이터클래스, 예외 처리 | 입력 구조를 클래스로 정의하고 실패를 예외로 처리. 작은 앱이므로 별도 서비스 클래스 계층은 만들지 않음 |
| day4 | Git 수업 파일과 프로젝트 README 구조 확인 | 파일 단위 역할 분리, DB·가상환경을 Git 제외. Git 명령은 실행하거나 원격으로 올리지 않음 |
| day5 | `labs/lesson01.py`, `labs/lesson04.py`, `calculator/main.py` 구조: FastAPI, GET/POST, HTMLResponse, Query, limit/skip | HTML 반환, 글 저장 POST, 페이지별 조회 |
| day6 | `ch07_fastapi/app.py`, BaseModel·Field 예제 구조: Pydantic, 길이 제약, 공백 정리, ValidationError, CRUD | 이름·본문 검증. 메모리 딕셔너리 대신 요청된 sqlite3로 저장 |
| day7 | `shop-web/shop_lab.py`: Request, 정적 파일, async/await, 동기·비동기 I/O | CSS 정적 제공, 요청 스트림 읽기. 동기 SQLite 작업은 기존 Starlette의 스레드 도구로 실행 |
| day8 | `lesson_04_ai_test_cases/solution.py`, `test_api.py`, `lesson_03_body_validation/solution.py`, 다른 레슨 함수 목록: 요청 계약, 422, 상태·경계 테스트 | 정상·실패 HTTP 응답과 영속성·입력 경계값 검증 |

## 사용한 처리 방식

1. 브라우저가 HTML 기본 폼을 POST합니다.
2. 요청 크기를 최대 16 KiB로 제한하고 표준 `urllib.parse.parse_qs`로 읽습니다. 중복·누락·추가 필드와 UTF-8 해석 오류를 거절합니다.
3. Pydantic으로 공백과 길이를 확인합니다. SQLite가 문자열 끝으로 취급할 수 있는 NUL 문자도 거절합니다.
4. SQL의 `?` 자리에 값을 전달해 저장합니다. 단일 쓰기 트랜잭션으로 최대 개수 검사와 저장을 묶습니다.
5. `ORDER BY id DESC`와 `LIMIT/OFFSET`으로 10개씩 읽습니다. 페이지 수는 `(전체 개수 + 9) // 10`입니다. 수업의 skip/limit와 정수 연산을 응용했습니다.
6. `html.escape`로 사용자 문자열을 변환하고 표준 `string.Template`으로 HTML에 넣습니다. 사용자 글을 HTML 코드로 실행하지 않습니다.
7. HTTP 303으로 목록으로 이동합니다.

별도의 검색·추천·암호화 알고리즘이나 외부 라이브러리는 추가하지 않았습니다. `sqlite3`는 요청된 내장 DB이고, 나머지 보조 모듈도 표준 라이브러리 또는 기존 FastAPI 의존성입니다. 새 외부 라이브러리나 별도 알고리즘이 필요한 확장은 `codex.md`의 규칙에 따라 먼저 사용자에게 문의해야 합니다.

## 범위와 자원

HTML 화면 한 개, CSS 한 개, DB 테이블 한 개를 사용합니다. 1,000건 제한과 한 페이지 10건 조회로 소규모 학습용 범위를 유지합니다. 이미지 업로드, 외부 API, 정기 작업, 복잡한 클라이언트 처리는 없습니다. 공개 서비스용 스팸 제한이나 관리자 기능은 구현 범위에 포함하지 않았습니다. 이 구조만으로 호스팅 업체의 트래픽·빌드·요금 한도를 강제할 수는 없습니다.
