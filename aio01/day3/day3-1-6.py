##### 4차시: 추상 클래스(ABC)와 데이터클래스(@dataclass) — 현대적 파이썬 OOP 끝판왕
### 2. 실습 예제 4-1: 다중 결제 게이트웨이 및 자동 정산 영수증 시스템

# 이 코드는 결제 방식마다 수수료 계산은 다르게 하되, 호출 방법과 영수증 형식은 통일하는 구조
# 결제 객체의 process_payment() 호출
# → 해당 결제 방식의 수수료 계산
# → PaymentReceipt 영수증 객체 반환
# → 영수증에서 정산 금액 조회

# 추상 클래스는 공통 기능의 틀, 
# 자식 클래스는 구체적인 구현, 
# 데이터클래스는 결과 데이터, 
# 프로퍼티는 계산된 값의 조회를 담당

from abc import ABC, abstractmethod
from dataclasses import dataclass

## 1. @dataclass는 데이터를 담는 클래스를 간단하게 만들어 줌
@dataclass
# @dataclass가 필드를 바탕으로 초기화 메서드 __init__ 등을 자동 생성
class PaymentReceipt: # PaymentReceipt는 영수증 정보를 담는 클래스 -> 문자열이 아니라 객체를 반환
    method: str
    buyer: str
    amount: int
    fee: int
    status: str
    ## 2. net_amount는 읽을 때 계산하는 프로퍼티 -> 정산 금액을 따로 저장하지 않고, 조회할 때 계산
    @property
    def net_amount(self) -> int:
        return self.amount - self.fee # amount나 fee가 바뀌면 다음 조회에 바뀐 계산 결과가 나옴

class PaymentGateway(ABC): # 추상 클래스 기능을 사용하는 부모 클래스
    ## 3. 추상 클래스는 자식이 구현해야 하는 기능의 틀을 정함 
    @abstractmethod  # def process_payment()를 자식에서 구현해야 할 메서드로 지정
    def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
        # buyer: str -> 구매자는 문자열이라는 타입 힌트 
        # amount: int -> 금액은 정수라는 타입 힌트
        # -> PaymentReceipt : 영수증 객체를 반환한다는 타입 힌트
        """모든 결제 수단 클래스가 반드시 구현해야 하는 추상 메서드"""
        pass # 실행 내용을 작성하지 않음
## 4. 자식 클래스는 실제 결제 로직을 구현
class CreditCardGateway(PaymentGateway):
    def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
        fee = int(amount * 0.025)
        return PaymentReceipt("신용카드", buyer, amount, fee, "APPROVED")
## 4. 자식 클래스는 실제 결제 로직을 구현
class KakaoPayGateway(PaymentGateway):
    def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
        fee = int(amount * 0.01)
        return PaymentReceipt("카카오페이", buyer, amount, fee, "APPROVED")

## 5. 반복문은 다형성을 활용
gateways: list[PaymentGateway] = [CreditCardGateway(), KakaoPayGateway()]
for gw in gateways:
    receipt = gw.process_payment("박파이썬", 50000)
    print(f"{receipt} | 정산 금액: {receipt.net_amount:,}원") 
    # -> {receipt.net_amount:,} : 프로퍼티로 정산 금액을 계산해 읽고, 천 단위 쉼표를 붙여 표시
    print('---')

# 실행 결과:
# PaymentReceipt(method='신용카드', buyer='박파이썬', amount=50000, fee=1250, status='APPROVED') | 정산 금액: 48,750원
# ---
# PaymentReceipt(method='카카오페이', buyer='박파이썬', amount=50000, fee=500, status='APPROVED') | 정산 금액: 49,500원
# ---
print("--------------------------")

## 1. @dataclass는 데이터를 담는 클래스를 간단하게 만들어 줌
# @dataclass
# class PaymentReceipt:
#     method: str
#     buyer: str
#     amount: int
#     fee: int
#     status: str
# 필드	         의미	        예시
# method	    결제 방식	    "신용카드"
# buyer	        구매자	        "박파이썬"
# amount	    결제 금액	    50000
# fee	        수수료	        1250
# status	    처리 상태	    "APPROVED"
# @dataclass가 필드를 바탕으로 초기화 메서드 __init__ 등을 자동 생성하므로, 직접 작성하지 않아도 다음처럼 객체를 만들 수 있음 
receipt = PaymentReceipt("신용카드", "박파이썬", 50000, 1250, "APPROVED")
print(receipt.buyer)   # 박파이썬
print(receipt.amount)  # 50000
# 또한 객체 내용을 보여 주는 __repr__도 자동 생성
# -> 그래서 print(receipt)에 필드와 값이 표시
print(receipt)
print('1---')

## 2. net_amount는 읽을 때 계산하는 프로퍼티
# @property
# def net_amount(self) -> int:
#     return self.amount - self.fee
# -> 정산 금액을 따로 저장하지 않고, 조회할 때 계산
print(receipt.net_amount)  # 50000 - 1250 → 48750
print('2---')

## 3. 추상 클래스는 자식이 구현해야 하는 기능의 틀을 정함 
# from abc import ABC, abstractmethod
# -> from abc import ABC, abstractmethod
# class PaymentGateway(ABC):
#     @abstractmethod
#     def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
#         """모든 결제 수단 클래스가 반드시 구현해야 하는 추상 메서드"""
#         pass
# 코드	                  의미
# PaymentGateway(ABC)	추상 클래스 기능을 사용하는 부모 클래스
# @abstractmethod	    자식에서 구현해야 할 메서드로 지정
# buyer: str	        구매자는 문자열이라는 타입 힌트
# amount: int	        금액은 정수라는 타입 힌트
# -> PaymentReceipt	    영수증 객체를 반환한다는 타입 힌트
# pass	                여기서는 실행 내용을 작성하지 않음

