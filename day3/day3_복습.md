# 2026년 10월 16일 파이썬 객체지향 개념과 예제 정리

클래스와 객체의 기초부터 캡슐화, 프로퍼티, 상속, 다형성, 추상 클래스, 데이터클래스, 반복문과 전처리까지 복습합니다. 10월 16일에 질문한 프로퍼티 설명을 유지하고, 10월 18일에 day3 폴더의 내용을 반영했습니다.

공부할 때는 **객체 만들기 → 상태 변경 → 접근 규칙 → 상속과 공통 인터페이스 → 데이터 검증과 리팩토링** 순서로 읽으면 연결하기 쉽습니다.

## 파일별 학습 내용

| 파일 | 내용 |
|---|---|
| [day3-1.py](day3-1.py) | 수강생과 바리스타 객체, 디지털 지갑, 모델 설정, 상속과 다형성, 결제 추상 클래스와 영수증 |
| [day3-2.py](day3-2.py) | 수동 번호 매기기와 enumerate 비교 |
| [day3-3.py](day3-3.py) | 점수 정규화 전처리의 기존 코드와 오류 |
| [교재 PDF](kdt_python_oop_codex_curriculum.pdf) | 객체지향 수업 개념과 실습 자료 |

문서의 간소화 예제와 개선 예제는 원본 코드와 구분해 설명합니다. 서로 다른 코드 블록에서 같은 클래스 이름을 쓸 때는 해당 예제를 별도로 실행하세요.

## 클래스와 객체와 초기화

클래스는 객체의 상태와 동작을 정의하고, 인스턴스는 그 클래스로 만든 개별 객체입니다. 상태는 속성으로, 동작은 메서드로 표현합니다.

```python
class Student:
    def __init__(self, name, level=1):
        self.name = name
        self.level = level

    def study(self):
        self.level += 1
        return self.level

student1 = Student("철수")
student2 = Student("영희")
print(student1.study())  # 2
print(student2.level)    # 1: 다른 객체의 상태는 그대로
```

`Student("철수")`로 인스턴스를 만들 때 `__init__`이 초기화 메서드로 호출됩니다. 엄밀히 객체 생성 자체는 `__new__`가 담당하며, 지금은 `__init__`으로 초기 상태를 정한다고 이해하면 됩니다. 메서드는 보통 클래스 본문에 정의하고 `__init__`에서는 필요한 인스턴스 속성을 설정합니다.

- `self`: 호출 대상 인스턴스를 받습니다. 값을 받지 않는 자리가 아닙니다.
- `level=1`: 인자를 생략했을 때 사용할 기본값입니다.
- `return`: 결과를 반환하고 현재 함수 실행을 끝냅니다. 아래 코드는 실행하지 않습니다.
- `print`: 화면에 출력합니다. 값을 반환해 다른 계산에 사용하는 것과 다릅니다.
- `pass`: 아무 작업도 하지 않는 문장입니다.
- 클래스 이름의 첫 글자를 대문자로 쓰는 것은 관례이며 문법상 의무는 아닙니다.

### 수강생 성장 시뮬레이터

`KDTStudent`는 이름, 트랙, 레벨, 에너지, 완료한 미션 목록을 관리합니다.

| 호출 순서 | 에너지 | 레벨 | 미션 목록 |
|---|---|---|---|
| 생성 직후 | 100 | 1 | 빈 리스트 |
| 첫 study_coding 호출 | 75 | 2 | 첫 주제 추가 |
| 두 번째 study_coding 호출 | 50 | 3 | 두 번째 주제 추가 |
| drink_coffee 호출 | 90 | 3 | 그대로 |

에너지가 부족하면 일찍 `return`해서 상태 변경을 막습니다. `min(100, self.energy + boost)`는 두 값 중 작은 값을 골라 에너지가 100을 넘지 않게 합니다. `self.completed_missions = []`는 객체를 만들 때마다 각자의 미션 리스트를 만듭니다.

### 바리스타 로봇

`BaristaBot`은 이름, 원두량, 누적 추출 잔 수를 관리합니다. `brew_espresso(cups=1)`은 한 잔당 18g의 원두를 사용합니다.

| 로봇 | 호출 | 결과 |
|---|---|---|
| 원두 50g | 2잔 | 36g 사용, 14g 남음, 누적 2잔 |
| 위 로봇 | 다시 2잔 | 부족하므로 상태 변경 없이 반환 |
| 별도 원두 80g 로봇 | 2잔 → 1잔 → 1잔 | 44g → 26g → 8g, 누적 4잔 |

이것이 객체마다 상태를 독립적으로 관리하는 예입니다. 원본은 음수 잔 수 같은 잘못된 입력까지 검증하지 않으므로, 확장할 때는 양의 정수인지 검사하는 조건도 필요합니다.

## 변수와 속성과 메서드와 프로퍼티

