students = [
    {
        'student_num': '001',
        'info': {
            'name':'홍길동',
            'score':{
                'kor':100, 'eng':98, 'math':100
            },
            'address':'서울시 강남구 대치동',
            'grade':1,
        }
    },
    {
        'student_num': '002',
        'info': {
            'name':'이순신',
            'score':{
                'kor':90, 'eng':95, 'math':100
            },
            'address':'서울시 강남구 대치동',
            'grade':1,
        }
    }
]

print(students)
print('---')

def read_information(s):
    # s[0]['info']['score']['kor'] = 50
    score = s[0]['info']['score']
    score['kor'] += 50 
    # -> score는 원본과 복사본이 함께 참조하는 점수 딕셔너리이므로, 원본의 국어 점수도 100 → 150으로 바뀜.
    # -> 이것이 얕은 복사
    # print(scores)
    return score

scores1 = read_information(students.copy())
print(f'scores1: {scores1}')
print('---')
scores2 = read_information(students)
print(f'scores2: {scores2}')
print('---')

print(students)
print('---')


### 추가 예시: 깊은 복사본을 수정하면 원본은 바뀌지 않음
from copy import deepcopy
scores3 = read_information(deepcopy(students))
# -> 내부 점수까지 별도로 복사하려면 깊은 복사를 사용
print(f'scores3 (깊은 복사): {scores3}')  # 국어 250
print(f"원본 국어: {students[0]['info']['score']['kor']}")  # 국어 200 유지


## students.copy()를 하면 목록은 새로 만들지만, 학생 정보 상자는 새로 만들지 않음 
# students ──────→ 원본 목록 ──────┐
#                                 ├──→ 같은 학생 정보 {'kor': 100}
# students.copy() → 새 목록 ───────┘
# -> 그래서 복사한 목록을 통해 학생 정보를 수정해도, 결국 같은 학생 정보를 수정하게 됨
copied = students.copy()
copied[0]['info']['score']['kor'] = 50
print(students[0]['info']['score']['kor'])  # 원본도 50
# -> 반면, 목록 자체에 학생을 추가하는 작업은 원본에 영향을 주지 않음. (목록은 따로 만들었기 때문에)
copied.append({'info': {'name': '새 학생'}})
print(len(copied))    # 2
print(len(students))  # 1
### -> copy()를 하면 목록은 따로 있지만, 그 안에 있던 학생 정보는 함께 사용함. deepcopy()는 학생 정보까지 따로 만들어 줌

