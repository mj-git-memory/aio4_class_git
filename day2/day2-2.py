### 논리연산자 : AND , OR 
is_Success = True
is_Pass = False

if is_Success and is_Pass :
    print('A')
else :
    print('B')
print('-------')



###  단락평가 Short-circuit
# 단락 평가 : 논리식에서 왼쪽 값만으로 결과가 결정되면 오른쪽 식은 실행하지 않는 방식
def expensive_check() :
    print("시간이 오래 걸리는 함수 실행")
    return True

is_active = False

if is_active and expensive_check() :
# -> is_active가 False이기 때문에, expensive_check()는 실행도 안됨 (and로 연결)
    print('통과')
else :
    print('차단 (expensive_check 실행 안됨)')
# 차단 (expensive_check 실행 안됨)
print('-------')

if is_active or expensive_check() :  
# -> is_active가 False여도, expensive_check()는 실행됨 (or로 연결)
    print('통과')
else :
    print('차단 (expensive_check 실행 안됨)')
# 시간이 오래 걸리는 함수 실행
# 통과  # expensive_check()에서 True 리턴 
print('-------')

is_active = True
if is_active or expensive_check() :  
# -> is_active가 True여서, expensive_check()는 실행 안됨 (or로 연결)
    print('통과')
else :
    print('차단 (expensive_check 실행 안됨)')
# 통과  # expensive_check()에서 True 리턴 
# -> 왼쪽만으로 전체 결과가 True로 확정되므로 함수를 실행하지 않음. 이것이 단락 평가
print('-------')
# 연산자	왼쪽 값	    오른쪽 실행 여부
# or	    True	    건너뜀
# or	    False	    실행
# and	    True	    실행
# and	    False	    건너뜀



### 사용자 정보가 있는지 먼저 확인하고, 정보가 있으면 인증 여부를 확인하는 코드
user_profile = None # None은 여기서 사용자 정보가 없음을 나타냄 

if user_profile is not None and user_profile.get('is_verified'):
#  ① 사용자 정보가 있는가?       ② 인증 여부가 참인가?
# -> 현재는 ①이 False이므로, and의 단락 평가에 따라 ②는 실행하지 않음 
    print('인증된 사용자')
else :
    print('비인증된 사용자')
print('-------')

user_profile = {"name": "지민", "is_verified": True}
if user_profile is not None and user_profile.get("is_verified"):
    print("인증된 사용자")
else:
    print("비인증된 사용자")
print('-------')

user_profile = None # None은 여기서 사용자 정보가 없음을 나타냄 
if user_profile is None and user_profile.get('is_verified'): # AttributeError 발생
#  ① 사용자 정보가 있는가?       ② 인증 여부가 참인가?
# -> 현재는 ①이 False이므로, and의 단락 평가에 따라 ②는 실행하지 않음 
    print('인증된 사용자')
else :
    print('비인증된 사용자')
# -> AttributeError: 'NoneType' object has no attribute 'get'
# -> None에는 .get()을 사용할 수 없음 
print('-------')