| 용어 | 의미 | 예시 |
|---|---|---|
| 변수 | 객체를 가리키는 이름 | `owner = "철수"` |
| 매개변수 | 함수 호출 시 전달된 값을 받는 변수 | `def __init__(self, owner)`의 `owner` |
| 속성 | 객체에 속한 이름으로 접근하는 값이나 기능 | `wallet.owner`, `wallet.balance` |
| 메서드 | 객체와 관련된 동작을 정의한 함수 | `wallet.deposit(1000)` |
| 프로퍼티 | 속성처럼 읽거나 대입할 때 정해진 로직이 실행되도록 만든 속성 | `wallet.balance` |

프로퍼티는 속성의 한 종류입니다. `self.`가 붙었다고 모두 프로퍼티는 아닙니다. 또한 속성에는 데이터뿐 아니라 메서드 등도 포함될 수 있습니다.

### 매개변수와 일반 속성

```python
class Person:
    def __init__(self, owner):
        self.owner = owner

person = Person("철수")
print(person.owner)  # 철수
```

`self.owner = owner`의 오른쪽 `owner`는 전달받은 값을 가리키는 매개변수이고, 왼쪽 `self.owner`는 그 객체의 속성입니다. 이름이 같아도 서로 다른 역할입니다.

`self`는 해당 인스턴스를 가리키는 매개변수입니다. 일반적인 인스턴스 메서드를 `객체.메서드(...)` 형태로 호출하면 파이썬이 그 객체를 첫 인자로 전달합니다. `self`는 관례적으로 사용하는 이름입니다.

## 디지털 지갑 전체 예제

```python
class DigitalWallet:
    def __init__(self, owner: str, initial_balance: int = 0):
        self.owner = owner  # 소유자 이름을 저장하는 일반 속성
        self.__balance = 0  # 실제 잔액을 저장하는 내부 속성
        self.balance = initial_balance  # setter를 거쳐 초기 잔액 설정

    @property
    def balance(self) -> int:
        # balance를 읽을 때 실행되는 getter
        print("balance 읽기 호출")
        return self.__balance

    @balance.setter
    def balance(self, amount: int) -> None:
        # balance에 대입할 때 실행되는 setter
        print("balance 설정 호출")
        if amount < 0:
            print("잔액은 음수가 될 수 없습니다!")
            return
        self.__balance = amount

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            print("입금액은 0원보다 커야 합니다.")
            return
        self.balance += amount

wallet = DigitalWallet("철수", 1000)
# balance 설정 호출

print(wallet.balance)
# balance 읽기 호출
# 1000

wallet.balance = 2000
# balance 설정 호출

wallet.balance = -500
# balance 설정 호출
# 잔액은 음수가 될 수 없습니다!

print(wallet.balance)
# balance 읽기 호출
# 2000
```

| 이름 | 역할 |
|---|---|
| `self.owner` | 소유자 이름을 저장하는 일반 속성 |
| `self.__balance` | 실제 잔액을 저장하는 내부 속성 |
| `self.balance` | getter와 setter를 통해 잔액에 접근하는 프로퍼티 |

이 예제의 `: int`, `: str`, `-> int`, `-> None`은 타입 힌트입니다. 타입을 자동 변환하거나 실행 중에 강제로 제한하지는 않습니다. 예제의 setter는 음수 여부를 검사하며, 정수 타입을 별도로 검증하지는 않습니다.

## 메서드와 프로퍼티의 사용 차이

일반 메서드는 괄호를 붙여 호출합니다.

```python
class MethodExample:
    def get_balance(self):
        return 1000

account = MethodExample()
print(account.get_balance())  # 1000
```

프로퍼티는 괄호 없이 속성처럼 읽습니다.

```python
class PropertyExample:
    @property
    def balance(self):
        return 1000

account = PropertyExample()
print(account.balance)  # 1000
```

`@property` 자체는 메서드가 아니라 데코레이터입니다. 여기서는 아래에 정의한 메서드를 getter로 사용하는 프로퍼티를 만듭니다.

| 사용 코드 | 실행되는 동작 |
|---|---|
| `wallet.deposit(1000)` | 일반 메서드 호출 |
| `wallet.balance` | getter 실행 |
| `wallet.balance = 2000` | setter 실행 |

## balance를 따로 선언한 뒤 함수를 연결한 것일까

아닙니다. 다음 정의가 `balance`라는 프로퍼티를 만듭니다.

```python
@property
def balance(self):
    return self.__balance
```

따라서 `self.balance`는 앞에서 만든 프로퍼티를 사용하는 표현입니다. 별도의 잔액 저장 변수를 만든 다음, 같은 이름의 함수를 찾아 연결하는 구조가 아닙니다.

`@balance.setter`는 기존 `balance` 프로퍼티에 쓰기 동작을 추가합니다. 같은 이름의 두 `def balance`는 일반 메서드 두 개를 독립적으로 남기는 것이 아니라, getter와 setter를 가진 하나의 프로퍼티를 구성합니다.

프로퍼티는 클래스에 정의되므로, 파일에서 클래스 정의가 완성된 뒤 객체를 만들 때는 이미 존재합니다. 그래서 코드상 위쪽인 `__init__`에서도 `self.balance = initial_balance`로 setter를 사용할 수 있습니다.

## 왜 이름을 balance 또는 bal로 맞춰야 할까

