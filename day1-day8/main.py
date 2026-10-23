"""실행: python -m uvicorn main:app --reload (현재 폴더: day1-day8)."""

import os
import sqlite3
from contextlib import asynccontextmanager
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

from database import add_entry, init_db, list_entries

BASE = Path(__file__).resolve().parent
MAX_BODY_BYTES = 16384
TEMPLATE = Template((BASE / "templates" / "index.html").read_text(encoding="utf-8"))


class EntryIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=20, pattern=r"^[^\x00]+$")
    message: str = Field(min_length=1, max_length=500, pattern=r"^[^\x00]+$")


def render_page(path: Path, page=1, error="", name="", message="", saved=False):
    rows, total, page, pages = list_entries(path, page)
    cards = []
    for row in rows:
        cards.append(
            '<article class="entry">'
            f'<header><h3>{escape(row["name"])}</h3>'
            f'<time datetime="{escape(row["created_at"])}">'
            f'{escape(row["created_at"][:16].replace("T", " · "))} KST</time></header>'
            f'<p>{escape(row["message"])}</p></article>'
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
    return TEMPLATE.substitute(
        notice=notice, name=escape(name), message=escape(message), total=total,
        entries="".join(cards) or '<p class="empty">아직 남겨진 이야기가 없어요.<br>첫 번째 인사를 남겨 주세요.</p>',
        pagination="".join(links),
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
    def home(page: str = "1", saved: str = ""):
        # 지나치게 긴 숫자나 잘못된 페이지는 첫 페이지로 안내한다.
        if not page.isascii() or not page.isdigit() or len(page) > 6 or int(page) < 1:
            return RedirectResponse("/", status_code=303)
        return render_page(path, int(page), saved=(saved == "1"))

    @app.post("/entries", response_class=HTMLResponse)
    async def create_entry(request: Request):
        async def error_page(text, status=422, name="", message=""):
            html = await run_in_threadpool(render_page, path, 1, text, name, message)
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
                              max_num_fields=2, encoding="utf-8", errors="strict")
            if set(fields) != {"name", "message"} or any(len(v) != 1 for v in fields.values()):
                raise ValueError("잘못된 양식")
            entry = EntryIn(**{key: values[0] for key, values in fields.items()})
        except (ValueError, ValidationError):
            return await error_page("이름은 1~20자, 내용은 1~500자로 입력해 주세요. 공백만 있는 글이나 잘못된 양식은 저장할 수 없습니다.")
        try:
            await run_in_threadpool(add_entry, path, entry.name, entry.message)
        except ValueError as error:
            return await error_page(str(error), 409, entry.name, entry.message)
        except sqlite3.OperationalError:
            return await error_page("지금은 저장할 수 없습니다. 잠시 후 다시 시도해 주세요.", 503, entry.name, entry.message)
        # 저장 후 조회로 이동해서 일반적인 새로고침에 따른 재등록을 막는다.
        return RedirectResponse("/?saved=1#entries", status_code=303)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
