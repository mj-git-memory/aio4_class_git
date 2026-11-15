import sqlite3
from pathlib import Path

import pytest
from werkzeug.security import check_password_hash

from app import create_app
from app.db import connect, get_db, new_id, now
from app.masking import FALLBACK, Masker, validate_rule
from conftest import api, login, signup, token


def make_post(client, body='안녕하세요, 반가워요!'):
    response = api(client, '/api/posts', 'POST', {'body': body})
    assert response.status_code == 201
    return response.json['id']


def promote(app, email='one@example.com'):
    with app.app_context():
        db = get_db()
        with db:
            db.execute("UPDATE users SET role='admin' WHERE email=?", (email,))


def test_signup_login_hash_and_logout(app, client):
    assert signup(client).status_code == 302
    assert signup(client, 'ONE@example.com').status_code == 400
    with app.app_context():
        user = get_db().execute('SELECT * FROM users').fetchone()
        assert user['role'] == 'user'
        assert user['password_hash'] != 'test-password'
        assert check_password_hash(user['password_hash'], 'test-password')
    assert client.post('/login', data={'email': 'one@example.com', 'password': 'wrong', 'csrf_token': token(client)}).status_code == 400
    assert login(client).status_code == 302
    with client.session_transaction() as session:
        assert 'user_id' in session and 'role' not in session and 'password_hash' not in session
    assert client.post('/logout', data={'csrf_token': token(client)}).status_code == 302
    assert api(client, '/api/posts', 'POST', {'body': '거부'}).status_code == 401


@pytest.mark.parametrize('email,nickname,password', [('bad', '별명', 'password'), ('', '별명', 'password'),
                                                      ('ok@example.com', ' ', 'password'), ('ok@example.com', '별명', 'short')])
def test_invalid_signup(client, email, nickname, password):
    assert client.post('/signup', data=dict(email=email, nickname=nickname, password=password, csrf_token=token(client))).status_code == 400


def test_six_character_password_signup_login_and_admin_cli(app, client):
    html = client.get('/signup').get_data(as_text=True)
    assert 'minlength="6"' in html and '6~128자' in html
    signup_data = dict(email='six@example.com', nickname='여섯자리', password='abc123', csrf_token=token(client))
    assert client.post('/signup', data=signup_data).status_code == 302
    assert client.post('/login', data=dict(email='six@example.com', password='abc123', csrf_token=token(client))).status_code == 302
    result = app.test_cli_runner().invoke(args=['create-admin', '--email', 'six-admin@example.com', '--nickname', '관리자'], input='xyz789\nxyz789\n')
    assert result.exit_code == 0, result.output
    with app.app_context():
        user = get_db().execute('SELECT * FROM users WHERE email=?', ('six-admin@example.com',)).fetchone()
        assert user['role'] == 'admin' and check_password_hash(user['password_hash'], 'xyz789')


def test_forgot_is_mock(client):
    response = client.post('/forgot-password', data={'email': 'who@example.com', 'csrf_token': token(client)})
    assert response.status_code == 200
    assert '이메일을 발송하거나 비밀번호를 변경하지 않습니다.' in response.get_data(as_text=True)


def test_csrf_and_registration_role_injection(client):
    assert client.post('/signup', data={'email': 'one@example.com'}).status_code == 400
    assert client.post('/api/posts', json={'body': 'x'}).status_code == 400
    assert client.get('/logout').status_code == 405
    assert client.post('/signup', data={'email': 'one@example.com', 'nickname': '닉네임', 'password': 'test-password', 'role': 'admin', 'csrf_token': token(client)}).status_code == 302
    login(client)
    assert client.get('/admin').status_code == 403


def test_empty_listing_and_hidden_region(client):
    data = client.get('/api/posts').json
    assert data == dict(page=1, pages=1, posts=[], total=0)
    html = client.get('/').get_data(as_text=True)
    assert 'id="post-detail"' in html and 'tabindex="-1" hidden' in html


def test_paging_and_last_page_delete(member):
    ids = [make_post(member, f'기록 {i:02}') for i in range(11)]
    first = member.get('/api/posts').json
    assert first['total'] == 11 and len(first['posts']) == 10 and first['pages'] == 2
    second = member.get('/api/posts?page=2').json
    assert len(second['posts']) == 1 and second['posts'][0]['id'] == ids[0]
    assert api(member, '/api/posts/' + ids[0], 'DELETE').status_code == 200
    assert member.get('/api/posts?page=999').json['page'] == 1
    assert member.get('/api/posts?page=bad').json['page'] == 1
    assert member.get('/api/posts?page=-2').json['page'] == 1


