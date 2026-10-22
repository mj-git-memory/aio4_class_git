# 숫자 맞추기 게임
# 규칙
# 컴퓨터가 1~100 사이의 값을 임의로 생성한 후, 사용자가 맞추는 게임
# 사용자가 입력한 값이 크면 크다, 작으면 작다라고 알려줌 

# 필요한 기능
# 입력 : int(input())
# 컴퓨터가 1~100 사이의 임의의 숫자 선택
# 비교 연산자를 통해 크다/작다 판별
# 순환문, 조건문, break


import random
## 난수 생성 
num = random.randint(1,100)

# for i in range(3) : 
#     num = random.randint(1,100)
#     print(num)


## 사용자 입력
# user_num = int(input("숫자 입력 : "))

count = 0 

# while True : 
#     count = count+1 
#     print(count, "번째 시도")

#     user_num = int(input("숫자 입력 : "))

#     if user_num > num :
#         print("정답 보다 크다")
#     elif user_num < num :
#         print("정답 보다 작다")
#     else :
#         print(num, " : 정답")
#         break


for _ in range(10) : 
    # count = count+1 
    count += 1
    print(count, "번째 시도")
    
    user_num = int(input("숫자 입력 : "))

    if user_num > num :
        print("정답 보다 크다")
    elif user_num < num :
        print("정답 보다 작다")
    else :
        print(f"정답: {num}.    총 시도 횟수: {count}")
        break