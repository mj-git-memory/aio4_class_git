# note-demo

PythonAnywhere 무료 계정에 배포하는 Flask + SQLite 방명록입니다. Node.js나 프런트엔드 빌드가 필요하지 않습니다.

**배포·자료 확인일: 2026-10-27 (한국 시간).** 아래 안내는 이날 확인한 공식 문서와 실제 구현을 기준으로 합니다. PythonAnywhere 무료 계정에 실제 배포하고 HTTPS 화면을 확인했습니다.

## 혼자 배포할 때 먼저 읽기

**현재 `mjlee` 계정에는 이미 서비스가 배포되어 있습니다. 같은 계정에서 연습한다면 아래 ‘3-8. 현재 계정에서 직접 다시 배포하기’부터 따라 하세요.** 기존 앱을 삭제할 필요가 없습니다. 처음 설치하는 빈 계정이라면 3-2부터 3-7까지 순서대로 진행합니다.

| 상황 | 따라 할 순서 |
| --- | --- |
| 현재 mjlee 계정에서 다시 배포 연습 | 3-8 → 3-7의 화면 확인 |
| 앱이 없는 계정에서 처음 배포 | 3-2 → 3-3 → 3-4 → 3-5 → 3-6 → 3-7 |
| 관리자만 만들기 | PythonAnywhere Bash에서 가상환경 활성화 → `create-admin` |
| 오류가 생김 | 5절에서 증상 확인 → Web의 error log 읽기 |

### 명령은 어디에 입력하나요?

| 장소 | 여는 방법 | 여기서 하는 일 |
| --- | --- | --- |
| 내 컴퓨터 터미널 | macOS 터미널 또는 VS Code 터미널 | 프로젝트에서 배포 ZIP 생성 |
| PythonAnywhere Files | 로그인 후 상단 Files | ZIP 업로드·파일 위치 확인 |
| PythonAnywhere Bash | 상단 Consoles → Start a new console → Bash | 압축 해제·Python 패키지 설치·DB·관리자 준비 |
| PythonAnywhere Web | 상단 Web → mjlee.pythonanywhere.com | WSGI·가상환경·정적 파일·HTTPS 설정, Reload |
| 서비스 페이지 | https://mjlee.pythonanywhere.com/ | 일반 회원가입·로그인·방명록 사용 확인 |

터미널의 `$`, `(note-demo-env)` 같은 프롬프트 표시는 직접 입력하지 않습니다. 코드 블록 안의 명령만 한 줄씩 복사하고 Enter를 누릅니다. 설치 중에는 다시 프롬프트가 나올 때까지 기다리고, 오류가 나오면 다음 단계로 넘어가기 전에 5절을 확인하세요. 관리자 비밀번호 입력 중 글자나 별표가 보이지 않는 것은 정상입니다.

`YOUR_USERNAME`은 예시 표기입니다. 현재 계정에서 작업한다면 모두 **mjlee**로 바꿉니다. ‘PythonAnywhere 로그인 계정’, 앱에서 가입하는 ‘방명록 회원’, CLI로 만드는 ‘방명록 관리자’는 서로 다른 계정입니다.

## 현재 배포 정보