`balance`로 정의했다면 `wallet.balance`로 접근하고, `bal`로 정의했다면 `wallet.bal`로 접근합니다. **정의한 이름으로 사용하는 것**입니다. 이름을 맞춰 의도만 알려주는 주석 같은 장치가 아닙니다.

```python
class ShortNameWallet:
    def __init__(self, initial_balance=0):
        self.__balance = 0
        self.bal = initial_balance

    @property
    def bal(self):
        return self.__balance

    @bal.setter
    def bal(self, amount):
        if amount < 0:
            return
        self.__balance = amount

wallet = ShortNameWallet(1000)
wallet.bal = 2000
print(wallet.bal)  # 2000
```

여기서는 getter 이름, `@bal.setter`, setter 이름, 사용하는 이름을 모두 `bal`로 맞춥니다. 실제 저장 속성 `__balance`는 그대로 두어도 됩니다. 저장 이름과 프로퍼티 이름은 같을 필요가 없습니다.

### 이름을 바꾸고 사용 부분을 놓쳤을 때

위 `ShortNameWallet`처럼 일반적인 인스턴스 속성 추가를 허용하는 클래스에서는 다음과 같이 됩니다.

```python
wallet = ShortNameWallet(1000)
wallet.balance = -500  # bal과 다른 이름의 일반 속성이 새로 생김

print(wallet.balance)  # -500
print(wallet.bal)      # 1000
```

`balance`와 `bal`은 별개의 이름이므로 `bal`의 setter는 실행되지 않습니다. 클래스 구조에 따라 새 속성 추가가 제한될 수도 있지만, 현재 예제는 추가를 허용합니다.

## 초기화와 입금 시 실행 순서

### 초기 잔액 설정

```python
self.__balance = 0
self.balance = initial_balance
```

1. 실제 잔액을 저장하는 내부 속성을 0으로 만듭니다.
2. `balance` 프로퍼티에 초기값을 대입합니다.
3. setter가 초기값을 검사합니다.
4. 0 이상이면 `__balance`에 저장하고, 음수라면 기존 0을 유지합니다.

### 잔액 읽기

```python
print(wallet.balance)
```

getter가 `self.__balance`를 반환하고, `print()`가 반환된 값을 출력합니다. getter 안의 `print("balance 읽기 호출")`은 동작 확인용 출력입니다. getter는 출력할 때만이 아니라 값을 읽는 다른 상황에서도 실행됩니다.

### 입금액 더하기

```python
self.balance += amount
```

이 예제의 정수 잔액에서는 다음 순서입니다.

1. getter로 현재 잔액을 읽습니다.
2. 입금액을 더합니다.
3. setter로 새 잔액을 대입합니다.

현재 잔액이 1000이고 입금액이 500이라면 setter에 1500이 전달됩니다. 이때 대입은 500으로 바꾸는 것이 아니라 기존 잔액에 500을 더하는 동작입니다.

## setter가 있으면 외부에서 잔액을 바꿀 수 있을까

**현재 코드에서는 바꿀 수 있습니다.** setter는 외부 변경을 전부 막는 것이 아니라, 허용할 변경 조건을 정합니다.

| 대입 | 현재 setter의 처리 |
|---|---|
| `wallet.balance = 3000` | 허용 |
| `wallet.balance = 0` | 허용 |
| `wallet.balance = -1000` | 거부하고 기존 잔액 유지 |

이 코드가 보장하는 것은 음수 잔액을 거부한다는 규칙입니다. 입출금 절차를 반드시 거치게 하는 설계는 아닙니다.

### 직접 대입을 막고 입금 메서드만 허용하는 예제

```python
class DepositOnlyWallet:
    def __init__(self):
        self.__balance = 0

    @property
    def balance(self):
        return self.__balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다.")
        self.__balance += amount

wallet = DepositOnlyWallet()
wallet.deposit(1000)
print(wallet.balance)  # 1000

try:
    wallet.balance = 5000
except AttributeError:
    print("setter가 없어 직접 대입할 수 없습니다.")
```

setter가 없으므로 `balance`는 읽기 전용 프로퍼티가 됩니다. 입금 메서드는 내부 저장 속성을 변경합니다. 이는 공개된 사용 방법을 제한하는 설계이며, 내부 속성에 대한 모든 접근을 막는 보안 장치는 아닙니다.

## 언더바 두 개는 완전한 접근 차단일까

`__balance`는 클래스 정의 안에서 대략 `_클래스이름__balance` 형태로 이름이 바뀝니다. 이를 이름 맹글링이라고 합니다.

예를 들어 `DigitalWallet`에서는 외부의 `wallet.__balance`로 내부 값을 바로 읽을 수 없지만, 실제 이름을 알면 `wallet._DigitalWallet__balance`로 접근할 수 있습니다.

따라서 다음처럼 이해해야 합니다.

- `__balance`: 내부 구현용 속성임을 나타내고, 상속 관계에서 이름 충돌이나 실수로 접근하는 일을 줄입니다.
- 프로퍼티: 외부에서 사용할 접근 창구와 검사 로직을 제공합니다.
- setter: 그 창구를 통해 들어온 대입에만 적용됩니다.

## 주석을 정확하게 쓰는 방법

