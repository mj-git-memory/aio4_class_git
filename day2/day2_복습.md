# Day 2 파이썬 개념과 예제 정리

조건으로 실행 흐름을 나누고, 반복문으로 데이터를 처리한 뒤, 함수와 테스트로 결과를 확인하는 과정을 복습합니다. 예제는 별도 코드 블록 단위로 실행할 수 있으며, 원본에서 주의할 동작은 따로 설명했습니다.

## 소스코드별 학습 내용

| 파일 | 학습 내용 |
|---|---|
| [day2-1.py](day2-1.py) | 점수에 따른 조건 분기 |
| [day2-2.py](day2-2.py) | 논리 연산자, 단락 평가, None 확인 |
| [day2-3.py](day2-3.py) | 클래스, 객체, 메서드 |
| [day2-4.py](day2-4.py) | 삼항 연산자 |
| [day2-5.py](day2-5.py) | 포함 여부 검사 |
| [day2-6.py](day2-6.py) | 딕셔너리 순회, 언패킹 |
| [day2-7.py](day2-7.py) | 사용자 권한 검사 실습 |
| [day2-8.py](day2-8.py) | 반복문, 짝수 판별, continue |
| [day2-9.py](day2-9.py) | 문제 정의, 입력과 출력, 제약조건, 검증 |
| [day2-10.py](day2-10.py) | zip, 이터레이터 소진 |
| [day2-11.py](day2-11.py) | 리스트 컴프리헨션, 정렬, 집합, 정규표현식 |
| [day2-12.py](day2-12.py) | 리스트 순회 중 삭제 문제, 필터링 |
| [even_sum_and_count/main.py](even_sum_and_count/main.py) | 짝수 합과 개수, 함수, assert |
| [even_sum_and_count/day2-11.py](even_sum_and_count/day2-11.py) | 채팅 필터 요구사항 작성 |
| [smart_fizzbuzz/main.py](smart_fizzbuzz/main.py), [테스트](smart_fizzbuzz/test_main.py) | 배수 분류, 딕셔너리 누적, 테스트 |
| [chat_filter/main.py](chat_filter/main.py), [선생님 코드](chat_filter/main_teacher.py), [테스트](chat_filter/test_main.py) | 금지어 마스킹과 겹치는 문자열 처리 |

## 조건문과 논리 연산자

`if → elif → else` 순서로 검사하고, 처음 참인 분기 하나만 실행합니다. 점수처럼 조건 범위가 겹칠 때는 검사 순서가 중요합니다.

```python
score = 85

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("F")
# B
```

| 표현 | 의미 |
|---|---|
| `a and b` | 두 조건이 모두 참인지 검사 |
| `a or b` | 하나 이상의 조건이 참인지 검사 |
| `not a` | 참과 거짓을 뒤집음 |
| `x in values` | x가 포함되어 있는지 검사 |
| `x not in values` | x가 포함되어 있지 않은지 검사 |

파이썬 코드는 소문자 `and`, `or`, `not`을 사용합니다. `and`와 `or` 자체는 평가한 피연산자 중 하나를 반환하며, 조건문에서는 그 값의 참과 거짓을 판단합니다.

```python
allowed_roles = ["admin", "manager", "staff"]
role = "admin"

if role in allowed_roles:
    print("접근 허용")
# 접근 허용
```

### 단락 평가와 None 확인

결과가 정해지면 뒤의 식을 평가하지 않습니다. `and`는 앞이 거짓이면, `or`는 앞이 참이면 멈춥니다.

```python
def expensive_check():
    print("추가 검사 실행")
    return True

is_active = False
print(is_active and expensive_check())  # False만 출력
print(is_active or expensive_check())   # 추가 검사 실행 후 True 출력
```

이 성질로 `None`의 메서드를 호출하는 오류를 피할 수 있습니다.

```python
user_profile = None

if user_profile is not None and user_profile.get("is_verified"):
    print("인증된 사용자")
else:
    print("비인증된 사용자")
# 비인증된 사용자
```

여기서는 `user_profile`이 딕셔너리 또는 `None`이라고 가정합니다. `None`이 아니라는 조건만으로 모든 객체에 `.get()`이 있다고 보장되지는 않습니다.

## 클래스와 객체

클래스는 객체의 구조와 동작을 정의합니다. 클래스를 호출해 만든 객체를 인스턴스라고 하고, 객체에 속한 함수를 메서드라고 합니다.

```python
class SafeProfile:
    def __init__(self):
        pass

    def get(self, key):
        return True

profile = SafeProfile()
print(profile.get("is_verified"))  # True
```

