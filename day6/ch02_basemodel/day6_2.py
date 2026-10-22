# # 필수/기본값 설정, 모델 생성/검증

print()
from pydantic import BaseModel, ValidationError

class Member(BaseModel) : # BaseModel : 값이 제대로 들어오는지 검증
    username: str
    age: int
    active: bool = True # 기본값은 True
    nickname : str | None = None

print('***')
m = Member(username='홍길동', age=20, active=True, nickname=None)
print(m.username)
print('day6_3', __name__)
print('***')

# python 파일을 직접 실행할 때, '__name__'이라는 변수가 자동으로 생성되고, 그 변수의 값은 '__main__' 으로 할당 됨
if __name__ == '__main__' :
    m = Member(username='홍길동', age=20, active=True, nickname=None)
    print(m.username)
    print('day6_3', __name__)
print('-----------------')



class Member(BaseModel) : # BaseModel : 값이 제대로 들어오는지 검증
    username: str
    age: int
    active: bool = True # 기본값은 True
    nickname : str | None = None

class MemberOut(Member) : 
    id : int 


# [복습: model_validate()]
# 역할: 외부에서 받은 파이썬 데이터를 모델의 필드 규칙에 맞춰 검증하고,
#       성공하면 모델 객체를 반환하는 클래스 메서드. ex) Member.model_validate(data)로 호출한다.
# 언제 쓰나: API 응답이나 파일에서 읽은 딕셔너리 등을 Member 객체로 다루고 싶을 때.
#
# 1. 딕셔너리 입력
#    Member.model_validate({'username': 'kim', 'age': '34'})
#    -> Member 객체 반환. 기본 설정에서는 문자열 '34'를 정수 34로 변환한다.
#    -> 생략한 active와 nickname에는 기본값 True와 None이 들어간다.
#    -> age처럼 기본값이 없는 필수 항목이 빠지면 ValidationError가 발생한다.
#
# 2. 기존 Member 객체 입력
#    Member.model_validate(member)
#    -> 현재 모델의 기본 설정에서는 필드 값을 다시 검증하지 않고 같은 객체를 반환한다.
#       새 복사본을 만드는 용도가 아니다. 재검증 여부는 revalidate_instances 설정에 따른다.
#
# 3. 일반 클래스 객체 입력
#    Member.model_validate(user, from_attributes=True)
#    -> user.username, user.age 같은 속성을 읽어서 검증한다.
#
# 사용 방법 비교
# - 값을 직접 지정: Member(username='kim', age=34) (이 방식도 검증한다.)
# - 기존 데이터를 전달: Member.model_validate(data)
# - JSON 문자열을 전달: Member.model_validate_json('{"username":"kim","age":34}')
# - 반대 방향인 모델 -> 딕셔너리 변환: member.model_dump()
#
# 오류 처리: try 안에서 오류가 발생하면 나머지 줄은 건너뛰고 except로 이동한다.
# er.errors()는 오류 딕셔너리들의 리스트, [0]은 첫 번째 오류이다.
# ['loc']는 오류 위치(예: ('age',)), ['type']은 오류 종류(예: 'missing')이다.
# 참고: https://docs.pydantic.dev/latest/concepts/models/


def main() -> None : 
    member = Member(username='lee', age=20) # active와 nickname은 default값을 설정해 놓았으므로, 안 써도 됨
    print(member)
    print('----')

    raw = {'username':'kim', 'age':'34', 'active':False}
    parsed = Member.model_validate(raw)
    print(parsed, 'age 타입:', type(parsed.age))
    print(parsed, 'age 타입:', type(parsed.age).__name__)
    print('----')

    print('nickname 기본값', parsed.nickname)
    print('----')

    # - 필수 필드 누락
    # Member(username='kim')
    try : 
        Member(username='kim')
    except ValidationError as er :
        print("필수 항목 누락:", er)
        print('---')
        # er.errors()[0]  # r.errors() → 오류 정보를 리스트로 가져옴. [0] → 첫 번째 오류 선택
        # age
        #   Field required [type=missing, input_value={'username': 'kim'}, input_type=dict]
            # {
            #     "loc": ("age",),
            #     "type": "missing",
            #     "msg": "Field required",
            #     "input": {"username": "kim"}
            # }
        # er.errors()[0]["loc"]   # ("age",) → 오류가 발생한 위치
        # er.errors()[0]["type"]  # "missing" → 오류의 종류
        print(er.errors()[0]['loc'], er.errors()[0]['type']) 
    print('------')
    try :
        # 기존 Member 객체이므로 기본 설정에서는 같은 객체를 반환한다.
        parsed2 = Member.model_validate(member)
        print(parsed2)
        print('---')
        # age 누락 -> ValidationError 발생 -> 아래 print는 건너뛰고 except로 이동한다.
        parsed1 = Member.model_validate({"username": "kim"})
        print(parsed1)
        print('---')

    except ValidationError as er:
        print("딕셔너리 검증 오류:", er.errors()[0]["type"])

    # # - memberout 객체 생성
    # Member(username='kim', age= 20)
    # memberout = MemberOut(id = 1, username='lee', age= 30)
    # print(memberout)

if __name__ == '__main__' :
    main()