| 헷갈리기 쉬운 설명 | 정확한 설명 |
|---|---|
| balance 변수를 선언하고 같은 이름의 함수를 연결한다 | balance 프로퍼티를 정의하고 self.balance로 사용한다 |
| @property도 메서드다 | @property는 메서드를 getter로 사용하는 프로퍼티를 만드는 데코레이터다 |
| getter는 출력할 때 호출된다 | getter는 프로퍼티를 읽을 때 호출된다 |
| __를 붙이면 외부 접근이 완전히 차단된다 | 이름 맹글링으로 직접 접근을 어렵게 한다 |
| setter가 있으므로 외부에서 값을 못 바꾼다 | setter가 허용하는 조건 안에서는 값을 바꿀 수 있다 |
| @property는 곧 @balance.getter다 | @property는 처음 프로퍼티를 만들고, @balance.getter는 이미 있는 프로퍼티의 getter를 지정한다 |

## 프로퍼티 복습 문제

1. `self.owner = owner`에서 왼쪽과 오른쪽 `owner`는 각각 무엇인가요?
2. `self.balance = 1000`은 일반 저장 속성을 새로 만드는 코드인가요?
3. `balance`를 `bal`로 바꾸면 `__balance`도 반드시 바꿔야 하나요?
4. `self.balance += 500`에서는 getter와 setter 중 무엇이 실행되나요?
5. setter가 없는 프로퍼티에 대입하면 어떻게 되나요?
6. 현재 DigitalWallet 코드에서 양수 잔액을 외부에서 직접 대입할 수 있나요?

정답:

1. 왼쪽은 객체의 일반 속성, 오른쪽은 매개변수입니다.
2. 아닙니다. balance 프로퍼티의 setter를 실행합니다.
3. 아닙니다. 프로퍼티 정의와 사용 이름은 맞추되 실제 저장 이름은 달라도 됩니다.
4. getter로 읽고 더한 다음 setter로 저장합니다.
5. 일반적으로 AttributeError가 발생합니다.
6. 가능합니다. 현재 setter는 음수만 거부합니다.

## 모델 설정과 문자열 표현

### ModelConfig로 값의 범위 제한하기

`day3-1.py`의 `ModelConfig`는 모델 이름, 학습률, 학습 횟수를 관리합니다. 지갑의 잔액 검사와 같은 원리로 학습률을 검사합니다.

| 속성 | 역할 |
|---|---|
| `model_name` | 모델 이름 |
| `__learning_rate` | 실제 학습률 저장 |
| `learning_rate` | 0보다 크고 1 이하인지 검사하는 프로퍼티 |
| `epochs` | 학습 반복 횟수 |

```python
class ModelConfig:
    def __init__(self, model_name, learning_rate, epochs):
        self.model_name = model_name
        self.__learning_rate = 0.001
        self.learning_rate = learning_rate
        self.epochs = epochs

    @property
    def learning_rate(self):
        return self.__learning_rate

    @learning_rate.setter
    def learning_rate(self, value):
        if not (0.0 < value <= 1.0):
            print("학습률 범위를 벗어나 기존 값을 유지합니다.")
            return
        self.__learning_rate = value

    def __str__(self):
        return f"{self.model_name}: lr={self.learning_rate}, epochs={self.epochs}"

cfg = ModelConfig("ResNet-50", 0.01, 30)
print(cfg)  # ResNet-50: lr=0.01, epochs=30
cfg.learning_rate = 5.0  # 경고 출력, 변경 거부
print(cfg.learning_rate)  # 0.01
```

이 예제는 출력 형식을 간소화했습니다. 초기값부터 잘못 주면 내부 기본값 `0.001`이 유지됩니다. `epochs`는 일반 속성이므로 원본에는 학습 횟수에 대한 검증이 없습니다.

### 매직 메서드와 __str__

`__init__`, `__str__`처럼 특별한 동작에 연결된 메서드를 특수 메서드 또는 매직 메서드라고 합니다.

| 메서드 | 대표 실행 시점 | 역할 |
|---|---|---|
| `__init__` | 인스턴스 초기화 | 초기 속성 설정 |
| `__str__` | `str(obj)`, `print(obj)` | 사람이 읽기 쉬운 문자열 반환 |
| `__repr__` | `repr(obj)`, 리스트 안 객체 표시 등 | 객체를 식별하기 좋은 표현 반환 |

`__str__` 안에서 직접 출력하기보다 문자열을 `return`해야 합니다. 원본 `DigitalWallet.__str__`은 소유자와 실제 잔액을 문자열로 반환합니다. `f"{value:,}"`는 숫자에 천 단위 쉼표를 붙입니다.

## 상속과 super와 오버라이딩

상속은 기존 클래스의 기능을 물려받아 확장하는 방법입니다. `class Child(Parent):` 형태로 작성합니다.

