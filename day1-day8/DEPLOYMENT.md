# 이전 무료 호스팅 비교와 배포 방법

> **현재 선택: Render Free.** 아래 내용은 서비스 선택 전의 비교 기록입니다. 실제 배포에는 [최신 Render 전용 배포 가이드](RENDER_DEPLOYMENT.md)를 사용하세요. 저장소·브랜치·환경변수와 문제 해결 방법을 현재 프로젝트에 맞춰 정리했습니다.

확인일: **2026-10-23, 한국 시간**. 공식 요금표와 문서를 검색해 정리했습니다. 계정 생성·업로드·실제 배포는 수행하지 않았습니다. 아래 명령은 우리 앱에 맞춰 구성한 배포 예시이며 대상 계정에서 실행 검증하지 않았습니다.

## 비교

평가 기준은 기존 FastAPI·Uvicorn 유지, SQLite 파일 보존, 외부 DB·새 라이브러리 없이 배포, 학습자가 관리할 수 있는 복잡도입니다.

| 서비스 | 현재 무료 조건 | 장점 | 단점과 SQLite 제약 | 판단 |
| --- | --- | --- | --- | --- |
| alwaysdata Free | 1 GB SSD, 256 MB RAM, ¼ CPU, 개인 용도, 3일 백업 | ASGI User program 지원, 계정 파일 저장 공간과 SSH 제공 | 비상업 용도, 무료 웹 주소만 사용, 관리자 로그인 유지 필요 | **현재 앱에 가장 적합** |
| PythonAnywhere Free | 512 MiB 디스크, 웹 앱 1개·워커 1개, 웹 앱 만료 1개월 | Python 중심 관리와 계정 저장 공간 | ASGI는 베타이며 장기 가격 미확정, CLI 설정 필요. 무료 ASGI의 장기 운영 조건을 확정하기 어려움 | 조건부 대안 |
| Render Free | 웹 서비스 무료, 워크스페이스 월 750시간 | Git 연동 배포와 HTTPS가 간편 | 15분 무접속 절전. 재시작·재배포·절전 시 SQLite 소실. 무료 영구 디스크 없음 | 초기화 가능한 시연용 |
| Koyeb Free | 조직당 1개, RAM 512 MB·0.1 vCPU·로컬 SSD 2 GB | Python/Git 배포 가능 | 1시간 무접속 시 0으로 축소, 로컬 디스크 임시 저장, 무료 인스턴스는 볼륨 불가 | SQLite 유지 조건에 부적합 |
| Hugging Face Spaces | Static은 무료. 신규 Gradio·Docker Space 생성은 유료 플랜 필요(개인 ZeroGPU 예외 있음) | 데모 공유 기능 | 현재 앱에 필요한 Docker 무료 신규 생성 경로가 아님. 기본 디스크도 비영구 | 현 조건에서 제외 |

