## s6: MCP 서버에서 도구 목록을 받아, LLM의 판단에 따라 실행하는 에이전트
# mcp 세션 + LLM API + 외부 API 연동이 결합된 에이전트 

# 사용자
#   ↓ 자연어 요청
# s6: LLM이 도구 선택
#   ↓ MCP 통신
# s5: 선택한 도구 실행
#   ↓ HTTP 요청
# s3: 주문 조회·환불 API
#   ↓ 결과가 역순으로 전달
# s6: LLM이 결과를 읽고 답변

import asyncio # 비동기 함수 실행(ex. asyncio.run(...))
import sys # 현재 파이썬 실행 정보 제공(ex. sys.executable)
from pathlib import Path # 파일 경로 구성(ex. Path(__file__).resolve().parent)
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
# 대화와 도구 결과 표현(ex. HumanMessage, ToolMessage)
from langchain_openai import ChatOpenAI # OpenAI 모델 호출(ex. ChatOpenAI(...))
from mcp import ClientSession, StdioServerParameters 
from mcp.client.stdio import stdio_client

SCRIPT_DIR = Path(__file__).resolve().parent # -> 반환값은 현재 s6 파일이 들어 있는 폴더의 Path 객체
load_dotenv(find_dotenv(), override=True)

async def run_mcp_llm_agent(user_query:str)->str:
    ## ① 실행할 서버 경로 만들기
    server_params =  StdioServerParameters(  # 서버 실행 설정 객체
        command=sys.executable, # 현재 실행 중인 파이썬의 경로
        args=[str(SCRIPT_DIR / "s5_order_mcp_server.py")], # 경로 객체를 문자열로 변환
        # -> 이 단계는 설정만 만들고, 다음 단계에서 서버를 실행
    )
    ## ② 서버 실행과 세션 초기화
    async with stdio_client(server_params) as (read_stream, write_stream):
    # -> async with는 연결에 들어가고 나올 때 필요한 정리 작업을 관리
        async with ClientSession(read_stream,write_stream) as session:
            await session.initialize()  # MCP 연결 초기화 기다리기
            # -> wait는 비동기 작업의 결과를 기다림
            ## ③ 도구 목록을 받아 이름으로 찾을 수 있게 만들기
            mcp_tools = (await session.list_tools()).tools  # await session.list_tools() : 도구 목록 기다리기
            # list_tools()는 도구 목록 응답 객체를 반환하고, .tools가 실제 도구 객체 리스트 
            # # 구조를 단순화한 예시
            # [
            #     Tool(name="mcp_get_order", ...),
            #     Tool(name="submit_refund_via_rest", ...),
            # ]
            tool_map = {tool.name: tool for tool in mcp_tools} # 이름으로 도구를 찾는 딕셔너리
            ## ④ 도구 객체를 LLM이 이해하는 형식으로 변환하기
            tool_schemas = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name, # 도구 이름 ->	모델이 선택할 이름
                        "description": tool.description or "", # 기능 설명 ->	언제 사용할지 판단하는 근거
                        "parameters": tool.input_schema, # 입력 구조 ->	어떤 인자를 만들어야 하는지 안내
                    },
                }
                for tool in mcp_tools
            ]
            # # 주문 조회의 입력 스키마
            # {
            #     "type": "object",
            #     "properties": {
            #         "order_id": {"type": "string"}
            #     },
            #     "required": ["order_id"],
            # }

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tool_schemas)
            # bind_tools()는 도구 정의가 연결된 모델 실행 객체를 반환
            messages = [
                SystemMessage(content="주문 및 환불 업무는 MCP 서버에서 제공된 도구를 사용해 처리하세요."),
                HumanMessage(content=user_query),
            ]

            for _ in range(5):
                ## ⑤ LLM의 반환값에서 도구 이름과 인자 추출하기
                ai_msg = await llm.ainvoke(messages) # 반환값은 AIMessage 객체  # LLM 응답 기다리기
                messages.append(ai_msg)
                if not ai_msg.tool_calls: # 도구 호출 요청 목록
                    return ai_msg.content # 답변 내용
                # -> 더 이상 도구 호출이 없으면 최종 답변을 반환
                # # 도구 호출 요청 예시
                # {
                #     "name": "mcp_get_order",
                #     "args": {"order_id": "ORD_1001"},
                #     "id": "call_123",
                #     "type": "tool_call",
                # }

                for call in ai_msg.tool_calls:
                    tool = tool_map[call["name"]]
                    result = await session.call_tool(tool.name, arguments=call["args"]) # await session.call_tool(...) : MCP 도구 결과 기다리기
                    # -> call_tool()은 이 도구의 정상 완료 시 MCP 도구 실행 결과 객체를 반환
                    ## ⑥ 실행 결과를 다시 LLM에 전달하기
                    tool_out = result.model_dump_json(by_alias=True, exclude_none=True) # 반환값은 JSON 문자열
                    # by_alias=True: 모델에 정의된 별칭을 출력 필드명으로 사용 / exclude_none=True: 값이 None인 필드 제외
                    print(f"  [MCP Tool 실행] {call['name']} - ({call['args']}) -> {tool_out}")
                    messages.append(ToolMessage(content=tool_out, tool_call_id=call["id"]))
                    # -> 그 문자열을 대화 기록에 추가 / tool_call_id는 “이 결과가 어떤 도구 호출의 답인지” 연결하는 번호
            return "최대 반복 횟수 초과"
        
if __name__ == "__main__":
    q = "ORD_1001의 상품명과 금액을 확인하고, ORD_1002는 '배송 지연 우려'로 환불 접수해줘."
    print(asyncio.run(run_mcp_llm_agent(q)))  # 비동기 함수를 실행하고 최종 반환값을 출력
