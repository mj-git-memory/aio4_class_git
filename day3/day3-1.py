# __init__   : 자동으로 함수 호출. 여기에서 내가 필요한 함수들 정의
# self :  class 안에 있는 함수에서, 가장 처음 나오는 변수 (self는 클래스에만 존재)
# self 자리는 값을 받는게 아님

# class의 구성 요소 : 변수, 함수 (변수는 없고, 함수만 존재해도 됨)
# return : 함수 내에서 return을 만나면, 아래까지 안 내려가고 그 값을 바로 실행.
# class는 무조건 첫 글자는 대문자로 정의

# 클래스에 값을 넣으면, 그 값이 들어간 객체 생성

##### 1차시: 클래스(Class)와 객체(Object)의 탄생 — 붕어빵 틀을 넘어 '스마트 캐릭터 공장'으로
### 2. 실습 예제 1-1 (기초): KDT AI 캠퍼스 수강생 성장 시뮬레이터
class KDTStudent:
    def __init__(self, name: str, track: str):
        self.name = name
        self.track = track
        self.level = 1
        self.energy = 100
        self.completed_missions = []

    def study_coding(self, topic: str, cost_energy: int = 25) -> str:
        if self.energy < cost_energy:
            return f"[휴식 필요] {self.name}님의 에너지가 부족합니다! (현재: {self.energy})"
        self.energy -= cost_energy
        self.level += 1
        self.completed_missions.append(topic)
        return f"[레벨업!] {self.name}님이 '{topic}' 실습을 완료했습니다! (Lv.{self.level}, 남은 에너지: {self.energy})"

    def drink_coffee(self, boost: int = 40) -> str:
        self.energy = min(100, self.energy + boost)
        return f"[충전 완료] 아이스 아메리카노 수혈! 현재 에너지: {self.energy}"

student1 = KDTStudent("김루키","AI 엔지니어링")
print(student1.study_coding("Python 클래스 기초"))
print(student1.study_coding("예외처리 마스터"))
print(student1.drink_coffee())
print("--------------------------")


### 3. 실습 예제 1-2 (응용): 원두 재고를 스스로 관리하는 스마트 바리스타 로봇
class BaristaBot:
    # 생성자 (__init__)
    def __init__(self, bot_name: str, bean_grams: int):
        self.bot_name = bot_name
        self.bean_grams = bean_grams
        self.total_cups = 0

    def brew_espresso(self, cups: int = 1) -> str:
        required_beans = cups * 18
        if self.bean_grams < required_beans:
            return f"[{self.bot_name}] 원두 부족! (필요: {required_beans}g, 현재: {self.bean_grams}g)"
        self.bean_grams -= required_beans
        self.total_cups += cups
        return f"[{self.bot_name}] 에스프레소 {cups}잔 추출 완료! (남은 원두: {self.bean_grams}g, 누적: {self.total_cups}잔)"
    
bot = BaristaBot("코덱스바리스타-1호", 50)
print(bot.brew_espresso(2))
print(bot.brew_espresso(2))
# 실행 결과:
# [코덱스바리스타-1호] 에스프레소 2잔 추출 완료! (남은 원두: 14g, 누적: 2잔)
# [코덱스바리스타-1호] 원두 부족! (필요: 36g, 현재: 14g)
bot2 = BaristaBot("알바생", 80)
print(bot2.brew_espresso(2))
print(bot2.brew_espresso(1))
print(bot2.brew_espresso(1))
print("--------------------------")


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
        return f"[{self.owner}] {amount:,}원 입금 완료 (현재 잔액: {self.balance:,}원)"  # self.balance를 읽으므로 getter 실행

    def __str__(self) :
        return f"owner : {self.owner} __balance : {self.__balance}"
    
    
wallet = DigitalWallet("이코딩", 10000)
print("----")
# print(wallet.deposit(5000))
# wallet.balance = -99999  # 외부에서 불법 음수 대입 시도 -> setter가 즉시 차단!
wallet.balance = 1000  # 외부에서도 balance에 대입하면 setter 실행. 0 이상의 잔액 변경은 허용됨
# wallet.bal = 1000  # 현재 프로퍼티 이름은 balance이므로, bal에 대입하면 별도 일반 속성이 생김 (setter 실행 안 됨)
print(f"최종 안전 잔액: {wallet.balance:,}원")  # getter로 잔액을 읽고, :, 형식으로 천 단위 쉼표 표시
print("----")
print(wallet)
# print(wallet.__balance)
# AttributeError: 'DigitalWallet' object has no attribute '__balance'. Did you mean: 'balance'?
print("--------------------------")


### 3. 실습 예제 2-2 (응용): AI 모델 하이퍼파라미터 컨트롤러와 __str__ 매직 메서드
class ModelConfig:
    def __init__(self, model_name: str, learning_rate: float, epochs: int):  # 객체 생성 시 자동 호출
        self.model_name = model_name
        self.__learning_rate = 0.001
        self.learning_rate = learning_rate
        self.epochs = epochs
    @property
    def learning_rate(self) -> float:
        return self.__learning_rate
    @learning_rate.setter
    def learning_rate(self, value: float) -> None:
        if not (0.0 < value <= 1.0):
            print(f"[검증 경고] 비정상 학습률({value}) 감지! 기존 안전값({self.__learning_rate})을 유지합니다.")
            return
        self.__learning_rate = value
    def __str__(self) -> str:  # 특정 사건 발싱 시 자동 호출. str은 print(생선된 객체) 출력 시 자동 호출 
        return f"ModelConfig(name='{self.model_name}', lr={self.learning_rate}, epochs={self.epochs})"
    
