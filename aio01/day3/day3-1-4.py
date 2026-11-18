
#### 2차시: 캡슐화(Encapsulation)와 프로퍼티(@property) — 내 지갑과 AI 가중치는 아무나 못 건드려!
### 3. 실습 예제 2-2 (응용): AI 모델 하이퍼파라미터 컨트롤러와 __str__ 매직 메서드
class ModelConfig:
    def __init__(self, model_name: str, learning_rate: float, epochs: int):  # 객체 생성 시 자동 호출
        self.model_name = model_name
        self.__learning_rate = 0.001
        self.learning_rate = learning_rate
        self.epochs = epochs
    
    @property
    def learning_rate(self) -> float:
        print('calling getter')
        return self.__learning_rate
    
    @learning_rate.setter
    def learning_rate(self, value: float) -> None:
        print('calling setter')

        if not (0.0 < value <= 1.0):
            print(f"[검증 경고] 비정상 학습률({value}) 감지! 기존 안전값({self.__learning_rate})을 유지합니다.")
            return
        self.__learning_rate = value

    def __str__(self) -> str:  # 특정 사건 발싱 시 자동 호출. str은 print(생선된 객체) 출력 시 자동 호출 
        return f"ModelConfig(name='{self.model_name}', lr={self.learning_rate}, epochs={self.epochs})"
        # -> calling getter 호출 


cfg = ModelConfig("ResNet-50", 0.01, 30)
# calling setter
print("1----")
print(cfg)
# calling getter
# ModelConfig(name='ResNet-50', lr=0.01, epochs=30)
print("2----")
cfg.learning_rate = 5.0  # 허용 범위(0~1.0) 초과 대입 시도
# calling setter
# [검증 경고] 비정상 학습률(5.0) 감지! 기존 안전값(0.01)을 유지합니다.
print("3----")
cfg.learning_rate = 1.0  # 허용 범위 안의 값 → 변경 성공
# calling setter
print("4----")
print(cfg)
# calling getter
# ModelConfig(name='ResNet-50', lr=1.0, epochs=30)
print("--------------------------")


# 이 코드는 프로퍼티로 학습률의 허용 범위를 검사하고, __str__로 객체의 현재 설정을 보여 주는 예제
## 1. 실제 저장 위치와 접근 창구를 구분하세요.
# 이름	                         역할
# self.__learning_rate	        실제 학습률 저장
# self.learning_rate	        getter·setter를 통한 접근
# self.model_name, self.epochs	일반 속성

# cfg.learning_rate = 0.01  # setter 실행 → 내부 값 저장
# print(cfg.learning_rate) # getter 실행 → 내부 값 반환

## 2. 객체를 초기화할 때도 setter가 실행
# self.__learning_rate = 0.001
# self.learning_rate = learning_rate
# -> 먼저 기본값 0.001을 준비하고, 전달받은 학습률은 setter의 검사를 거쳐 저장
# cfg = ModelConfig("ResNet-50", 0.01, 30)
# -> 0.01은 허용 범위이므로 내부 값이 0.001에서 0.01로 바뀜. 초기값부터 잘못 전달하면 기본값 0.001이 유지

## 3. print(cfg)는 __str__을 호출하고, 그 안에서 getter가 실행
# def __str__(self) -> str:
#     return f"ModelConfig(name='{self.model_name}', lr={self.learning_rate}, epochs={self.epochs})"

# print(cfg)
# → __str__ 실행
# → self.learning_rate를 읽으므로 getter 실행
# → 완성된 문자열 반환
# → print가 문자열 출력

# 실행	                    호출되는 메서드	            내부 학습률
# 객체 생성, 초기값 0.01	    __init__ → setter	    0.01
# 첫 print(cfg)	             __str__ → getter	     0.01
# cfg.learning_rate = 5.0	setter → 경고 후 종료	   0.01 유지
# cfg.learning_rate = 1.0	setter	                 1.0
# 마지막 print(cfg)	          __str__ → getter        1.0