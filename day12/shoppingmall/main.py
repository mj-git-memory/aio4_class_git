"""FastAPI + Supabase PostgreSQL 쇼핑몰. 실제 청구 없는 모의 결제."""
import hashlib
import hmac
import os
import re
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from psycopg.rows import dict_row
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ROOT = Path(__file__).resolve().parent
# shoppingmall/.env를 우선 사용하고 없으면 상위 폴더의 .env를 탐색
load_dotenv(ROOT / '.env')
load_dotenv()


def connect():
    if os.getenv('DATABASE_URL'):
        return psycopg.connect(os.environ['DATABASE_URL'], sslmode='require',
                               connect_timeout=10, row_factory=dict_row)
    config = {key: os.getenv(key) for key in ('host', 'port', 'dbname', 'user', 'password')}
    if not all(config.values()):
        raise RuntimeError('DB 연결 환경변수가 없습니다. .env.example과 README를 확인하세요.')
    return psycopg.connect(**config, sslmode='require', connect_timeout=10, row_factory=dict_row)


@asynccontextmanager
async def lifespan(app):
    with connect() as conn:
        conn.execute((ROOT / 'schema.sql').read_text(encoding='utf-8'))
    yield


app = FastAPI(title='소소상점 API', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')


@app.middleware('http')
async def csrf_check(request: Request, call_next):
    # 쿠키 인증을 사용하는 변경 요청은 브라우저의 같은 출처에서만 허용
    if request.method in ('POST', 'PATCH', 'DELETE'):
        origin = request.headers.get('origin')
        expected = f'{request.url.scheme}://{request.url.netloc}'
        if request.headers.get('sec-fetch-site') == 'cross-site' or (origin and origin != expected):
            return JSONResponse({'detail': '다른 출처의 요청은 허용하지 않습니다.'}, status_code=403)
    response = await call_next(request)
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


class Profile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(min_length=1, max_length=50)
    address: str = Field(default='', max_length=300)

    @field_validator('name')
    @classmethod
    def valid_name(cls, value):
        if not re.fullmatch(r'[가-힣ㄱ-ㅎㅏ-ㅣA-Za-z]+', value):
            raise ValueError('이름에는 공백 없이 한글과 영문만 입력하세요.')
        return value


class Signup(Profile):
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class CartItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=99, strict=True)


class Checkout(BaseModel):
    address: str = Field(min_length=1, max_length=300)

    @field_validator('address')
    @classmethod
    def valid_address(cls, value):
        if not value.strip():
            raise ValueError('배송지를 입력하세요.')
        return value.strip()


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 600000).hex()
    return f'{salt}${digest}'


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def current_user(request: Request):
    token = request.cookies.get('session', '')
    with connect() as conn:
        user = conn.execute('''SELECT u.id, u.name, u.email, u.address
            FROM shoppingmall.sessions s JOIN shoppingmall.users u ON u.id=s.user_id
            WHERE s.token_hash=%s AND s.expires_at>NOW() AND u.active''',
            (token_hash(token),)).fetchone()
    if not user:
        raise HTTPException(401, '로그인이 필요합니다.')
    return user


def lock_user(conn, user_id):
    # 같은 회원의 장바구니 수정·결제·탈퇴를 직렬화
    row = conn.execute('SELECT id FROM shoppingmall.users WHERE id=%s AND active FOR UPDATE',
                       (user_id,)).fetchone()
    if not row:
        raise HTTPException(401, '사용할 수 없는 회원입니다.')


def get_cart(conn, user_id):
    row = conn.execute("SELECT id FROM shoppingmall.orders WHERE user_id=%s AND status='cart'",
                       (user_id,)).fetchone()
    if not row:
        row = conn.execute('INSERT INTO shoppingmall.orders(user_id) VALUES (%s) RETURNING id',
                           (user_id,)).fetchone()
    return row['id']


