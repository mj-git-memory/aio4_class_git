user_score = 85

if user_score >= 80 :
    grade = 'Pass'
else :
    grade = 'Fail'

### 삼항연산자 (조건부 표현식)
# 삼항 연산자는 조건에 따라 두 값 중 하나를 선택하는 표현식
# 조건이_참일_때_값 if 조건 else 조건이_거짓일_때_값

grade = 'Pass' if user_score >= 80 else 'Fail'
#       참일 때 값    조건              거짓일 때 값
print(grade)
# -> “점수가 80 이상이면 'Pass', 아니면 'Fail'을 grade에 저장한다”는 뜻입니다.

# 분기에서 여러 작업을 해야 한다면 일반 if / else가 읽기 편함 