"""FastAPI + Supabase PostgreSQL 쇼핑몰. 실제 청구 없는 모의 결제."""
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import psycopg
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from auth import (authenticated_user, auth_request, end_session, start_session, validate_config)
from fastapi.staticfiles import StaticFiles
from psycopg.rows import dict_row
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ROOT = Path(__file__).resolve().parent
# 파일별로 누락한 항목을 상위 설정에서 보완한다. 실행 위치에 의존하지 않는다.
for folder in (ROOT, ROOT.parent, ROOT.parent.parent):
    load_dotenv(folder / '.env', override=False, interpolate=False)


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
    validate_config()
    with connect() as conn:
        conn.execute((ROOT / 'schema.sql').read_text(encoding='utf-8'))
    yield


class ForbiddenResponse(BaseModel):
    detail: str
    code: str | None = None
    hint: str | None = None


app = FastAPI(title='소소상점 API', lifespan=lifespan, responses={
    403: {'model': ForbiddenResponse,
          'description': '요청 보호 헤더 누락, 다른 출처 요청 또는 권한 부족. detail과 hint를 확인하세요.'},
})
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')


def shop_openapi():
    if app.openapi_schema is None:
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        # 미들웨어가 검사하는 헤더도 API 문서에 표시한다. Swagger는 기본값 1을 전송한다.
        for path, operations in schema['paths'].items():
            if not path.startswith('/api/'):
                continue
            for method in ('post', 'put', 'patch', 'delete'):
                if method in operations:
                    operations[method].setdefault('parameters', []).append({
                        'name': 'X-Shop-Request', 'in': 'header', 'required': True,
                        'description': '변경 요청 보호용 헤더입니다. 기본값 1을 유지하세요. 로그인 토큰이 아닙니다.',
                        'schema': {'type': 'string', 'enum': ['1'], 'default': '1'},
                    })
        app.openapi_schema = schema
    return app.openapi_schema


app.openapi = shop_openapi


def forbidden_request(code, detail, hint):
    # detail/hint는 고객 안내, code는 개발자가 원인을 구분하는 식별값이다.
    return JSONResponse({'detail': detail, 'code': code, 'hint': hint}, status_code=403,
                        headers={'Cache-Control': 'no-store'})


@app.middleware('http')
async def csrf_check(request: Request, call_next):
    # 쿠키 인증을 사용하는 변경 요청은 브라우저의 같은 출처에서만 허용
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        # same-origin JS만 이 헤더를 보낼 수 있다. CORS로 외부 출처를 허용하지 않는다.
        if request.headers.get('x-shop-request') != '1':
            return forbidden_request(
                'SHOP_REQUEST_HEADER_REQUIRED',
                '요청을 안전하게 확인하지 못했습니다. 페이지를 새로고침한 뒤 다시 시도해주세요.',
                '계속 진행되지 않으면 쇼핑몰 홈으로 돌아가 다시 시도해주세요. '
                '같은 문제가 반복되면 고객지원에 문의해주세요.',
            )
        origin = request.headers.get('origin')
        expected = f'{request.url.scheme}://{request.url.netloc}'
        if request.headers.get('sec-fetch-site') == 'cross-site' or (origin and origin != expected):
            return forbidden_request(
                'CROSS_ORIGIN_REQUEST_BLOCKED',
                '쇼핑몰에서 직접 진행한 요청인지 확인할 수 없습니다. 쇼핑몰 홈에서 다시 진행해주세요.',
                '다른 사이트의 링크나 오래 열어둔 화면을 이용했다면 닫고, '
                '쇼핑몰 홈에 다시 접속해주세요.',
            )
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


def current_user(request: Request):
    return authenticated_user(connect, request)


def admin_user(user=Depends(current_user)):
    # UI에서 버튼을 숨기는 것과 별개로 모든 관리자 요청을 서버에서 검사한다.
    if user['role'] != 'admin':
        raise HTTPException(403, '관리자 권한이 필요합니다.')
    return user


@app.exception_handler(RequestValidationError)
def validation_error(request: Request, exc: RequestValidationError):
    # 비밀번호와 입력 원문을 응답에 포함하지 않는다.
    return JSONResponse({'detail': [
        {'loc': e['loc'], 'type': e['type'], 'msg': '입력 형식과 필수 항목을 확인하세요.'}
        for e in exc.errors()]}, status_code=422)


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
    # 비밀번호를 자체 users 테이블에 저장하지 않는다. 이메일 확인은 Supabase가 담당한다.
    auth_request('POST', 'signup', payload={
        'email': str(data.email).lower(), 'password': data.password,
        'data': {'name': data.name, 'address': data.address},
    })
    return {'message': '가입 요청을 처리했습니다. 확인 메일이 오면 인증 후 로그인하세요.'}


@app.post('/api/login')
def login(data: Login, request: Request, response: Response):
    result = auth_request('POST', 'token?grant_type=password', payload={
        'email': str(data.email).lower(), 'password': data.password,
    })
    # 기존 브라우저 세션도 폐기해 계정 전환 후 이전 쿠키를 재사용하지 못하게 한다.
    end_session(connect, request, response)
    start_session(connect, result, response)
    return {'message': '로그인되었습니다.'}


