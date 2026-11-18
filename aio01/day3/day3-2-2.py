## 6차시: 사용자 정의 예외(Custom Exception)와 raise — 비즈니스 규칙을 지키는 맞춤형 경보 시스템!
# 파이썬 기본 예외(ValueError, RuntimeError)만 쓰면 "무언가 잘못됨!"이라는 사이렌만 울릴 뿐, 
# '일일 AI 토큰 한도가몇 개 부족해서 실패했는지' 즉시 파악하기 어려움
# Exception 클래스를 상속받아 우리 서비스만의 도메인 맞춤 예외 클래스를 만들고 raise로 직접 경보를 발령하면, 에러 처리 코드가 문서처럼 명확해짐


## -> 이 코드는 요청을 처리하기 전에 빈 입력과 토큰 부족을 검사하고, 문제가 있으면 종류별 예외를 발생시키는 연습. 
## -> 실제 API 호출이나 코드 생성은 하지 않고, 토큰 차감과 메시지 반환만 함

### 2. 실습 예제 6-1: Codex API 토큰 쿼터 및 프롬프트 보안 제어 시스템

## 1. 사용자 정의 예외를 만듦
class AIServiceError(Exception): # 파이썬의 내장 클래스인 Exception을 상속해서 이 서비스에서 사용할 기본 예외를 만듦
    """AI 서비스 최상위 기본 예외 클래스"""
    pass # 추가로 정의할 내용이 없음을 의미 
class PromptEmptyError(AIServiceError):
    """프롬프트가 비어있을 때 발생하는 예외"""
    pass # -> pass만 있어도 부모에게서 예외 기능을 상속하므로, 다음처럼 메시지를 넣어 사용할 수 있음 (PromptEmptyError("입력해주세요."))
    ## PromptEmptyError("입력해주세요.")는 클래스 안에 문자열을 넣는 문법이 아님
    # -> 클래스를 호출해 객체를 만들면서 문자열을 인자로 전달하는 것
    # ex) student = KDTStudent("김루키", "AI 엔지니어링")
    # ex) error = PromptEmptyError("입력해주세요.")
    # error = PromptEmptyError("입력해주세요.")  # 예외 객체 생성만 함 / raise error : # 실제로 예외 발생
    # -> 상속받은 예외 초기화 기능이 인자를 보관하고, 예외의 문자열 표현 기능이 메시지를 보여줌
    # print(error)       # 입력해주세요.
    # print(error.args)  # ('입력해주세요.',)

## 2. 토큰 부족 예외에는 추가 정보를 저장
class TokenQuotaExceededError(AIServiceError):
    """토큰 한도 초과 시 요청량과 잔여 한도 컨텍스트를 함께 전달하는 예외"""
    def __init__(self, requested: int, remaining: int):
        self.requested = requested
        self.remaining = remaining
        # 부모에 직접 작성한 __init__이 없어도, 조상에게서 물려받은 초기화를 사용할 수 있음 
        # AIServiceError에는 직접 정의한 __init__이 없지만, Exception에서 물려받은 초기화 기능은 있음
        super().__init__(f"토큰 한도 초과! (요청: {requested}개, 잔여 한도: {remaining}개)")
        # error = TokenQuotaExceededError(40, 20)
        # -> 부모 객체를 따로 만드는 것이 아니라, 하나의 자식 객체를 초기화하면서 상속받은 초기화 로직도 재사용
        # 자식의 __init__ 실행
        # → requested와 remaining 속성 저장
        # → super().__init__(메시지) 실행
        # → 상속 경로에서 사용할 수 있는 예외 초기화 기능 실행
        # → 같은 error 객체에 메시지 보관

## 3. 클라이언트 객체가 남은 토큰을 기억
class CodexClient:
    def __init__(self, daily_quota: int = 100):
        self.remaining_tokens = daily_quota

    ## 4. 요청 처리 순서는 ‘입력 검사 → 한도 검사 → 차감’
    def generate_code(self, prompt: str, estimated_tokens: int) -> str:
        if not prompt.strip():
            raise PromptEmptyError("프롬프트에 최소 1글자 이상의 명령어를 입력해주세요.") # raise가 실행되면 메서드의 남은 코드는 건너뛰므로, 실패한 요청은 토큰을 차감하지 않음
        if estimated_tokens > self.remaining_tokens:
            raise TokenQuotaExceededError(estimated_tokens, self.remaining_tokens) # (요청: 40개, 잔여 한도: 20개) 
            # raise TokenQuotaExceededError(self.remaining_tokens, estimated_tokens) # (요청: 20개, 잔여 한도: 40개) 
        self.remaining_tokens -= estimated_tokens
        return f"[생성 성공]    '{prompt}' 코드 생성 완료 (남은 토큰: {self.remaining_tokens})"
    
client = CodexClient(daily_quota=50) # 기본값은 100이지만, 여기서는 50을 전달했으므로 남은 토큰은 50부터 시작

test_requests = [
    ("클래스 리팩토링 코드 작성", 30),
    ("   ", 10),
    ("대규모 프로젝트 전체 변환", 40),
]
## 5. 반복문에서 각 요청의 성공과 실패를 처리
# -> try/except가 반복문 안에 있으므로, 한 요청이 실패해도 처리 후 다음 요청으로 진행
for prompt_text, tokens in test_requests: # 각 튜플을 두 변수로 나눠 받음
    try:
        result = client.generate_code(prompt_text, tokens) 
        print(result) # # 성공하면 반환 문자열을 result로 받고 출력. 실패하면 해당 예외 종류의 except로 이동
    except PromptEmptyError as e:  # e는 발생한 예외 객체
        print(f"[입력 검증 실패]    {e}")
    except TokenQuotaExceededError as e:
        print(f"[쿼터 경보]     {e}     -> 기본 요금제를 업그레이드하거나 요청 길이를 줄이세요.")

## 꼭 기억할 내용은 raise는 오류를 알리고, except는 그 오류를 처리
# 실행 결과:
# [생성 성공]    '클래스 리팩토링 코드 작성' 코드 생성 완료 (남은 토큰: 20)
# [입력 검증 실패]    프롬프트에 최소 1글자 이상의 명령어를 입력해주세요.
# [쿼터 경보]     토큰 한도 초과! (요청: 40개, 잔여 한도: 20개)     -> 기본 요금제를 업그레이드하거나 요청 길이를 줄이세요.