- `__init__`: 인스턴스를 만들 때 초기화하는 메서드입니다.
- `self`: 메서드를 호출한 인스턴스를 가리킵니다.
- `pass`: 아무 작업도 하지 않고 넘어갑니다.

원본 `SafeProfile.get()`은 `key`를 사용하지 않고 항상 `True`를 반환합니다. 딕셔너리의 `get()`처럼 실제 값을 조회하는 구현은 아닙니다. `None.get(...)`을 호출하면 `AttributeError`가 발생합니다.

## 삼항 연산자

조건에 따라 두 값 중 하나를 선택합니다. 파이썬에서는 조건 표현식이라고도 합니다.

```python
# 참일_때_값 if 조건 else 거짓일_때_값
user_score = 85
grade = "Pass" if user_score >= 80 else "Fail"
print(grade)  # Pass
```

짧은 값 선택에 적합합니다. 분기마다 여러 작업을 해야 한다면 일반 `if`문이 읽기 쉽습니다.

## 딕셔너리와 언패킹

딕셔너리는 키와 값을 짝지어 저장합니다. 리스트는 주로 인덱스로, 딕셔너리는 키로 값을 찾습니다.

```python
scores = {"kor": 80, "eng": 80, "math": 90}
print(scores["kor"])           # 80
print(scores.get("science"))   # None

for key, value in scores.items():
    print(f"{key}: {value}")
# kor: 80
# eng: 80
# math: 90
```

| 메서드 | 가져오는 내용 |
|---|---|
| `keys()` | 키들 |
| `values()` | 값들 |
| `items()` | `(키, 값)` 쌍들 |

`key, value`처럼 묶인 값을 여러 변수로 나누어 받는 것을 언패킹이라고 합니다.

```python
num1, num2 = (10, 20)
print(num1, num2)  # 10 20
```

## 반복문과 흐름 제어

`for`는 요소를 하나씩 꺼내 반복합니다. `range(1, n + 1)`은 1부터 n까지 순회합니다. 끝값은 포함하지 않습니다.

```python
for i in range(1, 6):
    if i % 2 == 0:
        continue
    print(i)
# 1, 3, 5가 각각 한 줄씩 출력
```

`%`는 나머지를 구합니다. `i % 2 == 0`이면 짝수입니다.

| 문법 | 동작 |
|---|---|
| `continue` | 현재 반복의 남은 코드를 건너뛰고 다음 반복으로 이동 |
| `break` | 가장 안쪽 반복문 종료 |
| `return` | 함수 종료 및 결과 반환 |

사용자 권한 실습에서는 정지된 사용자를 처리한 뒤 `continue`로 다음 사용자에게 넘어갑니다. `break`를 쓰면 나머지 사용자 검사까지 모두 중단됩니다.

```python
users = [
    {"username": "alpha", "is_suspended": True},
    {"username": "bravo", "is_suspended": False},
]

for user in users:
    if user["is_suspended"]:
        print(f"{user['username']}: 정지된 계정")
        continue
    print(f"{user['username']}: 검사 진행")
# alpha: 정지된 계정
# bravo: 검사 진행
```

## zip과 이터레이터

`zip()`은 여러 반복 대상의 같은 위치에 있는 요소를 튜플로 묶습니다. 기본적으로 가장 짧은 대상에 맞춰 종료합니다.

```python
letters = ["a", "b", "c"]
numbers = [100, 200, 300]

print(list(zip(letters, numbers)))
# [('a', 100), ('b', 200), ('c', 300)]

print(dict(zip(letters, numbers)))
# {'a': 100, 'b': 200, 'c': 300}
```

`zip()`의 반환값은 이터레이터입니다. 꺼낸 요소를 다시 제공하지 않으므로 한 번 끝까지 사용하면 소진됩니다.

```python
result = zip(["a", "b"], [100, 200])
print(dict(result))  # {'a': 100, 'b': 200}
print(list(result))  # []
```

원본 `day2-10.py`의 첫 `print(list(result))` 다음에 있는 `for i in result`도 같은 이유로 아무것도 출력하지 않습니다. 재사용하려면 리스트로 저장합니다.

```python
pairs = list(zip(["a", "b"], [100, 200]))
print(dict(pairs))  # {'a': 100, 'b': 200}
print(pairs)        # [('a', 100), ('b', 200)]
```

딕셔너리로 만들 때 키가 중복되면 나중 값이 남습니다.

## 리스트 컴프리헨션

반복 결과를 새 리스트로 만드는 문법입니다.

