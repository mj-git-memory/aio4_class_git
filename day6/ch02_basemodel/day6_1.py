## 라이브러리: 특정 기능을 제공하는 재사용 가능한 코드 모음. ex) Pydantic은 데이터 검증과 변환 기능을 제공
## 패키지: 파이썬에서 모듈들을 묶어 관리하고 불러오는 구조. ex) pydantic은 그런 패키지의 이름
## 모듈: 보통 함수나 클래스 등을 담은 파이썬 파일 하나. ex) day6_1.py도 모듈
# 라이브러리는 무슨 기능을 제공하는가, 패키지는 코드를 어떻게 묶어 불러오는가에 초점을 둔 표현
# 하나의 라이브러리가 여러 패키지와 모듈로 구성될 수도 있음

## 모듈: 관련 코드를 담은 파이썬 파일
## 클래스: 데이터와 동작을 묶어 객체를 만드는 설계도
## 함수: 특정 작업을 수행하는 코드 묶음
## 메서드: 클래스 안에 정의한 함수 
## 객체:  클래스를 바탕으로 실제로 만든 대상
## 상속: 존 클래스의 속성과 메서드를 물려받아 새로운 클래스를 만드는 것
# class 자식클래스(부모클래스):
#     # 추가할 내용
# 왜 상속할까요?
# - 코드를 재사용하려고: 공통 기능을 여러 클래스에 반복해서 작성하지 않아도 됨
# - 기능을 확장하려고: 기존 기능을 사용하면서 새로운 기능을 추가할 수 있음
# - 동작을 바꾸려고: 부모 메서드를 자식에서 다시 정의할 수 있음. 이를 오버라이딩이라고 함
## 초기화: 객체를 처음 만들 때, 그 객체가 사용할 값을 설정하는 것
## __init__()은 객체의 초기값을 설정하는 메서드
# __init__()은 이미 만들어진 객체를 초기화하는 역할 (객체 생성은 __new__()가 담당)
# 객체 생성 후 __init__()이 자동으로 실행
# 클래스 정의는 초기화 방법을 정하는 것이고, 객체를 만들 때 __init__()이 실행
# __init__()은 생성된 객체(self)에 name 같은 초기값을 설정
# 문자열 같은 값을 반환하는 메서드는 아니므로 보통 return을 작성하지 않음 
# 파이썬이 새 객체를 만든 뒤 __init__()을 자동으로 호출
## super()는 부모 쪽의 메서드를 호출할 때 사용
# **“부모 클래스의 기능을 가져와서 실행한다”**
# super().메서드이름(전달할_값)
# super().__init__(전달할_값) : 부모의 초기화 메서드 호출 
## self: 메서드가 현재 다루고 있는 객체를 받는 매개변수
# 매개변수 -  전달되는 것
# self -	방금 생성한 객체
# name -	"하늘"
# age - 	23
# 1. __new__() → 새 객체를 만들어 반환 : 생성 메서드
# 2. __init__() → 그 객체를 self로 받아 이름과 나이를 저장 : 초기화 메서드 
# 3. user → 초기화까지 끝난 객체를 가리켜요.
# 다만 입문 자료에서는 __init__()도 흔히 “생성자”라고 부름
# __new__() : 객체 만들기
#      ↓
# __init__() : 만들어진 객체에 초기값 설정
#      ↓
# user가 객체를 가리킴
## __str__() : 객체를 사람이 읽기 좋은 문자열로 표현하는 메서드. 객체를 설명하는 문자열 반환
# __str__() 안에서는 print()가 아니라 문자열을 return해야 함 
# __str__()를 작성하지 않은 일반 클래스의 객체는 보통 다음처럼 표시 : <__main__.Student object at 0x...>
## 오류 처리 
# try:
#     오류가 발생할 수 있는 코드
# except 오류종류:
#     해당 오류가 발생했을 때 실행할 코드

#-------------------------------------------------------------
## Ex) 
# student.py ← 이 파일이 모듈

def say_hello(name):             # 함수
    return f"안녕하세요, {name}님!"

class Student:                  # 클래스
    def __init__(self, name):
        self.name = name
    def introduce(self):        # 클래스 안의 함수 → 메서드
        return f"저는 {self.name}입니다."

# import student  # 모듈 가져오기

# # 모듈 안의 함수 호출
# message = student.say_hello("하늘")
# print(message)
# # 안녕하세요, 하늘님!

