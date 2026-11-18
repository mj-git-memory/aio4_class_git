# Day 6 핵심 정리 — 파이썬 클래스에서 Pydantic과 API까지

학습 흐름: **클래스로 데이터 묶기 → 입력 검증 → 조건 추가 → 중첩 구조 → 출력·수정 → API 활용**

현재 `day6`의 소스 코드·주석과 수업 중 직접 질문했던 내용을 함께 정리했습니다. 개념별 설명 뒤의 **질문 복습**에서 헷갈렸던 부분을 확인하세요. 코드 조각은 앞에서 정의한 모델을 이어 사용하는 경우가 있습니다.

## 1. 클래스와 객체: 데이터를 담을 틀 만들기

| 개념 | 쉬운 의미 | 예시 |
|---|---|---|
| 라이브러리 | 재사용할 기능을 모아 제공 | 데이터 검증 라이브러리 Pydantic |
| 패키지 | 모듈을 묶어 불러오는 구조 | `pydantic` |
| 모듈 | 보통 파이썬 파일 하나 | `day6_1.py` |
| 함수 | 특정 작업을 수행하는 코드 묶음 | `main()` |
| 클래스 | 객체의 데이터와 동작을 정의하는 틀 | `Student` |
| 객체·인스턴스 | 클래스로 만든 실제 대상 | `Student("하늘", 23)` |
| 메서드 | 클래스 안에 정의한 함수 | `__init__()`, `__str__()` |

```python
class Student:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __str__(self):
        return f"이름: {self.name}, 나이: {self.age}"

student = Student("하늘", 23)
print(student.name)  # 하늘
print(student)       # 이름: 하늘, 나이: 23
```

**꼭 기억:**

- `student`는 객체를 가리키는 변수이고, 그 객체는 `Student`의 인스턴스입니다.
- `self`는 현재 다루는 객체를 받는 관례적인 매개변수 이름입니다. 파이썬이 해당 객체를 자동으로 전달합니다.
- `self.name = name`은 “전달받은 `name` 값을 이번 객체의 `name` 속성에 저장”한다는 뜻입니다.
- 객체 생성은 `__new__()`, 생성된 객체의 초기값 설정은 `__init__()`이 담당합니다. 보통 `__init__()`만 직접 작성합니다.
- `__init__()`은 `None` 이외의 값을 반환하면 안 됩니다. `__str__()`은 `print(객체)` 등에 사용할 문자열을 반환합니다.
- 일반 클래스의 `age: int` 표시는 그 자체로 실행 중 타입을 검증하지 않습니다.

### 질문 복습: 객체와 인스턴스는 다른가요?

같은 대상을 다른 관점에서 부를 수 있습니다. “객체”는 실제 대상을, “Student의 인스턴스”는 그 대상과 클래스의 관계를 나타냅니다. `student` 자체는 객체를 가리키는 변수 이름입니다.

### 질문 복습: self에는 무엇이 전달되나요?

`self`에는 **지금 초기화하거나 메서드를 실행할 객체 자체**가 전달됩니다. 이름이나 나이가 전달되는 자리가 아닙니다.

```python
student1 = Student("하늘", 23)
student2 = Student("바다", 30)
```

첫 호출의 `self`는 나중에 `student1`이 가리킬 객체, 두 번째 호출의 `self`는 `student2`가 가리킬 객체입니다.

```text
student1 → [name: "하늘", age: 23]
student2 → [name: "바다", age: 30]
```

`self.name = name`에서 왼쪽은 **저장할 대상의 속성**, 오른쪽은 **전달받은 매개변수 값**입니다. 이름을 다르게 써도 됩니다.

```python
def __init__(self, input_name, input_age):
    self.name = input_name
    self.age = input_age
```

`self`는 예약어가 아닌 관례입니다. 다른 이름도 가능하지만, 첫 매개변수와 사용하는 이름을 함께 바꿔야 합니다. 보통은 `self`를 그대로 씁니다. `self.name`과 오타인 `self.nmae`는 서로 다른 속성입니다.

### 질문 복습: 객체를 만들 때 초기화한다면서 왜 “이미 만든 객체”인가요?

