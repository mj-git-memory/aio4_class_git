### s5: 주문 조회·환불 도구를 MCP 방식으로 제공하는 서버
# 사용자
#   ↓ 자연어 요청
# s6: LLM이 도구 선택
#   ↓ MCP 통신
# s5: 선택한 도구 실행
#   ↓ HTTP 요청
# s3: 주문 조회·환불 API
#   ↓ 결과가 역순으로 전달
# s6: LLM이 결과를 읽고 답변

import httpx # s3에 HTTP 요청 (ex. httpx.get(), httpx.post())
from mcp.server.mcpserver import MCPServer # MCP 서버 생성과 클라이언트 통신(ex. MCPServer, ClientSession)

mcp = MCPServer("OrderManageMCP") # MCP 서버 객체를 만듦
# -> 반환값은 MCP 서버 객체이며, 이후 이 객체로 도구·자료·프롬프트를 등록
BASE_URL = "http://127.0.0.1:8000"

@mcp.tool() # 아래 함수를 MCP 도구로 등록
def mcp_get_order(order_id:str)->dict:
    """주문 번호(order_id)로 외부 REST API에서 주문 상태와 금액을 조회합니다.""" # 도구의 기능을 설명하는 문서 문자열
    resp = httpx.get(f"{BASE_URL}/api/orders/{order_id}", timeout=5.0)
    # order_id="ORD_1001"이면 다음 URL로 요청 -> http://127.0.0.1:8000/api/orders/ORD_1001
    # -> httpx.get()은 HTTP 응답 객체를 반환 & 그 객체에서 필요한 정보를 꺼냄
    return resp.json() if resp.status_code == 200 else {"error": resp.text}
    # resp.status_code  # 예: 200 / resp.text # 응답 본문 문자열  / resp.json() # JSON 본문을 파이썬 데이터로 변환
    # {
    #     "order-id": "ORD-1001",
    #     "item": "big bag",
    #     "amount_krw": 100,
    # }

@mcp.tool()
def submit_refund_via_rest(order_id: str, reason: str) -> dict:
    """주문 번호(order_id)와 사유(reason)로 외부 REST API에 환불을 접수합니다."""
    resp = httpx.post(
        f"{BASE_URL}/api/orders/refund",
        json={"order_id": order_id, "reason": reason}, # json=은 서버에 전달할 JSON 데이터를 지정
        # 환불 처리에는 서버가 알아야 할 정보가 있음 -> 그 정보를 HTTP 요청의 본문에 담아 보내기 위해 json=을 사용
        timeout=5.0,
    )
    return resp.json() if resp.status_code == 200 else {"error": resp.text}  
    # {
    #     "order_id": "ORD_1002",
    #     "refund_status": "ACCEPTED",
    #     "reason": "배송 지연 우려",
    #     "refund_amount_krw": 200,
    # }

# 2. MCP Resource: 클라이언트/모델이 참고할 정책 문서
@mcp.resource("policy://refund-rules")  # 환불 정책 자료 제공
def get_refund_policy() -> str:
    """사내 환불 정책 안내 문서를 반환합니다."""
    return "환불 규정: 배송 준비중(PREPARING) 상태는 즉시 환불 가능하며, 배송 완료 후 7일 이내 단순 변심 환불이 가능합니다."
    # 환불 규정 문자열 반환 


# 3. MCP Prompt: 표준화된 응대 프롬프트 템플릿
@mcp.prompt() # LLM에 전달할 지시문을 만드는 기능 -> 고객 응대 지시문 생성
def cs_response_template(order_id: str) -> str:
    """고객 주문 응대를 위한 표준 프롬프트를 생성합니다."""
    return f"주문 번호 {order_id}의 현재 상태와 환불 가능 여부를 친절한 한국어로 안내해 주세요."
    # 주문 번호가 포함된 문자열 반환


if __name__ == "__main__":
    mcp.run(transport="stdio") # 서버 실행 
    # mcp :앞에서 생성한 MCP 서버 객체 / .run(...) : 서버를 실행하고 MCP 요청을 처리하는 메서드
    # transport= : 통신 방식을 지정하는 인자 / "stdio" : 표준 입력·출력으로 메시지를 주고받는 방식


# mcp dev s5_order_mcp_server.py --with "mcp[cli]==2.3.0" --with httpx  # 로 실행

 
# 개념	            쉬운 정의	                           정확한 정의
# MCP	           AI 앱과 도구를 연결하는 공통 규칙	       AI 애플리케이션과 외부 도구·데이터 사이의 상호작용을 표준화한 프로토콜
# MCP 서버	        사용할 도구와 자료를 제공하는 프로그램	       MCP 요청을 받아 도구·리소스·프롬프트 등의 기능을 제공하는 프로그램
# MCP 클라이언트	  MCP 서버에 요청하는 쪽	               서버와 연결하여 MCP 요청을 전송하고 응답을 처리하는 구성 요소
# Tool	           실행할 수 있는 기능	                    이름·설명·입력 스키마로 정의되고 클라이언트가 호출할 수 있는 서버 기능
# Resource	       참고할 자료	                           URI로 식별되어 클라이언트가 읽을 수 있는 서버의 데이터
# Prompt	       재사용하는 질문·지시문 틀	              인자를 받아 메시지를 구성하는 서버 제공 프롬프트 템플릿
# 스키마	         데이터의 입력 양식	                      데이터의 구조, 타입, 필수 항목 등을 정의한 명세
# stdio	           프로그램의 입력·출력으로 대화하기	        표준 입력과 표준 출력을 통해 MCP 메시지를 교환하는 전송 방식
# 비동기	        응답을 기다리는 동안 다른 작업도 가능하게 하기   대기 지점에서 실행권을 이벤트 루프에 돌려주는 방식
# 세션	            연결된 상대와 대화를 관리하는 객체	          초기화 및 요청·응답의 연결 관계 등을 관리하는 통신 객체

# 구분	                  쉬운 의미 	             현재 코드의 예
# @mcp.tool()	        “이 일을 해 줘”	            주문 조회, 환불 접수
# @mcp.resource(...)	“이 자료를 읽어 줘”	         환불 정책 문서
# @mcp.prompt()	        “이 지시문 틀을 만들어 줘”	   고객 응대용 프롬프트