@app.post('/api/logout')
def logout(request: Request, response: Response):
    return end_session(connect, request, response)


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
def delete_me(request: Request, response: Response, user=Depends(current_user)):
    end_session(connect, request, response)
    with connect() as conn:
        lock_user(conn, user['id'])
        # 구매 기록은 유지하되 회원 개인정보는 익명화
        conn.execute('''UPDATE shoppingmall.users SET active=FALSE,name='탈퇴회원',
            email=%s,password_hash='',address='' WHERE id=%s''',
            (f'deleted-{user["id"]}@invalid.local', user['id']))
        conn.execute('DELETE FROM shoppingmall.auth_sessions WHERE user_id=%s', (user['id'],))
        conn.execute("DELETE FROM shoppingmall.orders WHERE user_id=%s AND status='cart'", (user['id'],))
        conn.execute("UPDATE shoppingmall.orders SET shipping_address='' WHERE user_id=%s", (user['id'],))
    return {'message': '쇼핑몰 탈퇴가 완료되었습니다. 인증 계정 삭제는 운영자에게 요청하세요.'}


@app.get('/api/products')
def products():
    with connect() as conn:
        return conn.execute('SELECT * FROM shoppingmall.products WHERE active ORDER BY id').fetchall()


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
        product = conn.execute('SELECT * FROM shoppingmall.products WHERE id=%s AND active', (data.product_id,)).fetchone()
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
        items = conn.execute('''SELECT i.*,p.price,p.stock,p.name,p.active FROM shoppingmall.order_items i
            JOIN shoppingmall.products p ON p.id=i.product_id WHERE i.order_id=%s
            ORDER BY p.id FOR UPDATE OF p''', (order_id,)).fetchall()
        if not items:
            raise HTTPException(400, '장바구니가 비어 있습니다.')
        total = 0
        for item in items:
            if not item['active']:
                raise HTTPException(409, '판매 중지된 상품이 있습니다. 장바구니에서 삭제하세요.')
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


@app.get('/api/orders/{order_id}')
def order_detail(order_id: int, user=Depends(current_user)):
    with connect() as conn:
        # 관리자도 고객용 경로에서는 본인 주문만 본다. 전체 조회는 관리자 경로로 분리한다.
        order = conn.execute("""SELECT * FROM shoppingmall.orders
            WHERE id=%s AND user_id=%s AND status='paid'""", (order_id, user['id'])).fetchone()
        if not order:
            raise HTTPException(404, '주문이 없습니다.')
        order['items'] = conn.execute('''SELECT product_name,unit_price,quantity
            FROM shoppingmall.order_items WHERE order_id=%s ORDER BY id''', (order_id,)).fetchall()
        order['payment'] = conn.execute('''SELECT amount,method,status,created_at
            FROM shoppingmall.payments WHERE order_id=%s''', (order_id,)).fetchone()
        return order


class ProductInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    category: Literal['리빙', '패션', '문구']
    price: int = Field(gt=0, le=100000000, strict=True)
    stock: int = Field(ge=0, le=1000000, strict=True)
    emoji: str = Field(min_length=1, max_length=20)
    active: bool = True


class FulfillmentInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['preparing', 'shipped', 'delivered']


@app.get('/api/admin/products')
def admin_products(user=Depends(admin_user)):
    with connect() as conn:
        return conn.execute('SELECT * FROM shoppingmall.products ORDER BY id').fetchall()


@app.post('/api/admin/products', status_code=201)
def create_product(data: ProductInput, user=Depends(admin_user)):
    try:
        with connect() as conn:
            return conn.execute('''INSERT INTO shoppingmall.products
                (name,description,category,price,stock,emoji,active)
                VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *''',
                tuple(data.model_dump().values())).fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, '같은 이름의 상품이 있습니다.') from None


@app.put('/api/admin/products/{product_id}')
def update_product(product_id: int, data: ProductInput, user=Depends(admin_user)):
    try:
        with connect() as conn:
            product = conn.execute('''UPDATE shoppingmall.products SET
                name=%s,description=%s,category=%s,price=%s,stock=%s,emoji=%s,active=%s
                WHERE id=%s RETURNING *''', (*data.model_dump().values(), product_id)).fetchone()
            if not product:
                raise HTTPException(404, '상품이 없습니다.')
            return product
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, '같은 이름의 상품이 있습니다.') from None


@app.get('/api/admin/orders')
def admin_orders(user=Depends(admin_user)):
    with connect() as conn:
        return conn.execute("""SELECT o.*,u.name AS customer_name
            FROM shoppingmall.orders o JOIN shoppingmall.users u ON u.id=o.user_id
            WHERE o.status='paid' ORDER BY o.id DESC LIMIT 200""").fetchall()


@app.patch('/api/admin/orders/{order_id}/fulfillment')
def update_fulfillment(order_id: int, data: FulfillmentInput, user=Depends(admin_user)):
    with connect() as conn:
        order = conn.execute("""SELECT fulfillment_status FROM shoppingmall.orders
            WHERE id=%s AND status='paid' FOR UPDATE""", (order_id,)).fetchone()
        if not order:
            raise HTTPException(404, '결제된 주문이 없습니다.')
        states = ['preparing', 'shipped', 'delivered']
        current, target = states.index(order['fulfillment_status']), states.index(data.status)
        if target not in (current, current + 1):
            raise HTTPException(409, '배송 준비 → 배송 중 → 배송 완료 순서로 변경하세요.')
        conn.execute('UPDATE shoppingmall.orders SET fulfillment_status=%s WHERE id=%s',
                     (data.status, order_id))
    return {'message': '배송 상태를 변경했습니다.'}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