`Student("하늘", 23)`이라는 한 번의 호출 안에서 **객체 생성 → 초기화**가 차례로 일어나기 때문입니다.

```text
__new__()로 객체 생성
→ 생성된 객체를 self로 받아 __init__() 실행
→ 초기화가 끝난 객체를 변수에 대입
```

- 클래스 정의 시에는 초기화 방법을 정합니다. `__init__()` 본문이 실행되는 시점은 인스턴스를 만들 때입니다.
- 초기화는 사용할 값을 처음 설정하는 일이며, 값을 무조건 0으로 만든다는 뜻이 아닙니다.
- `__new__()`는 생성 메서드, `__init__()`은 초기화 메서드입니다. 입문 자료에서는 `__init__()`을 생성자라고도 부릅니다.
- `__init__(self, name, age)`라면 `Student()`는 인자가 부족해 오류입니다. `self`만 자동 전달되고, 이름과 나이는 직접 전달해야 합니다.

### 질문 복습: __init__에서 문자열을 반환하면 왜 오류인가요?

`__init__()`은 초기화만 담당하므로 `None` 이외의 값을 반환할 수 없습니다. 출력용 문자열은 `__str__()`에서 반환하세요.

```python
def __str__(self):
    return f"이름: {self.name}, 나이: {self.age}"
```

`print(student)`나 `str(student)`가 이 문자열 표현을 사용합니다. 객체 자체가 문자열로 바뀌지는 않습니다. `__str__()` 안에서 `print()`만 하고 문자열을 반환하지 않으면 안 됩니다.

### 질문 복습: Pydantic과 pydantic은 왜 다르게 쓰나요?

`Pydantic`은 프로젝트·라이브러리를 부르는 이름이고, `pydantic`은 import에 사용하는 패키지 이름입니다. 대문자는 라이브러리, 소문자는 패키지라는 일반 규칙은 아닙니다.

```python
from pydantic import BaseModel, ValidationError
# pydantic 패키지에서 두 클래스를 가져오기
```

## 2. 상속: 기존 기능을 물려받기

문법은 `class 자식(부모):`입니다. 공통 기능을 재사용하고 필요한 기능을 추가하거나 바꿀 때 사용합니다.

```python
class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    def __init__(self, name, student_id):
        super().__init__(name)       # 부모의 초기화 작업 실행
        self.student_id = student_id
```

**꼭 기억:** 자식이 `__init__()`을 새로 정의하면 부모의 초기화는 자동 실행되지 않습니다. 부모의 작업도 필요하면 `super().__init__(...)`으로 호출합니다. 부모 객체를 따로 만드는 것이 아니라 같은 객체를 초기화합니다.

### 질문 복습: 상속하면 name도 사용할 수 있나요?

자식이 부모의 `__init__()`을 그대로 물려받거나 호출하면, 그 초기화 코드가 실행되면서 `self.name`이 설정됩니다. 부모의 일반 메서드도 물려받습니다. 부모 메서드를 자식에서 다시 정의해 동작을 바꾸는 것은 **오버라이딩**입니다.

| 문법 | 의미 |
|---|---|
| `def __init__(self, ...):` | 초기화 방법 정의 |
| `super().__init__(...)` | 부모 쪽 초기화 메서드 호출 |
| `super().메서드(...)` | 부모 쪽의 다른 메서드 호출 |

`class Student(Person):`은 직접 부모가 하나인 **단일 상속**입니다. `class Student(Person, Learner):`처럼 여러 부모를 적는 **다중 상속**도 있습니다. 정확히는 `super()`가 메서드 탐색 순서에서 다음 클래스의 기능을 찾습니다.

## 3. BaseModel: 데이터 규칙을 선언하고 검증하기

Pydantic의 `BaseModel`을 상속하면 검증·변환과 데이터 출력 기능을 사용할 수 있습니다.

```python
from pydantic import BaseModel

class Member(BaseModel):
    username: str                  # 필수
    age: int                       # 필수
    active: bool = True            # 생략하면 True
    nickname: str | None = None    # 생략 가능, None도 허용

member = Member(username="kim", age="34")
print(member.age)       # 34
print(type(member.age)) # <class 'int'>
```

**꼭 기억:**