def test_owner_permissions_comments_and_cascade(app, member):
    post_id = make_post(member)
    other_post = make_post(member, '두 번째 기록')
    other = app.test_client()
    signup(other, 'two@example.com', '두번째')
    login(other, 'two@example.com')
    for method in ('PATCH', 'DELETE'):
        assert api(other, f'/api/posts/{post_id}', method, {'body': '변조'}).status_code == 403
    assert other.get(f'/api/posts/{post_id}/edit').status_code == 403
    assert api(other, f'/api/posts/{post_id}/comments', 'POST', {'body': '씨발 댓글'}).status_code == 201
    detail = member.get(f'/api/posts/{post_id}').json
    assert detail['comments'][0]['body'] == '** 댓글'
    assert member.get(f'/api/posts/{other_post}').json['comments'] == []
    assert api(member, f'/api/posts/{post_id}', 'PATCH', {'body': '수정한 본문'}).status_code == 200
    assert member.get(f'/api/posts/{post_id}/edit').json['body'] == '수정한 본문'
    assert api(member, f'/api/posts/{post_id}', 'DELETE').status_code == 200
    assert member.get(f'/api/posts/{post_id}').status_code == 404
    with app.app_context():
        assert get_db().execute('SELECT count(*) FROM comments').fetchone()[0] == 0


@pytest.mark.parametrize('body', ['', '  \n\t ', 'a' * 5001, None, 42])
def test_invalid_post_body(member, body):
    assert api(member, '/api/posts', 'POST', {'body': body}).status_code == 400


def test_invalid_comment_edit_and_anonymous_write(app, member):
    post_id = make_post(member)
    for body in (' ', 'a' * 1001):
        assert api(member, f'/api/posts/{post_id}/comments', 'POST', {'body': body}).status_code == 400
    assert api(member, f'/api/posts/{post_id}', 'PATCH', {'body': ' '}).status_code == 400
    anonymous = app.test_client()
    assert api(anonymous, f'/api/posts/{post_id}/comments', 'POST', {'body': 'x'}).status_code == 401
    assert anonymous.get(f'/api/posts/{post_id}/edit').status_code == 401


def test_masked_previews_and_no_raw_leak(member):
    raw = '앞부분123456씨발 끝\n씨.발'
    post_id = make_post(member, raw)
    listing = member.get('/api/posts').json
    assert listing['posts'][0]['preview'] == '앞부분123456*…'
    assert 'body' not in listing['posts'][0]
    assert raw not in member.get('/').get_data(as_text=True)
    assert '씨발' not in member.get(f'/api/posts/{post_id}').json['body']
    assert member.get(f'/api/posts/{post_id}/edit').json['body'] == raw


def test_xss_safe_template_and_read_api(member):
    payload = '<script>alert(1)</script>'
    signup(member, 'html@example.com', '<img src=x onerror=alert(1)>')
    login(member, 'html@example.com')
    post_id = make_post(member, payload)
    html = member.get('/').get_data(as_text=True)
    assert '<script>alert(1)</script>' not in html
    assert '&lt;img' in html
    assert member.get(f'/api/posts/{post_id}').json['body'] == payload
    script = (Path(__file__).parents[1] / 'app/static/app.js').read_text()
    assert 'innerHTML' not in script


def test_rules_authorization_validation_and_updates(app, member):
    post_id = make_post(member, '새금지어 확인')
    assert api(member, '/api/rules', 'POST', {'type': 'keyword', 'pattern': '새금지어'}).status_code == 403
    promote(app)
    assert member.get('/admin').status_code == 200
    for rule in [dict(type='regex', pattern='['), dict(type='regex', pattern='a*'),
                 dict(type='keyword', pattern=' '), dict(type='keyword', pattern='x', flags='i'),
                 dict(type='regex', pattern='a', flags='g'), dict(type='regex', pattern='a', flags='ii')]:
        assert api(member, '/api/rules', 'POST', rule).status_code == 400
    rule = {'type': 'keyword', 'pattern': '새금지어'}
    assert api(member, '/api/rules', 'POST', rule).status_code == 201
    assert api(member, '/api/rules', 'POST', rule).status_code == 409
    assert member.get(f'/api/posts/{post_id}').json['body'] == '**** 확인'
    with app.app_context():
        rule_id = get_db().execute('SELECT id FROM masking_rules WHERE pattern=?', ('새금지어',)).fetchone()[0]
    assert api(member, '/api/rules/' + rule_id, 'DELETE').status_code == 200
    assert member.get(f'/api/posts/{post_id}').json['body'] == '새금지어 확인'


