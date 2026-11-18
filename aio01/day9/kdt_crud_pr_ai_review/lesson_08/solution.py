### 이 코드는 두 목록을 ID 기준으로 합친 뒤, ID가 작은 순서대로 반환
def combine_tasks(main_tasks: list[dict], feature_tasks: list[dict]) -> list[dict]:
    by_id = {task["id"]: task for task in main_tasks}
    for task in feature_tasks:
        by_id[task["id"]] = task
    return [by_id[key] for key in sorted(by_id)]

if __name__ == "__main__":
    print(combine_tasks([{"id": 1}], [{"id": 2}]))

## 1. ID를 키로 사용하는 딕셔너리 만들기
# by_id = {task["id"]: task for task in main_tasks}
# by_id = {}
# for task in main_tasks:
#     by_id[task["id"]] = task
# -> main_tasks의 데이터를 하나씩 꺼내 ID를 키, 할 일 딕셔너리를 값으로 저장
# -> by_id = {
# ->    1: {"id": 1}
# -> }

## 2. 두 번째 목록 합치기
# for task in feature_tasks:
#     by_id[task["id"]] = task
# -> by_id = {
# ->    1: {"id": 1},
# ->    2: {"id": 2}
# -> }
# 딕셔너리는 같은 키를 중복해서 가질 수 없으므로, 이미 있는 ID라면 그 ID의 값을 교체
# main_tasks = [{"id": 1, "title": "기존"}]
# feature_tasks = [{"id": 1, "title": "변경"}]
# -> 이 경우 ID 1의 데이터는 {"id": 1, "title": "변경"}이 됨 

## 3. ID 순서대로 리스트 만들기
# return [by_id[key] for key in sorted(by_id)]
# sorted(by_id)는 딕셔너리의 키를 정렬한 리스트를 만듦 
# sorted(by_id)  # [1, 2]
# 그 순서대로 각 키에 해당하는 데이터를 꺼내 리스트로 반환
# -> [by_id[1], by_id[2]]
# -> # [{"id": 1}, {"id": 2}]