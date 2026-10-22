# import random
# ages = random.sample(range(100), 10)
# results = []
# for i in ages : 
#     if i >= 20 :
#         results.append('성인')
#     else :
#         results.append('미성년자')

# print(results)


### list에서 불량을 모두 지우고 정상만 남게
items = ['정상', '불량', '불량', '정상']
for item in items :
    if item == '불량' :
        items.remove('불량')
        continue

print(f"검수 결과 : {items}")

filter_items = [i for i in items if i =='정상']
print(filter_items)