- 기본 설정에서 정수로 변환 가능한 문자열 `"34"`는 `34`가 됩니다. `"스무살"`은 변환할 수 없어 오류가 납니다.
- **생략 가능 여부는 기본값**, **`None` 허용 여부는 타입**으로 정합니다.
- `nickname: str | None`만 쓰면 `None`은 허용하지만 입력 자체는 필수입니다. `= None`까지 있어야 생략할 수 있습니다.
- `str | None`은 `Optional[str]`, `int | str`은 `Union[int, str]`과 같은 의미입니다.
- `params = {"username": "kim", "age": 34}`일 때 `Member(**params)`는 키와 값을 이름 있는 인자로 펼칩니다.

### 입력과 출력을 구분하기

| 코드 | 역할 |
|---|---|
| `Member(username="kim", age=34)` | 값을 직접 지정해 검증하고 모델 생성 |
| `Member.model_validate(data)` | 기존 딕셔너리 등을 받아 검증하고 모델 반환 |
| `member.model_dump()` | 모델 데이터를 딕셔너리로 반환 |
| `member.model_dump_json()` | 모델 데이터를 JSON 문자열로 반환 |

```python
member = Member.model_validate({"username": "kim", "age": "34"})
data = member.model_dump()
# {'username': 'kim', 'age': 34, 'active': True, 'nickname': None}
```

`model_dump()`는 원본 입력이 아니라 **검증·변환과 기본값 적용을 마친 모델의 데이터**를 반환합니다. 기존 모델 객체가 딕셔너리로 바뀌는 것은 아닙니다.

기존 `Member` 객체도 `model_validate()`에 전달할 수 있지만, 현재 기본 설정에서는 필드를 재검증하지 않고 같은 객체를 반환합니다. 복사 용도가 아닙니다.

### 질문 복습: model_validate()에는 딕셔너리만 넣나요?

아닙니다. 기존 모델 객체나, 설정을 지정한 일반 객체도 받을 수 있습니다.

```python
Member.model_validate(member)  # 기존 Member 객체

class User:
    def __init__(self):
        self.username = "kim"
        self.age = "34"

parsed = Member.model_validate(User(), from_attributes=True)
# User 객체의 username, age 속성을 읽어 검증
```

`["kim", 34]` 같은 일반 리스트는 이 모델의 필드 이름과 대응되지 않아 오류입니다. JSON 문자열을 입력할 때는 `Member.model_validate_json(...)`을 사용합니다.

`model_dump(include={"username"})`은 지정 필드만, `model_dump(exclude={"age"})`는 지정 필드를 제외하고 반환합니다.

## 4. ValidationError: 잘못된 입력 처리하기

```python
from pydantic import ValidationError

try:
    member = Member.model_validate({"username": "kim"})  # age 누락
    print("성공")  # 오류가 발생하면 이 줄은 건너뜀
except ValidationError as error:
    for detail in error.errors():
        print(detail["loc"], detail["type"])
        # ('age',) missing

print("계속 실행")
```

- `try`: 오류가 발생할 수 있는 코드 실행.
- `except ValidationError as error`: 검증 오류를 잡아 `error`라는 이름으로 처리.
- `error.errors()`: 오류 정보 딕셔너리들의 리스트.
- `[0]`: 첫 번째 오류 선택. `loc`: 오류 위치, `type`: 오류 종류, `msg`: 설명.

**꼭 기억:** 오류를 처리해도 데이터가 자동으로 수정되지는 않습니다. 오류가 발생한 뒤 `try`의 나머지 줄은 실행하지 않으며, 실패한 생성 결과는 변수에 대입되지 않습니다. `except` 안에서 새로 발생한 오류도 자동으로 다시 잡아 주지 않습니다.

### 질문 복습: errors()[0]['loc']와 ['type']은 무엇인가요?

`age`가 누락되었을 때 오류 정보의 핵심 구조는 다음과 같습니다.

```python
# error.errors()의 결과 중 주요 항목만 표시
[
    {
        "loc": ("age",),
        "type": "missing",
        "msg": "Field required",
        "input": {"username": "kim"},
    }
]
```

