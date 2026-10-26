# fastapi라는 도구 묶음에서 FastAPI 클래스를 가져옴
# 클래스는 객체를 만드는 설계도라고 생각하면 됨
from fastapi import FastAPI
# fastapi.responses에서 HTMLResponse 클래스를 가져옴
from fastapi.responses import HTMLResponse

# 설계도(FastAPI)로 이번 실습에서 사용할 웹 앱 객체를 하나 만듦
# app은 그 객체를 가리키는 변수 이름이며, 다른 이름으로 바꿔도 됨
# title="Lesson 01"은 /docs 문서 화면의 제목이며 접속 주소를 나타내지는 않음
# 이 줄만 실행해도 서버가 켜지는 것은 아님. 아래 실행 명령으로 Uvicorn을 켜야 함
app = FastAPI(title="Lesson 01")

# 브라우저 주소창에 http://127.0.0.1:8000/ 를 입력하면 GET / 요청이 옴
# @app.get("/")는 "그 요청을 받으면 바로 아래 root 함수를 실행해라"라는 등록임
# 이런 @ 문법을 데코레이터라고 함 
@app.get("/", response_class=HTMLResponse) # response_class=HTMLResponse : HTML을 그대로 브라우저에 보여주겠다는 뜻
# @app.get("/") 
# root라는 함수를 정의. 접속할 때 FastAPI가 이 함수를 호출.
def root():  
    # 딕셔너리를 반환. return은 print처럼 터미널에 출력하는 명령이 아님
    # FastAPI가 이 값을 JSON 응답으로 바꾸므로 요청한 브라우저에 내용이 보임
    # return {"message": "Hello FastAPI"}
    return '''
            <h1>FastAPI Lesson 01: Hello FastAPI</h1>
            '''


# 이번에는 http://127.0.0.1:8000/sports 로 접속해 본다.
# 같은 서버지만 경로가 /sports이므로 root가 아니라 sports 함수가 실행됨 
@app.get('/sports')
def sports():
    # "sports"라는 키에 스포츠 이름 목록(리스트)을 담은 딕셔너리를 반환
    return {"sports": ["축구", "야구", "농구", "배구", "테니스"]}


# GET /menu 요청을 받으면 show_menu 함수를 실행하도록 등록한다.
# 예: http://127.0.0.1:8000/menu 에 접속하면 아래 음식 목록을 받는다.
@app.get('/menu')
# show_menu()라는 함수 이름만으로 URL이 생기지는 않음. 위의 등록이 필요
def show_menu():  
    # {키: 값}은 딕셔너리이고, 대괄호 안의 여러 음식은 리스트
    # 응답 예: {"menu": ["짜장면", "짬뽕", "탕수육", "군만두", "볶음밥"]}
    return {"menu": ["짜장면", "짬뽕", "탕수육", "군만두", "볶음밥"]}


# 직접 실행해 보기 (현재 터미널 위치: day5, 가상환경이 활성화된 상태)
# 1. python -m uvicorn day5.labs.lesson01:app --reload
#    day5.labs.lesson01:app -> day5/labs/lesson01.py 파일의 app 객체를 사용
# 2. 브라우저에서 http://127.0.0.1:8000/ 접속 -> 인사말 확인
# 3. 브라우저에서 http://127.0.0.1:8000/sports 접속 -> 스포츠 목록 확인
# 4. 위의 "Hello FastAPI"를 "안녕하세요"로 바꾸고 파일 저장
#    --reload 덕분에 서버가 자동 재시작됨. 브라우저를 새로고침하면 바뀐 인사말이 보임

# 5. http://127.0.0.1:8000/docs 접속 -> 자동 생성된 API 사용 설명서 확인
# 6. /sports의 GET 항목에서 Try it out -> Execute 클릭 -> 스포츠 목록 응답 확인
# 7. 터미널에서 Ctrl + C -> 서버 종료. 이후에는 브라우저에서 새 요청을 보낼 수 없음
# 참고: root와 sports라는 함수 이름을 바꿔도 데코레이터의 경로가 같으면 접속 주소는 같음



# ==================== 추가 설명 시작: 메서드 · 엔드포인트 · 라우팅 ====================

