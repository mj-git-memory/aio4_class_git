"""실제 요청으로 학생 코드와 정답 코드를 비교한다."""
import importlib
import sys
from fastapi.testclient import TestClient

module_name = sys.argv[1] if len(sys.argv) == 2 else "main"

if module_name not in {"main", "solution"}:
    raise SystemExit("사용법: python check.py main 또는 python check.py solution")

module = importlib.import_module(module_name)
client = TestClient(module.app)

before = client.get("/tasks")
print("GET /tasks:", before.status_code, before.json())
## python check.py solution 실행
# -> GET /tasks: 200 [{'id': 1, 'title': 'API 확인'}, {'id': 3, 'title': '테스트 작성'}]
## python check.py main 실행
# -> GET /tasks: 200 [{'id': 1, 'title': 'API 확인'}, {'id': 3, 'title': '테스트 작성'}]
assert before.status_code == 200
assert [item["id"] for item in before.json()] == [1, 3]

created = client.post("/tasks", json={"title": "PR 준비"})
print("POST /tasks:", created.status_code, created.json())
## python check.py solution 실행
# -> POST /tasks: 201 {'id': 4, 'title': 'PR 준비'}
## python check.py main 실행
# -> POST /tasks: 201 {'id': 3, 'title': 'PR 준비'}
assert created.status_code == 201
assert created.json()["title"] == "PR 준비"

ids = [item["id"] for item in client.get("/tasks").json()]
print("등록 후 ID:", ids)
## python check.py solution 실행
# -> 등록 후 ID: [1, 3, 4]
## python check.py main 실행
# -> 등록 후 ID: [1, 3, 3]
assert len(ids) == len(set(ids)), "중복 ID 발견: 새 ID를 만드는 보조 함수를 확인하세요." # set() : 중복 제거 
## python check.py solution 실행
# -> 아무것도 실행되지 않고 넘어감 
## python check.py main 실행
# -> AssertionError: 중복 ID 발견: 새 ID를 만드는 보조 함수를 확인하세요.
assert created.json()["id"] == 4, "새 항목은 현재 최대 ID 3 다음인 4여야 합니다."

print("PASS: 정상 조회 및 고유 ID 등록")
## python check.py solution 실행
# -> PASS: 정상 조회 및 고유 ID 등록