# 부모 자체는 객체로 만들 수 없음 (@abstractmethod가 붙어 있으면 추상 메서드라서 부모 객체 생성은 막힘)
# -> 추상 메서드는 자식에서 재정의해야 함 
# class PaymentGateway(ABC):
#     @abstractmethod
#     def process_payment(self, buyer, amount):
#         pass
# -> PaymentGateway()  # TypeError
# 자식도 추상 메서드를 구현하지 않으면 객체를 만들 수 없음 (pass로 기능 구현이 안됨)
# class BankGateway(PaymentGateway):
#     pass
# -> BankGateway()  # TypeError
# -> 핵심은 BankGateway()도 process_payment()라는 공통 기능을 가져야 한다는 점 
print('3---')

## 4. 자식 클래스는 실제 결제 로직을 구현
# class CreditCardGateway(PaymentGateway):
#     def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
#         fee = int(amount * 0.025)
#         return PaymentReceipt("신용카드", buyer, amount, fee, "APPROVED")
card = CreditCardGateway()
receipt = card.process_payment("박파이썬", 50000)
# 실행 순서는:
# 1. buyer에 "박파이썬", amount에 50000 전달
# 2. fee = int(50000 * 0.025) → 1250
# 3. 해당 값으로 PaymentReceipt 객체 생성
# 4. 만든 영수증 객체를 반환하여 receipt에 연결
# return PaymentReceipt(...)는 문자열이 아니라 객체를 반환한다는 점이 중요

## 5. 반복문은 다형성을 활용
# gateways: list[PaymentGateway] = [
#                                     CreditCardGateway(),
#                                     KakaoPayGateway(),
#                                 ]
# for gw in gateways:
#     receipt = gw.process_payment("박파이썬", 50000)
#     print(f"{receipt} | 정산 금액: {receipt.net_amount:,}원")
# -> list[PaymentGateway] : 부모 또는 그 자식 객체들을 담는 리스트라는 타입 힌트
# 반복문은 같은 process_payment()를 호출하지만, 실제 객체에 따라 실행되는 구현이 달라짐 -> 다형성
# 실제 객체	               수수료	    정산 금액
# CreditCardGateway	    1,250원	    48,750원
# KakaoPayGateway	    500원	    49,500원

print('4---')
# __repr__는 객체의 내용을 확인하기 위한 문자열을 만듦 
# 클래스 : <__main__.PaymentReceipt object at 0x...>
class Person:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Person(name={self.name!r})" # !r은 해당 값의 repr() 표현을 사용한다는 뜻이라, 문자열에는 따옴표도 표시
person = Person("철수")

print(repr(person))  # Person(name='철수')
print([person])      # [Person(name='철수')]
print('---')
# @dataclass는 이런 __repr__를 자동으로 만들어 줍
print(receipt)
# PaymentReceipt(method='신용카드', buyer='박파이썬', amount=50000, fee=1250, status='APPROVED')
# 메서드	      주된 목적	                     대표 사용
# __str__	    사람이 읽기 편한 표현	          str(obj), print(obj)
# __repr__	    개발 중 객체를 확인하기 좋은 표현	repr(obj), 리스트 안 객체 표시
print("--------------------------")






from abc import ABC, abstractmethod
from dataclasses import dataclass

## 1. 부모 클래스 (현재 클래스는 ABC를 상속하지 않았음)
# -> 따라서 현재 코드는 부모 객체도 만들 수 있음 
class PaymentGateway :
# -> PaymentGateway가 ABC를 상속하지 않아서, @abstractmethod를 붙여도 자식의 구현을 강제하지 않음 
    # 생성자 미 입력시, 빈 생성자를 디폴트로 생성. 
    @abstractmethod  # 추상화
    def process_payment(self, item : str, amount : int) -> str : 
        return f'구매품목 : {item}, 수량 : {amount}'
        pass

## 2. CreditCardGateway는 부모 메서드를 재정의 : 오버라이딩
class CreditCardGateway(PaymentGateway) :
    def process_payment(self, item : str, amount : int) -> str : 
            return f'구매품목2 : {item}, 수량2 : {amount}'
    pass 

## 3. BankGateway는 부모 메서드를 그대로 사용
class BankGateway(PaymentGateway) :
    pass # pass는 “상속을 받지 않는다”가 아니라 이 클래스 본문에서 추가로 작성할 내용이 없다는 뜻

for obj in [CreditCardGateway(), BankGateway()] :
    print(obj.process_payment('식료품', 100))
print('----')

obj2 = CreditCardGateway()
print(obj2.process_payment('b', 200))  
print(CreditCardGateway().process_payment("식품", 300))
# '구매품목2 : 식료품, 수량2 : 100'
# -> 자식 메서드가 실행되고, 부모 메서드는 자동으로 실행되지 않음 

print('----')

obj3 = BankGateway()
print(obj3.process_payment('c', 300))
print(BankGateway().process_payment("식품", 400))
# '구매품목 : 식료품, 수량 : 100'
# -> 자식에 메서드가 없으므로 부모에게서 찾아 실행. 현재는 추상 메서드 구현을 강제하지 않기 때문에 객체 생성도 가능

print("--------------------------")



