### 포함관계 (in, not in)

# if role == 'admin' or role == 'manger' or role == 'staff'
allowed_roles = ['admin', 'manager', 'staff']
role = 'admin'

# if role in ['admin', 'manager', 'staff'] :
if role in allowed_roles :  
    print('접근 허용')
else :
    print('접근 불가')