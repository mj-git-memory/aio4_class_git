##### 이 코드는 클래스로 만든 객체의 메서드를 호출하는 방법과 
##### 변수가 None이면 그 메서드를 호출할 수 없다는 점을 보여주는 예제

### 객체 안에는 변수, 함수 등이 들어있음

## 1. SafeProfile은 객체를 만들기 위한 설계도
class SafeProfile :
    def __init__(self) : # __init__: 객체를 만들 때 자동으로 실행되는 초기화 메서드
        pass # pass: 아무 작업도 하지 않고 넘어감 

    def gget(self, key) : # 직접 지은 메서드 이름
        return True
    def sset(self, key) : # 직접 지은 메서드 이름
        return True
    def jjet(self, key) : # 직접 지은 메서드 이름
        # self: 메서드를 호출한 객체 자신을 가리킴 / key: 호출할 때 전달받는 값
        return True
    # -> 현재 세 메서드는 전달받은 key를 사용하지 않고 항상 True를 반환

# SafeProfile.  # -> tab 누르면 gget, sset, jjet 다 보임
# SafeProfile.


## 2. SafeProfile()을 호출하면 객체가 만들어짐. 같은 클래스로 만든 서로 다른 객체 3개
user_profile1 = SafeProfile()
user_profile2 = SafeProfile()
user_profile3 = SafeProfile()
# user_profile1.gget("aaa")
# # ↓ 파이썬이 객체 자신을 self에 자동으로 전달

# def gget(self, key):
#     # self → user_profile1이 가리키는 객체
#     # key  → "aaa"
#     return True

# user_profile이 가리키는 객체의 gget()을 호출. 
# -> 어떤 문자열을 전달해도 항상 True를 반환하므로 다음처럼 출력
user_profile = SafeProfile()
print(user_profile.gget('is_verified')) # True   # 'is_verified'는 그냥 예시
print(user_profile.gget('aaa')) # True   # 'aaa'는 그냥 예시
print("-----------")


## 3. None을 대입하면 더 이상 해당 변수로 객체의 메서드를 호출할 수 없음
user_profile = None 
# # -> 이제 user_profile은 앞서 만든 객체 대신 None을 가리킴

if user_profile is not None and user_profile.gget("aaa"):
    print("성공")
else:
    print("실패")
# -> user_profile이 None이면 왼쪽 조건이 False이므로, 오른쪽 gget() 호출은 건너뛰고 "실패"를 출력

# print(user_profile.gget('bb')) # 에러 출력.   # 'bb'는 그냥 예시
# # -> AttributeError: 'NoneType' object has no attribute 'gget'
# # -> None에는 gget이 없으므로 오류가 발생
print("-----------")


user_profile = SafeProfile()
if user_profile.gget('aa') :
    print('성공')
else : 
    print('실패')