`error.errors()[0]`으로 첫 딕셔너리를 고르고, `["loc"]` 또는 `["type"]`으로 해당 값을 꺼냅니다. `('age',)`는 항목 하나가 든 튜플입니다.

| 오류 종류 | 뜻 |
|---|---|
| `missing` | 필수 값 누락 |
| `int_parsing` | 문자열을 정수로 변환하지 못함 |
| `string_pattern_mismatch` | 지정한 문자열 패턴과 불일치 |
| `value_error` | 직접 작성한 검증 등에서 값 거부 |

### 질문 복습: except 안에 넣었는데 왜 또 오류가 나나요?

```python
try:
    Member(username="kim")  # 이 오류는 아래 except가 처리
except ValidationError as error:
    print(error)
    Member.model_validate({"username": "kim"})  # 새로운 오류! 처리되지 않음
```

`except`는 앞의 `try`에서 넘어온 오류를 처리할 뿐입니다. 새 검증도 `age`가 없으면 실패합니다. 정상 데이터를 만들려면 `age`를 추가하고, 두 실패를 비교하려면 별도의 `try/except`로 각각 감싸세요.

`user3 = Member(...)`의 오른쪽에서 검증이 실패하면 `user3` 대입은 완료되지 않습니다. 이전에 정의하지 않았다면 이후 사용할 수 없고, 이전 값이 있었다면 그 값이 남습니다.

## 5. Field와 ConfigDict: 입력 조건 구체화하기

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Product(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=2, max_length=60)
    price: int = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    sku: str = Field(pattern=r"^SKU-[0-9]{4}$")
```

| 설정·타입 | 의미 | 예시 |
|---|---|---|
| `gt=0` / `ge=0` | 0 초과 / 0 이상 | 가격 0은 실패, 재고 0은 성공 |
| `lt=100` / `le=100` | 100 미만 / 100 이하 | 경계 포함 여부 구분 |
| `min_length`, `max_length` | 문자열 길이·리스트 항목 수 제한 | 제목 최소 2자 |
| `default=0` | 생략할 때 사용할 값 | 재고 생략 → 0 |
| `pattern` | 정규표현식으로 형태 제한 | `SKU-0001` 성공, `SKU-001` 실패 |
| `strict=True` | 타입 자동 변환 제한 | `int` 필드에서 `"20"` 거부 |
| `description` | 문서용 설명 | 실명 여부를 실제로 검사하지는 않음 |
| `EmailStr` | 이메일 형식 검증 | `sky@example.com` |
| `Literal["basic", "premium"]` | 지정된 값 중 하나만 허용 | `"vip"` 거부 |

`str_strip_whitespace=True`는 문자열 앞뒤 공백을 제거합니다. `extra="forbid"`는 선언하지 않은 추가 항목을 거부합니다.

**꼭 기억:** `Field(...)`는 조건을 지정하는 것이며, 기본값은 `default=...` 등으로 따로 지정합니다. `bool = Field(strict=True)`는 `True`와 `False` 모두 허용합니다. “반드시 동의”가 필요하면 `Literal[True]`처럼 별도 규칙이 필요합니다.

### 질문 복습: stock의 조건과 기본값은 함께 어떻게 쓰나요?

```python
stock: int = Field(default=0, ge=0)
# 생략 → 0, stock=20 → 성공, stock=-1 → 오류
```

`stock: int = Field(ge=0) = 20`은 잘못된 문법입니다. 기본값을 `Field()` 안에 넣으세요.

`EmailStr`은 이메일 형식을 검사하지만 실제 메일함 소유 여부는 확인하지 않습니다. `description="실명 기록해라"`도 실명 검증 기능은 아닙니다. 패턴 `^STU-[0-9]{4}$`은 시작부터 끝까지 `STU-`와 숫자 4자리인지 검사합니다. 문자열 앞의 `r`은 역슬래시를 그대로 다루는 표기입니다.

### 질문 복습: field_validator와 classmethod는 왜 쓰나요?

과거 `day6_5.py`에서 질문했던 내용입니다. 기본 타입·길이 검사 외에 **직접 만든 검사나 변환 규칙**을 적용할 때 사용합니다.

```python
from pydantic import BaseModel, field_validator, model_validator

