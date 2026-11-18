# 이 코드는 main.py 또는 solution.py의 combine_tasks()를 불러와 두 목록을 합치는지, 
# 같은 ID가 있으면 기능 쪽 데이터를 우선하는지 검사
import importlib
import sys

print(sys.argv)
name = sys.argv[1] if len(sys.argv) == 2 else "main"

if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
print(f'file name: {name}')

combine = importlib.import_module(name).combine_tasks
# 선택한 파일의 combine_tasks 함수를 가져와 combine이라는 이름으로 사용
# 아직 호출한 것은 아님 

main_items = [{"id": 1, "title": "메인"}]
feature_items = [{"id": 2, "title": "기능"}]

result = combine(main_items, feature_items)
print(result)
### python check.py main 실행
# -> [{'id': 2, 'title': '기능'}]
### python check.py solution 실행 
# -> [{'id': 1, 'title': '메인'}, {'id': 2, 'title': '기능'}]

assert [x["id"] for x in result] == [1, 2]
### python check.py main 실행
# -> AssertionError
# main의 결과에서 ID 추출
# [2] == [1, 2]     # False → AssertionError
### python check.py solution 실행
# solution의 결과에서 ID 추출
# [1, 2] == [1, 2]  # True → 다음 줄로 진행

assert combine([{"id": 1, "title": "기존"}], [{"id": 1, "title": "기능 우선"}])[0]["title"] == "기능 우선"
# merged = combine(
#     [{"id": 1, "title": "기존"}],
#     [{"id": 1, "title": "기능 우선"}]
# )
# first_item = merged[0]          # 결과 리스트의 첫 번째 데이터
# title = first_item["title"]     # 그 데이터의 제목
# assert title == "기능 우선"
# -> 같은 ID 1이 양쪽에 있을 때 feature_items 쪽 제목을 사용하는지 검사
# -> solution.py는 ID 1의 데이터를 기능 쪽 데이터로 덮어쓰므로 통과
print("PASS")
### python check.py solution 실행 
# PASS 