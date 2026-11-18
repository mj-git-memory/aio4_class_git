"""Supabase HTTP 경계의 요청 형식·오류 변환 검증. 외부 네트워크 불필요."""
import sys
from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import auth


def transport(monkeypatch, handler):
    monkeypatch.setenv('SUPABASE_URL', 'https://mock.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_mock')
    original = httpx.Client
    monkeypatch.setattr(auth.httpx, 'Client', lambda **kwargs:
                        original(transport=httpx.MockTransport(handler), **kwargs))


def test_auth_request_uses_api_key_and_user_jwt(monkeypatch):
    def handler(request):
        assert request.headers['apikey'] == 'sb_publishable_mock'
        assert request.headers['authorization'] == 'Bearer user-jwt'
        assert request.url.path == '/auth/v1/user'
        return httpx.Response(200, json={'id': 'verified-user'})
    transport(monkeypatch, handler)
    assert auth.auth_request('GET', 'user', token='user-jwt')['id'] == 'verified-user'


@pytest.mark.parametrize('status,code,expected', [
    (400, 'invalid_credentials', 401), (400, 'email_not_confirmed', 403),
    (429, 'over_request_rate_limit', 429), (500, '', 503), (401, '', 503),
])
def test_auth_errors_are_sanitized(monkeypatch, status, code, expected):
    transport(monkeypatch, lambda request: httpx.Response(status,
        json={'error_code': code, 'message': 'private upstream information'}))
    with pytest.raises(HTTPException) as caught:
        auth.auth_request('POST', 'token?grant_type=password', payload={'password': 'secret'})
    assert caught.value.status_code == expected
    assert 'private' not in caught.value.detail and 'secret' not in caught.value.detail


def test_auth_network_failure_is_service_unavailable(monkeypatch):
    def handler(request):
        raise httpx.ConnectError('private connection data', request=request)
    transport(monkeypatch, handler)
    with pytest.raises(HTTPException) as caught:
        auth.auth_request('GET', 'user', token='test')
    assert caught.value.status_code == 503


@pytest.mark.parametrize('code,status,text', [
    ('email_address_invalid', 400, '실제 메일을 받을 수 있는 이메일'),
    ('weak_password', 400, '비밀번호가 가입 조건'),
    ('email_address_not_authorized', 503, '메일 발송 설정'),
    ('email_exists', 409, '이미 가입된 이메일'),
    ('signup_disabled', 403, '신규 회원가입이 중단'),
    ('over_email_send_rate_limit', 429, '메일 발송 한도'),
])
@pytest.mark.parametrize('code_field', ['code', 'error_code'])
def test_signup_explains_actual_reason(monkeypatch, code, status, text, code_field):
    transport(monkeypatch, lambda request: httpx.Response(429 if status == 429 else 400,
        json={code_field: code, 'msg': 'private email/password information'}))
    with pytest.raises(HTTPException) as caught:
        auth.auth_request('POST', 'signup', payload={'email': 'user1@example.com', 'password': '12345678'})
    assert caught.value.status_code == status
    assert text in caught.value.detail
    assert '로그인 세션' not in caught.value.detail
    assert 'private' not in caught.value.detail and '12345678' not in caught.value.detail


def test_signup_unknown_error_does_not_claim_login_failure(monkeypatch):
    transport(monkeypatch, lambda request: httpx.Response(400, json={'code': 'new_error', 'msg': 'private data'}))
    with pytest.raises(HTTPException) as caught:
        auth.auth_request('POST', 'signup', payload={})
    assert caught.value.status_code == 400
    assert '회원가입' in caught.value.detail
    assert '로그인' not in caught.value.detail and 'private' not in caught.value.detail


def test_signup_email_error_reaches_customer_response(monkeypatch):
    from fastapi.testclient import TestClient
    import main
    transport(monkeypatch, lambda request: httpx.Response(422, json={'code': 'email_address_invalid'}))
    response = TestClient(main.app).post('/api/signup', headers={'X-Shop-Request': '1'}, json={
        'name': 'user', 'address': '', 'email': 'user1@example.com', 'password': '12345678',
    })
    assert response.status_code == 400
    assert 'example.com' in response.json()['detail']
    assert '실제 메일을 받을 수 있는 이메일' in response.json()['detail']