공식 근거: [alwaysdata 요금](https://www.alwaysdata.com/en/offers/), [ASGI 설정](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/), [무료 제한](https://help.alwaysdata.com/en/docs/admin-billing/profile/suspension/), [PythonAnywhere 무료 기능](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/), [PythonAnywhere ASGI 베타](https://help.pythonanywhere.com/pages/ASGICommandLine), [Render Free](https://render.com/docs/free), [Koyeb 인스턴스](https://www.koyeb.com/docs/reference/instances), [Koyeb 저장소](https://www.koyeb.com/docs/reference/storage), [Spaces 현재 정책](https://huggingface.co/docs/hub/en/spaces-overview).

## 추천 이유와 조건

개인 학습용 방명록에는 **alwaysdata Free**를 추천합니다. ASGI 실행과 계정 파일 공간을 제공하므로 현재 소스를 유지하고 SQLite를 계정 디렉터리에 저장할 수 있다고 판단합니다. 이는 공식 실행·저장 구조를 바탕으로 한 적합성 판단이며 실제 배포에서 저장·재시작 검증이 필요합니다. 외부 DB, ORM, Docker는 추가하지 않습니다.

공식 무료 조건상 상업·영리 용도는 허용되지 않습니다. 회사 사이트나 광고 수익용으로 전환하면 이 추천의 전제가 달라집니다. 새 계정은 120일에 한 번 관리자 페이지에 로그인해야 하며, 계정 연령 1~4년은 6개월, 4년 이상은 연 1회입니다. 무료 사이트는 계정의 `alwaysdata.net` 주소를 사용합니다. [정책 원문](https://help.alwaysdata.com/en/docs/admin-billing/profile/suspension/)

256 MB RAM에서 작은 방명록을 단일 워커로 실행하는 것은 합리적인 출발점이지만, 실제 메모리와 트래픽은 배포 후 확인해야 합니다. 전체 저장 공간에는 가상환경·로그·DB 등도 포함됩니다.

## alwaysdata 배포 순서

아래의 `ACCOUNT`는 실제 alwaysdata 계정명으로 바꿉니다. 기본 SSH 사용자를 기준으로 하며, 다른 사용자를 만들었다면 관리 화면의 실제 접속 정보를 사용합니다.

### 1. Free 계정 준비

[공식 요금 페이지](https://www.alwaysdata.com/en/offers/)에서 **Free, 0 €/month**를 선택합니다. Plus의 30일 체험과 구별합니다. 관리자 **Environment > Python**에서 기존 프로젝트와 같은 Python **3.13**을 선택합니다. 플랫폼 문서는 `python3` 대신 `python` 명령 사용을 안내합니다. [Python 설정](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/)

### 2. 서버 폴더 생성

로컬 터미널에서 접속합니다. [공식 접속 정보](https://help.alwaysdata.com/en/docs/technical-specifications/login-details/)

```sh
ssh ACCOUNT@ssh-ACCOUNT.alwaysdata.net
```

접속한 서버에서 실행합니다.

```sh
mkdir -p /home/ACCOUNT/guestbook /home/ACCOUNT/guestbook-data
exit
```

### 3. 앱 파일 업로드

다음은 **로컬 Mac 터미널**에서 실행합니다. 실행에 필요한 파일만 전송하며 로컬 가상환경·DB·다른 수업 폴더는 보내지 않습니다.

```sh
cd /Users/imijeong/Downloads/AIO_4_class/day1-day8
scp -r main.py database.py requirements.txt templates static ACCOUNT@ssh-ACCOUNT.alwaysdata.net:/home/ACCOUNT/guestbook/
```

기존 글을 이전하는 절차는 포함하지 않습니다. 새 배포는 빈 DB로 시작합니다. 기존 글도 옮기려면 로컬 서버를 종료하고 별도로 백업·복사해야 합니다.

### 4. 서버에 기존 의존성 설치

서버에 다시 접속하고 실행합니다.

```sh
ssh ACCOUNT@ssh-ACCOUNT.alwaysdata.net
cd /home/ACCOUNT/guestbook
python --version
python -m venv .venv
.venv/bin/python -m pip install --no-cache-dir -r requirements.txt
.venv/bin/python -c 'import sqlite3; print(sqlite3.sqlite_version)'
du -sh /home/ACCOUNT/guestbook
```

Python 버전이 3.13인지 확인합니다. 가상환경은 서버에서 새로 만듭니다. 마지막 두 명령은 내장 SQLite와 설치 폴더 크기를 확인합니다. 추가 앱 라이브러리는 필요하지 않습니다.

### 5. 관리자 화면에 사이트 등록

**Web > Sites > Add a site**에서 다음을 입력합니다. 기존 기본 사이트가 같은 주소를 차지하고 있다면 해당 사이트 설정을 수정합니다. [User program 공식 문서](https://help.alwaysdata.com/en/docs/web-hosting/sites/http-servers/user-program/)

| 항목 | 입력값 |
| --- | --- |
| Name | 작은 방명록 |
| Addresses | `ACCOUNT.alwaysdata.net` |
| Type | **User program** |
| Working directory | `/home/ACCOUNT/guestbook` |
| Environment | `GUESTBOOK_DB=/home/ACCOUNT/guestbook-data/guestbook.db` |

Command에는 한 줄로 입력합니다.

```sh
/home/ACCOUNT/guestbook/.venv/bin/python -m uvicorn main:app --app-dir /home/ACCOUNT/guestbook --host "$IP" --port "$PORT" --workers 1
```

`$IP`와 `$PORT`는 alwaysdata가 제공하는 값을 사용하므로 이 두 부분은 계정명으로 바꾸지 않습니다. 플랫폼의 IPv6 주소와 할당 포트에 맞춰야 합니다. 배포 실행에는 개발용 `--reload`를 넣지 않습니다. DB는 소스 폴더 밖에 두어 코드 업로드와 구분합니다. [공식 ASGI 실행 방식](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/)

### 6. 배포 후 검증

1. `https://ACCOUNT.alwaysdata.net/`에서 폼과 CSS를 확인합니다.
2. `/health`에서 `{"status":"ok"}`를 확인합니다.
3. 테스트 글을 하나 작성하고 새로고침합니다.
4. 관리자 **Web > Sites**에서 **Restart**를 누르고 같은 글이 유지되는지 확인합니다.
5. `guestbook-data/guestbook.db`가 생성되었는지 확인하고 메모리·디스크 사용량을 확인합니다.

관리형 사이트이므로 SSH 연결을 종료해도 사이트는 관리자가 실행합니다. SSH 터미널의 `Ctrl+C`는 관리형 사이트를 중지하는 방법이 아닙니다. 코드 수정 후에는 관리자 화면에서 Restart합니다. 실패 로그는 `/home/ACCOUNT/admin/logs/sites/`에서 확인합니다. [재시작](https://help.alwaysdata.com/en/docs/web-hosting/sites/restart-a-site/), [User program 로그](https://help.alwaysdata.com/en/docs/web-hosting/sites/http-servers/user-program/)

## 백업과 유지

Free에는 3일의 일일 백업이 제공됩니다. SQLite의 일관된 사본이 필요하면 앱의 쓰기를 멈춘 상태에서 복사하거나 SQLite backup API를 사용합니다. 운영 중 DB 파일을 단순 복사하는 방식은 피합니다. 중요한 글은 별도의 로컬 백업도 보관합니다. [공식 백업 안내](https://help.alwaysdata.com/en/docs/web-hosting/backups/)

현재 앱은 익명 공개 글 작성과 1,000건 제한을 갖고 있으며 관리자 삭제·스팸 차단은 없습니다. 우선 소규모 학습용으로 운영하는 것이 적합합니다.

## Render에서 단기 시연만 할 경우

Root Directory `day1-day8`, Build Command `pip install -r requirements.txt`, Start Command `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`, Plan **Free**, Health Check `/health`로 설정합니다. 이 폴더만 별도 저장소라면 Root Directory는 비웁니다. 무료 영구 디스크가 없으므로 글 보존 용도로 추천하지 않습니다. [무료 제한](https://render.com/docs/free)
