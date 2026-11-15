## Supabase Auth 연결 이메일 회원가입 API

## 두 개 계정으로 가입 -로그인-메모접근-갱신-로그아웃

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, Field
from supabase.client import Client

import os # 운영체제 기능을 다룸. 여기서는 환경변수 읽기에 사용 
from dotenv import load_dotenv # .env 파일의 내용을 환경변수로 등록하는 함수

load_dotenv() # .env 파일을 찾아 내용을 읽어옴 
# -> .env에는 보통 이름=값 형태로 설정을 저장

print(os.getenv('host', '')) # os.getenv() : host 환경변수를 읽음
# -> 'host': 읽을 환경변수 이름
# -> '': 해당 환경변수가 없을 때 반환할 기본값인 빈 문자열


##### Supabase 연결 설정을 읽고, FastAPI 앱과 회원가입 입력 형식을 정의하는 코드
## 1. Supabase 설정 읽기
supabase_url = os.getenv('SUPABASE_URL', '').strip()
# -> os.getenv('SUPABASE_URL'): 환경변수에서 Supabase 프로젝트 주소를 읽음
# -> .strip(): 문자열 양쪽의 공백과 줄바꿈을 제거
supabase_key = os.getenv('SUPABASE_PUBLISHABLE_KEY', '').strip()

## 2. 설정이 빠졌는지 검사
if not supabase_url or not supabase_key :
    raise RuntimeError('SUPABASE_URL or SUPABASE_URL missing')
    # -> 필수 설정이 빠졌다는 오류를 발생시켜 실행을 중단시킴 

## 3. FastAPI 앱 생성
app = FastAPI(title='Supabase Auth - 회원가입') # API 서버를 만들기 위한 앱 객체를 생성
# -> title은 Swagger 문서(/docs) 등에 표시되는 제목

## 4. 회원가입 입력 형식 정의
class SignupRequest(BaseModel) :  
# -> Pydantic의 BaseModel을 상속해서 회원가입 요청 데이터의 구조와 검사 규칙을 정의
    model_config = ConfigDict(extra='forbid') 
    # -> 정의하지 않은 추가 항목은 허용하지 않겠다는 설정
    email : EmailStr 
    # -> email을 필수 항목으로 받고, 이메일 주소 형식인지 검사
    password : SecretStr = Field(min_length=8, max_length=128) 
    # -> SecretStr : 비밀번호를 **********처럼 가려주는 자료형
    # -> Field(...): 길이 등의 검사 조건을 지정

#### cf)
### = : 값을 넣는다(대입)
### : : 어떤 자료형인지 표시한다(타입 힌트)
## email, password는 사용자가 보내는 데이터이고, model_config는 그 데이터를 처리하는 규칙
# model_config: ConfigDict = ConfigDict(extra='forbid')
#                  타입         실제 설정값
# 'model_config = ConfigDict(extra='forbid')' 
# -> ConfigDict(...)로 만든 설정값(데이터를 검사할 때 어떻게 처리할지 정한 규칙)을 model_config에 넣는 것. 
# -> 이 코드에 들어 있는 구체적인 규칙은 **“정해놓은 항목 외에 다른 항목이 들어오면 오류를 내라
# 'email: EmailStr' -> 나중에 받을 데이터의 타입을 정함. 이메일 형식의 값이 들어와야 한다”는 선언
# password: SecretStr = Field(min_length=8, max_length=128)
# ': SecretStr' → 비밀번호의 타입 / '= Field(...)' → 길이 등의 검사 규칙


@app.exception_handler(RequestValidationError) # 데코레이터
# -> 이 코드는 FastAPI에 다음 규칙을 등록
# -> “요청 데이터 검증 중 RequestValidationError가 발생하면, 바로 아래 함수를 호출해줘.”
# -> FastAPI에 “요청 데이터 검증 오류인 RequestValidationError가 발생하면 아래 함수를 실행해라”라고 등록

# "RequestValidationError" : 처리할 예외 클래스
# -> (from fastapi.exceptions import RequestValidationError) 이렇게 가져와서 사용

# 요청 데이터 검증에 실패했을 때 실행할 함수 (ex. 이메일 형식이 잘못되거나, 비밀번호가 최소 길이보다 짧을 때 실행)
def handler_validation_error(_request:Request, exc:RequestValidationError) :
    # _request -> 오류가 발생한 HTTP 요청 정보
    # RequestValidationError -> 오류의 종류(클래스)
    # exc -> 실제로 발생한 오류 정보를 담은 객체
    errors = [
        {'loc':error['loc'], 'type':error['type']}
        for error in exc.errors()
    ]
    # exc.errors()에서 오류 목록을 가져와, 각 오류의 위치와 종류만 추려 새 리스트를 만듦 
    # -> loc: 오류가 발생한 위치. 예: ('body', 'password')
    # -> type: 오류의 종류. 예: 'too_short'
    return JSONResponse(status_code=422, content={'detail':errors})
    # HTTP 상태 코드 422와 오류 목록을 JSON으로 반환
    # -> 422는 이 상황에서 요청 데이터가 검증 규칙을 만족하지 못했다는 뜻