```python
numbers = [1, 2, 3, 4, 5]

# 일반 반복문
result = []
for n in numbers:
    if n % 2 == 0:
        result.append(n)

# 같은 결과를 만드는 리스트 컴프리헨션
result2 = [n for n in numbers if n % 2 == 0]
print(result2)  # [2, 4]
```

### 변환과 필터링

```python
numbers = [1, 2, 3, 4, 5]
print([n * 2 for n in numbers])           # [2, 4, 6, 8, 10]
print([n * 2 for n in numbers if n > 3])  # [8, 10]

menu = ["아메리카노", "라떼", "초코"]
print(["ice_" + name for name in menu])
# ['ice_아메리카노', 'ice_라떼', 'ice_초코']

print([len(name) for name in menu if len(name) % 2 == 0])
# [2, 2]
```

### 삼항 연산자와 함께 사용

```python
ages = [20, 15, 60]
print([age for age in ages if age >= 20])
# [20, 60]

print(["성인" if age >= 20 else "미성년" for age in ages])
# ['성인', '미성년', '성인']
```

| 형태 | 역할 | 결과의 개수 |
|---|---|---|
| `[값 for 변수 in 대상 if 조건]` | 조건에 맞는 요소만 선택 | 입력보다 적거나 같음 |
| `[A if 조건 else B for 변수 in 대상]` | 각 요소마다 A 또는 B 선택 | 입력과 같음 |

여기서 20세 기준은 실습에서 정한 분류 조건입니다.

## 리스트 순회 중 삭제 주의

원본 `day2-12.py`는 다음 문제를 보여 줍니다.

```python
items = ["정상", "불량", "불량", "정상"]
for item in items:
    if item == "불량":
        items.remove("불량")
        continue

print(items)  # ['정상', '불량', '정상']
```

첫 불량을 삭제하면 다음 불량이 앞으로 당겨집니다. 반복문은 다음 인덱스로 이동하기 때문에 당겨진 불량을 건너뜁니다. `remove()`는 일치하는 첫 요소 하나만 삭제합니다.

정상만 모아 새 리스트를 만들면 안전합니다.

```python
items = ["정상", "불량", "불량", "정상"]
items = [item for item in items if item == "정상"]
print(items)  # ['정상', '정상']
```

`item != "불량"`으로 쓰면 불량 이외의 모든 값이 남고, `item == "정상"`으로 쓰면 정상만 남습니다.

## 참과 거짓 판정과 데이터 정리

빈 문자열 `""`, 빈 리스트 `[]`, 숫자 `0`, `None`은 조건문에서 거짓으로 판단합니다. 공백 문자열 `" "`은 비어 있지 않으므로 참입니다.

```python
print(bool(""))   # False
print(bool(" "))  # True
```

금지어 목록을 정리할 때 이 성질을 활용합니다.

```python
bad_words = ["바보", "멍청이", "멍텅구리", "", "바보"]
words = sorted(set(word for word in bad_words if word), key=len, reverse=True)
print(words)  # ['멍텅구리', '멍청이', '바보']
```

1. `if word`로 빈 문자열을 제외합니다. 공백 문자열은 남습니다.
2. `set(...)`으로 중복을 제거합니다. 대소문자가 다르면 별개로 취급합니다.
3. `sorted(..., key=len, reverse=True)`로 긴 단어부터 정렬합니다.

`(word for word in bad_words if word)`는 값을 차례로 제공하는 제너레이터 표현식입니다. 대괄호를 사용한 리스트 컴프리헨션과 구분합니다. 집합은 순서를 보장하지 않으므로 길이가 같은 단어끼리의 순서는 이 코드만으로 정해지지 않습니다.

## 정규표현식과 채팅 필터

`re`는 문자열의 패턴을 검색하거나 바꾸는 모듈입니다. `join()`은 여러 문자열을 구분자로 연결합니다.

```python
import re

words = ["바보", "bad", "a.b"]
pattern = "|".join(re.escape(word) for word in words)
print(pattern)  # 바보|bad|a\.b

message = "바보! BAD a.b aXb"
masked = re.sub(
    pattern,
    lambda match: "*" * len(match.group(0)),
    message,
    flags=re.IGNORECASE,
)
print(masked)  # **! *** *** aXb
```

