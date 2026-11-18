"""Supabase Auth와 서버 세션. 브라우저에는 JWT 대신 무작위 세션 ID만 전달한다."""
import hashlib
import logging
import os
import secrets
import time
from uuid import UUID

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

COOKIE = 'shop_session'
SESSION_SECONDS = 7 * 24 * 60 * 60
logger = logging.getLogger(__name__)


def raise_auth_failure(path, response):
    """Auth의 실제 오류 종류를 고객 안내로 번역한다. 원문에는 개인정보가 있어 노출하지 않는다."""
    try:
        body = response.json()
        code = (body.get('error_code') or body.get('code') or '') if isinstance(body, dict) else ''
        code = code if isinstance(code, str) else ''
    except ValueError:
        code = ''
    messages = {
        'email_address_invalid': (400, '가입할 수 없는 이메일 주소입니다. example.com 같은 예시 주소 대신 실제 메일을 받을 수 있는 이메일을 입력해주세요.'),
        'weak_password': (400, '비밀번호가 가입 조건을 충족하지 않습니다. 더 길게 입력하고 영문·숫자·특수문자를 조합해주세요.'),
        'email_address_not_authorized': (503, '현재 이 이메일 주소로 가입 확인 메일을 보낼 수 없습니다. 쇼핑몰의 메일 발송 설정 확인이 필요합니다.'),
        'email_exists': (409, '이미 가입된 이메일입니다. 로그인하거나 다른 이메일로 가입해주세요.'),
        'user_already_exists': (409, '이미 가입된 계정입니다. 로그인해주세요.'),
        'signup_disabled': (403, '현재 신규 회원가입이 중단되어 있습니다. 나중에 다시 이용해주세요.'),
        'email_provider_disabled': (503, '현재 이메일 회원가입·로그인을 이용할 수 없습니다. 잠시 후 다시 시도해주세요.'),
        'email_not_confirmed': (403, '이메일 인증이 아직 완료되지 않았습니다. 받은 메일의 가입 확인 링크를 눌러주세요.'),
        'over_email_send_rate_limit': (429, '가입 확인 메일 발송 한도에 도달했습니다. 잠시 후 다시 시도해주세요.'),
        'over_request_rate_limit': (429, '짧은 시간에 여러 번 요청했습니다. 잠시 기다린 뒤 다시 시도해주세요.'),
        'invalid_credentials': (401, '이메일 또는 비밀번호가 올바르지 않습니다. 입력한 내용을 확인해주세요.'),
        'user_banned': (403, '이용이 중지된 계정입니다.'),
        'captcha_failed': (400, '자동 가입 방지 확인을 완료하지 못했습니다. 페이지를 새로고침한 뒤 다시 시도해주세요.'),
    }
    # 요청 본문·이메일·비밀번호·토큰·Auth 메시지 원문은 기록하지 않는다.
    logger.warning('Auth request rejected: operation=%s status=%s code=%s',
                   path.split('?')[0], response.status_code, code if code in messages else 'unknown')
    # 서버 장애와 횟수 제한은 입력을 고쳐서 해결되는 문제가 아니다.
    if response.status_code == 429:
        status, message = messages.get(code, (429, '요청이 많아 잠시 이용할 수 없습니다. 잠시 후 다시 시도해주세요.'))
    elif response.status_code >= 500:
        status, message = 503, '일시적인 서비스 문제로 처리하지 못했습니다. 잠시 후 다시 시도해주세요.'
    elif code in messages:
        status, message = messages[code]
    elif path == 'signup':
        status = 503 if response.status_code in (401, 403) else 400
        message = '회원가입을 완료하지 못했습니다. 잠시 후 다시 시도해주세요.'
    elif path == 'token?grant_type=password' and response.status_code in (400, 422):
        status, message = 401, '이메일 또는 비밀번호가 올바르지 않습니다. 입력한 내용을 확인해주세요.'
    elif path == 'token?grant_type=password':
        status, message = 503, '현재 로그인 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.'
    else:
        status, message = 401, '로그인 유효기간이 끝났거나 로그인 상태를 확인할 수 없습니다. 다시 로그인해주세요.'
    raise HTTPException(status, message)