class Signup(BaseModel):
    username: str
    password: str
    password_confirm: str
    tags: list[str]

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        text = value.strip().lower()
        if " " in text:
            raise ValueError("아이디 내부에 공백을 넣을 수 없습니다")
        return text

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def verify_password(self) -> "Signup":
        if self.password != self.password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return self
```

- `@field_validator("username")`: 바로 아래 메서드를 해당 필드의 검증기로 등록합니다. 메서드 이름은 직접 정할 수 있습니다.
- 기본 `mode="after"`: 타입 검증 후 실행합니다. 검사 성공 시 사용할 값을 반환합니다.
- `mode="before"`: 타입 검증 전에 실행합니다. `"python, api"`를 리스트로 먼저 바꿔야 `list[str]` 검증을 통과합니다.
- `@model_validator(mode="after")`: 객체 생성 과정에서 필드 검증 후 여러 필드의 관계를 검사합니다. 예: 비밀번호 일치, 시작일 ≤ 종료일. 성공 시 `self`를 반환합니다.
- `@classmethod`: 첫 인자로 객체가 아닌 클래스를 자동으로 받습니다. “클래스에서만 호출 가능”이라는 뜻은 아닙니다.

| 이름 | 무엇을 받나? | 예약어인가? |
|---|---|---|
| `self` | 현재 객체 | 아니요. 관례적인 이름 |
| `cls` | 현재 클래스 | 아니요. 관례적인 이름 |
| `class` | 클래스 정의에 쓰는 문법 | 예. 매개변수 이름으로 사용 불가 |

`def show_class(my_class):`는 가능하지만 보통 `cls`를 씁니다. `def show_class(class):`는 문법 오류입니다.

**실제 오류 복습:** `@classmethod`를 두 번 붙이면 `'classmethod' object is not callable` 오류가 날 수 있습니다. 한 번만 붙이고, 태그 전처리는 `@field_validator("tags", mode="before")`로 연결하세요. `"username"`에 연결하면 잘못된 필드를 처리하게 됩니다.

## 6. 중첩 모델과 Enum: 복잡한 데이터를 구조화하기

딕셔너리 안의 딕셔너리, 리스트 안의 항목도 모델로 검증할 수 있습니다.

```python
from pydantic import BaseModel, Field

class Learner(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)

class Course(BaseModel):
    title: str
    learners: list[Learner] = Field(min_length=1)

course = Course.model_validate({
    "title": "Pydantic 기초",
    "learners": [{"name": "하늘", "score": 92}],
})
print(course.learners[0].name)  # 하늘
```

점수가 120이면 오류 위치는 `('learners', 0, 'score')`입니다. **수강생 목록의 첫 번째 항목에 있는 점수**라는 뜻입니다.

Enum은 배송 방식처럼 정해진 선택지를 이름으로 관리할 때 사용합니다.

```python
from enum import Enum