@app.get('/')
def index():
    return FileResponse(ROOT / 'static' / 'index.html')


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/api/signup', status_code=201)
def signup(data: Signup):
    try:
        with connect() as conn:
            conn.execute('''INSERT INTO shoppingmall.users(name,email,password_hash,address)
                VALUES (%s,%s,%s,%s)''',
                (data.name, str(data.email).lower(), password_hash(data.password), data.address))
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, '이미 사용 중인 이메일입니다.')
    return {'message': '회원가입이 완료되었습니다. 로그인하세요.'}


@app.post('/api/login')
def login(data: Login, response: Response):
    with connect() as conn:
        user = conn.execute('SELECT * FROM shoppingmall.users WHERE email=%s AND active FOR UPDATE',
                            (str(data.email).lower(),)).fetchone()
        # 없는 계정도 같은 해시 계산을 수행
        stored = user['password_hash'] if user else ('0' * 32 + '$' + '0' * 64)
        candidate = password_hash(data.password, stored.split('$')[0])
        if not hmac.compare_digest(candidate, stored) or not user:
            raise HTTPException(401, '이메일 또는 비밀번호가 올바르지 않습니다.')
        token = secrets.token_urlsafe(32)
        conn.execute('DELETE FROM shoppingmall.sessions WHERE expires_at<NOW()')
        conn.execute('INSERT INTO shoppingmall.sessions(token_hash,user_id) VALUES (%s,%s)',
                     (token_hash(token), user['id']))
    response.set_cookie('session', token, httponly=True, samesite='lax', max_age=604800,
                        secure=os.getenv('COOKIE_SECURE', 'false').lower() == 'true')
    return {'message': '로그인되었습니다.'}


@app.post('/api/logout')
def logout(request: Request, response: Response):
    with connect() as conn:
        conn.execute('DELETE FROM shoppingmall.sessions WHERE token_hash=%s',
                     (token_hash(request.cookies.get('session', '')),))
    response.delete_cookie('session')
    return {'message': '로그아웃되었습니다.'}


@app.get('/api/me')
def me(user=Depends(current_user)):
    return user


@app.patch('/api/me')
def update_me(data: Profile, user=Depends(current_user)):
    with connect() as conn:
        lock_user(conn, user['id'])
        conn.execute('UPDATE shoppingmall.users SET name=%s,address=%s WHERE id=%s',
                     (data.name, data.address, user['id']))
    return {'message': '회원정보가 수정되었습니다.'}


@app.delete('/api/me')
def delete_me(response: Response, user=Depends(current_user)):
    with connect() as conn:
        lock_user(conn, user['id'])
        # 구매 기록은 유지하되 회원 개인정보는 익명화
        conn.execute('''UPDATE shoppingmall.users SET active=FALSE,name='탈퇴회원',
            email=%s,password_hash='',address='' WHERE id=%s''',
            (f'deleted-{user["id"]}@invalid.local', user['id']))
        conn.execute('DELETE FROM shoppingmall.sessions WHERE user_id=%s', (user['id'],))
        conn.execute("DELETE FROM shoppingmall.orders WHERE user_id=%s AND status='cart'", (user['id'],))
        conn.execute("UPDATE shoppingmall.orders SET shipping_address='' WHERE user_id=%s", (user['id'],))
    response.delete_cookie('session')
    return {'message': '회원탈퇴가 완료되었습니다.'}


@app.get('/api/products')
def products():
    with connect() as conn:
        return conn.execute('SELECT * FROM shoppingmall.products ORDER BY id').fetchall()


@app.get('/api/cart')
def cart(user=Depends(current_user)):
    with connect() as conn:
        return conn.execute('''SELECT i.product_id,p.name,p.price,p.stock,p.emoji,i.quantity
            FROM shoppingmall.orders o JOIN shoppingmall.order_items i ON i.order_id=o.id
            JOIN shoppingmall.products p ON p.id=i.product_id
            WHERE o.user_id=%s AND o.status='cart' ORDER BY p.id''', (user['id'],)).fetchall()


