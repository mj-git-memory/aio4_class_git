"""실제 로컬 PostgreSQL + 모의 Auth. 운영 DB를 TEST_DATABASE_URL로 지정하지 마세요."""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import httpx
import psycopg
import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main
import auth

DSN = os.getenv('TEST_DATABASE_URL')


class FakeAuth:
    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.refreshes = 0
        self.revocations = 0

    def issue(self, email):
        user = self.users[email]
        access, refresh = 'access-' + str(uuid4()), 'refresh-' + str(uuid4())
        self.tokens[access] = user
        self.tokens[refresh] = user
        return dict(access_token=access, refresh_token=refresh, expires_in=3600, user=user)

    def __call__(self, method, path, *, payload=None, token=None):
        if path == 'signup':
            self.users[payload['email']] = dict(id=str(uuid4()), email=payload['email'],
                email_confirmed_at='2026-10-30T00:00:00Z', user_metadata=payload['data'])
            return {'user': self.users[payload['email']]}
        if path == 'token?grant_type=password':
            if payload['email'] not in self.users or payload['password'] != 'abcdefgh':
                raise HTTPException(401, '로그인 정보를 확인하세요.')
            return self.issue(payload['email'])
        if path == 'token?grant_type=refresh_token':
            self.refreshes += 1
            user = self.tokens.pop(payload['refresh_token'])
            return self.issue(user['email'])
        if path == 'user':
            if token not in self.tokens:
                raise HTTPException(401, '잘못된 토큰')
            return self.tokens[token]
        if path == 'logout?scope=local':
            self.revocations += 1
            return {}
        raise AssertionError(path)


@pytest.fixture
def shop(monkeypatch, request):
    dsn = request.config.getoption("--test-db") or DSN
    if not dsn:
        pytest.skip("TEST_DATABASE_URL 또는 --test-db로 로컬 테스트 DB를 지정하세요.")
    monkeypatch.setenv('AUTH_SESSION_KEY', Fernet.generate_key().decode())
    monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_test')
    monkeypatch.setenv('COOKIE_SECURE', 'false')

    def connect():
        c = psycopg.connect(dsn, row_factory=dict_row)
        if not c.info.dbname.endswith('_test'):
            c.close()
            raise RuntimeError('데이터 삭제 방지: 테스트 DB 이름은 _test로 끝나야 합니다.')
        return c

    monkeypatch.setattr(main, 'connect', connect)
    with connect() as c:
        c.execute((main.ROOT / 'schema.sql').read_text())
        c.execute('TRUNCATE shoppingmall.users RESTART IDENTITY CASCADE')
        c.execute('TRUNCATE shoppingmall.products RESTART IDENTITY CASCADE')
        c.execute('TRUNCATE shoppingmall.app_migrations')
        c.execute((main.ROOT / 'schema.sql').read_text())
    fake = FakeAuth()
    monkeypatch.setattr(auth, 'auth_request', fake)
    monkeypatch.setattr(main, 'auth_request', fake)
    with TestClient(main.app, headers={'X-Shop-Request': '1'}) as client:
        yield client, fake, connect
    main.app.dependency_overrides.clear()


def register(client, email='one@example.com'):
    assert client.post('/api/signup', json=dict(name='회원', email=email, password='abcdefgh')).status_code == 201
    assert client.post('/api/login', json=dict(email=email, password='abcdefgh')).status_code == 200
    return client.cookies.get(auth.COOKIE)


def test_guest_and_csrf(shop):
    client, _, _ = shop
    assert client.get('/api/products').status_code == 200
    for path in ['/api/me', '/api/cart', '/api/orders', '/api/admin/orders']:
        assert client.get(path).status_code == 401
    assert client.post('/api/logout', headers={'X-Shop-Request': ''}).status_code == 403
    assert client.post('/api/logout', headers={'Origin': 'https://evil.example'}).status_code == 403
    assert client.put('/api/admin/products/1', headers={'X-Shop-Request': ''}, json={}).status_code == 403


