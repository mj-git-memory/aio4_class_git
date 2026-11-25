import os
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv(find_dotenv(), override=True)

@tool
def multiply(a:int, b:int) -> int : 
    '''두 정수 곱하기'''
    return a*b 

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
llm_with_tools = llm.bind_tools([multiply])

message = [HumanMessage(content='7과 8을 곱한 결과를 알려줘')]
# print(message)
# print('-'*80)
response = llm_with_tools.invoke(message)
print(response)
print('-'*80)
message.append(response) 
# print(message)
# print('-'*80)
print(response.tool_calls)
print('-'*80)

tools_by_name = {'multiply': multiply}
print(tools_by_name)
print('-'*80)

for tool_call in response.tool_calls:
    selected_tools = tools_by_name[tool_call['name']]
    tool_result = selected_tools.invoke(tool_call['args'])
    print(f'실행 결과 {tool_call['name']} {tool_call['args']} {tool_result}')

    # 도구 호출 결과를 llm에 전달해서 최종 답변을 생성
    message.append(
        ToolMessage(
            content=(tool_result),
            tool_call_id = tool_call['id']
        )
    )
# 최종 답변
final_msg = llm_with_tools.invoke(message)
print(final_msg)
print(f'최종답변: {final_msg.content}')