def cipher():
    try:
        return Fernet(os.environ['AUTH_SESSION_KEY'].encode())
    except (KeyError, ValueError):
        raise RuntimeError('AUTH_SESSION_KEY에 Fernet 키를 설정하세요. 로컬테스트.md를 확인하세요.') from None


def validate_config():
    url = os.getenv('SUPABASE_URL', '').rstrip('/')
    if not url.startswith('https://') or not os.getenv('SUPABASE_PUBLISHABLE_KEY'):
        raise RuntimeError('SUPABASE_URL과 SUPABASE_PUBLISHABLE_KEY를 설정하세요.')
    cipher()


def auth_request(method, path, *, payload=None, token=None):
    # JWT 해독만으로 신뢰하지 않고 Supabase Auth 서버가 검증하게 한다.
    headers = {'apikey': os.environ['SUPABASE_PUBLISHABLE_KEY']}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.request(method, os.environ['SUPABASE_URL'].rstrip('/') +
                                      '/auth/v1/' + path, headers=headers, json=payload)
    except httpx.HTTPError:
        raise HTTPException(503, '인증 서비스에 연결할 수 없습니다. 잠시 후 다시 시도하세요.') from None
    if response.is_error:
        raise_auth_failure(path, response)
    if not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        raise HTTPException(502, '인증 서비스 응답 형식이 올바르지 않습니다.') from None


def token_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def token_fields(result):
    try:
        access, refresh = result['access_token'], result['refresh_token']
        if not isinstance(access, str) or not access or not isinstance(refresh, str) or not refresh:
            raise ValueError
        expires = int(result.get('expires_at') or time.time() + int(result['expires_in']))
    except (KeyError, ValueError, TypeError):
        raise HTTPException(502, '인증 서비스의 세션 응답이 올바르지 않습니다.') from None
    box = cipher()
    return box.encrypt(access.encode()).decode(), box.encrypt(refresh.encode()).decode(), expires


def verified_identity(access):
    identity = auth_request('GET', 'user', token=access)
    try:
        UUID(identity['id'])
        if not identity.get('email') or not identity.get('email_confirmed_at'):
            raise ValueError
    except (KeyError, ValueError, TypeError, AttributeError):
        raise HTTPException(403, '이메일 인증을 완료한 계정이 필요합니다.') from None
    return identity


def profile_for_identity(conn, identity):
    profile = conn.execute('''SELECT id,name,email,address,role,active,auth_user_id
        FROM shoppingmall.users WHERE auth_user_id=%s''', (identity['id'],)).fetchone()
    if profile:
        if not profile['active']:
            raise HTTPException(403, '탈퇴하거나 이용이 중지된 쇼핑몰 계정입니다.')
        return profile
    # 이메일 일치만으로 과거 구매 내역을 새 Auth 계정에 연결하지 않는다.
    email = identity['email'].lower()
    if conn.execute('SELECT id FROM shoppingmall.users WHERE email=%s', (email,)).fetchone():
        raise HTTPException(409, '기존 회원 정보가 있습니다. 운영자에게 Auth 계정 연결을 요청하세요.')
    metadata = identity.get('user_metadata') or {}
    # user_metadata는 사용자가 수정할 수 있다. 여기서 role을 가져오면 안 된다.
    name = str(metadata.get('name') or '회원')[:50]
    address = str(metadata.get('address') or '')[:300]
    return conn.execute('''INSERT INTO shoppingmall.users
        (name,email,address,auth_user_id) VALUES (%s,%s,%s,%s)
        ON CONFLICT(auth_user_id) DO UPDATE SET auth_user_id=EXCLUDED.auth_user_id
        RETURNING id,name,email,address,role,active,auth_user_id''',
        (name, email, address, identity['id'])).fetchone()