def test_tokens_encrypted_and_logout_revokes_cookie(shop):
    client, fake, connect = shop
    cookie = register(client)
    assert cookie and 'access-' not in cookie
    assert client.get('/api/me').json()['role'] == 'customer'
    with connect() as c:
        session = c.execute('SELECT * FROM shoppingmall.auth_sessions').fetchone()
        assert session['token_hash'] == auth.token_hash(cookie)
        assert not session['access_token'].startswith('access-')
        assert auth.cipher().decrypt(session['access_token'].encode()).decode().startswith('access-')
        assert c.execute('SELECT password_hash FROM shoppingmall.users').fetchone()['password_hash'] == ''
    assert client.post('/api/logout').status_code == 200
    client.cookies.set(auth.COOKIE, cookie)
    assert client.get('/api/me').status_code == 401
    assert fake.revocations == 1


def test_metadata_cannot_grant_admin_or_patch_role(shop):
    client, fake, _ = shop
    register(client)
    fake.users['one@example.com']['user_metadata']['role'] = 'admin'
    assert client.get('/api/admin/products').status_code == 403
    assert client.post('/api/admin/products', json={}).status_code == 403
    assert client.patch('/api/admin/orders/1/fulfillment', json={'status': 'shipped'}).status_code == 403
    assert client.patch('/api/me', json={'name': '회원', 'role': 'admin'}).status_code == 422
    assert client.get('/api/me').json()['role'] == 'customer'


def test_cart_orders_and_payment_are_isolated(shop):
    client, _, _ = shop
    first = register(client)
    product = client.get('/api/products').json()[0]
    assert client.post('/api/cart', json={'product_id': product['id'], 'quantity': 1}).status_code == 200
    order = client.post('/api/checkout', json={'address': '서울 테스트 주소'}).json()
    own = client.get('/api/orders/' + str(order['order_id']))
    assert own.status_code == 200 and own.json()['payment']['amount'] == product['price']
    register(client, 'two@example.com')
    assert client.get('/api/cart').json() == []
    assert client.get('/api/orders').json() == []
    assert client.get('/api/orders/' + str(order['order_id'])).status_code == 404
    # 다른 회원의 product ID로 삭제해도 첫 회원 주문이 바뀌지 않는다.
    assert client.delete('/api/cart/' + str(product['id'])).status_code == 200
    client.cookies.clear()
    client.cookies.set(auth.COOKIE, first)
    # 계정 전환 로그인으로 첫 세션도 폐기된다.
    assert client.get('/api/me').status_code == 401


def test_admin_product_visibility_delivery_and_immediate_demotion(shop):
    client, _, connect = shop
    register(client)
    with connect() as c:
        c.execute("UPDATE shoppingmall.users SET role='admin'")
    payload = dict(name='테스트상품', description='통합 검증', category='문구', price=12000,
                   stock=5, emoji='📦', active=True)
    r = client.post('/api/admin/products', json=payload)
    assert r.status_code == 201
    product_id = r.json()['id']
    assert client.post('/api/cart', json={'product_id': product_id, 'quantity': 1}).status_code == 200
    order = client.post('/api/checkout', json={'address': '테스트 배송지'}).json()
    order_id = order['order_id']
    endpoint = f'/api/admin/orders/{order_id}/fulfillment'
    assert client.patch(endpoint, json={'status': 'delivered'}).status_code == 409
    assert client.patch(endpoint, json={'status': 'shipped'}).status_code == 200
    assert client.patch(endpoint, json={'status': 'preparing'}).status_code == 409
    assert client.patch(endpoint, json={'status': 'delivered'}).status_code == 200
    payload.update(active=False, price=15000)
    assert client.put(f'/api/admin/products/{product_id}', json=payload).status_code == 200
    assert product_id not in [p['id'] for p in client.get('/api/products').json()]
    assert client.post('/api/cart', json={'product_id': product_id, 'quantity': 1}).status_code == 404
    assert client.get(f'/api/orders/{order_id}').json()['total'] == 12000
    with connect() as c:
        c.execute("UPDATE shoppingmall.users SET role='customer'")
    assert client.get('/api/admin/orders').status_code == 403


