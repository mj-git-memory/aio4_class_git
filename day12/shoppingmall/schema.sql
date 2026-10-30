CREATE SCHEMA IF NOT EXISTS shoppingmall;
CREATE TABLE IF NOT EXISTS shoppingmall.users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    address VARCHAR(300) NOT NULL DEFAULT '',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS shoppingmall.products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    emoji TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS shoppingmall.orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES shoppingmall.users(id),
    status TEXT NOT NULL DEFAULT 'cart' CHECK (status IN ('cart', 'paid')),
    total INTEGER NOT NULL DEFAULT 0,
    shipping_address VARCHAR(300) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    paid_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS one_cart_per_user
ON shoppingmall.orders(user_id) WHERE status = 'cart';
CREATE TABLE IF NOT EXISTS shoppingmall.order_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES shoppingmall.orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES shoppingmall.products(id),
    product_name TEXT NOT NULL,
    unit_price INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 99),
    UNIQUE(order_id, product_id)
);
CREATE TABLE IF NOT EXISTS shoppingmall.payments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES shoppingmall.orders(id),
    amount INTEGER NOT NULL CHECK (amount > 0),
    method TEXT NOT NULL DEFAULT 'demo',
    status TEXT NOT NULL DEFAULT 'completed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS shoppingmall.sessions (
    token_hash TEXT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES shoppingmall.users(id),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '7 days'
);
INSERT INTO shoppingmall.products (name, description, category, price, stock, emoji)
VALUES
('데일리 머그', '아침 커피에 어울리는 도자기 머그 · 350ml', '리빙', 18000, 50, '☕'),
('캔버스 에코백', '가볍게 들고 나가는 튼튼한 면 소재 가방', '패션', 24000, 40, '👜'),
('포켓 노트', '오늘의 생각을 기록하는 무지 노트 · A6', '문구', 6500, 100, '📓'),
('미니 테이블 램프', '책상 한 켠을 따뜻하게 채우는 조명', '리빙', 39000, 20, '💡'),
('코튼 양말 세트', '매일 신기 좋은 부드러운 양말 · 3켤레', '패션', 12000, 60, '🧦'),
('컬러 펜 세트', '작은 기록을 다채롭게 · 6색', '문구', 9000, 80, '🖍️'),
-- 추가 예시 상품 30개: 리빙 10개, 패션 10개, 문구 10개
('우드 트레이', '간식과 차를 담는 작은 원목 트레이', '리빙', 22000, 35, '🪵'),
('유리 물병', '식탁 위에 두기 좋은 유리 물병 · 1L', '리빙', 16000, 45, '🍶'),
('세라믹 볼', '샐러드와 요거트를 담는 도자기 볼', '리빙', 15000, 50, '🥣'),
('린넨 테이블 매트', '식탁에 포인트를 더하는 린넨 매트', '리빙', 11000, 70, '🍽️'),
('소이 캔들', '은은한 향으로 공간을 채우는 캔들', '리빙', 19000, 30, '🕯️'),
('미니 화분', '작은 책상에 어울리는 다육식물 화분', '리빙', 13000, 25, '🪴'),
('코튼 핸드타월', '흡수력이 좋은 면 소재 손수건 타월', '리빙', 7000, 90, '🧺'),
('티 코스터 세트', '컵 자국을 막아주는 코르크 받침 · 4개', '리빙', 8500, 65, '☕'),
('패브릭 쿠션', '소파에 편안함을 더하는 쿠션 · 40cm', '리빙', 27000, 30, '🛋️'),
('벽걸이 시계', '어느 공간에나 어울리는 심플한 시계', '리빙', 32000, 20, '🕰️'),
('베이직 볼캡', '가볍게 쓰기 좋은 면 소재 모자', '패션', 21000, 40, '🧢'),
('니트 비니', '쌀쌀한 날 머리를 따뜻하게 감싸는 비니', '패션', 17000, 35, '🧶'),
('데일리 스카프', '가볍게 두르기 좋은 부드러운 스카프', '패션', 23000, 30, '🧣'),
('코튼 티셔츠', '여유로운 핏의 면 티셔츠 · 프리사이즈', '패션', 19000, 60, '👕'),
('홈 슬리퍼', '집에서 편안하게 신는 슬리퍼 · 프리사이즈', '패션', 14000, 50, '🩴'),
('미니 크로스백', '필수 소지품을 가볍게 담는 크로스백', '패션', 35000, 25, '👝'),
('코튼 손수건', '주머니에 넣고 다니는 작은 면 손수건', '패션', 6000, 100, '🧵'),
('심플 헤어밴드', '머리를 편안하게 정리하는 헤어밴드', '패션', 8000, 70, '🎀'),
('라운드 선글라스', '외출에 포인트를 주는 둥근 프레임', '패션', 29000, 30, '🕶️'),
('패브릭 파우치', '작은 소지품을 정리하는 지퍼 파우치', '패션', 12500, 55, '👛'),
('위클리 플래너', '일주일의 계획을 한눈에 보는 플래너', '문구', 11000, 60, '🗓️'),
('도트 노트', '필기와 스케치에 편리한 도트 노트 · A5', '문구', 8500, 75, '📔'),
('마스킹 테이프 세트', '다이어리를 꾸미는 패턴 테이프 · 3개', '문구', 7000, 80, '🎨'),
('인덱스 스티커', '중요한 페이지를 표시하는 컬러 스티커', '문구', 3500, 120, '🏷️'),
('메탈 북마크', '읽던 페이지를 기억하는 얇은 책갈피', '문구', 5500, 90, '🔖'),
('샤프 펜슬', '안정적인 필기감을 주는 샤프 · 0.5mm', '문구', 6000, 100, '✏️'),
('소프트 지우개 세트', '부드럽게 지워지는 지우개 · 3개', '문구', 3000, 150, '🧽'),
('데스크 펜꽂이', '책상 위 필기구를 정리하는 펜꽂이', '문구', 9500, 50, '🖊️'),
('메모 패드', '할 일을 간단히 적는 메모지 · 100매', '문구', 4500, 110, '📝'),
('레터 세트', '마음을 전하는 편지지와 봉투 · 5세트', '문구', 6500, 80, '✉️')
ON CONFLICT (name) DO NOTHING;