```python
class BaseAIModel:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def predict(self, input_data):
        return f"{self.name}: 기본 추론 {input_data}"

class VisionClassifier(BaseAIModel):
    def __init__(self, name, version, resolution):
        super().__init__(name, version)
        self.resolution = resolution

    def predict(self, input_data):
        return f"{self.name}: 이미지 {input_data} 분석"

class TextSummarizerLLM(BaseAIModel):
    def __init__(self, name, version, max_tokens):
        super().__init__(name, version)
        self.max_tokens = max_tokens

    def predict(self, input_data):
        return input_data[:18] + "..." if len(input_data) > 18 else input_data

model = VisionClassifier("vision", "1.0", "1024")
print(model.name)             # vision: 부모 초기화 코드에서 설정
print(model.resolution)       # 1024: 자식 초기화 코드에서 설정
print(model.predict("cat"))   # vision: 이미지 cat 분석
```

- `super().__init__(...)`: 부모 쪽 초기화 로직을 재사용합니다. 정확히는 메서드 탐색 순서의 다음 클래스를 따라갑니다.
- 오버라이딩: 부모에게 있는 메서드를 자식에서 같은 이름으로 다시 정의합니다.
- 자식이 `__init__`을 따로 정의했다면 부모의 `__init__`이 자동으로 추가 실행되는 것은 아닙니다. 필요한 경우 `super()`로 호출합니다.

위 예제는 원본의 긴 출력 문장을 줄였습니다. 원본 `TextSummarizerLLM`도 실제 AI 모델을 호출하지 않고 문자열을 18글자까지 잘라 보여 줍니다. `max_tokens`는 속성과 출력에만 쓰이며 실제 토큰 제한을 구현하지 않습니다. `VisionClassifier`의 고양이 확률도 고정된 예시 문구입니다.

## 다형성과 공통 인터페이스

다형성은 같은 방식으로 호출해도 객체 종류에 따라 다른 동작을 수행하는 성질입니다. 오버라이딩은 이를 구현하는 방법 중 하나이며, 두 용어가 같은 뜻은 아닙니다.

앞의 모델 클래스들을 정의한 뒤 다음처럼 사용할 수 있습니다.

```python
pipeline = [
    BaseAIModel("base", "1.0"),
    VisionClassifier("vision", "1.0", "1024"),
    TextSummarizerLLM("text", "1.0", 512),
]

for model in pipeline:
    print(model.predict("test"))
# base: 기본 추론 test
# vision: 이미지 test 분석
# test
```

반복문은 각각의 구현을 몰라도 `predict()`를 호출하면 됩니다. 파이썬은 상속 관계가 없어도 필요한 메서드를 제공하는 객체를 같은 방식으로 사용할 수 있습니다. 이것을 덕 타이핑이라고 합니다.

## 추상 클래스와 추상 메서드

추상 클래스는 자식이 제공해야 할 공통 기능의 틀을 정합니다. 원본에서는 결제 수단들이 모두 `process_payment()`를 제공하도록 합니다.

```python
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, buyer, amount):
        pass

class CreditCardGateway(PaymentGateway):
    def process_payment(self, buyer, amount):
        return f"{buyer}: {amount}원 카드 결제"

class BankGateway(PaymentGateway):
    pass

print(CreditCardGateway().process_payment("철수", 1000))
# 철수: 1000원 카드 결제

try:
    BankGateway()
except TypeError:
    print("추상 메서드를 구현해야 객체를 만들 수 있습니다.")
```

`ABC`를 상속하고 `@abstractmethod`로 메서드를 표시하면, 해당 추상 메서드를 구현하지 않은 클래스는 인스턴스화할 수 없습니다. `pass` 자체는 이 규칙을 만드는 기능이 아닙니다.

### 원본 후반 코드가 오류 없이 실행되는 이유

`day3-1.py` 후반에는 앞과 같은 이름을 가진 `PaymentGateway`와 `CreditCardGateway`를 다시 정의하는 실험 코드가 있습니다.

```python
from abc import abstractmethod

class PaymentGateway:  # ABC를 상속하지 않음
    @abstractmethod
    def process_payment(self, item, amount):
        pass

class BankGateway(PaymentGateway):
    pass

print(BankGateway().process_payment("식료품", 100))  # None
```

이 코드에서는 추상 메서드 구현을 강제하는 `ABCMeta`가 적용되지 않습니다. `@abstractmethod`만 붙이는 것으로 인스턴스 생성을 막지 못하므로 `BankGateway()`가 만들어집니다. 상속한 메서드의 `pass`를 실행하고, 명시적 반환값이 없어 `None`이 반환됩니다.

원본 후반의 `obj2.process_payment('b', 200)`도 자식이 구현한 메서드를 호출하므로 오류가 나지 않습니다. 옆의 오류 관련 주석만 보고 판단하지 않도록 주의하세요.

같은 이름의 클래스를 다시 정의하면 그 이름은 새 클래스에 연결됩니다. 이미 정의된 앞쪽 자식 클래스의 부모까지 바뀌는 것은 아닙니다. 또한 `__init__`을 생략하면 상속 관계에 따라 기존 `__init__`을 물려받는 것이므로, 항상 새 빈 생성자가 생긴다고 이해하면 안 됩니다.

## 데이터클래스와 결제 영수증

`@dataclass`는 주로 데이터를 담는 클래스에서 필드 정의를 바탕으로 `__init__`, `__repr__`, `__eq__` 등을 기본 설정에 따라 자동 생성합니다.

