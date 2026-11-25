# tool_choice 정책 제어와 다중/병렬 동적 호출
import json
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv(), override=True)

### -> 이번 핵심은 tool_choice로 도구 사용 여부를 제어하고, 한 번의 LLM 응답에서 여러 도구 호출을 받는 것
## 1. 지연시간 조회 도구
@tool
def get_region_latency(region: str) -> dict:
    """리전(ap-northeast-2, us-east-1, eu-central-1)의 평균 네트워크 지연(ms)을 조회합니다."""
    latencies = {
        "ap-northeast-2": 14,
        "us-east-1": 148,
        "eu-central-1": 215,
    }
    r = region.lower()
    return {"region": r, "latency_ms": latencies.get(r, 99)}
    # get_region_latency.invoke({"region": "ap-northeast-2"})
    # -> {"region": "ap-northeast-2", "latency_ms": 14}

## 2. 질문과 도구 사용 정책 받기
def run_with_choice(query: str, tool_choice: str = "auto") -> str:
    # query -> 사용자 질문 / tool_choice -> 도구 사용 정책. 생략하면 "auto"
    # "auto" : LLM이 도구를 사용할지 판단 / "required" : LLM이 반드시 하나 이상의 도구 호출을 요청해야 함
    
    ## 3. 도구 이름으로 실행할 도구 찾기
    tools = [get_region_latency]
    registry = {t.name: t for t in tools} # 나중에 LLM이 반환하는 도구 이름으로 실제 도구를 찾기 위한 준비
    ## 4. 모델에 도구와 정책 연결하기
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools, tool_choice=tool_choice)
    # ChatOpenAI: OpenAI 모델을 호출하는 객체 / .bind_tools(): 도구 정보와 사용 정책 연결 / temperature=0: 응답의 무작위성을 낮춤
    ## 5. 질문을 보내고 도구 호출 정보 받기
    messages = [HumanMessage(content=query)]
    ai_msg = llm.invoke(messages)
    messages.append(ai_msg)
    # -> HumanMessage에 질문을 담아 보내고, 받은 AI 응답을 대화 기록에 추가

    print(f"[5차시 | tool_choice={tool_choice}] tool_calls 개수: {len(ai_msg.tool_calls)}")
    print('---')
    ## 6. 요청한 도구를 실행하기
    for call in ai_msg.tool_calls:
        out = registry[call["name"]].invoke(call["args"])
        print(f"  -> {call['name']}({call['args']}) => {out}")
        # call["name"] : registry에서 실행할 도구 선택 / call["args"] : 도구에 입력값 전달

        ## 7. 결과를 LLM에게 전달하기
        messages.append(ToolMessage(content=json.dumps(out, ensure_ascii=False), tool_call_id=call["id"]))
        # call["id"] : 실행 결과와 호출 요청 연결
        # json.dumps(): 결과 딕셔너리를 JSON 문자열로 변환 / ToolMessage: 도구 실행 결과를 담는 메시지 / tool_call_id: 어느 호출 요청의 결과인지 표시
    
    ## 8. 최종 응답 반환하기
    if ai_msg.tool_calls:
        return llm.invoke(messages).content  # 도구를 호출했다면: 결과를 포함해 LLM에 다시 질문하고 답변 반환
    return ai_msg.content  # 호출하지 않았다면: 처음 받은 답변을 바로 반환

    # LLM 응답인 AIMessage에는 서로 다른 정보를 담는 공간이 있음
    # 속성	             담기는 내용
    # .content	        사람이 읽는 답변 문장
    # .tool_calls	    파이썬에 실행을 요청하는 도구 이름과 입력값

## 9. 실행 결과와 현재 코드의 주의점
if __name__ == "__main__":
    # 첫 번째 질문은 두 지역을 비교해 달라는 요청
    print(run_with_choice("서울(ap-northeast-2)과 버지니아(us-east-1) 지연시간을 함께 비교해줘.", "auto"))
    # -> LLM은 보통 같은 도구를 입력값만 바꿔 두 번 호출하도록 요청
    print("-" * 60)
    print(run_with_choice("도구 없이 일반 인사만 해줘. 단 ap-northeast-2 지연시간도 함께 알려줘.", "required"))
    # -> 질문에 “도구 없이”라고 써도 API 설정이 도구 호출을 강제하므로 도구 호출이 필요
    # -> 도구 호출을 강제하면 LLM이 일반 답변 대신 “이 도구를 실행해줘”라는 요청을 반환하기 때문에 content가 비어 있을 수 있음
    # "required"로 요청하면 아래처럼 응답할 수 있음 -> 응답이 없는 게 아니라, 응답의 핵심이 content 대신 tool_calls에 들어 있는 것
    # ai_msg.content = ""
    # ai_msg.tool_calls = [
    #     {
    #         "name": "get_region_latency",
    #         "args": {"region": "ap-northeast-2"},
    #         "id": "call_001",
    #         "type": "tool_call"
    #     }
    # ]
    # LLM: “서울 지연시간 조회 도구를 실행해줘.” → tool_calls
    # 파이썬: 도구 실행 → 14ms
    # LLM: “서울 지연시간은 14ms입니다.”       → content
    # -> 그런데 마지막 단계에도 "required"를 적용하면, LLM은 다시 도구 호출 요청을 해야 함. 그래서 최종 문장인 .content가 비어 있을 수 있는 것
    # 다만 "required"가 무조건 content를 빈 문자열로 만드는 규칙은 아님. 도구 호출이 필수이고, 그 응답에는 일반 설명 문장이 생략될 수 있다고 이해하면 정확


# 첫 번째 질문은 두 지역을 비교해 달라는 요청이에요.
# 서울(ap-northeast-2)과 버지니아(us-east-1) 지연시간을 함께 비교해줘.
# LLM은 보통 같은 도구를 입력값만 바꿔 두 번 호출하도록 요청합니다.
# ai_msg.tool_calls = [
#     {
#         "name": "get_region_latency",
#         "args": {"region": "ap-northeast-2"},
#         "id": "call_001",
#         "type": "tool_call"
#     },
#     {
#         "name": "get_region_latency",
#         "args": {"region": "us-east-1"},
#         "id": "call_002",
#         "type": "tool_call"
#     }
# ]
# len(ai_msg.tool_calls) # 2

# out = registry[call["name"]].invoke(call["args"]) 
# # -> 아래와 같음 
# out = get_region_latency.invoke({
#     "region": "ap-northeast-2"
# })
# # {"region": "ap-northeast-2", "latency_ms": 14}

# # 파일 주석에는 “병렬”이라고 적혀 있지만, 실제 파이썬 실행은 for문으로 하나씩 순서대로 처리
# # -> 한 번의 LLM 응답에서 여러 호출 요청을 받는 구조

# 사용자 질문 -> AI의 도구 호출 요청 2개 -> 서울 조회 결과: 14ms -> 버지니아 조회 결과: 148ms
# [5차시 | tool_choice=auto] tool_calls 개수: 2
#   -> get_region_latency(...) => {'region': 'ap-northeast-2', 'latency_ms': 14}
#   -> get_region_latency(...) => {'region': 'us-east-1', 'latency_ms': 148}
# 서울은 14ms, 버지니아는 148ms로 서울의 지연시간이 134ms 더 낮습니다.
