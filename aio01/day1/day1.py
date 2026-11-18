num1 = 100
num2 = 200

print("num1+num2=", num1+num2)
print('---------')



# 사용자로부터 점수를 받아서 60점 이상이면 합격, 그 외에는 불합격
score = int(input("점수 입력 : "))

if score >= 60 :
    print("합격")
else :
    print("불합격")
print('---------')



# 사용자로부터 데이터를 입력 받아서 리스트에 저장
# 저장된 리스트의 값 중 짝수만 출력

for i in range(5) :
    print(f"{i+1}번째 숫자를 입력 : ")
print('---------')


scores = []
for i in range(5) :
    score = int(input(f"{i+1}번째 숫자를 입력 : "))
    scores.append(score)

print("scores : ", scores)
print('---------')


scores_filter = []
for i in scores :
    if i % 2 == 0 :
        print(i)
        scores_filter.append(i)

print("짝수 : ", scores_filter)
print('---------')


def get_even_numbers() : 
    scores = []

    for i in range(5) :
        score = int(input(f"{i+1}번째 숫자를 입력 : "))
        scores.append(score)

    scores_filter = []
    for i in scores :
        if i % 2 == 0 :
            scores_filter.append(i)
    print("짝수: ", scores_filter)

    return scores_filter

# if __name__ == '__main__' :
#     event_nums = get_even_numbers()
#     print("짝수 :", event_nums)

even_numbers = get_even_numbers()
print("짝수 :", even_numbers)