```python
from dataclasses import dataclass

@dataclass
class PaymentReceipt:
    method: str
    buyer: str
    amount: int
    fee: int
    status: str

    @property
    def net_amount(self) -> int:
        return self.amount - self.fee

receipt = PaymentReceipt("신용카드", "박파이썬", 50000, 1250, "APPROVED")
print(receipt.net_amount)  # 48750
print(receipt)
# PaymentReceipt(method='신용카드', buyer='박파이썬', amount=50000, fee=1250, status='APPROVED')
```

`net_amount`는 별도로 저장하지 않고 읽을 때 `amount - fee`를 계산하는 읽기 전용 프로퍼티입니다. 따라서 금액이나 수수료를 바꾸면 다음 조회에 반영됩니다. 데이터클래스도 타입이나 금액 범위를 자동으로 검증하지 않으며, 기본적으로 필드 변경이 가능합니다.

### 결제 실습의 연결 구조

`PaymentGateway`가 결제 메서드의 틀을 정하고, 카드·카카오페이 클래스가 각자의 수수료를 계산한 뒤 `PaymentReceipt`를 반환합니다.

| 결제 수단 | 결제 금액 | 수수료 계산 | 정산 금액 |
|---|---|---|---|
| 신용카드 | 50,000원 | `int(50000 * 0.025)` → 1,250원 | 48,750원 |
| 카카오페이 | 50,000원 | `int(50000 * 0.01)` → 500원 | 49,500원 |

`int()`는 이 계산에서 소수 부분을 버립니다. 이 예제는 결제 API에 실제 요청을 보내지 않고 영수증 객체를 만드는 연습입니다. 원본에서 결제 수단을 순회하는 코드는 주석 처리되어 있어 그대로 실행하면 영수증 출력은 나오지 않습니다.

## enumerate로 순서와 값을 함께 받기

`day3-2.py`는 직접 번호를 증가시키는 방법과 `enumerate()`를 비교합니다.

```python
names = ["홍길동", "이순신", "강감찬"]
number = 1
for name in names:
    number += 1
    print(f"{number}.{name}")
# 2.홍길동
# 3.이순신
# 4.강감찬
```

먼저 증가시킨 다음 출력하므로 2부터 시작합니다. 원본의 `id`라는 변수명은 파이썬 내장 함수 `id()`와 겹치므로 `number`나 `index` 같은 이름을 쓰면 이해하기 쉽습니다.

```python
for index, name in enumerate(names):
    print(f"{index}.{name}")
# 0.홍길동
# 1.이순신
# 2.강감찬

for number, name in enumerate(names, start=1):
    print(f"{number}.{name}")
# 1.홍길동
# 2.이순신
# 3.강감찬
```

`enumerate()`는 기본 0부터 번호와 요소를 함께 제공합니다. `start=1`은 번호만 1부터 붙이는 것이며 첫 요소를 건너뛰지 않습니다. `number, name`으로 두 값을 나누어 받는 문법은 언패킹입니다.

## 점수 정규화와 전처리 오류

정규화는 여기서 0부터 100 사이 점수를 100으로 나눠 0부터 1 사이 값으로 바꾸는 작업입니다.

### 원본 preprocess_legacy가 기대하는 입력

```python
def preprocess_legacy(data):
    res = []
    for row in data:
        score = float(row["score"])
        res.append(round(score / 100.0, 4))
    return res

print(preprocess_legacy([{"score": 50}, {"score": "80"}]))
# [0.5, 0.8]
```

| 표현 | 역할 |
|---|---|
| `for row in data` | 여러 행을 하나씩 꺼냄 |
| `row["score"]` | 행 딕셔너리에서 점수 조회 |
| `float(...)` | 실수로 변환 |
| `score / 100.0` | 점수를 100으로 나눔 |
| `round(..., 4)` | 소수점 이하 4자리 기준으로 반올림 |
| `res.append(...)` | 결과 리스트에 추가 |

`round()`가 출력 자릿수를 항상 4개로 맞추는 것은 아닙니다. 예를 들어 `0.5000` 대신 `0.5`로 표시됩니다.

### 현재 파일에서 실제 발생하는 오류

`day3-3.py`의 마지막 줄은 `preprocess_legacy(150)`입니다. 정수 150은 반복 가능한 행 목록이 아니므로 `for row in data`에서 `TypeError`가 발생합니다. 아직 정규화 계산에는 도달하지 않습니다.

```python
try:
    preprocess_legacy(150)
except TypeError:
    print("숫자 하나가 아니라 점수 딕셔너리들의 리스트가 필요합니다.")
```

| 입력 | 기존 함수 동작 |
|---|---|
| `150` | 반복 불가로 TypeError |
| `[{"score": 150}]` | 범위 검사 없이 `[1.5]` 반환 |
| `[{}]` | score 키가 없어 KeyError |
| `[{"score": "N/A"}]` | 숫자로 변환할 수 없어 ValueError |
| `[{"score": None}]` | 숫자로 변환할 수 없어 TypeError |
| `[]` | 빈 결과 리스트 반환 |

### 개선 예제

