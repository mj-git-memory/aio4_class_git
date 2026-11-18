### check.py: 둘(main.py / solution.py) 중 하나를 선택해서 응답이 올바른지 검사
# check.py가 solution.py의 app을 불러와 테스트합
# python solution.py를 직접 실행하는 것과는 다름 

from fastapi.testclient import TestClient
import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"

if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")

client = TestClient(importlib.import_module(name).app)

### 1. 테스트 요청과 응답 저장
found = client.get("/tasks/1")
print("existing:", found.status_code, found.json())

missing = client.get("/tasks/222")
print("missing:", missing.status_code, missing.json())

# found와 missing은 응답을 담아 둔 변수명
# 변수	    상태 코드	.json() 결과
# found	    200	        {"id": 1, "title": "Git 준비"}
# missing	404	        {"detail": "Task not found"}



## assert 조건
# assert는 조건이 참이면 아무것도 출력하지 않고 넘어감 
# 거짓이면 AssertionError를 발생
# if not 조건:
#     raise AssertionError
# 출력은 print()가 담당하고, assert는 검사만 함 
# -> solution을 검사했을 때 세 줄에서 출력이 없는 것이 정상


### 2. 첫 번째 assert: 기존 데이터 조회 검사
assert found.status_code == 200 and found.json()["id"] == 1
# -> found.status_code == 200  # 요청이 성공했는가? → True
# -> found.json()["id"] == 1   # 받은 데이터의 ID가 1인가? → True

### 3. 두 번째 assert: 없는 데이터의 상태 코드 검사
assert missing.status_code == 404
# “없는 ID를 요청했을 때 404로 응답했는가?”를 검사
# solution.py는 404를 반환하므로 통과

### 4. 세 번째 assert: 오류 설명 검사
assert missing.json()["detail"] == "Task not found"
# 응답 본문의 "detail" 값이 정확히 "Task not found"인지 검사
# missing.json()
# # {"detail": "Task not found"}
# missing.json()["detail"]
# # "Task not found"

print("PASS")


## solution과 main의 실행 결과 차이
# python check.py solution이면 세 검사를 모두 통과해서 다음처럼 출력
# existing: 200 {'id': 1, 'title': 'Git 준비'}
# missing: 404 {'detail': 'Task not found'}
# PASS

# main.py에는 함수 맨 앞에 다음 코드가 있음 : return tasks.get(task_id)
# return이 실행되면 함수가 끝나므로 그 아래의 404 처리 코드는 실행되지 않음. 
# 따라서 /tasks/222에도 200과 null이 응답
# python check.py main
# existing: 200 {'id': 1, 'title': 'Git 준비'}
# missing: 200 None
# assert missing.status_code == 404
# -> 실제로는 200이므로 AssertionError 발생
# -> 처리하지 않은 예외 때문에 실행이 중단되어 세 번째 assert와 마지막 print("PASS")는 실행되지 않음