# zip

list_1 = ['a', 'b', 'c']
list_2 = [100, 200, 300]
result = zip(list_1, list_2)
# print(range(5))

# print(dict(result)) # {'a': 100, 'b': 200, 'c': 300}
print(list(result)) # [('a', 100), ('b', 200), ('c', 300)]

for i in result :
    print(i)


# zip()이 반환하는 것은 **한 번 순회하면 소진되는 이터레이터(iterator)**이기 때문이에요.
result = zip(list_1, list_2)

print(dict(result))  # result의 요소를 모두 꺼내 사용
print(list(result))  # 남은 요소가 없어서 []