class DeliveryMethod(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"

DeliveryMethod.STANDARD       # 항목 직접 접근
DeliveryMethod["STANDARD"]   # 이름으로 찾기: 대괄호
DeliveryMethod("standard")   # 값으로 찾기: 소괄호
```

**꼭 기억:** `.name`은 `"STANDARD"`, `.value`는 `"standard"`입니다. 이름과 값을 혼동하지 마세요.

**질문했던 오류:** `DeliveryMethod("STANDARD")`는 이름이 아니라 **값** `"STANDARD"`를 찾으므로 위 정의에서는 `ValueError`입니다. 예전에 `STANDARD = "a"`였을 때는 `DeliveryMethod("a")`가 맞고, 현재 정의에서는 `DeliveryMethod("standard")`가 맞습니다.

주문 예제의 `@property`는 합계처럼 계산한 값을 `order.total` 형태로 읽게 합니다. `order.total()`처럼 호출하지 않습니다. 일반 `@property`는 자동으로 `model_dump()` 결과에 포함되지는 않습니다.

## 7. 직렬화와 PATCH: 필요한 값만 꺼내 안전하게 수정하기

직렬화는 모델 데이터를 전달·저장하기 좋은 형태로 바꾸는 작업입니다.

- `model_dump()`: 딕셔너리 반환. 날짜는 기본적으로 `date` 객체로 남을 수 있습니다.
- `model_dump(mode="json")`: 날짜 등을 JSON에 맞는 값으로 바꾼 딕셔너리 반환.
- `model_dump_json()`: JSON 문자열 반환.

부분 수정에서는 **입력하지 않은 항목**과 **명시적으로 `None`을 입력한 항목**을 구분해야 합니다.

```python
class ProfilePatch(BaseModel):
    bio: str | None = None

ProfilePatch().model_dump(exclude_unset=True)         # {}
ProfilePatch(bio=None).model_dump(exclude_unset=True) # {'bio': None}
```

`exclude_unset=True`는 **입력하지 않은 항목을 제외**합니다. `exclude_none=True`는 **값이 None인 항목을 제외**하므로 의미가 다릅니다.

수정 순서는 **기존 데이터 + 실제 입력한 변경값 병합 → 원래 모델로 재검증 → 저장**입니다.

```python
changes = patch.model_dump(exclude_unset=True)
merged = {**stored.model_dump(), **changes}  # 같은 키는 뒤쪽 변경값이 우선
updated = Profile.model_validate(merged)
```

**꼭 기억:** 수정용 모델에서 `None`을 허용해도 최종 모델의 규칙을 위반할 수 있습니다. 병합 후 재검증해야 합니다. 폴더의 Task 예제는 제목·완료 여부의 `null`을 거부하고, Profile 예제의 `bio=None`은 소개 글을 지우는 값으로 허용합니다.

## 8. FastAPI: 검증한 데이터를 API에서 사용하기

`ch07_fastapi/app.py`는 작업 데이터를 파이썬 딕셔너리에 저장하는 CRUD 예제입니다.

| 모델 | 용도 |
|---|---|
| `TaskIn` | 새로 생성하거나 전체 교체할 입력 데이터 |
| `TaskPatch` | 일부 항목만 수정할 입력 데이터 |
| `TaskOut(TaskIn)` | 입력 필드에 서버가 만든 `id`를 추가한 응답 데이터 |

```python
@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskIn) -> TaskOut:
    ...
```

`payload: TaskIn`으로 요청 본문을 검증하고, `response_model=TaskOut`으로 응답의 구조를 정합니다.

| HTTP 메서드 | 역할 | 예제 경로 |
|---|---|---|
| POST | 생성 | `/tasks` |
| GET | 목록·개별 조회 | `/tasks`, `/tasks/1` |
| PUT | 전체 교체 | `/tasks/1` |
| PATCH | 일부 수정 | `/tasks/1` |
| DELETE | 삭제 | `/tasks/1` |

응답 상태는 **201 생성 성공, 204 본문 없는 성공, 404 대상 없음, 422 입력 검증 실패**를 기억하세요. 예제의 `_db`는 실제 데이터베이스가 아니므로 서버를 재시작하면 변경 데이터가 유지되지 않습니다.

프로젝트 최상위 `AIO_4_class`에서 실행:

```bash
uvicorn day6.ch07_fastapi.app:app --reload
```

형식은 `모듈경로:객체이름`이고 `.py`는 붙이지 않습니다. 실행 후 `http://127.0.0.1:8000/docs` 또는 `ch07_fastapi/requests.http`로 요청을 확인합니다.

## 9. 파일 실행과 import 구분하기

```python
def main() -> None:
    print("실습 실행")

if __name__ == "__main__":
    main()
```

- 파일 직접 실행: 그 파일의 `__name__`은 `"__main__"` → 조건문 안 실행.
- import로 불러오기: `__name__`은 모듈 이름 → 조건문 안 실행하지 않음.
- 조건문 밖의 코드는 처음 import할 때도 실행됩니다.
- 함수 이름 `main`은 관례입니다. 함수 이름을 바꿔도 비교 문자열 `"__main__"`은 그대로 둡니다.

프로젝트 전체 경로로 import한 `ch02_basemodel/main.py`는 최상위에서 다음처럼 실행할 수 있습니다.

```bash
python -m day6.ch02_basemodel.main
```

### 질문 복습: main2로 바꾸면 '__main2__'로 바꾸나요?

