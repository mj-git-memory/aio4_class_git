from concurrent.futures import ThreadPoolExecutor
import sqlite3

import pytest
from fastapi.testclient import TestClient

import database
from main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "guestbook.db")) as session:
        yield session


def post(client, **changes):
    data = {"name": "방문자", "message": "반갑습니다."}
    data.update(changes)
    return client.post("/entries", data=data, follow_redirects=False)


def test_page_and_css(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'lang="ko"' in response.text
    assert "아직 남겨진 이야기가 없어요" in response.text
    assert "<script" not in response.text
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_save_redirect_and_refresh(client):
    response = post(client, name="  손님  ", message="  첫째 줄\n둘째 줄  ")
    assert response.status_code == 303
    page = client.get(response.headers["location"])
    assert "방명록을 남겼습니다" in page.text
    assert "첫째 줄\n둘째 줄" in page.text
    assert "KST" in page.text
    for _ in range(2):
        assert client.get("/").text.count('<article class="entry">') == 1


@pytest.mark.parametrize("changes", [
    {"name": ""}, {"name": "   "}, {"name": "가" * 21},
    {"message": ""}, {"message": "\n \t"}, {"message": "가" * 501},
    {"message": "hello\x00world"},
])
def test_invalid_input_does_not_save(client, changes):
    assert post(client, **changes).status_code == 422
    assert '<article class="entry">' not in client.get("/").text


def test_maximum_lengths(client):
    assert post(client, name="가" * 20, message="나" * 500).status_code == 303


def test_html_escape_and_sql_parameters(client):
    assert post(client, name="<b>손님</b>", message="<script>alert(1)</script> & '); DROP TABLE entries; --").status_code == 303
    page = client.get("/").text
    assert "<script>" not in page
    assert "&lt;script&gt;" in page
    assert "&lt;b&gt;손님&lt;/b&gt;" in page
    assert post(client).status_code == 303


def test_order_and_pagination(client):
    for number in range(11):
        assert post(client, message=f"글번호 {number:02d}").status_code == 303
    first = client.get("/").text
    assert first.count('<article class="entry">') == 10
    assert first.index("글번호 10") < first.index("글번호 09")
    assert "글번호 00" not in first
    assert "글번호 00" in client.get("/?page=2").text
    assert "2 / 2" in client.get("/?page=999999").text
    assert "1 / 2" in first


@pytest.mark.parametrize("page", ["0", "-1", "abc", "1.5", "9" * 100, "²"])
def test_bad_page_redirects(client, page):
    assert client.get("/", params={"page": page}, follow_redirects=False).status_code == 303


def test_bad_forms_and_size(client):
    assert client.post("/entries", json={"name": "손님"}).status_code == 415
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    for body in [b"name=a", b"name=a&message=b&name=c", b"name=a&message=%FF"]:
        assert client.post("/entries", content=body, headers=headers).status_code == 422
    assert client.post("/entries", content=b"message=" + b"a" * 17000, headers=headers).status_code == 413


def test_restart_preserves_one_table(tmp_path):
    path = tmp_path / "guestbook.db"
    with TestClient(create_app(path)) as first:
        post(first, message="서버를 다시 시작해도 남는 글")
    with TestClient(create_app(path)) as second:
        assert "서버를 다시 시작해도 남는 글" in second.get("/").text
    with sqlite3.connect(path) as db:
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        assert tables == [("entries",)]


def test_capacity_under_concurrent_writes(tmp_path, monkeypatch):
    path = tmp_path / "guestbook.db"
    database.init_db(path)
    monkeypatch.setattr(database, "MAX_ENTRIES", 1)

    def write(number):
        try:
            database.add_entry(path, "손님", str(number))
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(write, range(2)))
    assert sum(results) == 1
    with TestClient(create_app(path)) as client:
        assert post(client).status_code == 409
