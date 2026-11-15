# 소소상점

FastAPI / Supabase PostgreSQL / Supabase Auth / HTML·CSS·JavaScript로 만든 학습용 쇼핑몰입니다. 결제는 실제 청구 없는 모의 결제입니다.

## 로컬 실행

자세한 설정·명령어·검증 순서·피드백 양식은 **[로컬테스트.md](로컬테스트.md)**에 있습니다.

```bash
conda activate py313
cd day12/shoppingmall
python -m pip install -r requirements.txt
# .env.example과 로컬테스트.md를 보고 DB/Auth 연결값과 AUTH_SESSION_KEY 설정
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- 쇼핑몰: http://127.0.0.1:8000
- API 문서: http://127.0.0.1:8000/docs
- `shoppingmall/.env`를 먼저 읽고 상위 `.env`도 탐색합니다. 기존 환경변수가 우선합니다.
- 시작할 때 `schema.sql`로 Auth 연결 컬럼·서버 세션·관리자 역할·배송 상태를 준비합니다. 개발용 Supabase 프로젝트에서 먼저 실행하세요.

## 인증과 권한

- 회원가입·비밀번호 확인·이메일 인증·JWT 발급/갱신은 Supabase Auth에 위임합니다.
- JWT와 refresh token은 서버 DB에 암호화해 보관합니다. 브라우저는 HttpOnly 세션 쿠키만 받습니다.
- 로그아웃은 쇼핑몰 세션을 즉시 삭제하고 Supabase 현재 세션 해제를 요청합니다.
- 회원의 장바구니·회원정보·주문 상세·결제 정보는 본인만 접근합니다.
- 관리자는 상품 등록·수정·판매 중지·재고 관리, 전체 결제 주문 조회, 배송 상태 변경을 할 수 있습니다.
- 역할은 DB에서 조회합니다. 관리자 지정은 신뢰할 수 있는 SQL 운영자만 하며 웹을 통한 자기 승격은 허용하지 않습니다.
- 브라우저의 Supabase Data API 직접 접근은 차단하고 백엔드의 소유권·역할 검사로 DB 작업을 제한합니다.
- POST/PUT/PATCH/DELETE에는 같은 출처 확인과 `X-Shop-Request: 1` 헤더를 적용합니다.

기존 회원은 이메일만 같다는 이유로 자동 연결하지 않습니다. 기존 주문을 보존하는 수동 연결 SQL은 로컬 테스트 문서를 확인하세요. 쇼핑몰 탈퇴는 이용 중지·개인정보 익명화이며 Supabase Auth 계정 삭제는 별도 운영 절차입니다.

## 파일

- `main.py`: 쇼핑·회원·관리자 API와 서버 권한 검사
- `auth.py`: Supabase Auth HTTP API, 토큰 암호화·검증·갱신·세션 폐기
- `schema.sql`: 기존 데이터를 보존하는 스키마 추가와 Data API 접근 제한
- `static/`: 쇼핑몰과 관리자 화면
- `tests/`: 임시 PostgreSQL + 모의 Auth 통합 테스트
- [ERD.md](ERD.md): 현재 구조
- `테이블정의.md`, `main코드설명.md`, `상품구매시뮬레이션.md`: 전환 전 학습 자료 (이전 인증 설명 포함)

## 배포

아직 배포하지 않았습니다. 로컬 검증과 사용자 피드백 후 진행합니다. Render를 사용한다면 Root Directory는 `day12/shoppingmall`, Build Command는 `pip install -r requirements.txt`, Start Command는 `uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers`, Health Check Path는 `/health`입니다. 환경변수와 영구적인 암호화 키를 등록하고 HTTPS에서 `COOKIE_SECURE=true`를 사용하세요.
