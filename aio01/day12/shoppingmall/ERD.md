# 쇼핑몰 ERD

Supabase Auth 계정은 `users.auth_user_id`로 연결합니다. 토큰 열은 암호화된 값입니다. 이전 `sessions`와 `password_hash`는 호환성을 위해 DB에 남지만 인증에는 사용하지 않습니다. `app_migrations`는 예시 상품 초기화 이력용이며 아래 업무 ERD에서는 생략합니다.

```mermaid
erDiagram
    users ||--o{ orders : places
    users ||--o{ auth_sessions : authenticates
    orders ||--o{ order_items : contains
    products ||--o{ order_items : selected_in
    orders ||--o| payments : paid_by

    users {
        bigint id PK
        varchar name
        varchar email UK
        uuid auth_user_id UK
        text role
        varchar address
        boolean active
        timestamptz created_at
    }
    products {
        bigint id PK
        text name UK
        text description
        text category
        integer price
        integer stock
        text emoji
        boolean active
    }
    orders {
        bigint id PK
        bigint user_id FK
        text status
        text fulfillment_status
        integer total
        varchar shipping_address
        timestamptz created_at
        timestamptz paid_at
    }
    order_items {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        text product_name
        integer unit_price
        integer quantity
    }
    payments {
        bigint id PK
        bigint order_id FK, UK
        integer amount
        text method
        text status
        timestamptz created_at
    }
    auth_sessions {
        text token_hash PK
        text access_token
        text refresh_token
        bigint token_expires_at
        bigint user_id FK
        timestamptz expires_at
    }
```
