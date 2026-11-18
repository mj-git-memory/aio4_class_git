from concurrent.futures import ThreadPoolExecutor
import sqlite3

import pytest
from fastapi.testclient import TestClient

import database
from main import create_app
from passwords import verify_password


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "guestbook.db")) as session:
        yield session


def post(client, **changes):
    data = {"name": "방문자", "message": "반갑습니다.", "password": "0123"}
    data.update(changes)
    return client.post("/entries", data=data, follow_redirects=False)


def test_page_and_css(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'lang="ko"' in response.text
    assert "아직 남겨진 이야기가 없어요" in response.text
    assert "<script" not in response.text
    assert 'pattern="[0-9]{4}" inputmode="numeric"' in response.text
    assert 'minlength="4" maxlength="4"' in response.text
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
            database.add_entry(path, "손님", str(number), "0123")
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(write, range(2)))
    assert sum(results) == 1
    with TestClient(create_app(path)) as client:
        assert post(client).status_code == 409


def edit(client, entry_id=1, **changes):
    data = {"name": "수정한 이름", "message": "수정한 이야기", "password": "0123"}
    data.update(changes)
    return client.post(f"/entries/{entry_id}/edit", data=data, follow_redirects=False)


@pytest.mark.parametrize("password", ["", "123", "12345", "abcd", "12a4", "１２３４", " 123", "1234 ", "123\n", "hello\x00password"])
def test_bad_password_does_not_create_entry(client, password):
    assert post(client, password=password).status_code == 422
    assert '<article class="entry">' not in client.get("/").text


def test_password_required(client):
    assert client.post("/entries", data={"name": "손님", "message": "안녕"}).status_code == 422


def test_leading_zero_password(client):
    assert post(client, password="0001").status_code == 303
    assert edit(client, password="0001").status_code == 303


def test_edit_requires_correct_password(client):
    post(client)
    page = client.get("/entries/1/edit")
    assert page.status_code == 200
    assert "반갑습니다." in page.text
    assert 'action="/entries/1/edit"' in page.text
    assert 'autocomplete="current-password"' in page.text
    assert "0123" not in page.text
    wrong = edit(client, password="9999")
    assert wrong.status_code == 403
    assert "비밀번호가 일치하지 않습니다" in wrong.text
    assert "9999" not in wrong.text
    assert "수정한 이야기" not in client.get("/").text
    response = edit(client)
    assert response.status_code == 303
    assert "방명록을 수정했습니다" in client.get(response.headers["location"]).text
    assert "수정한 이야기" in client.get("/").text
    assert "반갑습니다." not in client.get("/").text
    assert client.get("/").text.count('<article class="entry">') == 1


def test_password_is_per_entry(client):
    post(client)
    post(client, password="9876")
    assert edit(client, entry_id=2).status_code == 403
    assert edit(client, entry_id=2, password="9876").status_code == 303


def test_edit_keeps_identity_date_and_hash(tmp_path):
    path = tmp_path / "guestbook.db"
    with TestClient(create_app(path)) as client:
        post(client)
        before = dict(database.get_entry(path, 1))
        assert edit(client, message="<script>alert(1)</script>").status_code == 303
        page = client.get("/").text
        assert "&lt;script&gt;" in page and "<script>" not in page
        after = dict(database.get_entry(path, 1))
        for key in ["id", "created_at", "password_hash"]:
            assert before[key] == after[key]


@pytest.mark.parametrize("changes", [{"name": " "}, {"message": "가" * 501}, {"password": ""}])
def test_invalid_edit_preserves_original(client, changes):
    post(client)
    assert edit(client, **changes).status_code == 422
    assert "반갑습니다." in client.get("/").text


def test_missing_entry(client):
    assert client.get("/entries/999/edit").status_code == 404
    assert edit(client, entry_id=999).status_code == 404


@pytest.mark.parametrize("entry_id", ["0", "-1", "abc", "9223372036854775808"])
def test_bad_entry_identifier(client, entry_id):
    assert client.get(f"/entries/{entry_id}/edit").status_code == 422
    assert edit(client, entry_id=entry_id).status_code == 422


def test_passwords_are_hashed_and_not_listed(tmp_path):
    path = tmp_path / "guestbook.db"
    with TestClient(create_app(path)) as client:
        post(client)
        post(client)
        first = database.get_entry(path, 1)["password_hash"]
        second = database.get_entry(path, 2)["password_hash"]
        assert first.startswith("pbkdf2_sha256$") and first != second
        assert "0123" not in first
        assert verify_password("0123", first)
        assert "password_hash" not in database.list_entries(path, 1)[0][0].keys()
        for url in ["/", "/entries/1/edit"]:
            html = client.get(url).text
            assert first not in html and "0123" not in html


def test_legacy_long_password_still_works(tmp_path):
    path = tmp_path / "legacy.db"
    password = " password-with-spaces "
    database.init_db(path)
    database.add_entry(path, "이전 손님", "긴 비밀번호로 작성한 글", password)
    with TestClient(create_app(path)) as client:
        assert edit(client, password=password.strip()).status_code == 403
        assert edit(client, password=password).status_code == 303
        assert 'maxlength="128"' in client.get("/entries/1/edit").text


def test_old_database_migrates_without_losing_entries(tmp_path):
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE entries (id INTEGER PRIMARY KEY, name TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)")
        db.execute("INSERT INTO entries VALUES (1, '이전 손님', '예전 글 보존', '2026-10-23T12:00+09:00')")
    for _ in range(2):
        with TestClient(create_app(path)) as client:
            assert "예전 글 보존" in client.get("/").text
            assert client.get("/entries/1/edit").status_code == 403
            assert edit(client).status_code == 403
    with TestClient(create_app(path)) as client:
        assert post(client).status_code == 303
        assert edit(client, entry_id=2).status_code == 303
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 2
        assert db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == [("entries",)]


def test_new_password_survives_restart(tmp_path):
    path = tmp_path / "guestbook.db"
    with TestClient(create_app(path)) as client:
        post(client)
    with TestClient(create_app(path)) as client:
        assert edit(client).status_code == 303


def test_edit_does_not_count_as_new_entry(client, monkeypatch):
    post(client)
    monkeypatch.setattr(database, "MAX_ENTRIES", 1)
    assert post(client).status_code == 409
    assert edit(client).status_code == 303


@pytest.mark.parametrize("stored", ["", "broken", "pbkdf2_sha256$bad$salt$hash", "other$600000$a$b"])
def test_bad_hash_fails_closed(stored):
    assert not verify_password("0123", stored)