## 사용자가 다음 요청을 보냈을 때
# {"password": "abc"}
## 다음 순서로 처리
# 1. FastAPI가 비밀번호 길이를 검사
# 2. 8자 미만이므로 RequestValidationError가 발생
# 3. 데코레이터로 등록한 handler_validation_error()가 실행
# 4. 그 함수에서 만든 오류 응답이 사용자에게 전달
# -> ex) 비밀번호가 너무 짧을 때 오류 목록 
# {
#   "detail": [
#     {
#       "loc": ["body", "password"],
#       "type": "too_short"
#     }
#   ]
# }


### 회원가입 요청을 받아 Supabase에 전달하고, 성공 여부에 따라 응답하는 API
# 사용자가 이메일·비밀번호 전송
# → FastAPI가 입력 검사
# → Supabase에 회원가입 요청
# → 오류가 있으면 오류 응답
# → 예외 없이 끝나면 안내 메시지 응답

## 1. 필요한 기능 가져오기
import httpx # httpx(패키지) : HTTP 요청을 보내는 기능 제공
from supabase import create_client, AuthApiError, AuthRetryableError, ClientOptions

class SignupResponse(BaseModel) : 
    message : str
# -> 회원가입 응답에 message라는 문자열 항목이 있어야 한다고 정의
# ex)
# {
#   "message": "회원가입이 완료되었습니다."
# }

## 2. 회원가입 API 등록
@app.post('/auth/signup', response_model=SignupResponse) # 회원가입 API 등록
# -> “/auth/signup 주소에 POST 요청이 오면 아래 함수를 실행해라”라는 데코레이터
# -> response_model=SignupResponse : 반환할 데이터를 SignupResponse 형식에 맞춰 검사하고 응답하도록 지정
# -> 위 모델을 API에 적용하려면 앞서 작성한 것처럼 response_model로 지정 (response_model=SignupResponse)

def signup(body: SignupRequest) :
# 회원가입을 처리하는 함수
# -> body: 사용자가 보낸 요청 데이터를 담는 변수
# -> SignupRequest: 요청 데이터의 형식과 검사 규칙
    
    ## 3. 오류가 발생할 수 있는 코드 실행
    try : 
    # -> 이 안의 코드를 실행하다가 예외가 발생하면, 아래의 해당 except에서 처리 
        
        ## 4. HTTP 클라이언트 만들기. 요청할때마다 클라이언트를 만들고 통신이 끝나면 자동으로 닫음 
        with httpx.Client(timeout=10.0) as http_client :
        # -> 외부 서버와 HTTP 통신할 때 사용할 객체를 만듦 
        # httpx.Client(...): HTTP 클라이언트 객체 생성
        # timeout=10.0: 네트워크 작업의 대기 제한을 10초로 설정
        # as http_client: 만든 객체를 http_client라는 이름으로 사용
        # with: 블록을 벗어날 때 연결 등의 자원을 자동으로 정리
            
            ## 5. Supabase 클라이언트 만들기
            # -> Supabase 기능을 호출할 객체를 만들어 supabase에 저장
            supabase = create_client(  # create_client(함수) : Supabase 클라이언트 객체 생성
                supabase_url = supabase_url, # 함수의_매개변수_이름 = 전달할_변수의_값
                # -> 왼쪽은 create_client()가 받는 인자 이름이고, 오른쪽은 앞에서 환경변수로 읽어둔 값
                supabase_key = supabase_key,
                options = ClientOptions( # ClientOptions(클래스) : 클라이언트의 동작 설정
                # -> ClientOptions는 Supabase 연결에 사용할 설정을 묶는 클래스
                    persist_session=False, # 로그인 세션을 저장하지 않음
                    auto_refresh_token = False, # 토큰을 자동으로 갱신하지 않음
                    httpx_client=http_client # 위에서 만든 HTTP 클라이언트 사용
                )
            )
            ### 6. Supabase에 회원가입 요청
            supabase.auth.sign_up(
            # -> supabase.auth: Supabase의 인증 기능에 접근
            # -> .sign_up(...): 회원가입 요청을 보내는 메서드
            # -> {...}: 가입에 필요한 데이터를 담은 딕셔너리
                {
                    'email' : str(body.email),  # 검증된 이메일을 문자열로 변환해서 전달
                    'password' : body.password.get_secret_value() # 출력하면 비밀번호가 가려짐 
                    # get_secret_value() : 실제 비밀번호 문자열을 꺼내는 메서드
                }
                # 검증을 통과한 후 함수 안에서 이렇게 접근할 수 있음 
                # body.email
                # body.password
            )
    ## 7. 인증 API 오류 처리
    except AuthApiError as err : # AuthApiError(예외 클래스) : 인증 API에서 반환한 오류. 
    # -> AuthApiError가 발생하면 오류 객체를 err에 담아서 처리
        if err.status == 429 :
            raise HTTPException(429, '요청이 많습니다. 잠시 후 다시 시도하세요.')
            # -> Supabase가 429 오류를 보내면, 사용자에게도 HTTP 429 응답을 보냄 
        if err.status >= 500 or err.status == 401 :
            raise HTTPException(503, '인증 서비스 상태 또는 연결 설정을 확인')
            # -> Supabase의 오류가 다음 중 하나면 사용자에게 503을 반환하도록 작성 (500 이상: 서버 측 오류, 401: 인증 관련 오류)
        raise HTTPException(400, '입력과 auth 설정을 확인하세요.')
        # -> 앞의 조건에 해당하지 않는 나머지 AuthApiError는 400으로 반환
        # -> 함수의 정상 진행이 중단되고 FastAPI가 해당 오류 응답을 만듦 
    
    ## 8. 연결 관련 오류 처리
    except(AuthRetryableError, httpx.HTTPError) : # AuthRetryableError(예외 클래스) : 일시적인 연결 문제 등 재시도할 수 있는 인증 오류
        raise HTTPException(503, '인증서비스에 연결할 수 없습니다.')
    # -> 괄호 안의 두 예외 중 하나가 발생하면 같은 방식으로 처리
    # -> 연결 실패나 타임아웃 등의 문제가 생기면 사용자에게 503 응답을 보냄 
    
    ## 9. 정상 응답 반환
    return SignupResponse(message='가입 요청을 처리했습니다. 이메일 확인 설정이 켜져있다면 받은 메일을 확인해주세요.')
    # -> 예외 없이 처리가 끝나면 응답 객체를 만듦. FastAPI가 이를 JSON으로 변환해 반환

