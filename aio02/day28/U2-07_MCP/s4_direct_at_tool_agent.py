# REST API를 Python @tool로 직접 래핑해 LLM 바인딩 --> langchain  LCEL  chatopenai & openai
# systemmessage humanmessage toolmessage(id)
# message(system, human) -> llm -> message추가 -> tools 순환하면서 각 결과를 message에 추가(toolmessage)
# llm ai_msg 추가 -> 툴을 찾고 -> 툴을 순환하면서 결과를 가지고 메시지에 추가 -> 마지막에 다시 한번 llm에 전달 


### s4: REST API를 사용하는 AI 에이전트
import json # 	파이썬 데이터를 JSON 문자열로 변환 (ex. json.dumps(out))
import httpx # 	서버에 HTTP 요청 (ex. httpx.get(), httpx.post())
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage 
# 대화와 도구 결과를 표현 (ex. HumanMessage(...) 등)
from langchain_core.tools import tool  # 함수를 AI 도구로 구성 (ex.	@tool)
from langchain_openai import ChatOpenAI # OpenAI 모델을 LangChain에서 호출(ex.ChatOpenAI(...))

load_dotenv(find_dotenv(), override=True)
BASE_URL = "http://127.0.0.1:8000"  
# -> s4_direct_at_tool_anget.py를 실행하려면 s3_fastapi_server.py가 실행되어 있어야 함


@tool
def fetch_order_via_rest(order_id: str) -> dict:
    """주문 번호(order_id)로 외부 REST API에서 주문 상태와 금액을 조회합니다."""
    resp = httpx.get(f"{BASE_URL}/api/orders/{order_id}", timeout=5.0) 
    # httpx.get()의 반환값은 주문 딕셔너리가 아니라 HTTP 응답 객체
    if resp.status_code != 200: # resp.status_code  # 상태 코드: 예) 200
        return {"error": resp.text, "status_code": resp.status_code} # resp.text : 응답 본문 문자열
    return resp.json() # resp.json() : JSON을 파이썬 데이터로 변환 -> 이 API에서는 주문 딕셔너리 반환


@tool
def submit_refund_via_rest(order_id: str, reason: str) -> dict:
    """주문 번호(order_id)와 사유(reason)로 외부 REST API에 환불을 접수합니다."""
    resp = httpx.post(
        f"{BASE_URL}/api/orders/refund",
        json={"order_id": order_id, "reason": reason},
        timeout=5.0,
    )
    if resp.status_code != 200:
        return {"error": resp.text, "status_code": resp.status_code}
    return resp.json()

### AI의 선택이 실제 함수 실행으로 이어지는 부분
def run_direct_tool_agent(query: str) -> str:
    tools = [fetch_order_via_rest, submit_refund_via_rest]
    # -> @tool이 적용된 함수는 LangChain 도구 객체가 됨
    registry = {t.name: t for t in tools} # registry는 도구 이름으로 도구를 찾는 사전
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools) 
    # bind_tools() : 모델이 도구를 선택하도록 정의를 전달

    messages = [
        SystemMessage(content="주문 조회 및 환불 처리는 제공된 REST API 도구를 호출해 안내하세요."),
        HumanMessage(content=query),
    ]

    for _ in range(5):
        ai_msg = llm.invoke(messages) # 실제 함수 실행
        messages.append(ai_msg)
        if not ai_msg.tool_calls: # 도구 호출이 없으면 최종 답변을 반환하고 종료
            return ai_msg.content       # ai_msg.content : 답변 내용
        for call in ai_msg.tool_calls:  # ai_msg.tool_calls : 호출할 도구 목록
            out = registry[call["name"]].invoke(call["args"])
            # {
            #     "name": "submit_refund_via_rest",
            #     "args": {
            #         "order_id": "ORD_1002",
            #         "reason": "중복 주문",
            #     },
            #     "id": "call_123",
            #     "type": "tool_call",
            # }
            print(f"  [@tool 직접 호출] {call['name']} - ({call['args']}) -> {out}")
            messages.append(ToolMessage(content=json.dumps(out, ensure_ascii=False), tool_call_id=call["id"]))
            # json.dumps() → 딕셔너리를 JSON 문자열로 변환
            # ensure_ascii=False → 한글을 그대로 표현
            # tool_call_id → 어떤 도구 호출의 결과인지 연결
            # messages.append() → 대화 기록에 추가하며, 반환값은 None
    return "반복 초과"


if __name__ == "__main__":
    print(run_direct_tool_agent("ORD_1001 주문 상태 알려주고, ORD_1002는 '중복 주문' 사유로 환불 접수해줘."))