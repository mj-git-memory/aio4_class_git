# 작은 방명록

`codex.md`를 바탕으로 만든 HTML 중심의 Python 방명록입니다. 이름과 이야기를 남기고 최신순으로 읽을 수 있습니다. 수업의 FastAPI, Pydantic, Uvicorn을 유지하며 DB는 Python 내장 `sqlite3`를 사용합니다. JavaScript, 프런트엔드 프레임워크, 외부 DB, 템플릿 패키지는 사용하지 않습니다.

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
- 글은 최신 등록순이며 한 화면에 10개씩 표시합니다. 작성 시각은 한국 시간(KST)입니다.
- 저장 후 조회 페이지로 이동하므로 일반적인 새로고침으로 글이 다시 등록되지 않습니다.
- 최초 서버 시작 시 `data/guestbook.db`가 자동 생성됩니다. 로컬에서는 서버를 재시작해도 파일이 유지됩니다.
- DB 위치는 `GUESTBOOK_DB` 환경변수로 변경할 수 있습니다. 경로를 지정하지 않으면 이 프로젝트 폴더 아래에 저장됩니다.
- 저장 공간을 제한하기 위해 최대 1,000개까지 저장하며, 가득 차면 기존 글을 보존하고 새 작성을 거절합니다. 이는 무료 호스팅의 용량을 보장하는 수치가 아니라 앱 자체의 제한입니다.
- 익명 작성형이며 이름은 본인 인증을 거치지 않습니다. 공개 글에 개인정보를 적지 마세요. 수정·삭제·회원·첨부파일 기능은 포함하지 않습니다.

## 파일

| 파일 | 역할 |
| --- | --- |
| `main.py` | 라우팅, 폼 해석, Pydantic 검증, HTML 생성 |
| `database.py` | SQLite 생성·저장·최신순 조회 |
| `templates/index.html` | 입력 폼과 목록 화면 |
| `static/style.css` | 작은 화면에도 맞는 CSS |
| `test_guestbook.py` | 저장, 경계값, 공격 문자열, 페이지 이동 검증 |
| `ANALYSIS.md` | day1~day8 학습 내용과 구현 연결 |
| [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) | 선택한 Render Free 배포 절차, 설정값, 오류 해결 |
| `DEPLOYMENT.md` | 서비스 선택 전의 무료 호스팅 비교 기록 |

## Render 배포

[Render 전용 배포 가이드](RENDER_DEPLOYMENT.md)를 따라 진행합니다. 현재 저장소 기준 Root Directory는 `day1-day8`, Branch는 소스를 올린 `study/day8`, 환경변수는 `PYTHON_VERSION=3.13.5`입니다. **Render Free에서는 재시작·재배포·절전 시 SQLite 글이 사라집니다.**

## 테이블

애플리케이션 테이블은 `entries` 한 개이며 외래키와 다른 테이블 관계가 없습니다. ORM을 사용하지 않습니다.

| 열 | SQLite 타입 | 의미 |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | 등록 순서를 위한 식별자 |
| `name` | TEXT NOT NULL | 이름, 1~20자 |
| `message` | TEXT NOT NULL | 이야기, 1~500자 |
| `created_at` | TEXT NOT NULL | `+09:00`이 포함된 ISO 작성 시각 |

## 테스트

`day1-day8` 폴더에서 실행합니다. 테스트 DB는 임시 폴더에 생성되어 실제 방명록에 영향을 주지 않습니다.

```sh
../.venv/bin/python -m pytest test_guestbook.py -q
```

새 환경에서 테스트할 때는 `python -m pip install -r requirements-dev.txt`로 수업에서 사용하던 pytest와 httpx도 설치합니다.
