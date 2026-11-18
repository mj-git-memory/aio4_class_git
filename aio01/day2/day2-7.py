# 시나리오
# 백엔드 api에서 요청을 보낸 사용자 정보(dict)를 검증해서 접근 가능여부와 
# 부여할 기능을 판별하는 분기 로직을 작성

# 요구사항
# 1. 사용자 정보는 user_role(문자열)과 is_suspended(정지계정여부)
# 2. is_suspended가 True이면 즉시 "정지된 계정입니다." 를 출력하고 검사를 종료
# 3. 역활은 admin,manager,user,guest 중 하나
# admin: "전체 시스템 관리 및 데이터 수정 권한 부여"
# manager: "팀 데이터 조회 및 수정 권한 부여"
# user: "개인 데이터 조회 권한 부여"
# guest: "게스트 권한 (읽기 전용 일부 허용)"
# 4. 정의되지 않은 역활일 경우 : [오류] 알수 없는 권한입니다.

test_users = [
    {"username": "alpha", "user_role": "admin", "is_suspended": False},
    {"username": "bravo", "user_role": "user", "is_suspended": True},
    {"username": "charlie", "user_role": "manager", "is_suspended": False},
    {"username": "delta", "user_role": "hacker", "is_suspended": False},
]

for user in test_users : 

    username = user['username']
    role = user['user_role']
    suspended = user['is_suspended']

    ### 1.
    if suspended :
        print(f"이름: {username} -  정지된 계정입니다.")

    elif role in ['admin', 'manager', 'user', 'guest'] : 
        if role == 'admin' :
            print(f"이름: {username} = {role} -> 전체 시스템 관리 및 데이터 수정 권한 부여")
        elif role == 'manager' :
            print(f"이름: {username} = {role} -> 팀 데이터 조회 및 수정 권한 부여")
        elif role == 'user' :
            print(f"이름: {username} = {role} -> 개인 데이터 조회 권한 부여")
        elif role == 'guest' :
            print(f"이름: {username} = {role} -> 게스트 권한 (읽기 전용 일부 허용)")
    else : 
        print(f"이름: {username} = {role} -  [오류] 알 수 없는 권한입니다.")
print('-----------')


for user in test_users : 

    username = user['username']
    role = user['user_role']
    suspended = user['is_suspended']

    ### 2.
    print(f"username = {username}", end = "\t")
    if suspended : 
        print('정지된 계정입니다.')
        continue  # suspended == Ture일 시, 아래 내용까지 안 돌고, 다시 위로 올라감
        # continue는 현재 사용자의 나머지 검사를 건너뛰고, 다음 사용자를 검사
        # break # 반복문 전체가 종료 so, 사용하면 안됨 

    if role == 'admin' :
        print("전체 시스템 관리 및 데이터 수정 권한 부여")
    elif role == 'manager' :
        print("팀 데이터 조회 및 수정 권한 부여")
    elif role == 'user' :
        print("개인 데이터 조회 권한 부여")
    elif role == 'guest' :
        print("게스트 권한 (읽기 전용 일부 허용)")
    else : 
        print("[오류] 알 수 없는 권한입니다.")