def test_refresh_is_serialized(shop):
    client, fake, connect = shop
    cookie = register(client)
    with connect() as c:
        c.execute('UPDATE shoppingmall.auth_sessions SET token_expires_at=%s', (int(time.time()) - 1,))
    class Request:
        cookies = {auth.COOKIE: cookie}
    with ThreadPoolExecutor(max_workers=2) as pool:
        users = list(pool.map(lambda _: auth.authenticated_user(connect, Request()), range(2)))
    assert users[0]['id'] == users[1]['id']
    assert fake.refreshes == 1


def test_legacy_email_requires_explicit_link(shop):
    client, _, connect = shop
    with connect() as c:
        c.execute("INSERT INTO shoppingmall.users(name,email,password_hash) VALUES ('기존회원','old@example.com','legacy')")
    assert client.post('/api/signup', json=dict(name='회원', email='old@example.com', password='abcdefgh')).status_code == 201
    assert client.post('/api/login', json=dict(email='old@example.com', password='abcdefgh')).status_code == 409
    with connect() as c:
        assert c.execute('SELECT auth_user_id FROM shoppingmall.users').fetchone()['auth_user_id'] is None


def test_withdrawal_blocks_all_sessions(shop):
    client, fake, connect = shop
    cookie = register(client)
    # 별도 장치 로그인으로 만든 세션도 탈퇴 시 무효화
    response = main.Response()
    auth.start_session(connect, fake.issue('one@example.com'), response)
    assert client.delete('/api/me').status_code == 200
    client.cookies.set(auth.COOKIE, cookie)
    assert client.get('/api/me').status_code == 401
    assert client.post('/api/login', json=dict(email='one@example.com', password='abcdefgh')).status_code == 403
    with connect() as c:
        assert c.execute('SELECT count(*) AS n FROM shoppingmall.auth_sessions').fetchone()['n'] == 0


def test_schema_rerun_preserves_profiles_and_data_api_denied(shop):
    client, _, connect = shop
    register(client)
    with connect() as c:
        c.execute((main.ROOT / 'schema.sql').read_text())
        assert c.execute('SELECT count(*) AS n FROM shoppingmall.users').fetchone()['n'] == 1
    for role in ['anon', 'authenticated']:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with connect() as c:
                c.execute('SET LOCAL ROLE ' + role)
                c.execute('SELECT * FROM shoppingmall.auth_sessions')


def test_seed_does_not_resurrect_renamed_product(shop):
    client, _, connect = shop
    product = client.get('/api/products').json()[0]
    with connect() as c:
        c.execute('UPDATE shoppingmall.products SET name=%s WHERE id=%s', ('수정한 상품', product['id']))
        c.execute((main.ROOT / 'schema.sql').read_text())
        assert c.execute('SELECT count(*) AS n FROM shoppingmall.products').fetchone()['n'] == 36
        assert c.execute('SELECT name FROM shoppingmall.products WHERE id=%s', (product['id'],)).fetchone()['name'] == '수정한 상품'


def test_hidden_product_already_in_cart_cannot_be_checked_out(shop):
    client, _, connect = shop
    register(client)
    product = client.get('/api/products').json()[0]
    assert client.post('/api/cart', json={'product_id':product['id'], 'quantity':1}).status_code == 200
    with connect() as c:
        c.execute('UPDATE shoppingmall.products SET active=FALSE WHERE id=%s', (product['id'],))
    assert client.post('/api/checkout', json={'address':'테스트 배송지'}).status_code == 409
    with connect() as c:
        assert c.execute('SELECT count(*) AS n FROM shoppingmall.payments').fetchone()['n'] == 0


def test_logout_still_blocks_cookie_when_auth_is_unavailable(shop, monkeypatch):
    client, fake, _ = shop
    cookie = register(client)
    def unavailable(*args, **kwargs):
        raise HTTPException(503, '인증 서비스 일시 중단')
    monkeypatch.setattr(auth, 'auth_request', unavailable)
    result = client.post('/api/logout')
    assert result.status_code == 200 and '확인되지' in result.json()['message']
    client.cookies.set(auth.COOKIE, cookie)
    assert client.get('/api/me').status_code == 401
