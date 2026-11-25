# @tool 이나 프레임웍크 추상화를 제거, 순수 OpenAI SDK 레벨에서 
# tool선언 -> tool_calls추출 -> role="tool" 
# 3단계로 되어 있는 왕복루프를 눈으로 직접확인

import json
import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(), override=True)
client = OpenAI()


#1.실제 실행될 함수(모델은 이 함수의 존재와 구현을 모름)
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
#2.API에 전달할 tool 선언
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
available_functions = {
    'calculate_shipping_fee':calculate_shipping_fee,
}

def run_tool_loop(user_prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "당신은 배송비 안내 어시스턴트입니다. 배송비 계산이 필요하면 제공된 도구를 사용하세요.",
        },
        {"role": "user", "content": user_prompt},
    ]

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


if __name__ == "__main__":
    query = "4.5kg짜리 상자를 빠른 배송으로 보내면 배송비가 얼마인가요?"
    print("질문:", query)
    print("-" * 60)
    answer = run_tool_loop(query)
    print("-" * 60)
    print("최종 답변:\n", answer)