| 표현 | 역할 |
|---|---|
| `re.escape(word)` | `.`이나 `+` 같은 문자를 일반 문자로 검색하도록 이스케이프 |
| `"|".join(...)` | 정규표현식의 또는 연산으로 여러 패턴 연결 |
| `re.sub(pattern, replacement, text)` | 일치하는 부분을 치환한 새 문자열 반환 |
| `lambda match: ...` | 일치할 때마다 실행할 짧은 함수 |
| `match.group(0)` | 일치한 전체 문자열 |
| `"*" * len(...)` | 찾은 문자열 길이만큼 별표 생성 |
| `re.IGNORECASE` | 대소문자를 구분하지 않고 검색 |

`day2-11.py`의 마지막 `re.sub(...)`는 결과를 저장하거나 출력하지 않습니다. 문자열은 이 호출로 직접 바뀌지 않으므로, 결과를 쓰려면 `masked = re.sub(...)`처럼 받아야 합니다.

### 두 채팅 필터 구현의 차이

`chat_filter/main_teacher.py`는 빈 금지어 제외 → 중복 제거 → 긴 단어 우선 정렬 → `re.sub()` 치환 순서입니다. 금지어가 없으면 원본을 바로 반환합니다.

`chat_filter/main.py`는 원본 메시지에서 각 금지어가 차지하는 위치를 기록한 뒤, 표시된 모든 위치를 별표로 바꿉니다. 찾은 위치의 한 글자 뒤부터 다시 검색해서 겹치는 일치도 찾습니다.

| 메시지와 금지어 | 선생님 코드 결과 | main.py 결과 |
|---|---|---|
| `"BAD!"`, `["bad"]` | `"***!"` | `"***!"` |
| `"ababa"`, `["aba"]` | `"***ba"` | `"*****"` |
| `"abcde"`, `["abc", "cde"]` | `"***de"` | `"*****"` |

일반 `re.sub()`는 이미 매칭한 구간과 겹치는 일치를 다시 치환하지 않습니다. 긴 단어 우선 정렬만으로 모든 겹침을 처리할 수는 없습니다.

`main.py`의 추가 문법은 다음과 같습니다.

- `re.compile(...)`: 검색에 재사용할 패턴 객체 생성
- `pattern.search(message, start)`: 지정 위치부터 검색
- `match.start()`, `match.end()`: 일치 구간의 시작과 끝 인덱스이며 끝은 포함하지 않음
- `enumerate(message)`: 인덱스와 글자를 함께 제공
- `"".join(result)`: 글자 리스트를 하나의 문자열로 연결

## 함수와 테스트 실습

### 짝수 합과 개수

```python
def calculate_even_sum_and_count(n):
    even_sum = 0
    even_count = 0

    if n < 1:
        return {"Sum": 0, "Count": 0}

    for i in range(1, n + 1):
        if i % 2 == 0:
            even_sum += i
            even_count += 1

    return {"Sum": even_sum, "Count": even_count}

print(calculate_even_sum_and_count(10))  # {'Sum': 30, 'Count': 5}
print(calculate_even_sum_and_count(-5))  # {'Sum': 0, 'Count': 0}
```

`+=`는 기존 값에 더해 저장합니다. 함수는 `return`으로 결과를 돌려주며, `print()`처럼 화면에 출력하는 것과 다릅니다.

### Smart FizzBuzz

1부터 `limit`까지 숫자를 네 종류로 분류합니다. 여러 조건에 해당하는 15의 배수를 먼저 검사해야 합니다.

```python
def analyze_fizzbuzz(limit: int) -> dict:
    counts = {"FizzBuzz": 0, "Fizz": 0, "Buzz": 0, "Number": 0}

    for i in range(1, limit + 1):
        if i % 3 == 0 and i % 5 == 0:
            counts["FizzBuzz"] += 1
        elif i % 3 == 0:
            counts["Fizz"] += 1
        elif i % 5 == 0:
            counts["Buzz"] += 1
        else:
            counts["Number"] += 1

    return counts

print(analyze_fizzbuzz(15))
# {'FizzBuzz': 1, 'Fizz': 4, 'Buzz': 2, 'Number': 8}
```

이 예제는 원본의 `limit < 1` 조기 반환을 생략해도 빈 범위를 순회하므로 같은 결과를 냅니다. `Fizz`와 `Buzz` 개수에는 `FizzBuzz`로 분류한 숫자를 중복 집계하지 않습니다.

`limit: int`, `-> dict`는 입력과 반환값의 타입 힌트입니다. 타입 힌트가 값을 자동 변환하거나 실행 중 타입을 강제로 검사하지는 않습니다.

### assert로 예상 결과 검증

`assert`는 함수가 아니라 문장입니다. 조건이 참이면 계속 실행하고, 거짓이면 `AssertionError`를 발생시킵니다.

