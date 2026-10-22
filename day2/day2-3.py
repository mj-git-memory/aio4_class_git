### 객체 안에는 변수, 함수 등이 들어있음

class SafeProfile :
    def __init__(self) :
        pass
    def get(self, key) :
        return True
    def set(self, key) :
        return True
    def jet(self, key) :
        return True
# SafeProfile.  # -> tab 누르면 get, set, jet 다 보임
    
user_profile1 = SafeProfile()
user_profile2 = SafeProfile()
user_profile3 = SafeProfile()

user_profile = SafeProfile()
print(user_profile.get('is_verified')) # True   # 'is_verified'는 그냥 예시
print(user_profile.get('aaa')) # True   # 'aaa'는 그냥 예시
print("-----------")
# user_profile = None # 에러 출력. None -> False
## AttributeError: 'NoneType' object has no attribute 'get'
# print(user_profile.get('is_verified')) 
# print(user_profile.get('aaa')) 

if user_profile.get('aaa') :
    print('성공')
else : 
    print('실패')