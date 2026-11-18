import importlib
import sys

print(sys.argv)
name = sys.argv[1] if len(sys.argv) == 2 else "main"

if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
print(f'file name: {name}')

can_edit = importlib.import_module(name).can_edit
print('admin:', can_edit('admin'))
### python check.py main 실행
# -> admin: True
### python check.py solution 실행 
# -> admin: True
print('not-admin:', can_edit('not-admin'))
### python check.py main 실행
# -> not-admin: True
### python check.py solution 실행 
# -> not-admin: False
assert can_edit('admin') is True
assert can_edit('not-admin') is False
### python check.py main 실행
# -> AssertionError
assert can_edit('viewer') is False
print('PASS')
