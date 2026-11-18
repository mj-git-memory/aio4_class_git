import random
ages = random.sample(range(100), 10)
print(ages)

results = []
for i in ages : 
    if i >= 20 :
        results.append('성인')
    else :
        results.append('미성년자')

print(results)
print('---------')


### list에서 불량을 모두 지우고 정상만 남게
items = ['정상', '불량', '불량', '정상']
for item in items :
    if item == '불량' :
        items.remove('불량')
        # continue  # -> 이 코드에서는 continue가 있어도 없어도 결과가 같음 
    # 건너뛸 추가 코드가 없음

print(f"검수 결과 : {items}")  # 검수 결과 : ['정상', '불량', '정상']
# items = ['정상', '불량', '불량', '정상']
#  인덱스:    0      1      2      3
# -> 인덱스 1의 '불량'을 삭제하면 뒤의 요소들이 앞으로 이동
# ['정상', '불량', '정상']
#    0      1      2
# -> 반복문은 다음 인덱스인 2로 이동하므로, 인덱스 1로 당겨진 두 번째 '불량'은 검사하지 못함

filter_items = [i for i in items if i =='정상']
print(filter_items) # ['정상', '정상']