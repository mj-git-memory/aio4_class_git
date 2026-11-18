### Lesson 02: 같은 /method 주소라도 GET과 POST를 구분해서 처리하기
# 실행 위치: day5 폴더 / 실행 명령: python -m uvicorn labs.lesson02:app --reload
# 다른 실습 서버가 8000번 포트를 사용 중이면 해당 터미널에서 Ctrl + C로 먼저 종료한다.

# FastAPI 클래스를 가져온다. 이 클래스로 이번 실습의 웹 앱을 만든다.
from fastapi import FastAPI

# 이번 파일 전용 앱을 만든다. /docs에서 문서 제목이 Lesson 02인지 확인할 수 있다.
# lesson01.py의 app과 이름은 같지만, 서로 다른 파일에서 만든 별개의 객체다.
app = FastAPI(title="Lesson 02")

# *** 메서드: 요청으로 무엇을 하려는지 나타내는 HTTP의 구분. GET은 보통 조회, POST는 생성/처리. ***
# *** 경로: /method처럼 서버 주소 뒤에 붙는 부분. ***
# *** 여기서 다루는 API는 'HTTP 메서드 + 경로'로 구분한다. 예: GET /method, POST /method. ***
# *** 라우팅: 들어온 요청에 맞는 함수를 찾아 연결하는 것. ***
# *** 예: GET /method -> read_method(), POST /method -> create_method(). ***

# 브라우저 주소창에서 http://127.0.0.1:8000/method 로 접속하면 GET 요청이 온다.
### GET은 보통 데이터를 읽을 때 사용하지만, 아래 예제는 고정된 안내 데이터만 반환한다.
@app.get("/method")
# read_method는 GET /method 요청을 처리할 함수. 인자로 받을 입력값은 없다.
def read_method():  
    # "method"와 "purpose"는 응답 데이터의 키이고 "GET", "read"는 문자열 값이다.
    # 이 문자열을 적었다고 조회 기능이 자동으로 생기는 것은 아니다.
    # 상태 코드를 따로 지정하지 않았으므로 정상 응답은 기본값 200 OK다.
    return {"method": "GET", "purpose": "read"}


### POST /method 요청은 아래 함수가 처리한다. 경로가 같아도 GET과 구분된다.
# status_code=201: 정상 반환 시 "새 데이터 생성 성공"을 뜻하는 상태 코드를 보낸다.
# 중요: 이 예제는 DB 저장 코드가 없어서 실제 데이터를 생성하지 않는다. 상태 코드 설정 연습이다.
# 실제 주문 API라면 주문을 저장하는 코드를 작성하고, 저장 성공 결과를 201로 알려야 한다.
@app.post("/method", status_code=201)
# @app.post("/method") # 비교하려면 위 줄을 주석 처리하고 해당 줄을 사용. 정상 응답 코드가 201에서 200으로 바뀜. default:200
# create_method는 POST /method 요청이 왔을 때 FastAPI가 호출할 함수.
def create_method():  
    # 아래 딕셔너리는 두 설정에서 동일하다. 상태 코드와 응답 내용은 별개다.
    return {"method": "POST", "purpose": "create"}


# 직접 비교하기
# 1. 서버 실행 후 http://127.0.0.1:8000/docs 로 접속한다.
# 2. GET /method -> Try it out -> Execute: 응답 Code 200과 응답 내용 확인.
# 3. POST /method -> Try it out -> Execute: 응답 Code 201과 응답 내용 확인.
# 4. status_code=201을 생략하고 저장 후 문서를 새로고침해서 POST를 다시 실행한다.
#    Code는 200이지만 Response body는 이전과 같다. POST라고 자동으로 201이 되지는 않는다.
# 브라우저 주소창으로 /method에 접속하면 GET이므로, POST는 /docs에서 위 방법으로 요청한다.

# 로그 예: INFO: 127.0.0.1:61736 - "GET / HTTP/1.1" 404 Not Found
# 127.0.0.1:61736 -> 요청을 보낸 클라이언트의 IP와 임시 포트. 서버 포트 8000과 다르다.
# GET / -> 브라우저가 루트 경로(/)를 조회했다. HTTP/1.1은 통신 규약의 버전이다.
# 404 -> 이 앱에는 @app.get("/")가 없어서 해당 경로를 찾지 못했다는 뜻.
# 서버 고장이라는 뜻은 아니다. 등록된 /method 또는 /docs로 접속하면 된다.
