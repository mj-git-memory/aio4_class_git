# Field 범위, 길이, 패턴에 대해 엄격하게 검사

from pydantic import BaseModel, Field, ValidationError, EmailStr, ConfigDict
from typing import Literal

class Registration(BaseModel) :
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    name : str = Field(min_length=2, max_length=20, description='실명 기록해라') # default : Field( ~ )
    age : int = Field(ge=14, le=100) # 14 <= 나이 <= 100
    # age : int = Field(ge=14, le=100, strict=True) # strict=True : 문자형으로 입력된 숫자를 자동으로 int로 변환하지X
    email : EmailStr # 이메일 조건 
    level : Literal['basic', 'premium'] = 'basic' # Literal[] -> 문자열 리스트에 들어간 값 중 하나 선택 
    code : str = Field(pattern= r'^STU-[0-9]{4}$')  # STU-로 시작 + 0~9까지 숫자 4개 
    agreed : bool = Field(strict=True)

def main() -> None : 
    user1 = Registration(name = 'lee', age= '50', email='lee@abc.com', code='STU-0001', agreed=True)
    print('검증 성공 여부 :', user1.model_dump()) # user1.model_dump() : user1의 값을 딕셔너리 형태로 반환
    # 증 성공 여부 : {'name': 'lee', 'age': 50, 'email': 'lee@abc.com', 'level': 'basic', 'code': 'STU-0001', 'agreed': True}
    print('오류 확인')
    try : 
        user2 = Registration(name = 'lee', age= '500', email='lee@abccom', code='STU-001')
    except ValidationError as er :
        print(er)
        # 4 validation errors for Registration
        # age
        #   Input should be less than or equal to 100 [type=less_than_equal, input_value='500', input_type=str]
        #     For further information visit https://errors.pydantic.dev/2.14/v/less_than_equal
        # email
        #   value is not a valid email address: The part after the @-sign is not valid. It should have a period. [type=value_error, input_value='lee@abccom', input_type=str]
        # code
        #   String should match pattern '^STU-[0-9]{4}$' [type=string_pattern_mismatch, input_value='STU-001', input_type=str]
        #     For further information visit https://errors.pydantic.dev/2.14/v/string_pattern_mismatch
        # agreed
        #   Field required [type=missing, input_value={'name': 'lee', 'age': '5...com', 'code': 'STU-001'}, input_type=dict]
        #     For further information visit https://errors.pydantic.dev/2.14/v/missing
        print('---')
        print(er.errors()[0])
        # {'type': 'less_than_equal', 'loc': ('age',), 'msg': 'Input should be less than or equal to 100', 'input': '500', 'ctx': {'le': 100}, 'url': 'https://errors.pydantic.dev/2.14/v/less_than_equal'}
        print('---')
        for error in er.errors() :
            print(error['loc'], error['type'])
            # ('age',) less_than_equal
            # ('email',) value_error
            # ('code',) string_pattern_mismatch
            # ('agreed',) missing
    # except Exception
    
    # 오류 확인


if __name__ == '__main__' :
    main()