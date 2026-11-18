"""실행: python -m uvicorn main:app --reload (현재 폴더: day1-day8)."""

import os
# 기존
# import sqlite3
# 변경
import psycopg
from contextlib import asynccontextmanager
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi import Path as PathParameter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from starlette.concurrency import run_in_threadpool

from database import KST, add_entry, get_entry, init_db, list_entries, update_entry

BASE = Path(__file__).resolve().parent
MAX_BODY_BYTES = 16384
TEMPLATE = Template((BASE / "templates" / "index.html").read_text(encoding="utf-8"))


class EntryIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=20, pattern=r"^[^\x00]+$")
    message: str = Field(min_length=1, max_length=500, pattern=r"^[^\x00]+$")
    password: str = Field(min_length=4, max_length=4, pattern=r"^[0-9]{4}$")

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, value):
        if not value.strip():
            raise ValueError("공백만 있는 비밀번호는 사용할 수 없습니다.")
        # 비밀번호의 앞뒤 공백은 원문 그대로 비교한다.
        return value


class EntryEditIn(EntryIn):
    # 예전에 8~128자로 작성한 글은 원래 비밀번호로 수정할 수 있다.
    password: str = Field(min_length=4, max_length=128, pattern=r"^[^\x00]+$")


def render_page(path: Path, page=1, error="", name="", message="", saved=False,
                entry_id=None, updated=False):
    rows, total, page, pages = list_entries(path, page)
    cards = []
    for row in rows:
        created_at = row["created_at"]
        # 기존 TEXT 열과 PostgreSQL timestamp 열을 모두 표시합니다.
        if hasattr(created_at, "isoformat"):
            created_at = created_at.astimezone(KST).isoformat() if created_at.tzinfo else created_at.isoformat()
        cards.append(
            '<article class="entry">'
            f'<header><h3>{escape(row["name"])}</h3>'
            f'<time datetime="{escape(created_at)}">'
            f'{escape(created_at[:16].replace("T", " · "))} KST</time></header>'
            f'<p>{escape(row["message"])}</p>'
            f'<a class="edit-link" href="/entries/{row["id"]}/edit#write-title">수정</a></article>'
        )
    links = []
    if page > 1:
        links.append(f'<a href="/?page={page - 1}#entries">← 이전</a>')
    links.append(f'<span aria-current="page">{page} / {pages}</span>')
    if page < pages:
        links.append(f'<a href="/?page={page + 1}#entries">다음 →</a>')
    notice = ""
    if error:
        notice = f'<p class="notice error" role="alert">{escape(error)}</p>'
    elif saved:
        notice = '<p class="notice" role="status">방명록을 남겼습니다. 방문해 주셔서 고마워요!</p>'
    elif updated:
        notice = '<p class="notice" role="status">방명록을 수정했습니다.</p>'
    return TEMPLATE.substitute(
        notice=notice, name=escape(name), message=escape(message), total=total,
        entries="".join(cards) or '<p class="empty">아직 남겨진 이야기가 없어요.<br>첫 번째 인사를 남겨 주세요.</p>',
        pagination="".join(links),
        form_title="이야기 수정하기" if entry_id is not None else "안부 남기기",
        form_action=f"/entries/{entry_id}/edit" if entry_id is not None else "/entries",
        password_hint="작성할 때 정한 비밀번호" if entry_id is not None else "숫자 4자리 · 비밀번호는 저장되지 않습니다",
        password_attributes='minlength="4" maxlength="128"' if entry_id is not None else 'minlength="4" maxlength="4" pattern="[0-9]{4}" inputmode="numeric"',
        password_autocomplete="current-password" if entry_id is not None else "new-password",
        submit_label="수정 저장하기 ↗" if entry_id is not None else "방명록 남기기 ↗",
        cancel_link='<a href="/">수정 취소</a>' if entry_id is not None else "",
    )


