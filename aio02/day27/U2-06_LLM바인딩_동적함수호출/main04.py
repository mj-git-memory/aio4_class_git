# Pydantic args_chema 결합과 정밀 인자 추출
import json
from typing import Literal
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv(find_dotenv(), override=True)

## 1. 입력 규칙을 클래스로 정의하기
class BackupScheduleSpec(BaseModel): # Pydantic의 BaseModel을 상속하여 백업 계획에 필요한 입력값과 검사 규칙을 만듦
    target_db: Literal["orders_db", "logs_db", "analytics_db"] = Field(..., description="백업 대상 DB 이름")
    # Literal[...]: 나열한 값 중 하나만 허용 / Field(...): 필드의 조건과 설명 지정 / 첫 번째 인수인 ...: 기본값 없이 반드시 입력해야 한다는 의미
    retention_days: int = Field(..., ge=1, le=365, description="보관 기간 (1일~365일 사이 정수)")
    # ge=1 : 1 이상 / le=365 : 365 이하 / description: LLM이 입력값의 의미를 이해하도록 설명
    compression: Literal["gzip", "zstd", "none"] = Field(..., description="압축 방식 (gzip, zstd, none)")

## 2. 입력 규칙을 도구에 연결하기
@tool(args_schema=BackupScheduleSpec)  # @tool로 도구를 만들면서 args_schema에 앞서 정의한 클래스를 연결
# -> 이 함수를 도구로 만들고, 입력 규칙은 BackupScheduleSpec을 사용해라.
# -> 따라서 도구를 .invoke()로 실행할 때, 함수 본문 실행 전에 입력값이 해당 규칙에 맞는지 검사
# @tool은 파이썬 함수를 LLM이 선택할 수 있는 도구로 변환. & 그 도구에는 실행할 함수뿐 아니라 이름, 설명, 입력 규칙도 들어 있음.
def create_backup_plan(target_db: str, retention_days: int, compression: str) -> dict:
    """지정된 DB, 보관 기간, 압축 방식으로 백업 계획을 생성합니다."""
    return {    # 함수 본문은 전달받은 값을 딕셔너리로 반환
        "status": "scheduled",
        "target_db": target_db,
        "retention_days": retention_days,
        "compression": compression,
    }


if __name__ == "__main__":

    print("[4차시] Pydantic args_schema JSON Schema:")
    ## 3. 입력 규칙을 출력하기
    print(json.dumps(create_backup_plan.args_schema.model_json_schema(), indent=2, ensure_ascii=False)) # JSON Schema로 변환해 출력
    # create_backup_plan.args_schema -> 입력 규칙
    # create_backup_plan.args_schema.model_json_schema() -> 입력 규칙을 JSON Schema 딕셔너리로 표현
    # json.dumps(): 딕셔너리를 JSON 문자열로 변환 / indent=2: 들여쓰기로 보기 좋게 출력 / ensure_ascii=False: 한글을 그대로 표시
    print()
    ## 4. LLM에 도구를 연결하고 질문 보내기
    # chatopenai 객체생성
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([create_backup_plan]) 
    # -> .bind_tools()로 모델에 도구와 입력 규칙을 알려줌
    query = "로그 DB를 zstd 압축으로 30일 보관하게 백업 계획 잡아줘."
    # humanmessage를 이용해서 ai_msg 생성
    ai_msg = llm.invoke([HumanMessage(content=query)])
    # -> HumanMessage에 질문을 담고, .invoke()로 LLM의 응답을 받음
    print("동적 추출된 args:", ai_msg.tool_calls)
    # -> LLM은 질문과 도구 정보를 보고 보통 다음과 같은 호출 정보를 만듦 
    # [
    #     {
    #         "name": "create_backup_plan",
    #         "args": {
    #             "target_db": "logs_db",  # “로그 DB”라는 표현을 허용된 값인 "logs_db"로 해석하는 역할은 LLM이 함
    #             "retention_days": 30,
    #             "compression": "zstd"
    #         },
    #         "id": "call_...",
    #         "type": "tool_call"
    #     }
    # ]

    ## 5. 추출된 입력값으로 도구 실행하기
    for call in ai_msg.tool_calls:
        # call이 가지고 있는 함수를 실행해서 
        res = create_backup_plan.invoke(call["args"]) # call["args"]를 도구에 전달
        # -> 검사를 통과하면 res에 다음 결과가 저장
        # {
        #     "status": "scheduled",
        #     "target_db": "logs_db",
        #     "retention_days": 30,
        #     "compression": "zstd"
        # }
        ## 6. 결과를 LLM에게 전달해 답변 만들기
        t_msg = ToolMessage(content=json.dumps(res, ensure_ascii=False), tool_call_id=call["id"])
        # -> 도구 실행 결과를 메시지로 만들고, call["id"]로 해당 도구 호출 요청과 연결
        final_msg = llm.invoke([HumanMessage(content=query), ai_msg, t_msg])
        # -> LLM에 전달하는 내용은 세 가지
        # 메시지	              내용
        # HumanMessage(...)	    사용자 질문
        # ai_msg	            LLM이 요청한 도구 호출
        # t_msg	                도구 실행 결과
        # -> 이 정보를 바탕으로 최종 답변을 생성
        print("최종 답변:\n", final_msg.content)



# “로그 DB를 zstd 압축으로 30일 보관하게 백업 계획 잡아줘.”
#    ↓ LLM이 입력값 추출
# logs_db / 30 / zstd
#    ↓ Pydantic으로 입력 검사
# 백업 계획 도구 실행
#    ↓
# 결과를 LLM에 전달 → 최종 답변


# print(json.dumps(
#     create_backup_plan.args_schema.model_json_schema(),
#     indent=2,
#     ensure_ascii=False
# ))
# 단계별로 나누면 이해하기 쉬워요.
# ① 입력 규칙을 가져오기
# create_backup_plan.args_schema
# 앞에서 연결한 BackupScheduleSpec 클래스를 가리킵니다.
# ② 입력 규칙을 JSON Schema 딕셔너리로 표현하기
# schema = create_backup_plan.args_schema.model_json_schema()
# JSON Schema는 **“어떤 값을 입력해야 하는지 설명하는 표준 형식”**이에요. 핵심 부분은 다음과 같습니다.
# {
#     "properties": {
#         "target_db": {
#             "enum": ["orders_db", "logs_db", "analytics_db"],
#             "type": "string"
#         },
#         "retention_days": {
#             "minimum": 1,
#             "maximum": 365,
#             "type": "integer"
#         },
#         "compression": {
#             "enum": ["gzip", "zstd", "none"],
#             "type": "string"
#         }
#     },
#     "required": ["target_db", "retention_days", "compression"],
#     "type": "object"
# }