## 1. 사용할 패키지
import json
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
# SystemMessage	: 모델에게 처리 지침 전달
# HumanMessage : 사용자 질문 전달
# ToolMessage :	도구 실행 결과 전달 — 현재는 사용하지 않음
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI # ChatOpenAI : OpenAI 모델을 호출하는 객체

load_dotenv(find_dotenv(), override=True)

## 2. 첫 번째 도구: 사용자 호출 한도 조회
@tool  # 파이썬 함수를 LLM이 선택할 수 있는 도구로 변환
def lookup_user_quota(user_id: str) -> dict:        
    """사용자 ID(user_id)의 일일 API 호출 한도와 현재 사용량을 조회합니다."""
    quotas = {
        "U-100": {"daily_limit": 1000, "used": 640},
        "U-200": {"daily_limit": 5000, "used": 4890},
    }
    q = quotas.get(user_id.upper(), {"daily_limit": 500, "used": 120})  # .get(키, 기본값): 사용자를 찾고, 없으면 기본값 사용
    return {"user_id": user_id.upper(), **q, "remaining": q["daily_limit"] - q["used"]}
    # -> # 사용자 ID를 받아 일일 한도, 사용량, 남은 호출량을 반환
# 예를 들어 다음처럼 도구를 실행하면:  lookup_user_quota.invoke({"user_id": "U-100"})
# -> 반환값 
# {
#     "user_id": "U-100",
#     "daily_limit": 1000,
#     "used": 640,
#     "remaining": 360
# }

## 3. 두 번째 도구: 초과 요금 계산
@tool
def calc_overage_cost(overage_calls: int, unit_cost_krw: int = 50) -> dict:
    """초과 호출 건수(overage_calls)와 건당 단가(unit_cost_krw)로 추가 과금을 계산합니다."""
    safe_calls = max(0, overage_calls) # max()로 음수가 들어와도 초과 건수를 최소 0으로 처리
    return {"overage_calls": safe_calls, "unit_cost_krw": unit_cost_krw, "overage_krw": safe_calls * unit_cost_krw}
    # -> 초과 호출 건수와 건당 단가를 받아 요금을 계산
# calc_overage_cost.invoke({"overage_calls": 40})
# -> 반환값
# {
#     "overage_calls": 40,
#     "unit_cost_krw": 50,
#     "overage_krw": 2000
# }

