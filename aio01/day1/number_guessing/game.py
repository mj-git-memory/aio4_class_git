"""숫자 맞추기 게임의 로직을 담당하는 모듈."""

import random


def play_game():
    """1~100 사이의 숫자를 최대 10번 안에 맞추는 게임을 실행한다."""
    num = random.randint(1, 100)
    count = 0

    for _ in range(10):
        count += 1
        print(count, "번째 시도")

        user_num = int(input("숫자 입력 : "))

        if user_num > num:
            print("정답 보다 크다")
        elif user_num < num:
            print("정답 보다 작다")
        else:
            print(f"정답: {num}.    총 시도 횟수: {count}")
            break