def create_app(db_path: Path | None = None):
    path = Path(db_path or os.environ.get("GUESTBOOK_DB", BASE / "data" / "guestbook.db"))

    @asynccontextmanager
    async def lifespan(app):
        await run_in_threadpool(init_db, path)
        yield

    app = FastAPI(title="작은 방명록", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    def home(page: str = "1", saved: str = "", updated: str = ""):
        # 지나치게 긴 숫자나 잘못된 페이지는 첫 페이지로 안내한다.
        if not page.isascii() or not page.isdigit() or len(page) > 6 or int(page) < 1:
            return RedirectResponse("/", status_code=303)
        return render_page(path, int(page), saved=(saved == "1"), updated=(updated == "1"))

    @app.post("/entries", response_class=HTMLResponse)
    async def create_entry(request: Request):
        return await save_entry(request)

    @app.get("/entries/{entry_id}/edit", response_class=HTMLResponse)
    def edit_form(entry_id: int = PathParameter(ge=1, le=9223372036854775807)):
        entry = get_entry(path, entry_id)
        if entry is None:
            return HTMLResponse(render_page(path, error="방명록을 찾을 수 없습니다."), status_code=404)
        if not entry["password_hash"]:
            return HTMLResponse(render_page(path, error="비밀번호 기능 추가 전에 작성된 글은 수정할 수 없습니다."), status_code=403)
        return render_page(path, name=entry["name"], message=entry["message"], entry_id=entry_id)

    @app.post("/entries/{entry_id}/edit", response_class=HTMLResponse)
    async def edit_entry(request: Request, entry_id: int = PathParameter(ge=1, le=9223372036854775807)):
        return await save_entry(request, entry_id)

    async def save_entry(request: Request, entry_id=None):
        async def error_page(text, status=422, name="", message=""):
            html = await run_in_threadpool(render_page, path, 1, text, name, message,
                                          entry_id=entry_id)
            return HTMLResponse(html, status_code=status)

        if request.headers.get("content-type", "").split(";")[0].strip() != "application/x-www-form-urlencoded":
            return await error_page("화면의 입력 양식으로 작성해 주세요.", 415)
        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > MAX_BODY_BYTES:
                return await error_page("입력한 내용이 너무 큽니다.", 413)
            body.extend(chunk)
        try:
            # HTML 기본 폼을 표준 라이브러리로 읽어 추가 폼 패키지를 쓰지 않는다.
            fields = parse_qs(body.decode("utf-8"), keep_blank_values=True,
                              max_num_fields=3, encoding="utf-8", errors="strict")
            if set(fields) != {"name", "message", "password"} or any(len(v) != 1 for v in fields.values()):
                raise ValueError("잘못된 양식")
            model = EntryIn if entry_id is None else EntryEditIn
            entry = model(**{key: values[0] for key, values in fields.items()})
        except (ValueError, ValidationError):
            hint = "작성할 때 정한 비밀번호를 입력해 주세요." if entry_id is not None else "비밀번호는 숫자 4자리로 입력해 주세요."
            return await error_page(f"이름은 1~20자, 내용은 1~500자로 입력해 주세요. {hint} 공백만 있는 값이나 잘못된 양식은 저장할 수 없습니다.")
        try:
            if entry_id is None:
                await run_in_threadpool(add_entry, path, entry.name, entry.message, entry.password)
            else:
                await run_in_threadpool(update_entry, path, entry_id, entry.name, entry.message, entry.password)
        except LookupError as error:
            return await error_page(str(error), 404)
        except PermissionError as error:
            return await error_page(str(error), 403, entry.name, entry.message)
        except ValueError as error:
            return await error_page(str(error), 409, entry.name, entry.message)
        # # 기존
        # except sqlite3.OperationalError:
        # 변경
        except psycopg.OperationalError:
            return await error_page("지금은 저장할 수 없습니다. 잠시 후 다시 시도해 주세요.", 503, entry.name, entry.message)
        # 저장 후 조회로 이동해서 일반적인 새로고침에 따른 재등록을 막는다.
        target = "/?saved=1#entries" if entry_id is None else "/?updated=1#entries"
        return RedirectResponse(target, status_code=303)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