다음은 **최상위 입력은 리스트로 제한하고, 잘못된 행은 건너뛰며, 0부터 100 사이의 유한한 점수만 처리한다**는 규칙을 정한 예제입니다. 원본 파일은 수정하지 않았습니다.

```python
import math

def preprocess_scores(data):
    if not isinstance(data, list):
        raise TypeError("입력은 점수 딕셔너리들의 리스트여야 합니다.")

    result = []
    for row in data:
        if not isinstance(row, dict):
            continue

        raw_score = row.get("score")
        if isinstance(raw_score, bool):
            continue
        if not isinstance(raw_score, (int, float, str)):
            continue

        try:
            score = float(raw_score)
        except (TypeError, ValueError, OverflowError):
            continue

        if not math.isfinite(score) or not 0 <= score <= 100:
            continue

        result.append(round(score / 100.0, 4))

    return result

data = [
    {"score": 50}, {"score": "80"}, {"score": 120},
    {"score": "N/A"}, {}, {"score": None}, {"score": 0},
]
print(preprocess_scores(data))  # [0.5, 0.8, 0.0]
```

`try` 안에서 변환을 시도하고, 예상한 오류가 발생하면 `except`에서 해당 행을 건너뜁니다. `raise`는 호출자에게 잘못된 입력을 오류로 알립니다. `.get()`은 없는 키에 대해 기본적으로 `None`을 반환합니다. `math.isfinite()`는 무한대나 NaN 같은 값을 제외합니다.

잘못된 행을 건너뛰면 결과 개수가 입력보다 줄어듭니다. 원본 행과 위치를 맞춰야 하는 작업이라면 `None`을 남기거나 오류 목록을 별도로 반환하는 등 다른 정책을 정해야 합니다.

## PDF 교재 핵심 개념 요약

교재의 8차시는 **데이터와 동작을 객체로 묶고, 잘못된 입력을 검증하며, 실패 원인을 남기는 코드로 개선하는 과정**입니다. 앞에서 다룬 소스 예제와 연결해 읽으면 됩니다.

| 차시 | 핵심 개념 | 이해할 포인트 |
|---|---|---|
| 1 | 클래스와 객체 | 수강생이나 로봇마다 상태를 따로 관리하고 메서드로 바꿈 |
| 2 | 캡슐화와 프로퍼티 | 내부 데이터에 접근하는 규칙을 정함 |
| 3 | 상속과 다형성 | 공통 코드를 재사용하고 같은 메서드 이름으로 다른 동작 실행 |
| 4 | 추상 클래스와 데이터클래스 | 구현할 기능의 틀을 정하고 데이터 저장 코드를 줄임 |
| 5 | 예외처리 | 잘못된 입력 한 건을 처리하고 다음 데이터로 진행 |
| 6 | 사용자 정의 예외 | 입력 오류와 한도 초과 같은 실패 원인을 구별 |
| 7 | 주문 계산 리팩토링 | 의미 있는 이름, 검증, 데이터 구조로 코드를 명확하게 개선 |
| 8 | 전처리 리팩토링 | 점수를 검증하고 정상 결과와 제외 사유를 함께 반환 |

### 예외처리 네 단계

```python
text = "80"
try:
    score = float(text)
except ValueError:
    print("숫자로 바꿀 수 없습니다.")
else:
    print(score / 100)  # 0.8
finally:
    print("검사 종료")
```

| 문법 | 실행 시점 |
|---|---|
| `try` | 오류가 날 수 있는 작업 시도 |
| `except` | 대응하는 종류의 예외가 발생했을 때 처리 |
| `else` | try에서 예외가 발생하지 않았을 때 실행 |
| `finally` | 일반적인 예외 전파나 return 상황에서도 정리 작업 실행 |

교재의 학습 로그 파서는 한 줄마다 `try`를 사용합니다. 숫자 변환 실패는 `ValueError`, 필수 항목 누락은 `KeyError`로 구분하고, 성공한 기록만 모읍니다. 예시 4줄 중 정상 2줄을 반환합니다. `finally`는 파일 닫기 같은 정리 작업에 적합하며, 프로세스 강제 종료까지 실행을 보장하는 것은 아닙니다.

### 사용자 정의 예외와 raise

사용자 정의 예외는 서비스에서 구별해야 하는 실패에 이름을 붙인 클래스입니다.

```python
class TokenQuotaExceededError(Exception):
    pass

remaining = 20
requested = 40

try:
    if requested > remaining:
        raise TokenQuotaExceededError("요청량이 잔여 한도를 초과했습니다.")
except TokenQuotaExceededError as error:
    print(error)
```

`raise`는 예외를 발생시키고, `except`는 그 예외를 처리합니다. `as error`로 잡은 예외의 메시지나 추가 정보를 사용할 수 있습니다.

교재의 토큰 관리 예제는 빈 프롬프트를 `PromptEmptyError`, 한도 초과를 `TokenQuotaExceededError`로 나눕니다. `.strip()`은 문자열 양끝 공백을 제거하므로 공백만 있는 입력도 빈 입력으로 처리합니다. 교재의 클래스는 실제 API 호출 없이 한도를 계산하는 실습용 코드입니다.