## 4. 두 도구를 사용할 실행 함수
## 메인 실행 함수
def execute_dynamic_agent(prompt: str, tools_list: list) -> str:  # prompt: 사용자 질문 / tools_list: 사용할 도구 목록
    # if/elif 분기 대신 이름 -> BaseTool 매핑 레지스트리 사용
    tool_registry = {t.name: t for t in tools_list} # 딕셔너리 컴프리헨션. 함수 안에서는 먼저 도구를 이름으로 찾을 수 있도록 정리
    # {
    # "lookup_user_quota": lookup_user_quota,
    # "calc_overage_cost": calc_overage_cost
    # }
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools_list) 
    # -> .bind_tools() : 도구 이름·설명·입력 규칙을 모델에 연결 / 이 시점에 도구가 실행되지는 않음 

    messages = [   # 지침과 질문을 준비
        SystemMessage(content="쿼터 조회와 초과 과금 계산은 제공된 도구를 동적으로 호출해 처리하세요."),
        HumanMessage(content=prompt),
    ]

    ## 1. LLM 호출을 반복하기
    # 조회 결과를 바탕으로 계산 도구를 다시 호출할 수 있도록 반복합니다.
    for _ in range(10):  # range(10): 최대 10번 반복 / _: 반복 횟수 값을 코드에서 사용하지 않을 때 관례적으로 쓰는 변수
        ai_msg = llm_with_tools.invoke(messages) # .invoke(messages): 지금까지의 대화를 LLM에게 보내고 응답을 받음
        messages.append(ai_msg) # .append(ai_msg): LLM의 응답을 대화 기록에 추가
        # -> 반복하는 이유는 조회 결과를 받은 뒤, 그 결과를 바탕으로 계산 도구를 추가 호출해야 하기 때문
        # -> 추가 후의 구조 
        # messages = [
        #     SystemMessage(...),
        #     HumanMessage(...),
        #     ai_msg,                 # 이번 LLM 응답
        # ]
        ## 2. 도구 호출이 없으면 최종 답변 반환하기
        # 도구 호출 요청이 없으면 최종 답변입니다.
        if not ai_msg.tool_calls: # ai_msg.tool_calls에는 LLM이 요청한 도구 호출 정보가 들어감 
            # ai_msg.tool_calls   -> 가능: AI 응답 객체의 속성
            # messages.tool_calls  -> 불가능: 리스트에는 해당 속성이 없음 / messages[-1].tool_calls는 가능 
            return ai_msg.content  
            # -> 빈 리스트이면 not ai_msg.tool_calls가 참이 되어, 답변 내용인 ai_msg.content를 반환하고 함수를 종료
        
        ## 3. 도구 이름과 입력값으로 실제 실행하기
        for call in ai_msg.tool_calls:
            selected_tool = tool_registry[call["name"]]
            result = selected_tool.invoke(call["args"]) 
            ## 4. 실행 과정을 출력하기
            print(f"도구 실행: {call['name']} / 입력: {call['args']}")
            print("도구 결과:", result)
            # 도구 실행: lookup_user_quota / 입력: {'user_id': 'U-100'}
            # 도구 결과: {'user_id': 'U-100', 'daily_limit': 1000, 'used': 640, 'remaining': 360}

            ## 5. 도구 실행 결과를 대화에 추가하기
            # 실행 결과를 대화에 넣으면 다음 LLM 호출에서 참고합니다.
            messages.append(
                ToolMessage(     # ToolMessage: 도구 실행 결과를 나타내는 LangChain 메시지
                    content=json.dumps(result, ensure_ascii=False),  # json.dumps(result): 결과 딕셔너리를 JSON 문자열로 변환
                    tool_call_id=call["id"],   # tool_call_id: 어떤 호출 요청에 대한 결과인지 표시
                    # tool_call_id는 도구 실행 결과를 “LLM의 특정 도구 호출 요청”과 연결하는 값
                    # 사용자 질문
                    #     ↓
                    # LLM의 도구 호출 요청 [id="call_001"]
                    #     ↓
                    # 파이썬이 도구 실행
                    #     ↓
                    # 도구 실행 결과 [tool_call_id="call_001"]
                )
            )
    ## 6. 반복이 너무 길어지면 중단하기
    raise RuntimeError("도구 호출이 10회 반복되어 중단했습니다.") # 최대 10번의 LLM 응답 안에 최종 답변이 나오지 않으면 오류를 발생시킴

# -> 실행 예시 
# execute_dynamic_agent(
#     "U-100이 API를 400번 더 호출하면 초과 요금은 얼마야?",
#     [lookup_user_quota, calc_overage_cost]
# )

## 질문: U-100이 400번 더 호출하면 초과 요금은?
# lookup_user_quota 실행
# → remaining = 360
# LLM이 추가 호출량과 잔여량을 비교
# → 400 - 360 = 초과 40건
# calc_overage_cost에 overage_calls=40 전달
# → overage_krw = 2000
## 최종 답변
# → “40건 초과하므로 추가 요금은 2,000원입니다.”

if __name__ == "__main__":   # if __name__ == "__main__":는 이 파일을 직접 실행했을 때만 아래 코드를 실행한다는 뜻
    answer = execute_dynamic_agent(
        "U-100이 API를 400번 더 호출하면 초과 요금은 얼마야? "  # 질문에 있는 두 문자열은 나란히 작성되어 하나의 문자열로 자동 연결
        "먼저 잔여 호출량을 조회한 뒤 초과 건수의 요금을 계산해줘.",
        [lookup_user_quota, calc_overage_cost],
    )
    print("최종 답변:", answer)
    # ai_msg.content
    #   ↓ return
    # answer에 저장
    #   ↓ print
    # 화면에 최종 답변 출력



# -> LLM이 다음과 같은 호출 정보를 반환했다고 가정
# {
#     "name": "lookup_user_quota",
#     "args": {"user_id": "U-100"},
#     "id": "call_abc123",
#     "type": "tool_call"
# }
# -> 이 값들을 다음과 같이 사용
# 반환된 값	       사용하는 코드	                   역할
# "name"	    tool_registry[call["name"]]	     실행할 도구 찾기
# "args"	    .invoke(call["args"])	         도구에 입력값 전달
# "id"	        tool_call_id=call["id"]          도구 요청과 실행 결과 연결
# result = lookup_user_quota.invoke({"user_id": "U-100"})
# -> result에는 다음 딕셔너리가 저장
# {
#     "user_id": "U-100",
#     "daily_limit": 1000,
#     "used": 640,
#     "remaining": 360
# }