@app.post('/api/cart')
def add_cart(data: CartItem, user=Depends(current_user)):
    with connect() as conn:
        lock_user(conn, user['id'])
        product = conn.execute('SELECT * FROM shoppingmall.products WHERE id=%s', (data.product_id,)).fetchone()
        if not product:
            raise HTTPException(404, '상품이 없습니다.')
        order_id = get_cart(conn, user['id'])
        existing = conn.execute('SELECT quantity FROM shoppingmall.order_items WHERE order_id=%s AND product_id=%s',
                                (order_id, data.product_id)).fetchone()
        quantity = (existing['quantity'] if existing else 0) + data.quantity
        if quantity > min(99, product['stock']):
            raise HTTPException(409, '재고 또는 최대 구매 수량(99개)을 초과했습니다.')
        conn.execute('''INSERT INTO shoppingmall.order_items(order_id,product_id,product_name,unit_price,quantity)
            VALUES (%s,%s,%s,%s,%s) ON CONFLICT(order_id,product_id)
            DO UPDATE SET quantity=EXCLUDED.quantity''',
            (order_id, product['id'], product['name'], product['price'], quantity))
    return {'message': '장바구니에 담았습니다.'}


@app.delete('/api/cart/{product_id}')
def remove_cart(product_id: int, user=Depends(current_user)):
    with connect() as conn:
        lock_user(conn, user['id'])
        conn.execute('''DELETE FROM shoppingmall.order_items WHERE product_id=%s AND order_id IN
            (SELECT id FROM shoppingmall.orders WHERE user_id=%s AND status='cart')''', (product_id, user['id']))
    return {'message': '장바구니에서 삭제했습니다.'}


@app.post('/api/checkout', status_code=201)
def checkout(data: Checkout, user=Depends(current_user)):
    with connect() as conn:
        lock_user(conn, user['id'])
        order_id = get_cart(conn, user['id'])
        items = conn.execute('''SELECT i.*,p.price,p.stock,p.name FROM shoppingmall.order_items i
            JOIN shoppingmall.products p ON p.id=i.product_id WHERE i.order_id=%s
            ORDER BY p.id FOR UPDATE OF p''', (order_id,)).fetchall()
        if not items:
            raise HTTPException(400, '장바구니가 비어 있습니다.')
        total = 0
        for item in items:
            if item['quantity'] > item['stock']:
                raise HTTPException(409, f'{item["name"]}의 재고가 부족합니다.')
            total += item['price'] * item['quantity']
            conn.execute('UPDATE shoppingmall.products SET stock=stock-%s WHERE id=%s',
                         (item['quantity'], item['product_id']))
            conn.execute('UPDATE shoppingmall.order_items SET unit_price=%s,product_name=%s WHERE id=%s',
                         (item['price'], item['name'], item['id']))
        conn.execute("""UPDATE shoppingmall.orders SET status='paid',total=%s,
            shipping_address=%s,paid_at=NOW() WHERE id=%s""", (total, data.address, order_id))
        conn.execute('INSERT INTO shoppingmall.payments(order_id,amount) VALUES (%s,%s)', (order_id, total))
    return {'order_id': order_id, 'total': total, 'message': '모의 결제 완료 · 실제 청구되지 않습니다.'}


@app.get('/api/orders')
def orders(user=Depends(current_user)):
    with connect() as conn:
        result = conn.execute("SELECT * FROM shoppingmall.orders WHERE user_id=%s AND status='paid' ORDER BY id DESC",
                              (user['id'],)).fetchall()
        for order in result:
            order['items'] = conn.execute('SELECT product_name,unit_price,quantity FROM shoppingmall.order_items WHERE order_id=%s ORDER BY id',
                                          (order['id'],)).fetchall()
        return result


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