아니요. `"__main__"`은 파이썬이 직접 실행한 모듈에 지정하는 값이고, 함수 이름과 관계없습니다.

```python
def main2():
    print("실행")

if __name__ == "__main__":
    main2()
```

`main`만 정의하고 `main2()`를 호출하면 이름을 찾지 못해 오류가 납니다. 함수를 정의하는 것과 호출하는 것을 구분하세요.

### 질문 복습: import하면 함수는 아예 사용할 수 없나요?

아닙니다. 조건문 안의 자동 호출만 생략됩니다. 아래는 일반 함수를 정의한 `demo.py`를 다른 파일에서 사용하는 예입니다.

```python
import demo
demo.main()  # 직접 호출하면 실행
```

`demo.py` 안의 `__name__`은 이때 `"demo"`입니다. 패키지 경로로 import하면 `"day6.ch02_basemodel.day6_2"`처럼 전체 모듈 이름이 됩니다.

### 질문 복습: No module named 'day6'는 왜 나나요?

`python day6/ch02_basemodel/main.py`로 직접 실행하면 기본적으로 그 파일의 폴더가 검색 경로 맨 앞에 들어갑니다. 최상위의 `day6`를 찾지 못한다면 프로젝트 최상위에서 `python -m day6.ch02_basemodel.main`으로 실행하세요. 같은 폴더의 파일을 직접 실행하는 방식에서는 `import day6_2`처럼 가져올 수도 있습니다. 실행 방식과 import 경로를 함께 맞춰야 합니다.

### 질문 복습: Uvicorn의 <module>:<attribute> 오류는 무엇인가요?

`uvicorn ...app.py` 대신 `uvicorn day6.ch07_fastapi.app:app --reload`로 실행합니다. `:` 앞은 모듈, 뒤는 `app = FastAPI(...)`의 객체 이름입니다. 파일명이 바뀌면 모듈 경로도 함께 바꿉니다.

### 이어지는 학습: 비동기 main은 어떻게 실행하나요?

`day7/demo.py`에서 질문했던 내용입니다. `main`이 `async def`라면 일반 스크립트에서 다음처럼 실행합니다.

```python
import asyncio

async def main():
    print("비동기 함수 실행")

if __name__ == "__main__":
    asyncio.run(main())
```

`if`의 역할은 같습니다. 비동기 함수는 `main()`만 호출하면 본문 실행 대신 코루틴 객체를 반환하므로, 실행은 `asyncio.run()` 등에 맡깁니다.

## 부록: VS Code 자동 추천에 관해 질문한 내용

학습 개념과는 별도로, 편집기 기능은 다음처럼 구분합니다.

- **추천 목록:** 변수·함수 이름 등을 보여 주는 IntelliSense. 설정의 `Quick Suggestions`로 자동 표시를 조절하고 `Control + Space`로 직접 요청할 수 있습니다.
- **회색 글씨 제안:** inline suggestion. `Inline Suggest: Enabled` 및 사용 중인 확장의 설정으로 조절합니다.
- **Copilot의 Inline suggestions 100% used:** 해당 사용 한도 소진을 나타내는 표시이며, 기본 IntelliSense까지 막혔다는 뜻은 아닙니다. 구체적인 한도·초기화 날짜는 계정의 현재 사용량 화면에서 확인합니다.

## 마지막 복습: 이 흐름을 기억하기

**외부 입력 → Pydantic 모델로 검증·변환 → 객체의 속성으로 사용 → `model_dump()`로 출력·전달**

1. 타입 표시만 있는 일반 클래스와 실제 검증을 제공하는 `BaseModel`을 구분한다.
2. 필수·기본값·`None` 허용을 구분한다.
3. `model_validate()`는 입력 검증, `model_dump()`는 모델 데이터 출력이다.
4. 오류가 나면 `errors()`의 `loc`와 `type`부터 읽는다.
5. PATCH는 입력한 항목만 병합하고 최종 모델로 다시 검증한다.

복습 파일 순서: `ch02_basemodel/day6_1.py`, `day6_2.py` → `ch03_field/demo.py` → `ch05_nested/demo.py` → `ch06_serialization/demo.py`, `solution.py` → `ch07_fastapi/app.py`, `requests.http`.
