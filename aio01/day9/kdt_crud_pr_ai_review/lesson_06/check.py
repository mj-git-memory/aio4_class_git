# 이 코드는 main.py 또는 solution.py의 함수를 불러와, 삭제된 파일도 변경 목록에 포함하는지 검사

import importlib
import sys

print(sys.argv)
# python check.py solution로 실행했다면, ['check.py', 'solution'] 출력

name = sys.argv[1] if len(sys.argv) == 2 else "main"

if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
print(f'file name: {name}')

f = importlib.import_module(name).summarize_changes
# 선택한 파일에서 summarize_changes 함수 자체를 가져와 f라는 이름에 연결. 
# 아직 호출한 것은 아님 

sample = [{"path": "main.py", "status": "modified"}, {"path": "old.py", "status": "deleted"}]
result = f(sample)
print(result)
### python check.py main 실행
# -> {'changed': ['main.py']}
### python check.py solution 실행 
# -> {'changed': ['main.py', 'old.py']}

assert result == {"changed": ["main.py", "old.py"]}
### python check.py main 실행
# ->    assert result == {"changed": ["main.py", "old.py"]}
# ->           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# -> AssertionError

print("PASS")
### python check.py solution 실행 
# -> PASS