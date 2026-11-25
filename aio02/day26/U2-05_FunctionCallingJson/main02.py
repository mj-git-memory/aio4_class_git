# 차이점 비교
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from openai import OpenAI
load_dotenv('.env',override=True)
QUERY="4.5kg 상자를 빠른 택배로 보내면 배송비가 얼마인가요?"

# 호출될 함수
def calculate_shipping_fee(weight_kg:float, is_express: bool = False)->dict:
    """택배 무개와 당일/빠른 배송 여부를 받아 예상 배송비를 계산"""
    base_fee = 3000 if weight_kg <=3.0 else 3000+(weight_kg-3.0)*1000
    express_fee = 2500 if is_express else 0
    total_fee = int(round(base_fee+express_fee))
    return {
        'weight_kg':weight_kg,
        'is_express':is_express,
        "shipping_fee_krw" : total_fee
    }
################################################################################
# 방식1 순수 SDK방식
################################################################################
def run_pure_openai_sdk(user_prompt: str) -> str:
    client = OpenAI()    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate_shipping_fee",
                "description": "택배 무게(kg)와 빠른 배송 여부를 기준으로 배송비를 계산합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "weight_kg": {
                            "type": "number",
                            "description": "택배 무게 (단위: kg)",
                        },
                        "is_express": {
                            "type": "boolean",
                            "description": "빠른 배송 여부 (기본값 false)",
                        },
                    },
                    "required": ["weight_kg"],
                },
            },
        }  
    ]
    messages = [
        {
            "role": "system",
            "content": "당신은 배송비 안내 어시스턴트입니다. 배송비 계산이 필요하면 제공된 도구를 사용하세요.",
        },
        {"role": "user", "content": user_prompt},
    ]
    available_functions = {
        'calculate_shipping_fee':calculate_shipping_fee,
    }

    # [1단계] 사용자 질문 + tools 명세를 모델에 전송
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=messages,
        tools=tools,
    )

    assistant_msg = response.choices[0].message
    finish_reason = response.choices[0].finish_reason
    print(f"[1차 응답] finish_reason = {finish_reason}")
    print(f"[1차 응답] content = {assistant_msg.content!r}")
    print(f"[1차 응답] tool_calls = {assistant_msg.tool_calls}")

    # 도구 호출이 없으면 바로 답변 반환
    if not assistant_msg.tool_calls:
        return assistant_msg.content or ""

    # [2단계] 모델이 생성한 assistant 메시지(tool_calls 포함)를 대화 이력에 추가
    messages.append(assistant_msg)
    

    for tool_call in assistant_msg.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)        
        result = available_functions[func_name](**func_args)
        print(f"[함수 실행] {func_name}({func_args}) -> {result}")
        # [3단계] tool 역할 메시지를 추가해 모델에게 실행 결과 전달
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        })

    # [4단계] 도구 실행 결과가 반영된 messages로 2차 호출해 최종 답변 생성
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=messages,
        tools=tools,
    )
    return final_response.choices[0].message.content or ""


################################################################################
# 방식2 LangChain (@tool + bind_tools) : 스키마자동변환 + dict args + ToolMessage
################################################################################
@tool
def calculate_shipping_fee_lc(weight_kg:float, is_express:bool=False)->dict:
    '''택배 무게(kg)와 빠른 배송여부로 배송비를 계산합니다.'''
    return calculate_shipping_fee(weight_kg,is_express)

def run_langchain_bind_tools(query:str)->str:
    llm = ChatOpenAI(model='gpt-4o-mini',temperature=0)
    llm_with_tools =  llm.bind_tools([calculate_shipping_fee_lc])
    tool_map = {"calculate_shipping_fee_lc":calculate_shipping_fee_lc}
    messages = [
        SystemMessage(content="배송비 계산이 필요하면 도구를 호출하세요"),
        HumanMessage(content=query)
    ]
    # 1차 호출(모델이 도구를 호출하는 단계) 만약에 도구를 호출안하면 이 응답이 최종 응답이됨
    ai_msg= llm_with_tools.invoke(messages)
    if not ai_msg.tool_calls:
        return ai_msg.content

    messages.append(ai_msg)
    # 2차 도구의 실행결과를 이전메세지에 추가
    for call in ai_msg.tool_calls:
        args_dict = call['args']
        tool_result = tool_map[call['name']].invoke(args_dict)  # calculate_shipping_fee_lc(args_dict)
        # ToolMessage 객체로 전달
        messages.append(
            ToolMessage(
                content=json.dumps(tool_result,ensure_ascii=False),
                tool_call_id  = call['id'],
            )
        )
    #3 2차호출 : ToolMessage 포함해 최종 답변 생성
    final_msg = llm_with_tools.invoke(messages)
    return final_msg.content



if __name__ == "__main__":    
    print("순수 SDK 방식")    
    answer = run_pure_openai_sdk(QUERY)    
    print("최종 답변:\n", answer)
    print('='*100)

    print("langchain bind tools 방식")    
    answer = run_langchain_bind_tools(QUERY)    
    print("최종 답변:\n", answer)
    print('='*100)