- 서비스: **[https://mjlee.pythonanywhere.com](https://mjlee.pythonanywhere.com/)**
- 서버: PythonAnywhere 미국 리전, Python 3.13.1, Flask WSGI
- 프로젝트: `/home/mjlee/note-demo`
- 가상환경: `/home/mjlee/.virtualenvs/note-demo-env`
- DB: `/home/mjlee/note-demo/instance/note_demo.sqlite3`
- 비밀번호: **최소 6자, 최대 128자**. 기존 비밀번호를 바꾸는 기능이나 6자로 강제 재설정하는 변경은 아닙니다.
- Web 화면에 표시된 현재 무료 앱 만료일: **2026-11-27**. 이 날짜 전에 로그인하고 **Run until 1 month from today** 버튼으로 연장하세요.
- 기본 관리자 계정은 없습니다. 관리자가 필요하면 아래 `create-admin` 명령으로 직접 생성하세요. 로컬 검증 계정·DB·비밀 키는 업로드하지 않았습니다.

## 제공 기능

- 이메일·닉네임·비밀번호(최소 6자, 최대 128자) 회원가입, 로그인·로그아웃, 비밀번호 찾기 목업
- 제목 없는 본문 작성, 최신순 목록, 마스킹된 본문 10글자 미리보기, 페이지당 10개
- 현재 페이지의 숨김 영역에 상세 본문·댓글 펼침, 본인 글 수정·삭제
- 글별 댓글 작성·조회, 글 삭제 시 댓글 함께 삭제
- 키워드·정규식 마스킹, 관리자 규칙 추가·삭제, 재시작 후 데이터 유지
- 서버 권한·CSRF 검사, 비밀번호 해시 저장, HTML 텍스트 렌더링

SNS 로그인, 실제 비밀번호 재설정·이메일 발송, 댓글 수정·삭제와 대댓글은 제공하지 않습니다. 이메일 소유 확인이 없는 학습용 데모입니다. 기본 관리자 계정이나 공개된 초기 비밀번호는 없습니다.

## 1. 로컬 실행 — macOS / Linux

Python 3.9 이상이 필요합니다. 로컬은 Python 3.9.12, 실제 PythonAnywhere 앱은 Python 3.13.1에서 확인했습니다. 신규 배포에서는 호스팅에서 제공하는 지원 중인 Python 버전을 선택하고, Web 앱과 가상환경의 버전을 일치시키세요. PythonAnywhere에 제공되는 버전은 계정의 시스템 이미지에 따라 확인해야 합니다.

터미널에서 이 프로젝트 디렉터리로 이동한 후 실행합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app init-config
python -m flask --app app init-db
python -m flask --app app run --port 5050
```

브라우저에서 [로컬 방명록](http://127.0.0.1:5050)을 엽니다. 회원가입 후 로그인하면 기록과 댓글을 남길 수 있습니다.

`init-config`는 영속 비밀 키를 `instance/config.py`에 생성합니다. 이미 파일이 있으면 덮어쓰지 않고 오류로 종료합니다. `init-db`는 최초에만 테이블과 초기 규칙을 생성하고, 초기화된 DB에서 재실행하면 기존 데이터와 규칙을 유지합니다. 현재 작업 폴더는 로컬 검증을 위해 이미 초기화되어 있으며 검증용 계정·글이 있습니다. 이 데이터와 계정은 배포 ZIP에서 제외됩니다. 지금 바로 로컬에서 실행할 때는 아래 명령만 사용하면 됩니다.

```bash
source .venv/bin/activate
python -m flask --app app run --port 5050
```

Windows PowerShell에서는 `py -m venv .venv`와 `.\.venv\Scripts\Activate.ps1`를 사용한 뒤 위의 `python -m ...` 명령을 동일하게 실행합니다. Windows 환경에서는 별도로 실행 확인하지 않았습니다.

### 관리자 생성

서버를 실행하는 것과 별개의 터미널에서 같은 가상환경을 활성화합니다.

```bash
python -m flask --app app create-admin
```

이메일·닉네임·비밀번호를 입력합니다. 비밀번호는 숨김 입력이며 두 번 확인합니다. 생성 후 웹 로그인 화면에서 로그인하고 상단 **규칙 관리**로 이동합니다. 일반 회원가입에서 관리자 역할을 선택할 수 없으며, 관리자도 다른 사용자의 글을 수정·삭제할 수 없습니다.

## 2. 테스트

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m pip check
```

테스트는 임시 SQLite DB와 테스트 전용 계정을 사용하므로 실행 중인 앱의 데이터를 변경하지 않습니다. 검증 결과와 수동 확인 범위는 [검증 기록](docs/verification.md)을 확인하세요.

## 3. PythonAnywhere 무료 계정 배포

### 3-1. 현재 무료 계정 조건

공식 안내는 무료 계정에 웹 앱 1개, 웹 워커 1개, 512 MiB 디스크, 1개월 앱 만료 기간을 명시합니다. 이 디스크에는 코드·가상환경·DB가 모두 포함됩니다. 만료 전 Web 화면에서 연장해야 합니다. 실제 계정의 만료일과 사용량을 확인하세요. [무료 계정 공식 안내](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/)

신규 무료 계정은 MySQL을 기본 제공하지 않습니다. 기존 계정은 생성일에 따라 다르며, 이 프로젝트는 모두에게 제공되는 SQLite를 사용합니다. SQLite는 소규모 데모용이며 고부하 운영 DB로 권장하지 않는다는 공식 안내도 참고하세요. [DB 지원 안내](https://help.pythonanywhere.com/pages/KindsOfDatabases)

무료 계정의 외부 인터넷 요청은 허용 목록 제한을 받습니다. 앱은 실행 중 외부 API·크롤링·메일 발송을 사용하지 않고 초기 마스킹 파일과 CSS·JS를 함께 제공합니다. [외부 요청 제한](https://help.pythonanywhere.com/pages/403ForbiddenError)

### 3-2. 소스 업로드

권장 경로 예시는 `/home/YOUR_USERNAME/note-demo`입니다. 아래의 `YOUR_USERNAME`은 **실제 PythonAnywhere 사용자명**으로 바꾸세요. 미국·EU 사이트 중 가입한 곳에서 작업합니다.

**내 컴퓨터 터미널**에서 프로젝트 디렉터리로 이동합니다. 현재 컴퓨터의 경로는 다음과 같습니다. 다른 컴퓨터에서는 실제 프로젝트 위치로 바꿉니다.

```bash
cd /Users/imijeong/Downloads/AIO_4_class/day10/demo
```

제공된 도구로 배포용 ZIP을 생성합니다.

```bash
python3 tools/package.py
```

터미널에 ‘생성 완료’가 나오고 프로젝트의 `dist` 폴더 안에 **note-demo.zip**이 보이면 준비 완료입니다. `dist/note-demo.zip`에는 소스·문서·의존성 목록만 들어갑니다. `.venv`, `instance`, 테스트 실행 캐시, 로컬 DB·비밀 키는 제외됩니다. 프로젝트 전체를 Finder에서 임의로 압축하기보다 이 도구를 사용하세요.

PythonAnywhere에 로그인하고 다음 순서로 업로드합니다.

1. 상단 **Files**를 누릅니다.
2. 현재 폴더가 `/home/YOUR_USERNAME`인지 확인합니다. 현재 계정은 `/home/mjlee`입니다.
3. **Upload a file**을 누르고 내 컴퓨터의 `dist/note-demo.zip`을 선택합니다.
4. 파일 목록에 `note-demo.zip`이 나타나면 업로드 완료입니다.
5. 상단 **Consoles → Bash**를 열고 다음을 실행합니다. 이후 이 절의 명령은 내 컴퓨터가 아니라 PythonAnywhere Bash에 입력합니다.

```bash
cd ~
unzip note-demo.zip
cd ~/note-demo
```

`pwd`를 입력했을 때 `/home/YOUR_USERNAME/note-demo`가 나오고, `ls`에서 `app`, `requirements.txt`, `wsgi.py`가 보이면 정상입니다. `note-demo/note-demo`처럼 두 번 중첩되었다면 압축을 푼 위치를 확인하세요.

무료 계정은 Files 업로드와 Bash의 ZIP 해제를 사용할 수 있습니다. SFTP·rsync는 유료 계정 기능이므로 필수 절차로 사용하지 않습니다. Git 저장소를 운영 중이라면 HTTPS clone/pull도 대안입니다. [공식 소스 업로드 안내](https://help.pythonanywhere.com/pages/UploadingAndDownloadingFiles/)

### 3-3. Python 가상환경과 의존성

빈 계정에서는 **Web → Add a new web app → Next → Manual configuration (including virtualenvs) → Python 3.13 → Next** 순서로 웹 앱을 만듭니다. 기본 예제 화면이 생성되어도 아직 프로젝트 연결 전이므로 다음 설정을 계속합니다. 현재 `mjlee` 계정에서는 이 단계를 반복하지 않고 기존 앱을 선택합니다.

PythonAnywhere Bash에서 다음 명령을 한 줄씩 실행합니다. 실제 배포에 사용한 방식과 동일합니다. 다른 Python 버전을 선택했다면 경로도 그 버전으로 바꾸세요.

```bash
cd ~/note-demo
python3.13 -m venv ~/.virtualenvs/note-demo-env
source ~/.virtualenvs/note-demo-env/bin/activate
python -m pip install --no-cache-dir -r requirements.txt
python -m pip check
python -m flask --app app init-config
python -m flask --app app init-db
```

정상 확인 기준:

- 가상환경 활성화 후 프롬프트 앞에 `(note-demo-env)`가 표시됩니다.
- 설치가 끝나면 `Successfully installed ...` 또는 이미 설치되어 있다는 안내가 나옵니다.
- `pip check` 결과는 `No broken requirements found.`입니다.
- `init-config`는 설정 생성 완료, `init-db`는 DB 스키마·초기 규칙 생성 완료를 안내합니다.
- `python --version`은 Web에서 선택한 Python 버전과 일치해야 합니다.

관리자 기능을 사용할 경우 아래 명령을 추가로 실행합니다. 일반 회원가입·글 작성만 연습할 때는 필수가 아닙니다.

```bash
python -m flask --app app create-admin
```

`관리자 이메일`, `관리자 닉네임`, `관리자 비밀번호`, 비밀번호 재확인을 차례로 입력합니다. 기존 일반 회원과 다른 이메일을 사용하세요. 완료 후 서비스의 로그인 화면에서 해당 계정으로 로그인하면 ‘규칙 관리’ 메뉴가 나타납니다.

이미 가상환경이 있으면 새로 만들지 않고 `source ~/.virtualenvs/note-demo-env/bin/activate`로 활성화합니다. 새 Bash 콘솔을 열 때마다 다시 활성화해야 합니다. 서버에는 배포용 `requirements.txt`만 설치해 디스크 사용량을 줄입니다. 공식 Flask 가이드는 가상환경과 Web 앱의 Python 버전을 일치시키도록 안내합니다. [Flask 배포 가이드](https://help.pythonanywhere.com/pages/Flask/)

### 3-4. DB 경로와 비밀 설정

기본 DB 경로는 앱에서 계산한 절대 경로 `/home/YOUR_USERNAME/note-demo/instance/note_demo.sqlite3`이므로 같은 구조라면 수정할 필요가 없습니다. 경로를 변경하려면 `instance/config.py`에 다음 설정을 추가하고 새 경로에 DB를 준비합니다.

```python
DATABASE = '/home/YOUR_USERNAME/note-demo/instance/note_demo.sqlite3'
```

`init-config`가 만든 SECRET_KEY는 직접 공개하거나 다른 프로젝트와 공유하지 마세요. 이 키를 재배포 때마다 바꾸면 기존 로그인 세션이 무효화됩니다. `instance/config.py`는 앱 팩토리가 직접 로드하므로 Bash에 설정한 환경변수가 Web 앱에 자동 전달될 것이라고 가정할 필요가 없습니다. PythonAnywhere도 콘솔과 WSGI의 환경 설정은 별도로 로드해야 한다고 안내합니다. [환경 설정 공식 안내](https://help.pythonanywhere.com/pages/EnvironmentVariables/)

### 3-5. Web 설정과 WSGI

상단 **Web → 웹 앱 이름**을 누르고 **Code**와 **Virtualenv** 영역에서 다음을 설정합니다. 각 경로의 파란 글씨 또는 `Enter ...` 문구를 누르면 입력창이 열립니다. 입력 후 체크 버튼 또는 Enter로 저장하고, 입력창이 닫힌 뒤 **새 경로가 화면에 표시되는지** 확인하세요.

| 항목 | 값 |
| --- | --- |
| Source code | `/home/YOUR_USERNAME/note-demo` |
| Working directory | `/home/YOUR_USERNAME/note-demo` |
| Virtualenv | `/home/YOUR_USERNAME/.virtualenvs/note-demo-env` |

Web 화면의 **WSGI configuration file** 링크를 열고 기본 예제 앱 설정을 다음으로 교체합니다.

```python
import sys

project_path = '/home/YOUR_USERNAME/note-demo'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from wsgi import application
```

현재 계정에서는 `YOUR_USERNAME`을 `mjlee`로 바꿉니다. 편집기에서 **Save**를 누르세요. 위 코드는 Python 파일의 내용이므로 Bash에 그대로 붙여넣는 코드가 아닙니다. 변경 전 WSGI 내용을 별도 파일에 복사해 두면 되돌리기 쉽습니다. 현재 실제 배포 시의 원본은 `/var/www/mjlee_pythonanywhere_com_wsgi.py.before-note-demo`에 백업되어 있습니다.

이 파일은 프로젝트의 `wsgi.py`와 구분되는 PythonAnywhere 관리 파일입니다. 프로젝트의 `wsgi.py`는 Flask 앱을 만들고 Secure 쿠키와 debug 비활성화를 적용하며 비밀 키가 없으면 시작을 거부합니다. 파일 import 시 서버 실행이나 DB 초기화를 수행하지 않습니다.

배포 서버에서 `flask run`이나 `app.run()`을 계속 실행하지 마세요. PythonAnywhere는 Web 화면의 WSGI 설정을 통해 앱을 제공합니다. [WSGI 설정과 app.run 주의사항](https://help.pythonanywhere.com/pages/Flask/)

### 3-6. 정적 파일과 HTTPS

**Web → Static files**에 다음 매핑을 추가합니다.

| URL | Directory |
| --- | --- |
| `/static/` | `/home/YOUR_USERNAME/note-demo/app/static` |

`Enter URL`에는 `/static/`를, 같은 행의 `Enter path`에는 정적 파일 폴더를 넣습니다. 두 값을 각각 저장하고 같은 행에 나란히 표시되는지 확인합니다. `/static/` 행이 이미 있으면 새 행을 만들지 말고 기존 값을 확인합니다.

프로젝트 루트나 `instance` 폴더는 매핑하지 마세요. DB·설정 파일이 다운로드되지 않도록 정적 디렉터리를 분리했습니다. 설정 후 **Reload**를 누릅니다. [정적 파일 공식 안내](https://help.pythonanywhere.com/pages/StaticFiles/)

Web 화면의 **Force HTTPS**를 활성화하고 Reload합니다. Web 화면에 실제로 표시된 HTTPS 주소로 접속하세요. 미국 계정은 보통 `https://YOUR_USERNAME.pythonanywhere.com`, EU 계정은 `https://YOUR_USERNAME.eu.pythonanywhere.com` 형식입니다. 프로젝트 WSGI의 Secure 쿠키 때문에 로그인은 HTTPS로 확인해야 합니다. [HTTPS 강제 설정](https://help.pythonanywhere.com/pages/ForcingHTTPS/)

### 3-7. 배포 후 확인

1. 방명록과 CSS가 정상 표시되는지 확인합니다.
2. 새 회원가입·로그인, 글 작성, 댓글 작성, 본인 글 수정·삭제를 확인합니다.
3. 다른 계정·시크릿 창에서 기존 데이터를 읽고 다른 사람의 글을 수정할 수 없는지 확인합니다.
4. 관리자로 규칙을 추가·삭제하고 기존 글·댓글의 마스킹 반영을 확인합니다.
5. Web의 Reload 후 계정·글·댓글·규칙이 그대로 유지되는지 확인합니다.
6. Web의 error/access 로그를 확인하고, 만료 전 연장일을 확인합니다.

현재 배포에서는 PythonAnywhere의 Python 3.13.1 가상환경·의존성 설치·SQLite 초기화·WSGI 진입점·정적 파일 매핑·Force HTTPS·Reload를 적용하고, 공개 방명록과 회원가입 화면의 6~128자 안내를 확인했습니다. 자세한 검증 범위는 [검증 기록](docs/verification.md)을 따릅니다.

### 3-8. 현재 계정에서 직접 다시 배포하기 — 지금 따라 할 순서

현재 `mjlee` 무료 계정의 웹 앱과 가상환경·DB는 이미 준비되어 있습니다. 이번 연습은 같은 앱에 소스를 다시 올리고 Reload하는 과정입니다. 무료 계정은 웹 앱 1개이므로 새 앱을 추가하지 않고 기존 앱을 사용합니다.

**① PythonAnywhere Bash에서 먼저 백업합니다.**

```bash
cd /home/mjlee/note-demo
source /home/mjlee/.virtualenvs/note-demo-env/bin/activate
python -m flask --app app backup-db /home/mjlee/note-demo-backups/before-my-practice.sqlite3
cp -n instance/config.py /home/mjlee/note-demo-backups/config-before-my-practice.py
```

DB 백업 생성 완료를 확인합니다. 같은 백업 파일이 이미 있다는 오류가 나오면 `before-my-practice-2.sqlite3`처럼 새 이름으로 바꿔 다시 실행합니다. 설정 백업의 `cp -n`은 기존 파일을 덮어쓰지 않습니다.

**② 내 컴퓨터 터미널에서 ZIP을 만듭니다.**

```bash
cd /Users/imijeong/Downloads/AIO_4_class/day10/demo
python3 tools/package.py
```

**③ PythonAnywhere Files의 `/home/mjlee`에 새 `note-demo.zip`을 업로드합니다.**

같은 이름의 ZIP을 교체할지 묻는다면 방금 만든 배포 ZIP으로 교체합니다. `instance/config.py`나 DB 파일을 올리는 작업이 아닙니다.

**④ PythonAnywhere Bash에서 소스와 의존성을 갱신합니다.**

```bash
cd /home/mjlee
unzip -o note-demo.zip
cd /home/mjlee/note-demo
source /home/mjlee/.virtualenvs/note-demo-env/bin/activate
python -m pip install --no-cache-dir -r requirements.txt
python -m pip check
```

`unzip -o`는 ZIP에 담긴 소스·문서를 교체합니다. 제공된 패키징 도구는 `instance`를 제외하므로 서버의 회원·글·댓글·규칙과 비밀 설정은 유지됩니다. **이 재배포 연습에서는 init-config, init-db, create-admin을 다시 실행하지 않습니다.** DB 구조를 바꾼 작업은 별도의 스키마 변경 절차가 필요하지만 이번 비밀번호 길이 변경에는 해당하지 않습니다.

**⑤ Web에서 설정을 확인하고 Reload합니다.**

| 항목 | 현재 계정의 값 |
| --- | --- |
| 웹 앱 | `mjlee.pythonanywhere.com` |
| Python version | `3.13` |
| Source code | `/home/mjlee/note-demo` |
| Working directory | `/home/mjlee/note-demo` |
| Virtualenv | `/home/mjlee/.virtualenvs/note-demo-env` |
| WSGI configuration file | `/var/www/mjlee_pythonanywhere_com_wsgi.py` |
| 정적 URL → Directory | `/static/` → `/home/mjlee/note-demo/app/static` |
| Force HTTPS | Enabled |

경로가 위와 같다면 다시 입력할 필요가 없습니다. **Reload mjlee.pythonanywhere.com**을 누르고 로딩 표시가 끝날 때까지 기다립니다. Web 화면의 Reload가 배포 적용 단계이며, 내 컴퓨터에서 Flask 서버를 켜는 것과는 다릅니다.

**⑥ 서비스에서 결과를 확인합니다.**

1. https://mjlee.pythonanywhere.com/ 를 열고 새로고침합니다.
2. 회원가입 화면에 ‘6~128자로 입력해 주세요’가 표시되는지 확인합니다.
3. 새 계정으로 가입하거나 기존 계정으로 로그인하고, 본인이 작성한 글과 댓글을 확인합니다.
4. 재배포 전에 있던 글이 유지되는지 확인합니다.
5. CSS가 예전 모습이면 macOS의 `Command + Shift + R`, Windows의 `Ctrl + Shift + R`로 강력 새로고침합니다.
6. 오류가 나면 Web → **Error log**에서 마지막 오류를 확인하고 5절과 비교합니다.

여기까지 성공하면 직접 재배포한 것입니다. 이 절의 명령을 따라 실행할 필요 없이 현재 문서만 검토하는 동안에는 서비스가 바뀌지 않습니다.

## 4. 업데이트·백업·복원

### DB 백업

가상환경을 활성화하고 프로젝트 디렉터리에서 실행합니다. 파일명 날짜는 실제 백업 날짜로 바꾸세요. 기존 백업 파일을 덮어쓰지 않습니다.

```bash
python -m flask --app app backup-db ~/note-demo-backups/backup-2026-10-27.sqlite3
```

SQLite 백업 API로 실행 중인 DB의 일관된 사본을 생성합니다. 백업 파일은 Files 화면에서 내려받아 별도로 보관하고, SECRET_KEY가 들어 있는 `instance/config.py`도 안전하게 보관합니다. 비밀 설정과 백업을 Git에 올리지 마세요.

### 코드 업데이트

DB 백업 후 변경한 `app`, `wsgi.py`, `requirements.txt` 등을 업로드합니다. `instance`를 덮어쓰지 않습니다. 가상환경에서 의존성을 재설치하고 Web 화면에서 Reload합니다. 현재 스키마는 v1이며 자동 DROP·재생성하지 않습니다. 미래 스키마 변경은 [스키마 변경 원칙](migrations/readme.md)을 따릅니다.

### 복원

Web 화면에서 앱을 일시 비활성화하는 등 요청·쓰기를 중단한 상태에서 진행합니다. 기존 DB를 별도 파일로 보존한 후 백업을 `instance/note_demo.sqlite3`에 복사하고, 파일 소유권·쓰기 권한과 DB 경로를 확인한 뒤 다시 활성화·Reload합니다. 복원 전후 다음 검사로 무결성을 확인할 수 있습니다.

```bash
python -c "import sqlite3; db=sqlite3.connect('instance/note_demo.sqlite3'); print(db.execute('PRAGMA integrity_check').fetchone()[0]); db.close()"
```

DB가 없거나 손상되면 앱은 오류를 안내합니다. 요청 중 임의로 빈 DB를 생성하거나 기존 손상 파일을 지우지 않습니다. 데이터가 없어진 것처럼 보이면 먼저 설정한 절대 경로가 올바른지 확인하세요.

## 5. 문제 해결

| 증상 | 확인할 사항 |
| --- | --- |
| 500 / 502 | Web error log, WSGI의 프로젝트 경로, 가상환경, 비밀 설정 생성 여부 |
| ModuleNotFoundError | Web과 가상환경 Python 버전 일치, requirements 설치, sys.path |
| 503 저장소 오류 | init-db 실행 여부, DB 절대 경로, 폴더 쓰기 권한, DB 잠금·손상 |
| 로그인 후 로그인 유지 안 됨 | HTTPS 접속 여부, 안정적인 SECRET_KEY, 브라우저 쿠키 설정 |
| CSRF 400 | 오래 열린 화면을 새로고침하고 다시 로그인·입력, fetch의 토큰 확인 |
| CSS 미표시 | Static files 매핑, Reload, 브라우저 캐시 새로고침 |
| 무료 앱 접속 불가 | Web 화면 만료일·연장 상태 확인 |
| 표현 검사 지연 안내 | 관리자 규칙 복잡도·수·본문 길이 확인. 원문 대신 안내를 보여주는 정상 보호 동작 |

## 6. 구조와 문서

- [구현 계획](plan.md)
- [화면 구성·ERD·전체 테이블 구조](docs/design.md)
- [마스킹 규칙 출처·라이선스·오탐 한계](docs/masking-sources.md)
- [테스트 및 실제 확인 기록](docs/verification.md)
- [SQLite 스키마](app/schema.sql)

비로그인 읽기 허용, 로그인 후 작성, 최신 글 우선, 댓글 작성 순, 본인 글만 수정·삭제를 기본으로 합니다. 다른 사용자의 열린 화면은 다음 조회·새로고침 때 규칙 변경이 반영되며 실시간 푸시는 없습니다. SQLite 파일과 앱의 단일 워커 구성은 소규모 데모를 대상으로 합니다.