### 주문 계산 리팩토링

리팩토링은 코드 구조를 개선하면서 기존에 의도한 동작을 유지하는 작업입니다. 검증을 추가한다면 잘못된 입력의 처리 방식이 달라지므로 그 규칙도 명시해야 합니다.

교재는 숫자 `1`, `2`, `3`으로 표현한 등급을 `BASIC`, `GOLD`, `VIP`라는 이름과 할인율 딕셔너리로 바꿉니다. 의미를 알기 어려운 숫자를 매직 넘버라고 합니다.

- `@dataclass(frozen=True)`: 생성 후 필드에 일반적인 재대입을 막습니다. 필드 안의 리스트 같은 객체까지 모두 불변으로 만드는 것은 아닙니다.
- `__post_init__`: 데이터클래스가 생성한 `__init__` 뒤에 실행되어 가격·수량 등을 검증할 수 있습니다.
- `subtotal` 프로퍼티: 단가 × 수량을 계산합니다.
- 상수 테이블: 할인율이나 쿠폰 금액을 한곳에 모읍니다. 대문자 이름은 상수로 쓰겠다는 관례입니다.
- `InvalidOrderError`: 잘못된 가격·수량·등급을 호출자에게 알립니다.

예시 계산은 **15,000원 × 2권 → GOLD 10% 할인 → 27,000원 → 쿠폰 3,000원 차감 → 24,000원**입니다. 정상 주문에서는 개선 전후 결과가 같습니다.

### 전처리 결과와 오류를 함께 반환하기

교재의 `SafeScorePreprocessor`는 검증과 변환을 나누고 `PreprocessReport`로 결과를 돌려줍니다.

| 구성 | 역할 |
|---|---|
| 검증 메서드 | score 존재 여부, 숫자 변환, 허용 범위 확인 |
| `transform()` | 각 행을 처리하고 오류 행은 제외 사유 기록 |
| `normalized_scores` | 정상 점수의 정규화 결과 |
| `skipped_rows` | 제외한 행 번호와 이유 |
| `success_rate` | 정상 건수 ÷ 전체 건수 × 100 |

정규화 일반식은 `(점수 - 최솟값) / (최댓값 - 최솟값)`입니다. 최댓값은 최솟값보다 커야 0으로 나누는 문제를 피할 수 있습니다. 교재의 5건 예제에서는 정상 점수 85와 92.5만 통과해 `[0.85, 0.925]`, 성공률 40%를 반환합니다.

`raise DataValidationError("설명") from exc`는 바깥에 이해하기 쉬운 오류를 전달하면서 원래 변환 오류도 원인으로 연결하는 **예외 체이닝**입니다.

교재 예제는 각 행이 딕셔너리라는 입력 계약을 전제로 합니다. 예외처리는 명시적으로 다루는 오류에만 적용되므로, 모든 형태의 잘못된 입력을 자동으로 해결한다고 이해하면 안 됩니다.

### 개선할 때 확인할 것

클래스로 나누는 것 자체가 목표는 아닙니다. 데이터의 담당 주체, 허용할 입력, 실패 시 처리 방법을 명확하게 만드는 것이 목표입니다. 작은 작업은 함수만으로도 충분하며, 객체가 상태를 관리하거나 여러 구현이 공통 기능을 제공할 때 클래스를 적용하면 좋습니다.

코드 개선을 요청할 때는 “클래스로 바꿔줘”에 더해 **입출력 형식, 유지할 결과, 잘못된 입력의 처리 방식, 확인할 테스트**를 적으면 결과를 검증하기 쉽습니다.

## 전체 내용 복습 문제

1. 두 Student 객체 중 하나만 공부하면 다른 객체의 level도 변할까요?
2. `__init__`과 `__str__`은 각각 언제 쓰이나요?
3. 오버라이딩과 다형성은 어떻게 다른가요?
4. `@abstractmethod`만 붙이고 ABC를 상속하지 않은 원본 실험에서 BankGateway가 생성되는 이유는 무엇인가요?
5. PaymentReceipt의 net_amount를 별도로 저장하지 않아도 되는 이유는 무엇인가요?
6. enumerate의 start=1이 첫 요소를 건너뛰는 뜻인가요?
7. preprocess_legacy(150)과 preprocess_legacy([{"score": 150}])의 동작은 어떻게 다른가요?

정답:

1. 각자의 인스턴스 속성이므로 변하지 않습니다.
2. 각각 인스턴스 초기화와 읽기 쉬운 문자열 표현에 사용합니다.
3. 오버라이딩은 자식의 메서드 재정의이고, 다형성은 같은 호출이 객체별로 다른 동작을 하는 성질입니다.
4. 해당 실험의 클래스에는 추상 메서드 구현을 강제하는 ABCMeta가 적용되지 않았기 때문입니다.
5. getter에서 amount와 fee를 사용해 매번 계산하기 때문입니다.
6. 아닙니다. 첫 요소에 붙이는 번호를 1로 정합니다.
7. 전자는 반복 불가로 TypeError이고, 후자는 범위 검사 없이 [1.5]를 반환합니다.
