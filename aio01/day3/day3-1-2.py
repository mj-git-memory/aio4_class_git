##### 1차시: 클래스(Class)와 객체(Object)의 탄생 — 붕어빵 틀을 넘어 '스마트 캐릭터 공장'으로
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
print(bot)
print(bot.brew_espresso(2))
print(bot.brew_espresso(1))
# 실행 결과:
# <__main__.BaristaBot object at 0x10a18ef90>
# [코덱스바리스타-1호] 에스프레소 2잔 추출 완료! (남은 원두: 14g, 누적: 2잔)
# [코덱스바리스타-1호] 원두 부족! (필요: 18g, 현재: 14g)

bot2 = BaristaBot("알바생", 80)
print(bot2)
print(bot2.brew_espresso(2))
print(bot2.brew_espresso(2))
print(bot2.brew_espresso(1))
print("--------------------------")
# <__main__.BaristaBot object at 0x10c0accd0>
# [알바생] 에스프레소 2잔 추출 완료! (남은 원두: 44g, 누적: 2잔)
# [알바생] 에스프레소 2잔 추출 완료! (남은 원두: 8g, 누적: 4잔)
# [알바생] 원두 부족! (필요: 18g, 현재: 8g)


# 이 코드의 핵심은 같은 클래스로 만든 객체라도 각자의 원두량과 추출 잔 수를 따로 관리한다는 점

## 1. __init__에서 객체마다 초기 상태를 설정
# bot = BaristaBot("코덱스바리스타-1호", 50)
# bot2 = BaristaBot("알바생", 80)
# 속성	         bot	             bot2
# bot_name	    "코덱스바리스타-1호"	"알바생"
# bean_grams	50	                80
# total_cups	0	                0
# -> bot이 커피를 만들어도 bot2의 원두는 줄어들지 않음 

## 2. self는 메서드를 호출한 객체를 가리킴 
# bot.brew_espresso(2)   # 메서드 안의 self는 bot
# bot2.brew_espresso(2)  # 메서드 안의 self는 bot2
# -> 같은 메서드를 사용해도 self가 달라서 각자의 상태를 변경

## 3. 일반 변수와 객체 속성의 역할이 다름 
# required_beans = cups * 18
# -> required_beans는 호출할 때마다 계산하는 지역 변수
# self.bean_grams
# self.total_cups
# -> 이것들은 객체에 저장되어 다음 호출에도 유지되는 속성

## 4. 먼저 검사하고, 가능한 경우에만 상태를 변경
# if self.bean_grams < required_beans:
#     return "원두 부족!"
# 부족하면 return으로 메서드를 즉시 끝냄. 따라서 아래 코드는 실행되지 않음.
# self.bean_grams -= required_beans  # 원두 차감
# self.total_cups += cups           # 누적 잔 수 증가

## 5. 기본 인자와 반환값을 구분
# def brew_espresso(self, cups: int = 1) -> str:
# - cups=1: 잔 수를 생략하면 1잔을 만듦
# - cups: int: 잔 수가 정수라는 타입 힌트
# - -> str: 결과를 문자열로 반환한다는 타입 힌트
# print(bot.brew_espresso())
# -> 메서드가 반환한 결과 문자열을 바깥의 print()가 출력