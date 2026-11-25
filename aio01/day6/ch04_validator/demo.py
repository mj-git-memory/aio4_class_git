"""04장: field_validator before/after, model_validator after."""
from datetime import date
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

# @...는 바로 아래 함수에 특별한 역할을 지정하는 데코레이터 문법
# 문법                      	     역할	                        사용할 때
# @field_validator("필드명")	     특정 필드의 값을 검사·변환	         아이디 공백 검사, 태그 변환
# @classmethod	                    첫 인자로 클래스인 cls를 받게 함	이 코드의 필드 검증 메서드 작성
# @model_validator(mode="after")    필드 검증 후 모델 전체 검사	        비밀번호 일치, 날짜 순서 비교


# @field_validator('username', mode='before') # username : 검증할 값 
# mode='before' -> username: str = Field(min_length=3) 검사 실행하기 전에 @field_validator 검사 실행

# @classmethod는 파이썬이 첫 번째 인자로 개별 객체 대신 클래스 자체를 전달하도록 하는 문법
# 매개변수	받는 대상
# self	  현재 객체
# cls	  현재 클래스

class Signup(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)
    password_confirm: str
    tags: list[str] = []  # tags의 선언은 리스트

    @field_validator('username', mode='before') # username : 검증할 값 
    @classmethod
    def normalize_username(cls, value: str) -> str: # -> str: 문자열을 반환. cls는 예약어가 아닌 관례적인 이름
        text = value.strip().lower()
        if ' ' in text:
            raise ValueError('아이디에는 공백을 사용할 수 없습니다') # raise ValueError(...) : 잘못된 값이라는 오류 발생
        return text

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, value: object) -> object:  # 문자열을 리스트로 변환(ex. tags='python, api')
        # value: object -> 문자열뿐 아니라 리스트 등 여러 형태의 입력을 받을 수 있다는 표시
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()] 
            # item.strip():각 항목 앞뒤 공백 제거 / value.split(','):쉼표 기준으로 나누기
        return value

    @model_validator(mode='after')
    def verify_password(self) -> 'Signup': # -> 'Signup': Signup 객체를 반환한다는 타입 표시
        if self.password != self.password_confirm:
            raise ValueError('비밀번호 확인 값이 다릅니다')
        return self # 검사한 객체를 그대로 반환
    # -> 비밀번호 일치는 한 항목만 보고 판단할 수 없음 password와 password_confirm을 함께 봐야 하므로 모델 검증기를 사용
    ## field_validator가 필드 값을 반환한다면, 이 model_validator는 객체 자신을 반환한다는 차이가 있음 

class Reservation(BaseModel):
    start: date
    end: date
    # — 날짜 순서 검사
    @model_validator(mode='after') # 두 필드의 관계를 확인하므로 model_validator가 적합 
    def validate_period(self) -> 'Reservation': 
        if self.end < self.start:
            raise ValueError('종료일은 시작일보다 빠를 수 없습니다')
        return self


def main() -> None:
    signup = Signup(username='  STUDENT01  ', password='password12',
                    password_confirm='password12', tags='python, api')
    print('STEP 1 - 전처리와 교차 검증:', signup.username, signup.tags)
    print('STEP 2 - 날짜 유효성:', Reservation(start='2026-10-21', end='2026-10-22'))
    print('---')
    try:
        Signup(username='goodname', password='password12', password_confirm='wrong')
    except ValidationError as error:
        print('STEP 3 - 검증 실패:', error.errors()[0]['type'])
        print('STEP 3 - 검증 실패:', error.errors()[0])
    print('04장 성공')


if __name__ == '__main__':
    main()