def test_seed_not_restored_and_factory_reload(app, member):
    post_id = make_post(member)
    with app.app_context():
        db = get_db()
        with db:
            db.execute('DELETE FROM masking_rules')
    result = app.test_cli_runner().invoke(args=['init-db'])
    assert result.exit_code == 0
    fresh = create_app({'TESTING': True, 'SECRET_KEY': app.config['SECRET_KEY'], 'DATABASE': app.config['DATABASE']})
    with fresh.app_context():
        assert get_db().execute('SELECT count(*) FROM masking_rules').fetchone()[0] == 0
    assert fresh.test_client().get(f'/api/posts/{post_id}').status_code == 200


def test_database_constraints(app):
    with app.app_context():
        db = get_db()
        assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            with db:
                db.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?)', (new_id(), 'missing', 'text', now(), now()))
        with pytest.raises(sqlite3.IntegrityError):
            with db:
                db.execute("INSERT INTO masking_rules VALUES (?, 'keyword', '씨발', '', ?)", (new_id(), now()))


def test_missing_and_corrupt_database_are_not_replaced(tmp_path):
    path = tmp_path / 'missing.sqlite3'
    application = create_app({'TESTING': True, 'SECRET_KEY': 'testing', 'DATABASE': str(path)})
    assert application.test_client().get('/').status_code == 503
    assert not path.exists()
    path.write_bytes(b'corrupt database contents')
    assert application.test_client().get('/').status_code == 503
    assert path.read_bytes() == b'corrupt database contents'


def test_admin_cli_and_consistent_backup(app, tmp_path):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['create-admin', '--email', 'admin@example.com', '--nickname', '관리자'], input='admin-password\nadmin-password\n')
    assert result.exit_code == 0, result.output
    assert 'admin-password' not in result.output
    target = tmp_path / 'backup.sqlite3'
    assert runner.invoke(args=['backup-db', str(target)]).exit_code == 0
    db = connect(target)
    assert db.execute('SELECT role FROM users').fetchone()[0] == 'admin'
    db.close()
    assert runner.invoke(args=['backup-db', str(target)]).exit_code != 0


def test_headers_and_secure_session(app, client):
    app.config['SESSION_COOKIE_SECURE'] = True
    response = client.get('/')
    assert response.headers['Cache-Control'] == 'no-store'
    assert "frame-ancestors 'none'" in response.headers['Content-Security-Policy']
    assert 'Secure' in response.headers['Set-Cookie']
    assert 'HttpOnly' in response.headers['Set-Cookie'] and 'SameSite=Lax' in response.headers['Set-Cookie']


def test_grapheme_preview(member):
    make_post(member, '👨‍👩‍👧‍👦' * 11)
    assert member.get('/api/posts').json['posts'][0]['preview'] == '👨‍👩‍👧‍👦' * 10 + '…'


def test_literal_keyword_overlaps_and_regex_flags():
    rules = [dict(type='keyword', pattern='a.b', flags=''), dict(type='keyword', pattern='b!', flags=''),
             dict(type='regex', pattern='bad', flags='i')]
    assert Masker(rules).apply('a.b! axb BAD bad') == '**** axb *** ***'
    assert validate_rule('regex', 'test', 'mi')[2] == 'im'


def test_timeout_and_zero_width_fail_closed():
    bad = dict(type='regex', pattern='(a+)+$', flags='')
    assert Masker([bad], budget=0).apply('secret') == FALLBACK
    assert Masker([bad]).apply('a' * 5000 + '!') == FALLBACK
    assert Masker([dict(type='regex', pattern='(?=秘密)', flags='')]).apply('秘密') == FALLBACK
    assert Masker([dict(type='regex', pattern='[', flags='')]).apply('secret') == FALLBACK
