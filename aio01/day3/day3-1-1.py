# __init__   : 자동으로 함수 호출. 여기에서 내가 필요한 함수들 정의
# self :  class 안에 있는 함수에서, 가장 처음 나오는 변수 (self는 클래스에만 존재)
# self -> 호출한 객체를 받는 자리
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
print(student1) # <__main__.KDTStudent object at 0x10d502f90>
print(student1.study_coding("Python 클래스 기초"))
print(student1.study_coding("Python 클래스 기초2"))
print(student1.study_coding("예외처리 마스터", 55))

print(student1.drink_coffee())
print(student1.completed_missions)
print("--------------------------")

### 이 코드에서 꼭 알아야 할 것은 객체마다 상태를 저장하고, 메서드를 호출해 그 상태를 바꾼다는 점
## 1. 클래스는 정의이고, 객체는 실제로 만든 개별 대상
# class KDTStudent:
#     ...
# student1 = KDTStudent("김루키", "AI 엔지니어링")
# -> 이 클래스로 객체 하나를 만들고 student1이라는 이름으로 가리킴 

## 2. __init__은 객체의 초기 상태를 설정
# def __init__(self, name: str, track: str):
#     self.name = name
#     self.track = track
#     self.level = 1
#     self.energy = 100
#     self.completed_missions = []

# 생성 직후 상태
# name: "김루키"
# track: "AI 엔지니어링"
# level: 1
# energy: 100
# completed_missions: []
# -> __init__은 필요한 메서드를 정의하는 곳이 아니라, 여기서는 초기 속성을 설정하는 곳

## 3. self는 지금 동작하는 객체를 가리킴 
# student1.study_coding("Python 클래스 기초")
# -> 이렇게 호출하면 메서드의 self로 student1 객체가 자동 전달
# self.energy -= cost_energy
# -> 따라서 이 문장은 student1의 에너지를 줄이는 것

## 4. 기본값은 인자를 생략했을 때 사용
# def study_coding(self, topic: str, cost_energy: int = 25) -> str:
# student1.study_coding("기초")      # cost_energy = 25
# student1.study_coding("심화", 55)  # cost_energy = 55
# : str, : int, -> str은 입력과 반환값의 자료형을 알려주는 타입 힌트이며, 자동으로 자료형을 강제하지는 않음

## 5. return으로 일찍 종료하면 아래 상태 변경은 실행되지 않음 
# if self.energy < cost_energy:
#     return f"[휴식 필요] ..."
# -> 에너지가 부족하면 바로 종료하므로, 에너지·레벨·미션 목록이 모두 유지

## 6. return과 print()는 역할이 다름
# return "학습 완료"
# 메서드를 종료하고 호출한 곳에 문자열을 돌려줌
# print(student1.study_coding("Python 클래스 기초"))
# 메서드가 반환한 문자열을 print()가 화면에 출력