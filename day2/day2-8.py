list_a = [1,2,3,4,5,6,7,8,9,10]

for i in list_a : 
    if i % 2 == 0 :
        continue # 조건에 걸리면, continue 다음 문장은 skip됨  # 1,3,5,7,9
    print(i)
print("----------")

for i in list_a : 
    if i % 2 == 0 :
        print(i)  # 2,4,6,8,10

