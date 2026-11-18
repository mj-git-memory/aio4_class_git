# 이 코드는 조회 → 등록 → 수정 → 삭제를 순서대로 실행하면서 API가 올바르게 동작하는지 검사
# assert는 조건이 참이면 조용히 넘어가고, 거짓이면 AssertionError를 발생시킨다는 점을 기억
import importlib
import sys
from fastapi.testclient import TestClient

### 1. 검사할 파일 선택
name = sys.argv[1] if len(sys.argv) == 2 else "main"

if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
# python check.py main
# python check.py solution

### 2. 테스트 클라이언트 생성
client = TestClient(importlib.import_module(name).app, raise_server_exceptions=False)
# raise_server_exceptions=False: API 내부에서 처리되지 않은 오류가 나면, 테스트 코드에 예외를 직접 전달하지 말고 500 응답으로 받겠다는 설정
# 선택한 파일의 app을 가져와 테스트할 준비
# raise_server_exceptions=False : 서버 내부에서 처리하지 못한 예외가 발생해도, 
# 테스트 코드로 그 예외를 직접 전달하는 대신 500 응답으로 받도록 하는 옵션

### 3. 처음 목록 확인
before = client.get("/tasks")
print("GET /tasks:", before.status_code, before.json())
## python check.py solution 실행
# -> GET /tasks: 200 [{'id': 1, 'title': '첫째'}, {'id': 3, 'title': '셋째'}]
## python check.py main 실행
# -> GET /tasks: 200 [{'id': 1, 'title': '첫째'}, {'id': 3, 'title': '셋째'}]
assert before.status_code == 200
assert [t["id"] for t in before.json()] == [1, 3]
# [t["id"] for t in ...] : 각 데이터에서 ID만 뽑아 새 리스트를 만드는 리스트 컴프리헨션
# 조회한 목록의 ID가 순서대로 1, 3인지 검사
# tasks = [{"id": 1, "title": "첫째"}, {"id": 3, "title": "셋째"}]

### 4. 새 할 일 등록
created = client.post("/tasks", json={"title": "넷째"})
print("POST /tasks:", created.status_code, created.json())
## python check.py solution 실행
# -> POST /tasks: 201 {'id': 4, 'title': '넷째'}
## python check.py main 실행
# -> POST /tasks: 201 {'id': 4, 'title': '넷째'}
# 제목이 "넷째"인 할 일을 등록하고 두 가지를 검사
assert created.status_code == 201 and created.json()["id"] == 4
# 생성 성공 상태 코드가 201인가? / 생성된 데이터의 ID가 4인가?
# [
#     {"id": 1, "title": "첫째"},
#     {"id": 3, "title": "셋째"},
#     {"id": 4, "title": "넷째"}
# ]

### 5. ID 3의 제목 수정
changed = client.put("/tasks/3", json={"title": "수정"})
print("PUT /tasks/3:", changed.status_code, changed.json())
## python check.py solution 실행
# -> PUT /tasks/3: 200 {'id': 3, 'title': '수정'}
## python check.py main 실행
# -> PUT /tasks/3: 200 {'id': 3, 'title': '수정'}
assert changed.status_code == 200 and changed.json()["title"] == "수정"
# ID 3의 제목을 바꾸고, 응답 상태 코드가 200이며 반환된 제목이 "수정"인지 검사

### 6. ID 3 삭제
removed = client.delete("/tasks/3")
print("DELETE /tasks/3:", removed.status_code)
## python check.py solution 실행
# -> DELETE /tasks/3: 204
## python check.py main 실행
# -> DELETE /tasks/3: 500
# ID 3 삭제를 요청하고 응답 상태 코드를 출력 
# tasks.pop(task_id): 요청한 ID 3을 인덱스 3으로 사용. 이 시점에는 항목이 세 개여서 인덱스는 0, 1, 2뿐이므로 IndexError가 발생
# raise_server_exceptions=False 때문에 테스트는 이를 500 응답으로 받고, 204가 아니므로 이 assert에서 실패
assert removed.status_code == 204, "Task ID를 리스트 인덱스로 잘못 사용했을 수 있습니다"
# 삭제가 성공했다는 204 응답인지 검사. 실패하면 쉼표 뒤의 설명이 AssertionError 메시지로 표시

### 7. 삭제 후 남은 목록 확인
ids = [t["id"] for t in client.get("/tasks").json()]
print("remaining IDs:", ids)
## python check.py solution 실행
# -> remaining IDs: [1, 4]
assert ids == [1, 4]

### 8. 없는 ID 삭제 확인
assert client.delete("/tasks/999").status_code == 404
# 없는 ID 999의 삭제를 요청했을 때 404를 반환하는지 검사
# assert ... == 404는 404를 반환하라는 명령이 아니라, 실제 응답이 404인지 검사하는 코드
# raise_server_exceptions=False가 모든 오류를 500으로 바꾸는 것은 아님 
# - 직접 작성한 HTTPException(404) → FastAPI가 처리해서 404 응답
# - 처리하지 않은 IndexError 같은 내부 오류 → 500 응답

print("PASS")
