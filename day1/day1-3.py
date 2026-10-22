# 사용자로부터 데이터를 입력 받아서 리스트에 저장
# 저장된 리스트의 값 중 짝수만 출력

# for i in range(5) :
#     print(f"{i+1}번째 숫자를 입력 : ")

# scores = []

# for i in range(5) :
#     score = int(input(f"{i+1}번째 숫자를 입력 : "))
#     scores.append(score)

# print("scores : ", scores)


# scores_filter = []

# for i in scores :
#     if i % 2 == 0 :
#         print(i)
#         scores_filter.append(i)

# print("짝수 : ", scores_filter)



scores = []
# def list_set() : 
for i in range(5) :
    score = int(input(f"{i+1}번째 숫자를 입력 : "))
    scores.append(score)

scores_filter = []
for i in scores :
    if i % 2 == 0 :
        scores_filter.append(i)
print("짝수 : ", scores_filter)

