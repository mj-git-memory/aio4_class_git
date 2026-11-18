# 작은 방명록

`codex.md`를 바탕으로 만든 HTML 중심의 Python 방명록입니다. 이름·이야기·수정용 비밀번호를 입력해 글을 남기고, 같은 비밀번호로 수정할 수 있습니다. 수업의 FastAPI, Pydantic, Uvicorn을 유지하며 DB는 Python 내장 `sqlite3`를 사용합니다. JavaScript, 프런트엔드 프레임워크, 외부 DB, 템플릿 패키지는 사용하지 않습니다.

## 실행

현재 프로젝트에 있는 가상환경으로 실행합니다. 아래 명령의 시작 위치는 `AIO_4_class`입니다.

```sh
cd day1-day8
../.venv/bin/python -m uvicorn main:app --reload --port 8018
```

브라우저에서 <http://127.0.0.1:8018>에 접속합니다. Windows에서는 가상환경을 활성화한 뒤 `python -m uvicorn main:app --reload --port 8018`을 사용합니다.

### 서버 중지

서버를 실행한 터미널을 선택하고 다음 단축키를 누릅니다. 명령어를 입력하는 것이 아니라 `Ctrl` 키를 누른 상태에서 `C` 키를 누릅니다. macOS와 Windows 모두 같습니다.

```text
Ctrl + C
```

`Application shutdown complete`가 출력되고 터미널 입력 프롬프트가 돌아오면 서버가 종료된 것입니다. 다시 실행하려면 위의 Uvicorn 실행 명령을 입력합니다.

### 새 환경에서 설치

새 환경에서는 Python 3.10 이상과 다음 설치 명령을 사용합니다. 현재 작업에서는 패키지를 추가 설치하지 않았습니다.

```sh
python -m pip install -r requirements.txt
```

## 사용과 저장

- 이름 1~20자, 이야기 1~500자이며 앞뒤 공백을 제거합니다. 공백만 있는 글은 거절합니다.
- 새 글의 수정용 비밀번호는 **숫자 4자리**입니다. `0123`처럼 앞의 0도 그대로 저장·비교합니다. 문자·전각 숫자·공백은 허용하지 않습니다.
- 이전 버전에서 8~128자로 작성한 글은 원래 비밀번호로 계속 수정할 수 있습니다. 새 글 작성에만 숫자 4자리 규칙을 적용합니다.
- 각 글의 **수정** 링크를 누르고 이름·내용을 고친 다음, 작성할 때 정한 비밀번호를 입력해 저장합니다. 비밀번호가 틀리면 저장되지 않습니다. 작성 시각과 목록 순서는 유지됩니다.
- 비밀번호를 아는 사람이 해당 글을 수정할 수 있습니다. 비밀번호 변경·찾기·재설정 기능은 없으므로 별도로 기억해 두세요.
- 글은 최신 등록순이며 한 화면에 10개씩 표시합니다. 작성 시각은 한국 시간(KST)입니다.
- 저장 후 조회 페이지로 이동하므로 일반적인 새로고침으로 글이 다시 등록되지 않습니다.
- 최초 서버 시작 시 `data/guestbook.db`가 자동 생성됩니다. 로컬에서는 서버를 재시작해도 파일이 유지됩니다.
- DB 위치는 `GUESTBOOK_DB` 환경변수로 변경할 수 있습니다. 경로를 지정하지 않으면 이 프로젝트 폴더 아래에 저장됩니다.
- 저장 공간을 제한하기 위해 최대 1,000개까지 저장하며, 가득 차면 기존 글을 보존하고 새 작성을 거절합니다. 이는 무료 호스팅의 용량을 보장하는 수치가 아니라 앱 자체의 제한입니다.
- 익명 작성형이며 이름은 본인 인증을 거치지 않습니다. 공개 글에 개인정보를 적지 마세요. 삭제·회원·첨부파일 기능은 포함하지 않습니다.

## 기존 DB와 비밀번호

서버 시작 시 기존 `entries` 테이블에 `password_hash` 열이 없으면 자동으로 추가합니다. 기존 글을 삭제하거나 다른 테이블을 만들지 않습니다. 이전에 비밀번호 없이 작성된 글은 조회만 가능하며 수정은 차단됩니다. 새 글부터 작성 시 정한 비밀번호로 수정할 수 있습니다. 기존 DB를 별도로 보관하려면 서버를 종료한 상태에서 `data/guestbook.db`를 복사해 두세요.

