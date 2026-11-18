def combine_tasks(main_tasks: list[dict], feature_tasks: list[dict]) -> list[dict]:
    return feature_tasks

if __name__ == "__main__":
    print(combine_tasks([{"id": 1}], [{"id": 2}]))


# main_tasks, feature_tasks: 딕셔너리가 들어 있는 리스트를 받는 매개변수
# -> list[dict]: 반환값도 딕셔너리들이 들어 있는 리스트라는 타입 표시
# return feature_tasks: 두 번째 매개변수의 값만 반환해요. main_tasks는 사용하지 않음 

# combine_tasks([{"id": 1}], [{"id": 2}])
# #             main_tasks    feature_tasks
# 정확히 말하면 함수가 두 값을 모두 받고, return에서 두 번째 값만 돌려주는 것