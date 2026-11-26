## s3_fastapi_server.py와 s4_direct_at_tool_agent.py
# -> 두 파일은 함께 **“사용자의 말을 이해하고, 주문 조회·환불 API를 호출하는 AI 상담원”**을 만듦 
# - s3: 주문 조회와 환불 접수 기능을 제공하는 서버
# - s4: 사용자의 요청을 읽고, 필요한 서버 기능을 호출하는 AI 프로그램
# -> 현재 두 파일은 REST API와 LangChain 도구 호출로 연결
## 사용자 요청
#    ↓
# s4: LLM이 도구와 입력값 선택
#    ↓
# s4: httpx로 HTTP 요청
#    ↓
# s3: 주문 조회 또는 환불 접수 처리
#    ↓
# s4: 처리 결과를 LLM에 전달
#    ↓
# 사용자에게 자연어로 답변

### s3: 주문·환불 API 서버
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel # 요청 데이터의 필드와 타입을 정의
import uvicorn

app = FastAPI(title="external order & inventory api") # API 앱 객체를 생성 → app에 저장
 
ORDERS = {
    "ORD_1001":{'order-id':'ORD-1001', 'item':'big bag','amount_krw':100},
    "ORD_1002":{'order-id':'ORD-1002', 'item':'USB-C type','amount_krw':200}
}

class RefundRequest(BaseModel):
    order_id:str
    reason:str

@app.get("/api/orders/{order_id}") # GET 요청을 처리할 함수 등록
def get_order(order_id: str):
    order = ORDERS.get(order_id.upper()) # order = ORDERS.get(key) -> 그 문자열로 딕셔너리 조회
    if not order:
        raise HTTPException(status_code=404, detail="Order not found") # raise : 정상 실행을 중단하고 오류를 발생
    return order


@app.post("/api/orders/refund") # POST 요청을 처리할 함수 등록
def request_refund(req: RefundRequest):
    order = ORDERS.get(req.order_id.upper())
    if not order:
        raise HTTPException(status_code=404, detail="Order not found") # 오류 응답을 발생시킴
    return {
        "order_id": req.order_id.upper(),
        "refund_status": "ACCEPTED",
        "reason": req.reason,
        "refund_amount_krw": order["amount_krw"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) # 앱을 실행하고 요청을 기다림



# 개념	            쉬운 정의	                                 이 코드의 예시
# 서버	            요청을 기다렸다가 처리하는 프로그램	                s3
# 클라이언트	      서버에 요청을 보내는 프로그램	                    s4
# API	           다른 프로그램의 기능을 사용하는 약속	               주문 번호를 보내면 주문 정보 반환
# REST API	       URL과 HTTP 요청 방식으로 기능을 사용하는 API	      GET /api/orders/ORD_1001
# GET / POST	   GET은 조회, POST는 데이터 전송·처리 요청	         주문 조회 / 환불 접수
# JSON	           프로그램끼리 데이터를 주고받는 텍스트 형식	        {"order_id": "ORD_1001"}
# 데코레이터	      함수 위에 붙여 역할을 추가하는 문법	             @app.get(...), @tool
# LLM	           사용자의 말을 이해하고 답변을 만드는 AI 모델	        ChatOpenAI
# 도구 호출          AI가 사용할 함수 이름과 인자를 선택하는 것	          환불 함수와 주문 번호 선택
# 에이전트	         판단 → 도구 실행 → 결과 확인을 반복하는 프로그램      run_direct_tool_agent()


# 개념	         쉬운 정의	                             정확한 정의	                                                    	                                 이 코드의 예시
# 서버	         요청을 기다렸다가 처리하는 프로그램	        클라이언트의 요청을 받아 정해진 기능이나 데이터를 제공하는 프로그램	                                                  s3의 FastAPI 앱
# 클라이언트	   서버에 요청을 보내는 프로그램	            서버의 기능이나 데이터를 사용하기 위해 요청을 보내고 응답을 받는 프로그램	                                           s4에서 httpx로 요청
# API	        다른 프로그램의 기능을 사용하는 약            소프트웨어 구성 요소 간 상호작용을 위해 정의한 기능, 입력·출력 형식 및 사용 규칙의 집합	                                주문 번호를 전달하면 주문 정보를 반환
# REST API	    URL과 HTTP 방식으로 기능을 사용하는 API	    자원을 식별하고, 일관된 인터페이스와 무상태 통신 등 REST 아키텍처의 제약을 따르는 API	                                GET /api/orders/ORD_1001
# GET / POST	GET은 조회, POST는 데이터 전송·처리 요청     GET은 대상 자원의 표현을 요청하는 HTTP 메서드이며, POST는 전달한 데이터를 대상 자원의 규칙에 따라 처리하도록 요청하는 메서드	 주문 조회 / 환불 접수
# JSON	        프로그램끼리 데이터를 주고받는 텍스트 형식	    객체, 배열, 문자열, 숫자, 불리언, null로 구조화된 데이터를 표현하는 텍스트 기반 데이터 교환 형식	                      {"order_id": "ORD_1001"}
# 데코레이터	   함수 위에 붙여 역할을 추가하는 문법	         함수나 클래스를 인자로 받아, 처리 결과를 원래 이름에 다시 바인딩하는 파이썬 문법	                                     @app.get(...), @tool
# LLM	        사용자의 말을 이해하고 답변을 만드는 AI 모델    대규모 데이터로 학습하여 문맥에 따른 토큰의 확률을 모델링하고 텍스트 등을 생성하는 언어 모델	                           ChatOpenAI를 통해 호출하는 모델
# 도구 호출	      AI가 사용할 함수와 입력값을 선택하는 것	     모델이 도구 이름과 구조화된 인자를 출력하고, 실행 프로그램이 이를 받아 해당 도구를 실행하는 방식	                         모델이 환불 도구와 주문 번호·사유를 선택
# 에이전트	      판단하고 도구를 실행하며 작업하는 프로그램       목표 달성을 위해 모델의 판단, 도구 실행, 실행 결과의 관찰을 반복하며 다음 행동을 결정하는 시스템	                          run_direct_tool_agent()