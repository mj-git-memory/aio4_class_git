# 구현·검증 기록

검증일: 2026-10-27 (Asia/Seoul). 로컬 검증 후 PythonAnywhere 무료 계정에도 실제 배포했습니다. 로컬·서버 자동 테스트와 공개 브라우저 확인 범위를 구분해 기록합니다.

## 환경

- macOS, ARM64
- Python 3.9.12, SQLite 표준 라이브러리
- Flask 3.1.3, Werkzeug 3.1.9, Flask-WTF 1.2.2, regex 2026.1.15
- pytest 8.4.2
- 의존성은 프로젝트 `.venv`에 설치했으며 시스템 Python 패키지를 변경하지 않았습니다.

## 자동 검증

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/python -m compileall -q app wsgi.py tools
```

결과: **28 tests passed**, 의존성 충돌 없음, Python 구문 컴파일 성공.

| 범위 | 확인 내용 | 결과 |
| --- | --- | --- |
| 계정 | 가입 성공, 이메일 대소문자 정규화·중복, 형식·필수값·비밀번호 길이, 로그인 성공·실패 | 통과 |
| 비밀번호 | 평문 미저장, 해시 검증, 세션에 비밀번호·역할 미포함 | 통과 |
| 로그아웃·CSRF | 로그아웃 직후 쓰기 거부, GET 로그아웃 미허용, 토큰 누락 거부 | 통과 |
| 목업 | 비밀번호 찾기의 실제 메일 미발송 안내 | 통과 |
| 방명록 | 빈 목록, 1·10·11개 이상 페이징, 마지막 페이지 삭제·잘못된 페이지 보정 | 통과 |
| 권한 | 타인 글 PATCH/DELETE·원문 조회 거부, role 입력을 통한 관리자 승격 거부 | 통과 |
| 댓글 | 글별 연결·마스킹, 글 삭제 CASCADE, 비로그인·공백·최대 길이 거부 | 통과 |
| 본문 | 공백·길이·잘못된 입력 타입 거부, 수정 결과·수정 원문 확인 | 통과 |
| 미리보기 | 전체 마스킹 후 10글자 자르기, 가족 이모지 grapheme 보존 | 통과 |
| 마스킹 | 반복·겹침·키워드 특수문자·정규식 옵션, 원문 누출 방지, timeout·빈 일치·손상 규칙 대체 안내 | 통과 |
| 규칙 관리 | 일반 회원 거부, 관리자 허용, 잘못된 패턴·중복·옵션 거부, 추가·삭제 후 기존 글 반영 | 통과 |
| DB | 외래 키·UNIQUE, 앱 팩토리 재생성 후 영속성, 삭제한 초기 규칙 미복원 | 통과 |
| 장애 | 누락 DB 자동 생성 방지, 손상 DB 원본 보존, 일반 안내 503 | 통과 |
| CLI | init-db 재실행의 데이터 보존, 관리자 숨김 입력, 일관된 백업, 기존 백업 덮어쓰기 거부 | 통과 |
| 출력 | Jinja 이스케이프, JS innerHTML 미사용, CSP·no-store, Secure·HttpOnly·SameSite 쿠키 | 통과 |

초기 검증 중 CLI 명령의 Flask 앱 컨텍스트와 CSRF 유효시간 타입 오류를 발견해 수정한 뒤 전체 자동 테스트를 다시 실행했습니다.

## 실제 CLI·WSGI 확인

- `flask --app app init-config`: 로컬 영속 비밀 설정 생성 성공, 비밀값 미출력
- `flask --app app init-db`: 로컬 스키마와 초기 규칙 생성 성공
- WSGI `from wsgi import application`: import 성공, debug=False, SESSION_COOKIE_SECURE=True
- 로컬 개발 서버: `flask --app app run --port 5050 --no-reload`, HTTP 응답과 정적 파일 확인
- 배포용 ZIP을 별도 임시 디렉터리에 풀고 init-config → init-db → init-db 재실행: 성공, 기존 데이터 유지 안내 확인
- 압축 해제한 소스에서 WSGI import, `/` 및 `/static/app.js` 응답: HTTP 200, Secure 쿠키 설정 확인
- ZIP 내부 목록 검사: instance·가상환경·SQLite DB·pyc 미포함 확인. 총 32개 파일이며 스크린샷·설계·실행 문서도 포함
- 비밀번호 최소 길이 6자 변경 후 전체 테스트 재실행: **28 passed in 4.09s**
- 6자 비밀번호 회원가입·로그인·관리자 CLI 생성 성공, 5자 비밀번호 거부 및 화면 minlength=6 확인

## 브라우저 수동 검증

Codex 내장 브라우저에서 실제 로컬 HTTP 서버로 확인했습니다.

1. 회원가입 입력 후 키보드 제출 → 가입 완료·로그인 화면 이동
2. 로그인 → 현재 사용자명·로그아웃·글 작성 폼 표시
3. 글 작성 → 목록에 약 10글자 미리보기, 현재 body의 숨김 상세 영역 펼침
4. 상세 본문 줄바꿈과 키워드 마스킹 확인
5. 댓글 작성 → 해당 글의 댓글 수·목록 즉시 갱신, 분리 기호 정규식 마스킹 확인
6. 본인 글 수정 → 원문 편집 가능, 저장 후 목록·상세 동시 갱신
7. 로그아웃 → 글·댓글 작성 폼 해제
8. 관리자로 로그인 → 규칙 화면 진입, 규칙 추가·목록 재조회
9. 규칙 삭제 확인 단계와 취소 동작 확인. 실제 규칙·글 삭제는 자동 테스트의 임시 DB에서 확인
10. 다른 사용자 글 조회 시 관리자에게도 수정·삭제 버튼 미표시 확인
11. 좁은 브라우저 패널에서 폼·상세·댓글의 줄바꿈과 배치 확인

화면 증거: [상세·댓글 스크린샷](preview.png). 키보드 제출과 본문 펼침을 확인했지만 정식 접근성 감사나 모든 브라우저·화면 크기 조합을 검증한 것은 아닙니다.

## 미확인 사항·한계

- Windows 및 로컬 3.9.12·서버 3.13.1 이외 Python 버전은 실행 미확인
- 다수 사용자 부하·장시간 운영·대규모 댓글·DB 용량 증가에 대한 성능 시험 미수행
- 비밀번호 재설정·SNS·이메일 소유 확인은 의도적인 범위 제외
- 모든 최신 유해 표현이나 문맥 판단을 보장하지 않음. 출처 조사와 초기 목록 선별 범위는 `masking-sources.md`에 기록

## PythonAnywhere 실제 배포 확인

- 공개 주소: https://mjlee.pythonanywhere.com/
- 서버 Python 3.13.1 및 Python 3.13 Web 앱을 확인했습니다.
- 기존 웹 앱·프로젝트 데이터가 없는 새 계정에서 ZIP을 업로드했습니다. 로컬 instance·DB·비밀 키는 제외했습니다.
- `/home/mjlee/.virtualenvs/note-demo-env` 생성, 의존성 설치와 `pip check` 성공을 확인했습니다.
- `init-config`, `init-db` 성공. 새 비밀 키와 SQLite DB는 서버에서 생성했으며 값을 출력하거나 내려받지 않았습니다.
- `/var/www/mjlee_pythonanywhere_com_wsgi.py`의 기존 예제를 `.before-note-demo` 파일로 백업하고 프로젝트 WSGI 진입점으로 변경했습니다.
- Source code·Working directory, virtualenv, `/static/` 디렉터리, Force HTTPS를 설정하고 Reload했습니다.
- 공개 HTTPS 방명록·정적 스타일 및 `/signup`의 **6~128자** 안내가 표시되는 것을 브라우저에서 확인했습니다.
- Web 화면의 무료 앱 만료일: 2026-11-27. 자동 연장이 아니라 사용자가 관리 화면에서 연장해야 합니다.
- 관리자 계정은 임의로 만들지 않았습니다. 서버 콘솔의 `flask --app app create-admin`으로 사용자 본인이 생성할 수 있습니다.
- 실제 서비스 DB에 검증용 계정·글을 만들지 않았으며, 서버 자동 테스트는 임시 DB로 수행합니다.
- 서버 가상환경에 pytest 8.4.2를 설치하고 `python -m pytest -q --tb=short` 실행: **28 passed in 27.12s**. 이어서 `pip check`: 의존성 충돌 없음.
- 화면 증거: [배포된 회원가입 화면](deployed-signup.png).
