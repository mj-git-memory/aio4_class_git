### 딕셔너리
# -> key-value 한쌍이 하나의 값

# 리스트 vs 딕셔너리
list_1 = [10, 20, 30, [1,2,3]]
dict_1 = {'kor':80, 'eng':80, 'math':90}

print(dict_1.keys()) # dict_keys(['kor', 'eng', 'math'])
print(dict_1.values()) # dict_values([80, 80, 90])
print(dict_1.items()) # dict_items([('kor', 80), ('eng', 80), ('math', 90)])
print('-----')

for i in dict_1.items() :
    print(i, i[0], i[1])
# ('kor', 80) kor 80
# ('eng', 80) eng 80
# ('math', 90) math 90

for key, value in dict_1.items() :
    print(f"key = {key}, value = {value}")
# key = kor, value = 80
# key = eng, value = 80
# key = math, value = 90
print('-----')

### **언패킹(unpacking)**
# -> 여러 값을 풀어서 각각의 변수에 나누어 저장하는 기능
num1, num2 = (10,20) # 튜플
num1, num2 = 10, 20 # 괄호 생략 가능
print(num1, num2) #  # 10 20

name, age = ["지민", 25] # 리스트도 언패킹 가능 
print(name, age)


num1, num2 = (10,20, 3)
# -> ValueError: too many values to unpack (expected 2)