비밀번호는 사용자가 승인한 Python 표준 라이브러리의 **PBKDF2-HMAC-SHA256(600,000회, 글마다 무작위 salt)**으로 저장합니다. 원문 비밀번호나 저장된 해시는 목록·수정 화면에 넣지 않습니다. 외부 패키지는 추가하지 않았습니다. [Python hashlib](https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac), [OWASP 비밀번호 저장 안내](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

4자리 숫자는 가능한 조합이 10,000개라 추측에 취약합니다. 이 앱은 소규모 학습용이며 비밀번호 대입 시도 횟수 제한은 포함하지 않습니다. 공개 배포에서는 Render가 제공하는 HTTPS 주소를 사용하세요.

## 화면 디자인

교체된 `design.md`의 자주색(`#4a154b`) 기본 버튼, 크림·라벤더 색감, 넉넉한 pill 버튼, 16px 카드와 4px 입력창을 적용했습니다. 첨부된 참고 이미지처럼 살구빛 배경 위에 흰 종이를 얹은 느낌을 CSS의 파스텔 그라데이션·미세한 선과 옅은 그림자로 표현합니다. 데스크톱에서는 입력과 목록을 두 열로, 850px 이하에서는 한 열로 배치합니다. 폰트는 기기에 있는 Inter/Lato와 운영체제 폰트를 사용하며 외부 폰트 다운로드·이미지 파일·JavaScript는 추가하지 않았습니다.

## 배포 전 UI 파일럿 보기

**`pilot.html`은 서버 없이 브라우저에서 열 수 있는 화면 확인용 파일입니다.** 실제 템플릿과 CSS를 포함하며, 예시 글 3개만 보여 줍니다. 입력창에는 입력할 수 있지만 작성 버튼은 저장하지 않고 수정 링크는 입력창으로 이동만 합니다. 실제 방명록 DB를 읽거나 변경하지 않습니다.

1. VS Code에서 `pilot.html`을 우클릭하고 **Finder에서 보기 / Reveal in Finder**를 선택합니다.
2. Finder에서 `pilot.html`을 더블클릭하거나 **다음으로 열기 > Chrome 또는 Safari**를 선택합니다.
3. 배경·입력창·목록 배치를 보고, 브라우저 창을 좁혀 모바일 너비도 확인합니다.

HTML이나 CSS를 다시 수정했다면 프로젝트 루트에서 다음을 실행하고 파일럿 탭을 새로고침합니다. Python 표준 라이브러리만 사용합니다.

```sh
.venv/bin/python day1-day8/build_pilot.py
```

파일럿은 생성 시점의 화면 사본입니다. 새 CSS가 자동 반영되는 파일은 아니므로 디자인을 수정한 뒤에는 위 명령을 다시 실행합니다. 실제 작성·비밀번호·수정 기능은 위 **실행** 절차로 로컬 서버를 켜서 확인합니다. 화면 확인이 끝나기 전에는 Commit·Push하지 않으면 Render 자동 배포를 시작하지 않습니다.

## 파일

| 파일 | 역할 |
| --- | --- |
| `main.py` | 라우팅, 폼 해석, Pydantic 검증, HTML 생성 |
| `database.py` | SQLite 생성·저장·최신순 조회 |
| `passwords.py` | 비밀번호 해시 생성과 일치 여부 확인 |
| `templates/index.html` | 입력 폼과 목록 화면 |
| `static/style.css` | 작은 화면에도 맞는 CSS |
| `test_guestbook.py` | 저장, 경계값, 공격 문자열, 페이지 이동 검증 |
| `ANALYSIS.md` | day1~day8 학습 내용과 구현 연결 |
| `design.md` | 화면 디자인 참고 지침 |
| [pilot.html](pilot.html) | 브라우저에서 직접 여는 독립형 UI 파일럿 |
| `build_pilot.py` | 실제 템플릿·CSS와 예시 글로 파일럿 재생성 |
| [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) | 선택한 Render Free 배포 절차, 설정값, 오류 해결 |
| `DEPLOYMENT.md` | 서비스 선택 전의 무료 호스팅 비교 기록 |

## Render 배포

[Render 전용 배포 가이드](RENDER_DEPLOYMENT.md)를 따라 진행합니다. 현재 저장소 기준 Root Directory는 `day1-day8`, Branch는 수정 내용을 올릴 `main`, 환경변수는 `PYTHON_VERSION=3.13.5`입니다. 수정 후 재배포는 가이드의 **수정 버전 다시 배포하기**를 참고하세요. **Render Free에서는 재시작·재배포·절전 시 SQLite 글이 사라집니다.**

기존 서비스가 `study/day8`으로 연결돼 있다면 Render의 **Settings > Build & Deploy > Branch > Edit**에서 `main`으로 저장합니다. **Root Directory는 `day1-day8`을 유지**하고, 배포가 시작하지 않으면 **Manual Deploy > Deploy latest commit**을 선택합니다. 상세 절차는 배포 가이드의 **8-1**에 있습니다.

## 테이블

애플리케이션 테이블은 `entries` 한 개이며 외래키와 다른 테이블 관계가 없습니다. ORM을 사용하지 않습니다.

| 열 | SQLite 타입 | 의미 |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | 등록 순서를 위한 식별자 |
| `name` | TEXT NOT NULL | 이름, 1~20자 |
| `message` | TEXT NOT NULL | 이야기, 1~500자 |
| `created_at` | TEXT NOT NULL | `+09:00`이 포함된 ISO 작성 시각 |
| `password_hash` | TEXT NOT NULL | salt·반복 횟수·해시. 이전 글은 빈 문자열로 수정 차단 |

## 테스트

`day1-day8` 폴더에서 실행합니다. 테스트 DB는 임시 폴더에 생성되어 실제 방명록에 영향을 주지 않습니다.

```sh
../.venv/bin/python -m pytest test_guestbook.py -q
```

새 환경에서 테스트할 때는 `python -m pip install -r requirements-dev.txt`로 수업에서 사용하던 pytest와 httpx도 설치합니다.
