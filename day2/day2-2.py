### 논리연산자 : AND , OR 
# is_Success = True
# is_Pass = False

# if is_Success and is_Pass :
#     print('A')
# else :
#     print('B')


###  단락평가 Short-circuit
def expensive_check() :
    print("시간이 오래 걸리는 함수 실행")
    return True

is_active = False

# is_active가 False이기 때문에, expensive_check()는 실행도 안됨 (and로 연결)
# if is_active and expensive_check() :  
# is_active가 False여도, expensive_check()는 실행됨 (or로 연결)
if is_active or expensive_check() :  
    print('통과')
else :
    print('차단 (expensive_check 실행 안됨)')


### 객체지향
    
### None 값을 방어
user_profile = None
if user_profile is not None and user_profile.get('is_verified') :
    print('인증된 사용자')
else :
    print('비인증된 사용자')