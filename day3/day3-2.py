names = ['홍길동', '이순신', '강감찬']
id = 1
for name in names : 
    id += 1
    print(f'{id}.{name}')
print('------')
# for id, name in enumerate(names, start=1) :
for id, name in enumerate(names) :
    print(f'{id}.{name}')


