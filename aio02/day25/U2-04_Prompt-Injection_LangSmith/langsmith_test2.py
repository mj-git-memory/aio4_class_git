import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

load_dotenv(find_dotenv(), override=True)
@tool
def multiply(a:int, b:int)->int:
    '''두 정수를 곱합니다.(단가 x 수량)'''
    return a * b

@tool
def apply_discount(amount:float, discount_rate:float)->float:
    '''금액(amount)에 할인율(discount_rate)을 적용한 최종금액을 반환한다
    예) discount_rate은 10%할인은 0.1이다
    '''
    return round(amount*(1-discount_rate),2)

@tool
def convert_currency(amount_krw:float, exchange_rate:float = 1300.0) ->float:
    '''원화(krw)금액을 환율(exchange_rate)기준으로 usd로 변환'''
    return round(amount_krw / exchange_rate,2)

tools_by_name = {'multiply':multiply, 'apply_discount':apply_discount, 'convert_currency':convert_currency}

llm = ChatOpenAI(model='gpt-4o-mini',temperature=0)
tools = [multiply, apply_discount, convert_currency]
llm_with_tools = llm.bind_tools(tools)

message = [
    SystemMessage(
        content=(
            "당신은 계산을 정확히 하는 에이전트입니다. 필요한 도구는 반드시 제공되는 도구를 사용하고"
            "여러 단계가 필요하면 도구 결과를 확인한뒤 다음 도구를 호출하세요"
        )
    ),
    HumanMessage(
        content="단가 25,000원짜리 상품을 4개 사고 10%할인을 받은뒤 1달러당 1,400기준 달러금액도 알려줘"
    )
    ,
]

max_steps = 6
for step in range(max_steps):
    ai_msg =  llm_with_tools.invoke(message)
    message.append(ai_msg)
    # 도구 호출이 없으면 최종 답변단계
    if not ai_msg.tool_calls:
        print('최종답변\n',ai_msg.content)
        break
    print(f"[Step {step + 1} 요청된 도구의수 : {len(ai_msg.tool_calls)}]")
    for tool_call in ai_msg.tool_calls:
        
        tool_name = tool_call['name']
        tool_args = tool_call['args']

        selected_tool = tools_by_name[tool_name]
        result = selected_tool.invoke(tool_args)
        
        print(f'    - 실행:{tool_name}({tool_args}) -> {result}')

        message.append(
            ToolMessage(content=str(result),tool_call_id = tool_call["id"])
        )
