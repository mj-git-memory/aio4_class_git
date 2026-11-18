##### 3차시: 상속(Inheritance)과 다형성(Polymorphism) — 거인의 어깨 위에서 코드 재사용하기!
# super().__init__(...) : 부모 클래스의 출생 신고서를 먼저 호출해 공통 속성(이름, 버전)을 깔끔하게 세팅
# 오버라이딩: 부모의 메서드를 자식에서 다시 정의
# 다형성: 같은 predict() 호출이 객체 종류에 따라 다르게 동작

### 2. 실습 예제 3-1 & 3-2: 멀티모달 AI 모델 통합 추론 파이프라인
class BaseAIModel:
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
    print(obj)
    print(obj.predict('test'))
    print('---')
# <__main__.BaseAIModel object at 0x10de7ef90>
# [base v1.0] 기본 추론: test
# ---
# <__main__.VisionClassifier object at 0x10de7f0e0>
# [Vision vision (1024)] 이미지 'test' 분석 결과 -> '고양이 (확률 98.4%)'
# ---
# <__main__.TextSummarizerLLM object at 0x10de7f230>
# [LLM textsumarizer (max=1000000)] 텍스트 요약 결과 -> 'test'
# ---
print("--------------------------")


# 다형성의 위력: 서로 다른 모델 클래스들을 단일 for 루프로 일괄 실행!
pipeline: list[BaseAIModel] = [
                                VisionClassifier("YOLO-KDT", "8.2", "640x640"),
                                TextSummarizerLLM("Codex-   Mini", "2.0", 512),
                              ]
for model in pipeline:
    print(model)
    print(model.predict("실습 데이터 샘플 입력입니다"))
    print("---")
# 실행 결과:
# [Vision YOLO-KDT (640x640)] 이미지 '실습 데이터 샘플 입력입니다' 분석 결과 -> '고양이 (확률 98.4%)'
# [LLM Codex-Mini (max=512)] 텍스트 요약 결과 -> '실습 데이터 샘플 입력입니다
print("--------------------------")


# 이 코드에서는 상속·super()·오버라이딩·다형성의 차이를 꼭 기억하면 됨 

## 1. 상속은 공통 코드를 물려받는 것
# class VisionClassifier(BaseAIModel):
# -> VisionClassifier가 BaseAIModel을 상속. 
# -> 이름과 버전을 설정하는 공통 초기화 코드를 재사용할 수 있음 

# class TextSummarizerLLM(BaseAIModel):
# -> 텍스트 모델도 같은 부모를 상속하지만, 자신만의 속성과 동작을 추가


## 2. super().__init__()은 같은 객체에 부모의 초기화 코드를 실행
# def __init__(self, name, version, resolution):
#     super().__init__(name, version)
#     self.resolution = resolution
# model = VisionClassifier("vision", "1.0", "1024")
# 실행 순서
# -> 자식의 __init__ 실행
# → 부모의 __init__으로 name, version 설정
# → 자식의 코드로 resolution 설정


## 3. 오버라이딩은 부모 메서드를 자식에서 다시 정의하는 것
# -> 세 클래스 모두 predict()라는 이름을 사용
# model.predict("test")
# -> model이 비전 모델이면 자식의 predict()가 실행. 
# -> 부모의 predict()가 먼저 자동 실행되는 것은 아니

## 4. 다형성은 같은 호출이 객체에 따라 다르게 동작하는 성질
# for obj in pipeline:
#     print(obj.predict("test"))
# -> 반복문에서는 객체 종류를 구분하는 if 없이 같은 메서드를 호출
# -> 실제 객체에 따라 적절한 predict()가 실행

## 5. 타입 힌트는 객체의 종류를 바꾸지 않음 
# pipeline: list[BaseAIModel] = [
#     VisionClassifier(...),
#     TextSummarizerLLM(...),
# ]
# list[BaseAIModel] -> 부모 또는 그 자식 객체들을 담겠다는 타입 힌트


# pipeline: list[BaseAIModel] = [vision, text]
# 부분	                 의미
# pipeline	            변수 이름
# :	                    변수의 타입 힌트를 시작
# list[BaseAIModel]	    BaseAIModel 계열 객체를 담는 리스트
# =	                    오른쪽 리스트를 변수에 대입
# [vision, text]	    실제로 담는 객체들
## 그런데 왜 BaseAIModel이라고 쓸까요?
# -> 두 클래스가 모두 BaseAIModel을 상속하기 때문
# -> 라서 비전 모델과 텍스트 모델을 **“둘 다 BaseAIModel의 한 종류”**로 다룰 수 있음