# # 모듈 안의 클래스로 객체 만들기
# student1 = student.Student("하늘")

# # 객체의 메서드 호출
# print(student1.introduce())
# # 저는 하늘입니다.
#-------------------------------------------------------------
# student.py 모듈
# ├── say_hello() 함수
# └── Student 클래스
#     ├── __init__() 메서드
#     └── introduce() 메서드
#-------------------------------------------------------------
## Ex)
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        print(f"저는 {self.name}입니다.")

class Student(Person):
    def study(self):
        print(f"{self.name}이 공부합니다.")
# -> Student(Person)은 **“학생은 사람의 기능을 물려받는다”**는 뜻

student = Student("하늘")

print(student.name)    # 하늘
student.introduce()   # 저는 하늘입니다.
student.study()       # 하늘이 공부합니다.
# -> Student에는 __init__()이나 introduce()를 직접 작성하지 않았지만, 
# 부모인 Person에서 물려받았기 때문에 사용할 수 있음
# -> study()는 자식 클래스에 새로 추가한 메서드
#-------------------------------------------------------------
#-------------------------------------------------------------
### pydantic : 데이터 검증과 변환 기능을 제공
# -> 데이터의 유효성 및 타입을 체크
# 기능이 구현된 클래스를 상속받아서, pydanctic 클래스 또는 모델을 만들 수 있음
# -> **“Pydantic이 미리 만들어 둔 BaseModel 클래스를 물려받으면, 
# 내가 만든 클래스에서도 데이터 검증·변환 기능을 사용할 수 있다”**는 뜻
#-------------------------------------------------------------
from pydantic import BaseModel
class Student(BaseModel):
    name: str
    age: int
# -> class Student(BaseModel):은 **“BaseModel을 상속해서 Student 클래스를 만들겠다”**는 의미
# -> BaseModel이 제공하는 것: 데이터를 검증하고 변환하는 기능
# -> 내가 지정하는 것: name은 문자열, age는 정수라는 데이터 규칙
#-------------------------------------------------------------
# Ex) 
student = Student(name="하늘", age="23")
print(student.age)        # 23
print(type(student.age))  # <class 'int'>
# Student(name="하늘", age="스물셋")
# # ValidationError 발생
# -> 변환할 수 없는 값이면 검증 오류가 발생
#-------------------------------------------------------------
# -> 반면 일반 클래스에서는 타입 표시만 해도 자동으로 검증되지는 않음
class NormalStudent:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

student = NormalStudent(name="하늘", age="스물셋")
# # 별도의 검증 코드가 없으므로 그대로 저장됨
#-------------------------------------------------------------
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        print(f"저는 {self.name}입니다.")

class Student(Person):
    def study(self):
        print(f"{self.name}이 공부합니다.")
# -> Student(Person)은 **“학생은 사람의 기능을 물려받는다”**는 뜻
# -> study()는 자식 클래스에 새로 추가한 메서드
student = Student("하늘")

print(student.name)    # 하늘
student.introduce()   # 저는 하늘입니다.
student.study()       # 하늘이 공부합니다.
# -> Student에는 __init__()이나 introduce()를 직접 작성하지 않았지만, 
# 부모인 Person에서 물려받았기 때문에 사용할 수 있음 
#-------------------------------------------------------------
class Student(Person):
    def introduce(self):
        print(f"저는 학생 {self.name}입니다.")
# -> 사람(Person)에서 정의된 학생(Student)의 자기소개를 바꿀 수 있음 (오버라이딩)

student = Student("하늘")
student.introduce()
# 저는 학생 하늘입니다.
#-------------------------------------------------------------
# 자식에서 초기화할 값을 추가하려면 super()를 사용
# 부모의 초기화 작업을 유지하면서 값을 추가
class Student(Person):
    def __init__(self, name, student_id):
        super().__init__(name)       # 부모의 초기화 코드 실행
        self.student_id = student_id  # 학생에게 필요한 값 추가
# 자식에서 __init__()을 새로 작성하면 부모의 __init__()이 자동으로 호출되지 않으므로, 
# 여기서는 super().__init__(name)으로 호출한 거예요.

student = Student("하늘", "2024001")

print(student.name)        # 하늘
print(student.student_id)  # 2024001
student.introduce()        # 저는 하늘입니다.
#-------------------------------------------------------------
class Member(BaseModel):
    username: str
    age: int
