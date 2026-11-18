"""DB/외부 Auth 없이 Swagger 안내와 요청 보호 동작을 검증한다."""
import sys
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main

PAYLOAD = dict(name='user', address='', email='user1@example.com', password='12345678')


def test_missing_header_explains_cause_and_fix(monkeypatch):
    upstream = Mock()
    monkeypatch.setattr(main, 'auth_request', upstream)
    client = TestClient(main.app)  # lifespan을 실행하지 않아 실제 DB에 연결하지 않는다.
    response = client.post('/api/signup', json=PAYLOAD)
    assert response.status_code == 403
    body = response.json()
    assert body['code'] == 'SHOP_REQUEST_HEADER_REQUIRED'
    assert '새로고침' in body['detail']
    assert '홈' in body['hint']
    for technical_term in ('X-Shop-Request', 'Swagger', 'JSON', 'Postman'):
        assert technical_term not in body['detail'] + body['hint']
    assert response.headers['cache-control'] == 'no-store'
    assert PAYLOAD['password'] not in response.text
    upstream.assert_not_called()


def test_incorrect_header_value_is_rejected():
    response = TestClient(main.app).post('/api/signup', headers={'X-Shop-Request': '0'}, json=PAYLOAD)
    assert response.status_code == 403
    assert response.json()['code'] == 'SHOP_REQUEST_HEADER_REQUIRED'


def test_swagger_documents_header_and_forbidden_response():
    schema = TestClient(main.app).get('/openapi.json').json()
    for path, operations in schema['paths'].items():
        for method in ('post', 'put', 'patch', 'delete'):
            if method not in operations:
                continue
            operation = operations[method]
            header = next(p for p in operation['parameters'] if p['name'] == 'X-Shop-Request')
            assert header['in'] == 'header' and header['required']
            assert header['schema']['default'] == '1'
            assert '403' in operation['responses']
    assert not schema['paths']['/api/products']['get'].get('parameters')


def test_same_origin_header_allows_signup_to_reach_auth(monkeypatch):
    upstream = Mock(return_value={})
    monkeypatch.setattr(main, 'auth_request', upstream)
    response = TestClient(main.app).post('/api/signup', json=PAYLOAD, headers={
        'X-Shop-Request': '1', 'Origin': 'http://testserver',
    })
    assert response.status_code == 201
    upstream.assert_called_once()


def test_cross_origin_stays_blocked_with_fix_guidance(monkeypatch):
    upstream = Mock()
    monkeypatch.setattr(main, 'auth_request', upstream)
    client = TestClient(main.app)
    for headers in [{'Origin': 'https://other.example'}, {'Sec-Fetch-Site': 'cross-site'}]:
        response = client.post('/api/signup', json=PAYLOAD, headers={'X-Shop-Request': '1', **headers})
        assert response.status_code == 403
        assert response.json()['code'] == 'CROSS_ORIGIN_REQUEST_BLOCKED'
        assert '쇼핑몰 홈' in response.json()['detail']
        assert '/docs' not in response.json()['hint']
    upstream.assert_not_called()