### 1. 메서드(Method): 요청으로 무엇을 하려는지 나타내는 방식
# 여기서 메서드는 'HTTP 메서드'다. 클래스 안에 정의한 함수를 뜻하는 메서드와는 문맥이 다름
# GET: 보통 정보를 조회할 때 사용. 예: 음식 목록을 보여 줘.
# POST: 보통 데이터를 제출하거나 생성할 때 사용. 예: 새 주문을 등록해 줘.
# PUT: 보통 대상 데이터를 전체 교체. 예: 메뉴 한 개의 정보를 새 정보로 교체해 줘.
# PATCH: 보통 일부만 수정. 예: 메뉴 이름은 두고 가격만 바꿔 줘.
# DELETE: 보통 삭제. 예: 이 메뉴를 지워 줘.
# 메서드 이름만 지정한다고 DB 조회/저장이 자동 실행되지는 않음. 함수 안에 구현해야 함
# 이 파일의 @app.get은 모두 GET 요청을 받도록 등록한다는 뜻
# 브라우저 주소창에 http://127.0.0.1:8000/menu를 입력하면 GET /menu 요청을 보냄
# 브라우저도 버튼/폼/자바스크립트 등을 통해 다른 메서드로 요청할 수 있음

### 2. 엔드포인트(Endpoint): API의 기능에 접근하는 접점
# 예: 음식 목록 기능에 접근할 주소는 http://127.0.0.1:8000/menu
# 이 중 서버 주소는 http://127.0.0.1:8000이고 경로는 /menu
# *** 대화에서는 /menu 같은 경로 자체를 엔드포인트라고 부르기도 한다. ***
# 기능을 정확히 구분할 때는 메서드까지 함께 적음. 예: GET /menu.
# *** 이 파일에서 직접 만든 API 엔드포인트: ***
# GET /       -> 인사말 받기
# GET /sports -> 스포츠 목록 받기
# GET /menu   -> 음식 목록 받기
# 함수 이름 show_menu가 엔드포인트 주소를 정하는 것은 아님. @app.get('/menu')의 경로가 정함
# 예: 함수 이름만 view_menu로 바꿔도 등록 경로가 /menu이면 접속 주소는 그대로다.

### 3. 라우팅(Routing): 요청에 맞는 처리 함수를 찾아 연결하는 것
# 비유: 안내 직원이 '음식 목록을 보러 왔어요'라는 요청을 음식 목록 담당자에게 보내는 일.
# 이 파일의 @app.get(...)은 아래 연결 규칙을 미리 등록
# 메서드 | 경로    | 담당 함수
# GET    | /       | root
# GET    | /sports | sports
# GET    | /menu   | menu

### 실제로 GET /menu가 들어왔을 때:
# 1. Uvicorn이 브라우저의 요청을 받아 app에 전달함 
# *** 2. FastAPI가 등록된 규칙에서 GET과 /menu에 맞는 담당 함수를 찾는다. 이것이 라우팅이다. ***
# 3. 담당 함수 show_menu()를 실행한다.
# 4. 반환한 딕셔너리를 JSON 응답으로 만들어 브라우저에 보냄 
# 따라서 '엔드포인트'는 요청할 접점, '라우팅'은 그 요청을 담당 함수로 보내는 연결 과정이다.

### 만약 POST /menu를 요청한다면?
# 이 파일에는 GET /menu만 있고 POST /menu는 없음. 따라서 405 Method Not Allowed가 됨 
# POST 요청도 받으려면 @app.post('/menu')로 별도의 처리 규칙과 함수를 작성해야 함
# /unknown처럼 등록하지 않은 경로에 GET 요청을 보내면 404 Not Found가 됨 

# 직접 확인: 서버 실행 후 아래 두 주소를 브라우저에서 각각 열어 본다.
# http://127.0.0.1:8000/menu   -> GET /menu -> menu() -> 음식 목록 응답
# http://127.0.0.1:8000/sports -> GET /sports -> sports() -> 스포츠 목록 응답
# 같은 서버여도 경로가 다르므로 라우팅 결과인 담당 함수와 응답 내용이 달라진다.

# ==================== 추가 설명 끝: 메서드 · 엔드포인트 · 라우팅 ====================
