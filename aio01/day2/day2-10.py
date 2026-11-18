### zip
# zip()은 여러 자료의 같은 위치에 있는 요소를 하나의 튜플로 묶어주는 함수
# -> 결과를 리스트로 바로 만들어 주는 대신, **필요할 때 쌍을 하나씩 꺼내는 이터레이터(iterator)**를 반환
# -> zip 이터레이터는 꺼낸 요소가 소진됨 

## 1. zip() 객체 만들기
list_1 = ['a', 'b', 'c']
list_2 = [100, 200, 300]
result = zip(list_1, list_2)
# 'a' + 100 → ('a', 100)
# 'b' + 200 → ('b', 200)
# 'c' + 300 → ('c', 300)
print(result) # <zip object at 0x10a197c80> # 내부 요소 대신 객체를 나타내는 문구가 출력

print(range(5)) # range(0, 5) # 역시 리스트가 아닌 별도의 객체. 숫자를 모두 보고 싶으면 리스트로 변환
print(list(range(5)))  # [0, 1, 2, 3, 4]
print('-------')

## 2. 딕셔너리로 변환하기
print(dict(result)) # {'a': 100, 'b': 200, 'c': 300}
# -> result의 모든 요소를 꺼내 사용하므로 이터레이터가 소진

## 3. 리스트로 변환하기
result = zip(list_1, list_2) # 앞에서 사용한 result는 소진됐으므로, zip()을 다시 호출해 새 이터레이터를 만듦
print(list(result)) # [('a', 100), ('b', 200), ('c', 300)]
# -> list(result)는 쌍을 모두 꺼내서 튜플을 요소로 가진 리스트를 만듭
print('-------')

## 4. 반복문으로 하나씩 꺼내기
result = zip(list_1, list_2)
for i in result :
    print(i)
# ('a', 100)
# ('b', 200)
# ('c', 300)
print('-------')


## 5. 한 번 사용하면 왜 빈 리스트가 나올까?
# zip()이 반환하는 것은 **한 번 순회하면 소진되는 이터레이터(iterator)**이기 때문이에요.
result = zip(list_1, list_2)

print(dict(result))  # result의 요소를 모두 꺼내 사용
print(list(result))  # 남은 요소가 없어서 []
# -> 첫 번째 dict(result)에서 모든 쌍을 이미 꺼냄. 
# -> 따라서 두 번째 list(result)에서는 남은 요소가 없어 빈 리스트가 나옴
print('-------')


## 6. 두 리스트의 길이가 다르면?
# -> 기본적으로 가장 짧은 자료에 맞춰 종료
letters = ['a', 'b', 'c']
numbers = [100, 200]

print(list(zip(letters, numbers)))
# [('a', 100), ('b', 200)]
# -> 'c'는 짝지을 값이 없으므로 결과에 포함되지 않음 