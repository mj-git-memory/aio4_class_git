# 작은 방명록 Render 무료 배포 가이드

작성·공식 문서 확인일: **2026-10-23 (한국 시간)**

사용자가 선택한 Render Free에 현재 FastAPI 방명록을 배포하는 절차입니다. Render의 공개 공식 문서와 문서 내 대시보드 안내를 확인했습니다. 로그인된 사용자 대시보드나 실제 배포 서비스는 확인하지 않았습니다. 계정별 화면 배치는 달라질 수 있으므로 아래 필드 이름을 기준으로 설정하세요.

## 1. 배포할 구성

| 항목 | 현재 프로젝트 기준 |
| --- | --- |
| 로컬 저장소 | `/Users/imijeong/Downloads/AIO_4_class` |
| GitHub 원격 | `https://github.com/mj-git-memory/aio4_class_git.git` |
| 작성 시점 로컬 브랜치 | `study/day8` |
| 앱 폴더 | `day1-day8` |
| 앱 객체 | `main.py`의 `app` |
| Python | 로컬에서 사용 중인 `3.13.5` |
| 설치 파일 | `day1-day8/requirements.txt` |
| 서비스 | **Web Service / Python 3 / Free** |

위 저장소 주소와 브랜치는 로컬 Git 설정에서 확인한 값입니다. GitHub에 해당 브랜치와 파일이 실제로 올라갔는지는 다음 단계에서 확인합니다. 코드는 기존 FastAPI·Pydantic·Uvicorn과 내장 SQLite를 유지합니다. Docker나 추가 앱 라이브러리는 필요하지 않습니다.

## 2. 무료 배포에서 글이 보존되는 범위