# - 부모 클래스: BaseModel
# - 자식 클래스: Member
# - 물려받는 기능: 데이터 검증·변환, model_dump() 등
# - 내가 추가하는 내용: username, age라는 필드와 규칙

member = Member(username="하늘", age=23)
print(member.model_dump()) # model_dump(): 검증·변환을 마친 모델의 데이터를 딕셔너리로 반환
# {'username': '하늘', 'age': 23}
#-------------------------------------------------------------
class Person:
    def __init__(self, name):
        self.name = name

person = Person("하늘")
# person = Person("하늘") -> 이 코드를 실행하면, 
# 파이썬이 새 객체를 만든 뒤 __init__()을 자동으로 호출
# 새 객체의 name 속성에 "하늘"을 저장
print(person.name)  # 하늘
#-------------------------------------------------------------
# 사람의 이름에 더해 학생 번호도 저장
class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    # def __init__(self, ...):	이 클래스의 초기화 방법을 정의
    def __init__(self, name, student_id):
        # super().__init__(...)	부모 쪽의 초기화 메서드를 호출
        super().__init__(name)        # 부모 코드로 이름 저장
        self.student_id = student_id  # 학생 번호 추가 저장
# *** 자식이 __init__()을 새로 정의하면 부모의 __init__()은 자동으로 실행되지 않음 
# 따라서 부모의 초기화 작업도 필요하다면 super().__init__(...)을 호출 ***
# 반대로 자식에서 __init__()을 정의하지 않으면 부모의 것을 물려받아 사용

student = Student("하늘", "2024001")

print(student.name)        # 하늘
print(student.student_id)  # 2024001

# # 실행 흐름 
# Student("하늘", "2024001")
# → Student의 __init__ 실행
# → super().__init__("하늘")로 Person의 __init__ 실행
# → 같은 학생 객체에 name 저장
# → Student의 코드로 돌아와 student_id 저장
# 부모 객체를 별도로 만드는 것이 아니라, 같은 학생 객체를 초기화하는 과정
#-------------------------------------------------------------





print('#-------------------------------------------------------------')

from pydantic import BaseModel, ValidationError

# - 일반 파이썬 클래스 생성
class NormalClass:
    def __init__(self, name:str, age:int): 
        # 객체 변수(인스턴스 변수) 초기화
        self.name = name
        self.age = age
        # return f"이름: {self.name}, 나이: {self.age}"
        # *** __init__()은 객체의 초기값을 설정하는 메서드라서 None 이외의 값을 반환하면 안 됨 ***
        # 반환하면 다음 에러 발생 TypeError: __init__() should return None, not 'str' 
        
    # print(user)로 이름과 나이를 출력하고 싶다면, 문자열을 반환하는 코드를 __str__() 메서드로 분리
    def __str__(self):
        return f"이름: {self.name}, 나이: {self.age}"


params = {"name": "홍길동", "age": 20}
user = NormalClass(**params) # **params : 딕셔너리의 키와 벨류 값을 매개변수로 전달
print(user)
print('---------------------')

# user1 = NormalClass(name = "홍길동", age = 20)
user1 = NormalClass("홍길동", 20)
print('일반클래스', user1.age)
print('데이터 타입', type(user1.age))
print('---------------------')

user2 = NormalClass(20, '홍길동')
print('일반클래스', user2.age)
print('데이터 타입', type(user2.age))
print('---------------------')
print('---------------------')


# pydanctic 클래스 생성
class PydanticUser(BaseModel):
    name: str
    age: int

user2 = PydanticUser(name = "홍길동", age =20)
print('Pydantic 클래스', user2.age)
print('데이터 타입', type(user2.age))
print('---------------------')

try :
    user3 = PydanticUser(name = "홍길동", age ='스무살') # ValidationError 발생 -> user3 객체 생성 X
except ValidationError as e : # except가 오류를 받아 출력
    print('에러 :', e)
    # 에러 : 1 validation error for PydanticUser → PydanticUser 객체를 만드는 과정에서 데이터 검증 오류가 1개 발생
# try:
#     오류가 발생할 수 있는 코드
# except 오류종류:
#     해당 오류가 발생했을 때 실행할 코드
print('---------------------')

# user3 = PydanticUser(name = "홍길동", age ='스무살') # ValidationError 발생
# # pydantic_core._pydantic_core.ValidationError: 1 validation error for PydanticUser 
# # age
# # Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='스무살', input_type=str]