cfg = ModelConfig("ResNet-50", 0.01, 30)
print(cfg)
print("----")
cfg.learning_rate = 5.0  # 허용 범위(0~1.0) 초과 대입 시도
print(cfg)
print("--------------------------")



##### 3차시: 상속(Inheritance)과 다형성(Polymorphism) — 거인의 어깨 위에서 코드 재사용하기!
# 다형성 : 상속 받은 것을 일부 수정(다시 정의)해서 재사용
### 2. 실습 예제 3-1 & 3-2: 멀티모달 AI 모델 통합 추론 파이프라인
class BaseAIModel:
    # 생성자 (__init__)
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    def predict(self, input_data: str) -> str:
        return f"[{self.name} v{self.version}] 기본 추론: {input_data}"
    
class VisionClassifier(BaseAIModel):
    def __init__(self, name: str, version: str, resolution: str):
        super().__init__(name, version)  # 부모 초기화 코드 재사용 : super().__init__
        self.resolution = resolution
    def predict(self, input_data: str) -> str:  # 다형성 오버라이딩 (부모의 함수를 재정의)
        return f"[Vision {self.name} ({self.resolution})] 이미지 '{input_data}' 분석 결과 -> '고양이 (확률 98.4%)'"
    
class TextSummarizerLLM(BaseAIModel):
    def __init__(self, name: str, version: str, max_tokens: int):
        super().__init__(name, version)
        self.max_tokens = max_tokens
    def predict(self, input_data: str) -> str:  # 다형성 오버라이딩 (부모의 함수를 재정의)
        summary = input_data[:18] + "..." if len(input_data) > 18 else input_data
        return f"[LLM {self.name} (max={self.max_tokens})] 텍스트 요약 결과 -> '{summary}'"

pipeline = [
            BaseAIModel('base', '1.0'),
            VisionClassifier('vision', '1.0', '1024'),
            TextSummarizerLLM('textsumarizer', '1,0', 1000000)
            ]
for obj in pipeline : 
    print(obj.predict('test'))

# # 다형성의 위력: 서로 다른 모델 클래스들을 단일 for 루프로 일괄 실행!
# pipeline: list[BaseAIModel] = [
#                                 VisionClassifier("YOLO-KDT", "8.2", "640x640"),
#                                 TextSummarizerLLM("Codex-   Mini", "2.0", 512),
#                               ]
# for model in pipeline:
#     print(model.predict("실습 데이터 샘플 입력입니다"))
# 실행 결과:
# [Vision YOLO-KDT (640x640)] 이미지 '실습 데이터 샘플 입력입니다' 분석 결과 -> '고양이 (확률 98.4%)'
# [LLM Codex-Mini (max=512)] 텍스트 요약 결과 -> '실습 데이터 샘플 입력입니다
print("--------------------------")


##### 4차시: 추상 클래스(ABC)와 데이터클래스(@dataclass) — 현대적 파이썬 OOP 끝판왕
### 2. 실습 예제 4-1: 다중 결제 게이트웨이 및 자동 정산 영수증 시스템
from abc import ABC, abstractmethod
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

class PaymentGateway(ABC):
    @abstractmethod  # 추상화
    def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
        """모든 결제 수단 클래스가 반드시 구현해야 하는 추상 메서드"""
        pass

class CreditCardGateway(PaymentGateway):
    def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
        fee = int(amount * 0.025)
        return PaymentReceipt("신용카드", buyer, amount, fee, "APPROVED")

class KakaoPayGateway(PaymentGateway):
    def process_payment(self, buyer: str, amount: int) -> PaymentReceipt:
        fee = int(amount * 0.01)
        return PaymentReceipt("카카오페이", buyer, amount, fee, "APPROVED")

# gateways: list[PaymentGateway] = [CreditCardGateway(), KakaoPayGateway()]
# for gw in gateways:
#     receipt = gw.process_payment("박파이썬", 50000)
#     print(f"{receipt} | 정산 금액: {receipt.net_amount:,}원")

# # 실행 결과:
# # PaymentReceipt(method='신용카드', buyer='박파이썬', amount=50000, fee=1250, 
# status='APPROVED') | 정산 금액: 48,750원
# # PaymentReceipt(method='카카오페이', buyer='박파이썬', amount=50000, fee=500, 
# status='APPROVED') | 정산 금액: 49,500
print("--------------------------")



from abc import ABC, abstractmethod
from dataclasses import dataclass

class PaymentGateway :
    # 생성자 미 입력시, 빈 생성자를 디폴트로 생성. 
    @abstractmethod  # 추상화
    def process_payment(self, item : str, amount : int) -> str : 
        # return f'구매품목 : {item}, 수량 : {amount}'
        pass

class CreditCardGateway(PaymentGateway) :
    def process_payment(self, item : str, amount : int) -> str : 
            return f'구매품목2 : {item}, 수량2 : {amount}'
    pass # 

class BankGateway(PaymentGateway) :
    pass 

for obj in [CreditCardGateway(), BankGateway()] :
    print(obj.process_payment('식료품', 100))
print('----')
obj2 = CreditCardGateway()
print(obj2.process_payment('b', 200))  # error. 부모를 추상화했으면, 
print('----')
obj3 = BankGateway()
print(obj3.process_payment('c', 300))

print("--------------------------")