**현재 SQLite 방식의 Render Free 배포는 데이터가 초기화될 수 있는 학습·시연용입니다.** 재배포·재시작·절전 시 로컬 DB가 사라집니다. DB 경로를 환경변수로 바꾸어도 무료 저장소가 영구 저장소로 바뀌지는 않습니다. 앱이 다시 시작되면 빈 테이블을 자동으로 만듭니다. [공식 무료 정책](https://render.com/docs/free)

| 무료 조건 | 사용 시 의미 |
| --- | --- |
| 15분 동안 외부 요청이 없으면 절전 | 다음 접속 때 다시 시작하며 약 1분이 걸릴 수 있음 |
| 임시 파일 시스템 | 작성 글은 재시작·재배포·절전 후 소실 |
| 무료 영구 디스크 없음 | 현재 SQLite 구조로 무료 장기 보존을 보장할 수 없음 |
| 워크스페이스 월 750 무료 인스턴스 시간 | 다른 무료 웹 서비스와 사용 시간을 공유 |
| 무료 웹 서비스 SSH·Shell 미지원 | 서버에 들어가 DB를 내려받는 절차를 이 가이드에 포함하지 않음 |

트래픽·빌드 사용량도 계정 한도에 포함됩니다. 결제수단이 있는 계정은 한도 초과 시 추가 비용이 생길 수 있으므로 Dashboard의 Billing에서 사용량과 지출 설정을 확인하세요. 결제수단이 없으면 해당 한도 초과 시 서비스 또는 빌드가 중지될 수 있습니다. [무료 사용량·과금 조건](https://render.com/docs/free)

## 3. GitHub에 방명록 올리기

Render는 Mac에 저장된 파일을 직접 읽지 않습니다. 연결할 GitHub 브랜치에 방명록 소스가 있어야 합니다.

VS Code 터미널에서 프로젝트 루트로 이동해 현재 상태를 확인합니다.

```sh
cd /Users/imijeong/Downloads/AIO_4_class
git branch --show-current
git status --short
git remote -v
```

작성 시점에는 `study/day8` 브랜치였고 `day1-day8/`이 아직 추적되지 않은 상태였습니다. 다음 명령은 사용자가 실행하는 업로드 예시이며 이 가이드 작성 작업에서는 커밋·Push하지 않았습니다.

```sh
git add day1-day8
git diff --cached --name-only
```

표시된 목록에 의도한 파일만 있는지 확인합니다. 다른 작업이 이미 스테이징되어 있다면 함께 커밋하지 않도록 먼저 정리하세요. `data/`, DB, `.venv`, 캐시 파일은 이 폴더의 `.gitignore`에 의해 제외됩니다.

```sh
git commit -m "Add HTML guestbook and Render deployment guide"
git push -u origin study/day8
```

현재 브랜치가 달라졌다면 Push 대상과 Render Branch를 그 브랜치로 맞추세요. 위 명령으로 브랜치를 변경하거나 main에 병합할 필요는 없습니다.

GitHub에서 저장소를 열고 **study/day8** 브랜치를 선택한 뒤 다음 구조가 있는지 확인합니다.

```text
day1-day8/
├── main.py
├── database.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    └── style.css
```

`requirements.txt`의 현재 버전은 FastAPI 0.115.12, Pydantic 2.11.5, Uvicorn 0.34.2입니다. `data/guestbook.db`를 GitHub에 올릴 필요는 없습니다.

## 4. Render에서 GitHub 연결

1. [Render Dashboard](https://dashboard.render.com/)에 로그인합니다.
2. **New > Web Service**를 선택합니다. Python 서버가 필요하므로 **Static Site**를 선택하지 않습니다.
3. 소스에서 **Git Provider**를 선택하고 GitHub를 연결합니다.
4. 저장소 목록에서 **mj-git-memory/aio4_class_git**를 선택합니다.
5. 목록에 없다면 GitHub의 Render 앱 설정에서 이 저장소에 접근 권한이 있는지 확인합니다. 비공개 저장소도 연결할 수 있습니다.

공식 근거: [Web Service 생성](https://render.com/docs/web-services), [Git Provider 연결](https://render.com/docs/git-provider).

## 5. 생성 화면에 넣을 값

| Render 필드 | 입력값 | 설명 |
| --- | --- | --- |
| Name | `aio4-guestbook` | 예시 이름. 중복이면 고유한 이름 사용 |
| Language | **Python 3** | Python 네이티브 실행 |
| Branch | **study/day8** | 앞에서 소스를 올린 브랜치와 일치 |
| Region | **Singapore** | 한국 이용자를 고려한 시작점. 실제 지연 측정 결과는 아님 |
| Root Directory | **day1-day8** | 저장소 기준 상대 경로 |
| Build Command | `pip install -r requirements.txt` | 기존 의존성 설치 |
| Start Command | 아래 명령 | 앱 실행 |
| Instance Type / Compute plan | **Free ($0)** | 유료 플랜을 선택하지 않음 |
| Health Check Path | **/health** | Advanced 또는 생성 후 Settings에서 설정 |

Start Command에는 다음을 한 줄로 입력합니다.

```sh
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

`$PORT`는 그대로 둡니다. Render가 지정하는 포트를 사용합니다. `main:app`은 앱 폴더 안의 `main.py`에 있는 `app` 객체를 가리킵니다. `--reload`는 개발용이므로 넣지 않습니다. [공식 FastAPI 배포](https://render.com/docs/deploy-fastapi), [포트 바인딩](https://render.com/docs/web-services)

**Root Directory에 Mac 절대 경로를 넣지 마세요.** `day1-day8`을 지정하면 Build와 Start 명령은 그 폴더에서 실행됩니다. 따라서 명령에 `cd day1-day8`이나 `day1-day8/main.py`를 덧붙이지 않습니다. [Root Directory 규칙](https://render.com/docs/monorepo-support)

별도로 `day1-day8` 내용만 담은 저장소를 새로 만들었다면 Root Directory를 비웁니다. 현재 `aio4_class_git` 저장소를 그대로 사용한다면 반드시 `day1-day8`을 넣습니다.

Singapore는 공식 지원 리전입니다. 생성 후 기존 서비스의 리전 변경은 지원하지 않으므로 처음에 선택합니다. [리전 안내](https://render.com/docs/regions)

## 6. 환경변수

Environment Variables에 다음을 추가합니다.

| Key | Value | 필요 여부 |
| --- | --- | --- |
| `PYTHON_VERSION` | `3.13.5` | 이 가이드에서 지정하는 실행 버전 |

Render의 기본 Python은 서비스 생성일에 따라 달라집니다. 기존 의존성과 로컬 실행 버전에 맞춰 전체 버전을 지정합니다. `PYTHON_VERSION`에는 `3.13`처럼 일부만 쓰지 않습니다. [공식 Python 버전 설정](https://render.com/docs/python-version)

`PORT`는 별도로 설정하지 않습니다. `GUESTBOOK_DB`도 비워 두면 앱 폴더의 `data/guestbook.db`를 자동 생성하므로 추가 설정 없이 실행할 수 있습니다. 별도 DB 서비스·디스크·Pre-deploy Command는 이 가이드에서 사용하지 않습니다.

## 7. 배포와 첫 접속

1. 설정을 확인하고 **Create Web Service**를 누릅니다.
2. 서비스의 배포 로그에서 의존성 설치와 Uvicorn 시작을 확인합니다.
3. 배포 성공 후 서비스 화면에 표시된 `https://....onrender.com` 주소를 엽니다. 이름을 바탕으로 주소를 추측하지 말고 Render가 표시한 URL을 사용합니다.
4. `/health`에 접속해 다음 응답을 확인합니다.

```json
{"status":"ok"}
```

5. 기본 주소 `/`에서 이름과 내용을 작성합니다.
6. 목록에 글이 보이고 새로고침해도 중복 등록되지 않는지 확인합니다.
7. 모바일에서도 폼과 목록을 확인합니다.

현재 `/health`는 프로세스 응답만 검사합니다. DB 쓰기 성공까지 보장하지 않으므로 글 등록 확인도 필요합니다. Render의 HTTP 상태 검사는 지정 경로의 2xx·3xx 응답을 정상으로 판정합니다. [Health Check 공식 안내](https://render.com/docs/health-checks)

## 8. 이후 코드 수정과 재배포

연결된 브랜치에 수정 파일을 Commit·Push합니다. Auto-Deploy가 **On Commit**이면 자동 재배포됩니다. 직접 배포하려면 서비스의 **Deploys > Manual Deploy > Deploy latest commit**을 사용합니다. CI를 구성하지 않은 저장소에서는 **After CI Checks Pass**를 선택하지 않습니다. [자동·수동 배포](https://render.com/docs/deploys)

앱 폴더를 Root Directory로 지정하면 그 폴더 밖의 다른 수업 파일 변경은 자동 배포 대상에서 제외됩니다. [모노레포 규칙](https://render.com/docs/monorepo-support)

**재배포하거나 Restart하면 무료 SQLite 글이 사라질 수 있습니다.** 배포 성공 여부와 기존 글 보존 여부는 별개입니다. 실제 사용자의 중요한 글을 이 환경에만 저장하지 마세요.

## 9. 오류별 확인 위치

| 현상 / 로그 | 먼저 확인할 내용 |
| --- | --- |
| 저장소가 목록에 없음 | GitHub Render 앱의 저장소 접근 권한과 연결 계정 |
| `study/day8` 브랜치가 없음 | 해당 브랜치를 GitHub로 Push했는지 |
| `requirements.txt`를 찾을 수 없음 | Root Directory가 `day1-day8`인지, 파일이 선택 브랜치에 있는지 |
| `Could not import module "main"` | Root Directory와 Start Command의 `main:app` |
| `No module named database` | `database.py`가 `main.py`와 같은 폴더로 올라갔는지 |
| Python 패키지 설치 실패 | `PYTHON_VERSION=3.13.5`, 방명록의 requirements 사용 여부, 최초 오류 로그 |
| `No open ports detected` / 접속 불가 | `--host 0.0.0.0 --port $PORT`가 있는지 |
| CSS 404 / 템플릿 파일 없음 | `static/style.css`, `templates/index.html` 업로드 여부와 대소문자 |
| 502 / 배포 실패 | 서비스의 배포·런타임 로그에서 실제 최초 오류 확인 |
| `/health` 정상인데 등록 실패 | 등록 요청 시점의 런타임 로그와 DB 경로의 쓰기 가능 여부 |
| 일정 시간 뒤 첫 접속이 느림 | Free 절전 후 시작 지연 가능성 |
| 글이 없어짐 | Free의 임시 파일 시스템과 절전·재시작·재배포 여부 |

Free에는 서버 SSH·Shell 접근이 없으므로 로그를 중심으로 확인합니다. 캐시 문제의 근거가 있을 때만 **Clear build cache & deploy**를 사용합니다. [무료 제한](https://render.com/docs/free), [수동 배포 옵션](https://render.com/docs/deploys)

## 10. 이 가이드의 검증 범위

- 공식 공개 문서의 설정 필드, 실행 명령, 버전 지정, 무료 제한을 확인했습니다.
- 로컬 저장소 주소·현재 브랜치·requirements·앱의 `app`, `/health`, DB 경로 처리 구조를 확인했습니다.
- 기존 로컬 테스트 결과는 `VERIFICATION.md`에 있습니다. 이번 작업은 문서 작성이므로 앱 코드나 패키지는 변경하지 않았습니다.
- Render 계정 연결·서비스 생성·원격 빌드·실제 URL 접속은 수행하지 않았습니다. 위 절차의 배포 후 검증을 완료해야 실제 배포 성공으로 볼 수 있습니다.
