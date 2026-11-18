### Redis로 세션을 생성하고, 세션으로 사용자를 확인하고, 로그아웃하는 실습 프로그램
# -> 세션은 “이 ID를 가진 사람이 어떤 사용자인지” 서버에서 기억하는 정보라고 생각
# -> 이 코드에서는 비밀번호 확인 없이 가상 사용자로 세션을 만듦 
# 터미널 명령 입력
#     ↓
# 명령어 분석 → .env 설정 읽기 → 설정값 검사
#     ↓
# Redis 클라이언트 준비
#     ↓
# create → 세션 생성하고 Redis에 저장
# get    → 세션으로 사용자 조회
# logout → 세션 삭제
#     ↓
# 연결 정리 후 프로그램 종료


# argparse는 명령줄 입력, secrets는 추측하기 어려운 세션 ID 생성에 사용한다.
import argparse
import os
import secrets

import redis
from dotenv import load_dotenv
from pathlib import Path

## 1. 가상 사용자와 유효기간 준비
# 가상의 계정 목록이다. 실제 회원 DB나 비밀번호 인증을 대신하지 않는다.
DEMO_USERS = {"demo-a": "민수", "demo-b": "지연"}
SESSION_TTL = 60  # 생성 시점부터 60초이며 조회할 때 연장하지 않는다.
# -> demo-a는 민수, demo-b는 지연이에요.
# -> 세션은 생성 후 60초 동안 유효해요.
# -> 조회해도 유효기간은 늘어나지 않아요.


def main():

    ## 3. 터미널에 입력한 명령어 분석
    # command와 value는 CMD에서 python main.py 뒤에 입력하는 두 인자다.
    parser = argparse.ArgumentParser(description="Redis 세션 생성·조회·로그아웃 실습")
    parser.add_argument("command", choices=["create", "get", "logout"], help="수행할 동작")
    parser.add_argument("value", help="create: 가상 사용자 ID, 그 외: 발급받은 세션 ID")
    args = parser.parse_args()  # 잘못된 명령·누락된 인자는 도움말과 종료 코드 2로 처리한다.
    
    # main3.py의 상위 폴더인 AIO_4_class의 .env를 읽기
    env_path = Path(__file__).resolve().parent.parent / ".env"
    # load_dotenv(env_path, override=False, interpolate=False)
    load_dotenv()
    
    host = os.getenv("REDIS_HOST", "")
    port_text = os.getenv("REDIS_PORT", "")
    if not host.strip() or not port_text.strip():
        raise ValueError("REDIS_HOST와 REDIS_PORT의 필수 설정을 확인하세요.")
    try:
        port = int(port_text)
    except ValueError:
        raise ValueError("REDIS_PORT는 1~65535 범위의 정수여야 합니다.") from None
    if not 1 <= port <= 65535:
        raise ValueError("REDIS_PORT는 1~65535 범위의 정수여야 합니다.")
    # 블록 종료 시 이 클라이언트가 소유하는 연결 풀도 닫는다.
    with redis.Redis(
        host=host,                 # 외부 설정에서 읽은 서버 주소
        port=port,                 # PC에 공개된 Redis 포트
        decode_responses=True,     # True는 str 응답, 기본 False는 bytes 응답
        socket_connect_timeout=2,  # 연결 단계의 제한 시간(초)
        socket_timeout=2,          # 소켓 읽기/쓰기 단계의 제한 시간(초)
    ) as client:
        if args.command == "create":
            if args.value not in DEMO_USERS:
                raise ValueError("create에는 demo-a 또는 demo-b를 사용하세요.")
            # 32는 난수 바이트 수다. sid_ 접두사는 ID가 -로 시작해 CLI 옵션으로 오인되는 일을 막는다.
            session_id = "sid_" + secrets.token_urlsafe(32)
            key = f"lesson03:session:{session_id}"
            client.set(key, args.value, ex=SESSION_TTL)  # 사용자 ID와 60초 만료를 함께 저장한다.
            # 가상 로컬 실습에서 다음 명령으로 전달하기 위해서만 ID를 표시한다.
            print("SESSION_ID:", session_id)
            print("생성한 사용자:", DEMO_USERS[args.value])
            print("만료 시간(초):", SESSION_TTL)
        else:
            key = f"lesson03:session:{args.value}"
            if args.command == "get":
                # 조회 시 사용자 ID를 입력받아 신뢰하지 않고 Redis에서 찾은 값만 사용한다.
                user_id = client.get(key)
                if user_id is None:
                    print("접근 거절: 세션이 없거나 만료되었습니다.")
                    raise SystemExit(1)
                if user_id not in DEMO_USERS:
                    raise ValueError("저장된 세션의 사용자 정보를 확인하세요.")
                print("세션 사용자:", DEMO_USERS[user_id])
                # TTL 조회는 관찰용이다. GET과 TTL 사이에도 시간이 흐를 수 있다.
                print("남은 TTL:", client.ttl(key))
            else:
                # 서버 측 키를 지워 같은 ID를 다시 써도 조회가 실패하도록 만든다.
                print("로그아웃으로 삭제한 세션 수:", client.delete(key))

## 2. 프로그램 실행 시작
# 이 파일을 직접 실행할 때만 실습을 시작한다.
if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        # 직접 만든 검증 오류 메시지이며 설정값·세션 원문은 포함하지 않는다.
        print("입력/설정 오류:", exc)
        raise SystemExit(1)
    except redis.exceptions.RedisError as exc:
        # 연결 문자열 등을 노출하지 않도록 상세 내용 대신 종류만 보여준다.
        print("Redis 오류:", type(exc).__name__)
        print("서버 상태·설정·실습 키의 자료형을 확인하세요.")
        raise SystemExit(1)

# python main3.py create demo-a 로 실행. 