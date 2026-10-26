import importlib
import sys

name = sys.argv[1] if len(sys.argv) == 2 else "main"
if name not in {"main", "solution"}:
    raise SystemExit("python check.py main|solution")
print(f'file name: {name}.py')

ready = importlib.import_module(name).is_ready
print('true:', ready('true'))
print('false:', ready('false'))
assert ready('true') is True
assert ready('false') is False
print('PASS')


### python check.py main 실행
# file name: main.py
# true: True
# false: True
# Traceback (most recent call last):
#   File "/Users/imijeong/Downloads/AIO_4_class/day9/kdt_crud_pr_ai_review/lesson_05/check.py", line 13, in <module>
#     assert ready('false') is False
#            ^^^^^^^^^^^^^^^^^^^^^^^
# AssertionError
# bool("true")   # True
# bool("false")  # True — "false"도 내용이 있는 문자열
# bool("")       # False

### python check.py solution 실행 
# file name: solution.py
# true: True
# false: False
# PASS
# "true".lower() == "true"   # True
# "false".lower() == "true"  # False
# "TRUE".lower() == "true"   # True