# 사용자가 다음 JSON을 보내면:
# {
#   "email": "test@example.com",
#   "password": "abcdefgh"
# }
# 검증을 통과한 후 함수 안에서 이렇게 접근할 수 있음 
# body.email
# body.password



class LoginRequest(BaseModel) : 
    model_config = ConfigDict(extra='forbid')
    email : EmailStr
    password : SecretStr = Field(min_length=1)

class LoginResponse(BaseModel) : 
    access_token: str 
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: int | None
    user_id: str
    email: str | None

from fastapi import Response 
@app.post('/auth/login', response_model=LoginResponse) # response_model : 반환할 모델을 검증
# -> 반환할 json 구조를 검증하고, Swagger에 표시
def login(body:LoginRequest, response:Response) :
    with httpx.Client(timeout=10.0) as http_client :
        # -> 외부 서버와 HTTP 통신할 때 사용할 객체를 만듦 
        # httpx.Client(...): HTTP 클라이언트 객체 생성
        # timeout=10.0: 네트워크 작업의 대기 제한을 10초로 설정
        # as http_client: 만든 객체를 http_client라는 이름으로 사용
        # with: 블록을 벗어날 때 연결 등의 자원을 자동으로 정리
        
        supabase = create_client(  # create_client(함수) : Supabase 클라이언트 객체 생성
            supabase_url = supabase_url,
            supabase_key = supabase_key,
            options = ClientOptions( # ClientOptions(클래스) : 클라이언트의 동작 설정
            # -> ClientOptions는 Supabase 연결에 사용할 설정을 묶는 클래스
                persist_session=False, # 로그인 세션을 저장하지 않음
                auto_refresh_token = False, # 토큰을 자동으로 갱신하지 않음
                httpx_client=http_client # 위에서 만든 HTTP 클라이언트 사용
            )
        )
        result = supabase.auth.sign_in_with_password(
            {
                'email' : str(body.email),  # 검증된 이메일을 문자열로 변환해서 전달
                'password' : body.password.get_secret_value() # 출력하면 비밀번호가 가려짐 
                # get_secret_value() : 실제 비밀번호 문자열을 꺼내는 메서드
            }
            # 검증을 통과한 후 함수 안에서 이렇게 접근할 수 있음 
            # body.email
            # body.password
        )
    session = result.session 
    user = result.user
    response.headers['Cache-Contrl'] = 'no-store'
    
    return LoginResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type=session.token_type,
        expires_in=session.expires_in,
        expires_at=session.expires_at,
        user_id=user.id,
        email=user.email
    )





### 실행 : uvicorn main:app --reload