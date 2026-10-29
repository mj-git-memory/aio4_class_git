# Supabase 연결 및 Render 배포

현재 앱은 `guestbook.entries`를 사용합니다. `day11` 앱의 `public.entries`와는 별개입니다.
기존 `RENDER_DEPLOYMENT.md`의 SQLite 저장소 설명 대신 이 안내를 따릅니다.

## 로컬

`config.json`의 host, port, dbname, user, password를 읽습니다.
이 파일은 Git에서 제외되며 변경하거나 삭제하지 않습니다.
환경변수가 있으면 파일 값보다 우선합니다.
비밀번호를 파일에서 빼려면 password 키를 지우고 PGPASSWORD를 설정할 수 있습니다.
`.env` 파일은 자동으로 읽지 않습니다.

```bash
cd day1-day8
python -m pip install -r requirements.txt
```

기존 데이터를 옮기려면 앱을 종료하고 다음 명령을 한 번 실행합니다.
원본 SQLite를 읽기 전용으로 열며 ID, 내용, 작성일, 비밀번호 해시를 보존합니다.
대상에 데이터가 있으면 중단합니다. 기본 원본은 `data/guestbook.db`입니다.

```bash
python migrate_to_supabase.py
python -m uvicorn main:app --reload
```

기존 글 조회, 원래 비밀번호로 수정, 새 글 작성을 확인합니다.
기존 `test_guestbook.py`는 SQLite 기준이므로 실제 Supabase 연결로 실행하지 않습니다.

## Render

서비스의 Environment → Environment Variables에 아래 값을 직접 입력합니다.
config.json은 업로드하지 않아도 됩니다. 웹 서버는 터미널 비밀번호 입력을 기다리지 않습니다.

| 변수 | 입력할 값 |
|---|---|
| PGHOST | config.json의 host |
| PGPORT | config.json의 port (보통 5432) |
| PGDATABASE | config.json의 dbname |
| PGUSER | config.json의 user |
| PGPASSWORD | Supabase DB 비밀번호 |

Root Directory는 `day1-day8`, Build Command는 `pip install -r requirements.txt`,
Start Command는 `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`로 설정합니다.
앱 코드를 Push하고 환경변수를 저장한 뒤 재배포합니다.
이전 스크립트는 Build/Start Command에 넣지 않습니다.

접속정보 로더인 `db_config.py`도 반드시 함께 커밋합니다.
배포 후 조회, 작성, 수정을 다시 확인합니다.

공식 안내: https://render.com/docs/configure-environment-variables
