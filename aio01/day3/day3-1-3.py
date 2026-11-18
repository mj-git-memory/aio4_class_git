### 캡슐화 : 데이터와 그 데이터를 다루는 로직을 묶고 접근 규칙을 정하는 것
## __balance의 이름 맹글링도 완전한 보안 차단은 아님

##### 2차시: 캡슐화(Encapsulation)와 프로퍼티(@property) — 내 지갑과 AI 가중치는 아무나 못 건드려!
### 2. 실습 예제 2-1 (기초): 음수 조작을 원천 차단하는 해킹 방지 디지털 금고
class DigitalWallet:
    def __init__(self, owner: str, initial_balance: int = 0):
        self.owner = owner  # 소유자 이름을 저장하는 일반 속성
        self.__balance = 0  # 실제 잔액을 저장하는 내부 속성. __는 이름을 바꿔 직접 접근을 어렵게 함 (완전한 접근 차단은 아님)
        self.balance = initial_balance  # balance 프로퍼티에 대입 → setter가 초기 잔액을 검사한 뒤 __balance에 저장
    
    # 클래스 안의 함수는 메서드. @property는 메서드를 프로퍼티의 getter로 만드는 데코레이터
    # balance 프로퍼티를 정의했으므로 self.balance로 사용함. 별도의 balance 저장 변수를 만드는 것은 아님
    @property
    def balance(self) -> int:
        # self.balance를 읽으면 실행되는 getter: 실제 저장 속성인 __balance의 값을 반환
        print('balance 출력 호출')
        return self.__balance

    @balance.setter  # 앞에서 정의한 balance 프로퍼티에 setter를 연결
    def balance(self, amount: int) -> None:
        # self.balance = 값 형태로 대입하면 실행됨. 음수는 거부하고 0 이상의 값은 저장
        print('balance 세팅 호출')

        if amount < 0:
            print(f"[보안 경고] 잔액은 음수가 될 수 없습니다! (입력값: {amount}원 -> 거부됨)")
            return
        self.__balance = amount

    def deposit(self, amount: int) -> str:
        if amount <= 0:
            return "[오류] 입금액은 0원보다 커야 합니다."
        
        self.balance += amount  # getter로 현재 잔액 읽기 → 입금액 더하기 → setter로 새 잔액 저장
        # -> balance 출력 호출 & balance 세팅 호출
        return f"[{self.owner}] {amount:,}원 입금 완료 (현재 잔액: {self.balance:,}원)"  # self.balance를 읽으므로 getter 실행
        # -> balance 출력 호출

    def __str__(self) :
        return f"owner : {self.owner} __balance : {self.__balance}"
    
    
wallet = DigitalWallet("이코딩", 10000) # @balance.setter의 def balance 호출
# balance 세팅 호출 
print(wallet)
# owner : 이코딩 __balance : 10000
print("1----")
print(wallet.deposit(5000))
# balance 출력 호출
# balance 세팅 호출
# balance 출력 호출
# [이코딩] 5,000원 입금 완료 (현재 잔액: 15,000원)
print("2----")
print(wallet.deposit(-5000))
# [오류] 입금액은 0원보다 커야 합니다.
print("3----")
wallet.balance = -99999  # 외부에서 불법 음수 대입 시도 -> setter가 즉시 차단!
# balance 세팅 호출
# [보안 경고] 잔액은 음수가 될 수 없습니다! (입력값: -99999원 -> 거부됨)
print("4----")
wallet.balance = 1000  # 외부에서도 balance에 대입하면 setter 실행. 0 이상의 잔액 변경은 허용됨
# balance 세팅 호출
## -> wallet.bal = 1000  # 현재 프로퍼티 이름은 balance이므로, bal에 대입하면 별도 일반 속성이 생김 (setter 실행 안 됨)
print("5----")
print(f"최종 안전 잔액: {wallet.balance:,}원")  # getter로 잔액을 읽고, :, 형식으로 천 단위 쉼표 표시
# balance 출력 호출
# 최종 안전 잔액: 1,000원
print("6----")
print(wallet)
# owner : 이코딩 __balance : 1000

## print(wallet.__balance)
## AttributeError: 'DigitalWallet' object has no attribute '__balance'. Did you mean: 'balance'?

# wallet = DigitalWallet("철수", 1000)
# 1. owner에 "철수", initial_balance에 1000이 전달됩니다.
# 2. self.__balance = 0으로 내부 잔액을 먼저 준비합니다.
# 3. self.balance = initial_balance에서 setter가 실행됩니다.
# 4. setter의 amount에 1000이 전달됩니다.
# 5. 음수가 아니므로 self.__balance = amount가 실행되어 실제 잔액이 1000이 됩니다.
# 이후 wallet.balance를 읽으면 getter가 self.__balance의 값인 1000을 반환해요.
print("--------------------------")


# 이 코드에서 가장 중요한 것은 실제 잔액은 __balance에 저장하고, balance 프로퍼티를 통해 읽기·변경 규칙을 적용한다는 점

## 1. balance와 __balance는 저장 공간 두 개가 아니에요.
# 이름	             역할
# self.owner	    소유자를 저장하는 일반 속성
# self.__balance	실제 잔액을 저장하는 내부 속성
# self.balance	    잔액을 읽거나 변경하는 프로퍼티

# wallet.balance = 1000
# -> 이 코드는 setter를 실행하고, setter 안의 다음 줄에서 실제 값을 저장
# self.__balance = amount

## 2. 읽으면 getter, 대입하면 setter가 실행
# print(wallet.balance)  # getter 실행
# wallet.balance = 1000  # setter 실행
# 객체를 초기화할 때도 같은 규칙
# -> self.balance = initial_balance  # setter 실행
# -> balance를 읽지 않고 대입만 하면 getter는 실행되지 않음 

## 3. +=는 읽기와 쓰기를 모두 수행
# self.balance += amount
# getter로 현재 잔액 읽기
# → 입금액 더하기
# → setter로 새 잔액 저장
# 반환 문자열에서도 잔액을 읽음
# -> return f"... 현재 잔액: {self.balance:,}원"
# -> 그래서 정상 입금 한 번에 getter → setter → getter 순서로 실행

## 4. 직접 대입과 입금은 다름 
# wallet.deposit(1000)  # 기존 잔액에 1000을 더함
# wallet.balance = 1000 # 기존 잔액을 1000으로 바꿈

## 5. print(wallet)은 __str__()을 사용
# def __str__(self):
#     return f"owner : {self.owner} __balance : {self.__balance}"
# -> 여기서는 __balance를 직접 읽으므로 balance의 getter는 실행되지 않음 