```python
assert 2 + 3 == 5, "덧셈 결과 오류"

# 같은 코드 블록에서 위 짝수 함수 정의 후 실행
assert calculate_even_sum_and_count(100) == {"Sum": 2550, "Count": 50}
assert calculate_even_sum_and_count(1) == {"Sum": 0, "Count": 0}
assert calculate_even_sum_and_count(-5) == {"Sum": 0, "Count": 0}
```

테스트에는 정상 입력뿐 아니라 0, 음수, 빈 문자열, 중복, 겹침 등 경계 조건도 포함합니다. FizzBuzz 테스트는 모든 분류 개수의 합이 `max(0, limit)`인지도 확인합니다. 채팅 필터 테스트는 결과 문자열, 길이, 입력 목록 보존을 확인합니다.

`python -O`로 실행하면 `assert` 검사가 생략되므로, 반드시 필요한 입력 검사는 `if`와 `raise` 등으로 작성합니다.

### 직접 실행과 입력 처리

```python
if __name__ == "__main__":
    n = int(input("정수 n을 입력하세요: "))
```

이 블록은 파일을 직접 실행할 때 동작하고 다른 파일에서 import할 때는 실행하지 않습니다. `input()`은 문자열을 반환하고, `int()`로 정수로 변환합니다. 정수가 아닌 문자열을 입력하면 `ValueError`가 발생합니다. 짝수 실습의 `json.dumps(...)`는 딕셔너리를 JSON 문자열로 변환합니다.

## 실행 경로와 검증 명령

터미널이 `AIO_4_class` 폴더에 있을 때 다음 명령을 사용합니다. 명령은 한 줄씩 실행합니다.

```bash
python day2/even_sum_and_count/main.py
python day2/smart_fizzbuzz/test_main.py
python day2/chat_filter/test_main.py
python day2/chat_filter/main_teacher.py
```

터미널이 이미 `day2` 폴더 안이라면 앞의 `day2/`를 빼야 합니다.

```bash
python even_sum_and_count/main.py
```

경로는 터미널의 현재 폴더를 기준으로 해석합니다. `..`은 상위 폴더입니다.

## 문제를 코드로 옮기는 순서

`day2-9.py`와 `even_sum_and_count/day2-11.py`의 실습에서는 코드 작성 전에 요구사항을 구체적으로 정합니다.

1. **문제**: 무엇을 계산하거나 바꿀지 설명합니다.
2. **입력**: 자료형과 예시를 정합니다.
3. **출력**: 반환 자료형, 딕셔너리 키 등을 정합니다.
4. **제약조건**: 사용할 문법, 빈 입력, 대소문자, 겹침 처리 등을 정합니다.
5. **검증**: 예상 결과가 있는 테스트를 작성하고 실행합니다.

예를 들어 “짝수 합 구해줘”를 “정수 n을 받아 1부터 n까지의 짝수 합과 개수를 `{"Sum": int, "Count": int}`로 반환하고, n이 1 미만이면 두 값 모두 0으로 반환한다”로 구체화할 수 있습니다.

## 복습 문제

1. 점수가 95, 85, 75, 60일 때 각각 어떤 학점이 출력되는지 설명해 보세요.
2. `False and expensive_check()`와 `False or expensive_check()`의 실행 차이를 설명해 보세요.
3. `zip()` 결과를 딕셔너리와 리스트로 모두 쓰려면 어떻게 저장해야 할까요?
4. `[n for n in range(1, 11) if n % 2 == 0]`의 결과를 예상해 보세요.
5. `["짝수" if n % 2 == 0 else "홀수" for n in [1, 2, 3]]`의 결과를 예상해 보세요.
6. 리스트를 순회하면서 삭제하면 왜 요소를 놓치는지 인덱스로 설명해 보세요.
7. `re.sub()`의 결과를 저장하지 않으면 원본 문자열은 어떻게 될까요?
8. `ababa`에서 `aba`를 가릴 때 두 채팅 필터의 결과가 다른 이유를 설명해 보세요.

정답 확인: 1번은 A, B, C, F / 2번은 and에서는 호출하지 않고 or에서는 호출 / 3번은 `list(zip(...))`로 저장 / 4번은 `[2, 4, 6, 8, 10]` / 5번은 `['홀수', '짝수', '홀수']` / 6번은 삭제 후 요소가 앞으로 이동하지만 반복 인덱스는 진행 / 7번은 원본 그대로 / 8번은 일반 치환은 겹치는 일치를 다시 처리하지 않고 위치 기록 방식은 겹침까지 표시하기 때문입니다.