def start_session(connect, result, response):
    encrypted_access, encrypted_refresh, expires = token_fields(result)
    access = result['access_token']
    identity = verified_identity(access)
    token = secrets.token_urlsafe(32)
    with connect() as conn:
        # 동시 최초 로그인도 같은 Auth UUID 단위로 직렬화한다.
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', (identity['id'],))
        profile = profile_for_identity(conn, identity)
        conn.execute('DELETE FROM shoppingmall.auth_sessions WHERE expires_at<NOW()')
        conn.execute('''INSERT INTO shoppingmall.auth_sessions
            (token_hash,user_id,access_token,refresh_token,token_expires_at)
            VALUES (%s,%s,%s,%s,%s)''',
            (token_hash(token), profile['id'], encrypted_access, encrypted_refresh, expires))
    response.set_cookie(COOKIE, token, httponly=True, samesite='lax', max_age=SESSION_SECONDS,
                        secure=os.getenv('COOKIE_SECURE', 'false').lower() == 'true', path='/')


def authenticated_user(connect, request):
    token = request.cookies.get(COOKIE, '')
    if not token:
        raise HTTPException(401, '로그인이 필요합니다.')
    with connect() as conn:
        # refresh token을 동시에 소비하지 않도록 세션 행을 잠근다.
        session = conn.execute('''SELECT * FROM shoppingmall.auth_sessions
            WHERE token_hash=%s AND expires_at>NOW() FOR UPDATE''', (token_hash(token),)).fetchone()
        if not session:
            raise HTTPException(401, '다시 로그인하세요.')
        try:
            box = cipher()
            access = box.decrypt(session['access_token'].encode()).decode()
            if session['token_expires_at'] <= time.time() + 30:
                refresh = box.decrypt(session['refresh_token'].encode()).decode()
                result = auth_request('POST', 'token?grant_type=refresh_token',
                                      payload={'refresh_token': refresh})
                encrypted_access, encrypted_refresh, expires = token_fields(result)
                access = result['access_token']
                conn.execute('''UPDATE shoppingmall.auth_sessions SET access_token=%s,
                    refresh_token=%s,token_expires_at=%s WHERE token_hash=%s''',
                    (encrypted_access, encrypted_refresh, expires, token_hash(token)))
                # Auth가 이미 회전시킨 refresh token은 이후 사용자 조회가 일시 실패해도 보존한다.
                conn.commit()
            identity = verified_identity(access)
        except InvalidToken:
            raise HTTPException(401, '세션 암호화 키가 변경되었습니다. 다시 로그인하세요.') from None
        profile = conn.execute('''SELECT id,name,email,address,role FROM shoppingmall.users
            WHERE id=%s AND auth_user_id=%s AND active''',
            (session['user_id'], identity['id'])).fetchone()
        if not profile:
            raise HTTPException(401, '사용할 수 없는 쇼핑몰 계정입니다.')
    return profile


def end_session(connect, request, response):
    # 먼저 이 앱의 세션을 폐기한다. JWT 만료 전에도 이 쿠키를 다시 사용할 수 없다.
    with connect() as conn:
        session = conn.execute('''DELETE FROM shoppingmall.auth_sessions WHERE token_hash=%s
            RETURNING access_token''', (token_hash(request.cookies.get(COOKIE, '')),)).fetchone()
    response.delete_cookie(COOKIE, path='/')
    response.delete_cookie('session', path='/')  # 이전 자체 인증 쿠키 정리
    revoked = True
    if session:
        try:
            access = cipher().decrypt(session['access_token'].encode()).decode()
            auth_request('POST', 'logout?scope=local', token=access)
        except (HTTPException, InvalidToken):
            revoked = False
    return {'message': '로그아웃되었습니다.' if revoked else
            '쇼핑몰에서 로그아웃되었습니다. 인증 서버 세션 해제는 확인되지 않았습니다.'}
