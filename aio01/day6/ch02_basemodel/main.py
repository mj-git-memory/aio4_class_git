### 모듈 import test 

print()

import day6.ch02_basemodel.day6_2 as day6_2
# import day6_2 # main.py와 day2_3.py가 같은 폴더에 있어서 에러 안남 

member = day6_2.Member(username = '홍길동', age = 20, active=True, nickname =None)

if member.age > 19 :
    print('성인입니다.')

print('main.py', __name__)
print('-----------------')

# 다른 파일에서 day6_3 import하면, day6_3 파일의 Member(모듈)가 실행 될 때 __name__ 변수에 할당되는 값은 모듈이 들어있는 파일의 이름임 