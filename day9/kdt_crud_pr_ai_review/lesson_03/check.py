### 1. 필요한 도구 가져오기
# PUT과 PATCH API가 의도대로 작동하는지 자동으로 검사하는 테스트 코드
import importlib
# importlib: 파일 이름을 문자열로 받아 파이썬 모듈을 불러와요.
import sys
# sys: 실행할 때 입력한 명령줄 인자를 읽어요.
from fastapi.testclient import TestClient
# TestClient: 서버를 따로 실행하지 않고 FastAPI 앱에 테스트 요청을 보냅니다.

name = sys.argv[1] if len(sys.argv) == 2 else "main"
# sys.argv : 파이썬 프로그램을 실행할 때 입력한 인자들을 담은 리스트. 값이 들어 있는 변수
# python check.py solution <- 예를 들어 터미널에서 이렇게 실행하면
# sys.argv에는 아래 값들이 들어 있음 
# ["check.py", "solution"]
#    0번         1번
# -> **“리스트 항목이 정확히 2개면 두 번째 값을 사용하고, 그렇지 않으면 기본값 "main"을 사용해라”**라는 뜻
## python check.py solution 실행하면 
# sys.argv → ["check.py", "solution"]
# 길이가 2이므로, name = "solution"
## python check.py 실행하면
# sys.argv → ["check.py"]
# 길이가 1이므로, name = "main"
## python check.py aaa 실행하면
# sys.argv        # ["check.py", "aaa"]
# len(sys.argv)   # 2
# sys.argv[1]     # "aaa"

### 2. 검사할 파일 선택하기
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
# 선택한 이름이 main, solution 중 하나가 아니면 사용법을 출력하고 프로그램을 종료
# 여기서 “사용법”은 터미널에서 이 프로그램을 어떻게 실행해야 하는지 알려주는 안내 문구
# 다음 두 명령 중 하나로 실행하라는 뜻 : python check.py main / python check.py solution
# => raise SystemExit("main 또는 solution을 입력하세요. 예: python check.py main")   

### 3. 테스트용 클라이언트 만들기
client = TestClient(importlib.import_module(name).app)
# name이 "main"이면 main.py를 불러와 그 안의 app을 가져옴 
# 아래와 같음 
# -> import main
# -> client = TestClient(main.app)
# name이 "solution"이면 solution.py를 불러와 그 안의 app 객체를 가져옴
# 정확히 말하면 app을 함수처럼 호출하는 것이 아니라, app 객체를 TestClient에 전달하는 것
# 이후 client.put(...)이나 client.patch(...)를 실행하면 solution.py에 정의한 API를 테스트함 

### 4. 정상적인 PUT 요청 검사하기
put = client.put("/tasks/1", json={"title": "완전교체", "done": True})
# 제목과 완료 여부를 모두 보내고, 응답을 put에 저장
print("PUT:", put.status_code, put.json())
# put.status_code: 응답 상태 코드
# put.json(): JSON 응답을 파이썬 딕셔너리 등의 값으로 변환
# .json()은 JSON으로 된 응답 본문을 파이썬 값으로 변환하는 메서드. JSON 응답이 배열이면 파이썬 리스트로 변환
# 서버의 파이썬 딕셔너리
#     → FastAPI가 JSON으로 변환해서 응답
#     → 클라이언트가 .json()으로 파이썬 딕셔너리로 변환
assert put.status_code == 200 and put.json()["done"] is True
# assert 조건: 조건이 참이면 계속 진행하고, 거짓이면 AssertionError를 발생시킴 
# 여기서는 응답이 200이고 done이 True인지 확인

### 5. 필수 값이 빠진 PUT 요청 검사하기
invalid = client.put("/tasks/1", json={"title": "누락"})
# TaskPut에서 필수인 done을 일부러 빼고 보냄 
print("PUT invalid:", invalid.status_code)
assert invalid.status_code == 422
# 요청 데이터가 형식에 맞지 않다는 422 응답이 와야 테스트를 통과. 잘못된 요청을 제대로 거절하는지도 검사.

### 6. PATCH가 제목만 바꾸는지 검사하기
patch = client.patch("/tasks/1", json={"title": "제목만"})
print("PATCH:", patch.status_code, patch.json())
assert patch.status_code == 200 and patch.json()["title"] == "제목만"
# 요청이 성공했고 제목이 바뀌었는지 확인
assert patch.json()["done"] is True, "PATCH가 지정하지 않은 done을 변경했습니다"
# 앞의 PUT에서 설정한 done=True가 그대로 유지되는지 확인
# 쉼표 뒤 문자열은 검사가 실패했을 때 보여주는 메시지
# AssertionError: PATCH가 지정하지 않은 done을 변경했습니다
print("PASS")
# 모든 assert를 통과해야 마지막에 PASS가 출력