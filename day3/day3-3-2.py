## 2. 실습 예제 7-1: 온라인 서점 주문/할인 계산기 Before & After 완벽 비교
# -> 이 코드는 책 주문 금액에 회원 할인과 쿠폰을 적용하는 계산기
# -> 개선 전후 결과는 같지만, 개선 후에는 주문 데이터·입력 검증·할인 계산의 역할을 나눴음 

# [Before: 리팩토링 전 — 매직 넘버와 if-elif가 얽힌 취약한 절차지향 함수]
## 1. 개선 전 함수: calc_order_legacy()
def calc_order_legacy(u_type, price, qty, coupon):
    # 문제점 1: u_type 1, 2, 3이 무슨 등급인지 작성자 외에는 알 수 없음 (매직 넘버)
    # 문제점 2: price나 qty에 음수가 들어와도 아무런 검증 없이 잘못된 금액을 계산함
    total = price * qty
    if u_type == 1:
        total = total * 0.95
    elif u_type == 2:
        total = total * 0.90
    elif u_type == 3:
        total = total * 0.80
    if coupon == "YES":
        total = total - 3000
    if total < 0:
        total = 0
    return int(total)
# calc_order_legacy(2, 15000, 2, "YES")
# 15,000 × 2 = 30,000원
# 30,000 × 0.90 = 27,000원
# 27,000 - 3,000 = 24,000원


# [After: Codex 리팩토링 후 — 불변 데이터클래스 + 상수 테이블 + 커스텀 예외 검증]
from dataclasses import dataclass

## 2. InvalidOrderError: 잘못된 주문을 알리는 예외
class InvalidOrderError(ValueError): # ValueError를 상속해서 주문 관련 오류에 이름을 붙임
    """주문 데이터 또는 멤버십 등급이 유효하지 않을 때 발생하는 도메인 예외"""
    pass

## 3. OrderItem: 주문 정보를 담는 데이터클래스
@dataclass(frozen=True) # frozen=True: 생성 후 필드의 일반적인 재대입(저장된 값을 바꾸는 것)을 막음
# -> 수량이 다른 주문이 필요하면 새 객체를 만들어야 함

## -> @dataclass는 여러 데이터를 묶어 보관하는 클래스를 간단하게 만드는 기능
## -> frozen=True는 그렇게 만든 객체의 필드 값을 나중에 바꾸지 못하게 하는 옵션
## -> 1. @dataclass가 없으면 초기화 코드를 직접 작성해야 함 
# -> @dataclass가 __init__ 등을 자동 생성하므로 직접 초기화 메서드를 작성하지 않아도 됨
# book_order = OrderItem("파이썬 클린 아키텍처", 15000, 2)
# book_order.quantity = 5  # FrozenInstanceError

class OrderItem:
    name:str
    unit_price:int
    quantity:int

    ## 4. __post_init__(): 생성 직후 입력(주문) 검증
    def __post_init__(self): # 데이터클래스가 자동 생성한 __init__에서 필드를 설정한 다음 호출
        if self.unit_price < 0 or self.quantity <= 0:
            raise InvalidOrderError(f"유효하지 않은 가격({self.unit_price}) 또는 수량({self.quantity})입니다.")
    ## 5. subtotal: 할인 전 금액을 계산하는 프로퍼티
    @property
    def subtotal(self) -> int:
        return self.unit_price * self.quantity
        # print(book_order.subtotal)  # 30000
        # -> 프로퍼티이므로 subtotal()처럼 괄호를 붙이지 않음. 별도로 금액을 저장하지 않고 읽을 때 계산
# -> OrderItem(...) 호출
# → 필드 설정
# → __post_init__ 실행
# → 유효하면 생성 완료, 잘못됐으면 예외 발생

## 6. MembershipCheckout: 할인 규칙과 계산 담당
class MembershipCheckout:
    # 대문자는 상수로 사용하겠다는 관례이며, 파이썬이 변경을 자동으로 막는 것은 아님
    DISCOUNT_RATES = { 
        "BASIC": 0.05,
        "GOLD": 0.10,
        "VIP": 0.20,
    }
    COUPON_AMOUNT = 3000

    def calculate_final_price(self, item:OrderItem, tier:str, use_coupon:bool= False)-> int:
        
        if tier not in self.DISCOUNT_RATES:
            raise InvalidOrderError(f"알 수 없는 멤버십 등급입니다: '{tier}'")
        discount_rate = self.DISCOUNT_RATES[tier]
        discounted = int(item.subtotal * (1.0 - discount_rate))

        if use_coupon:
            discounted -= self.COUPON_AMOUNT
        return max(0, discounted) # 두 값 중 큰 값을 반환해 최종 금액이 음수가 되지 않게 함 
    
checkout = MembershipCheckout()
book_order = OrderItem("파이썬 클린 아키텍처", 15000, 2)

print("Before 결과:", calc_order_legacy(2, 15000, 2, "YES"))
print("After 결과:", checkout.calculate_final_price(book_order, tier="GOLD", use_coupon=True))
# checkout.calculate_final_price(
#     book_order,
#     tier="GOLD",
#     use_coupon=True
# )
# -> 메서드 안에서 self는 checkout, item은 book_order를 가리킴 
#  
## 실행 결과:
# Before 결과: 24000
# After 결과: 24000


## @dataclass가 기본적으로 만들어 주는 주요 기능은 다음과 같아요.
# 자동 생성 기능	역할
# __init__	전달받은 값으로 필드 초기화
# __repr__	객체의 필드와 값을 문자열로 표시
# __eq__	같은 클래스의 객체끼리 필드 값을 비교

# class OrderItem:
#     def __init__(self, name, unit_price, quantity):
#         self.name = name
#         self.unit_price = unit_price
#         self.quantity = quantity

# from dataclasses import dataclass
# @dataclass
# class OrderItem:
#     name: str
#     unit_price: int
#     quantity: int

# book = OrderItem("파이썬 책", 15000, 2)
# print(book)
# # -> OrderItem(name='파이썬 책', unit_price=15000, quantity=2)

# other = OrderItem("파이썬 책", 15000, 2)
# print(book == other)  # True