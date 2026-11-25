# bind_tools() 바인딩 AIMessage.tool_calls 동적생성
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI  # OpenAI
## 1. .env에서 API 키 불러오기
load_dotenv(find_dotenv(),override=True)

# -> LLM은 다음 정보를 보고 도구 사용을 판단
# 코드	                     의미
# get_cluster_load	        도구 이름
# cluster_name: str	        입력값 이름과 타입
# '''클러스터명…조회합니다.'''	  도구 설명
# -> dict	                함수 반환값이 딕셔너리라는 타입 힌트

## 2. 사용률을 조회하는 도구 만들기
@tool # @tool : LangChain의 데코레이터. 파이썬 함수를 LLM에게 알려줄 수 있는 도구 객체로 변환
def get_cluster_load(cluster_name: str) ->dict:
    '''클러스터명(prod-a, prod-b, staging)의 cpu 및 메모리 사용률을 조회합니다.'''
    data = {
        'prod-a':{'cpu_pct':68.5, 'mem_pct':74.0},
        'prod-b':{'cpu_pct':58.5, 'mem_pct':54.0},
        'staging':{'cpu_pct':38.5, 'mem_pct':34.0},
    }
    key = cluster_name.lower()
    return {"cluster":key, **data.get(key, {'cpu_pct':0.0, 'mem_pct':0.0})}
    # data.get(key, 기본값): 해당 키의 데이터를 가져오고, 없으면 기본값 반환
    # **딕셔너리: 딕셔너리 안의 항목들을 펼쳐서 합침
    # -> prod-a를 입력하면 다음 값을 반환
    # {
    #     'cluster': 'prod-a',
    #     'cpu_pct': 68.5,
    #     'mem_pct': 74.0
    # }

if __name__ =='__main__':
    ## 3. 모델에 도구 알려주기
    base_llm = ChatOpenAI(model='gpt-4o-mini',temperature=0) 
    # ChatOpenAI(...): OpenAI 모델을 호출할 객체를 만듦 / temperature=0: 응답의 무작위성을 낮춤
    bound_llm = base_llm.bind_tools([get_cluster_load])
    # .bind_tools(...): 모델에게 사용할 수 있는 도구의 정보를 연결
    # -> 이 단계에서는 get_cluster_load를 실행하지 않음. 모델에게 도구 이름, 설명, 입력 규칙을 알려주는 단계

    ## 4. 질문을 보내고 도구 호출 정보 받기
    query = 'prod-a 클러스터의 현재 cpu와 메모리 사용률을 확인해줘'
    messages = [HumanMessage(content=query)] # HumanMessage: 사용자 질문을 담는 메시지

    ai_msg = bound_llm.invoke(messages) # .invoke(messages): 메시지를 모델에 보내고 응답을 받는 메서드
    messages.append(ai_msg) # .append(...): 리스트 마지막에 값을 추가하는 파이썬 메서드
    
    print('AIMessage.content:',ai_msg.content)
    # AIMessage.content:  # content는 비어 있을 수 있음 
    print('AIMessage.tool_calls:',ai_msg.tool_calls)  
    # AIMessage.tool_calls: [
    #     {
    #         'name': 'get_cluster_load',
    #         'args': {'cluster_name': 'prod-a'},
    #         'id': 'call_...',  # ID는 실행마다 달라질 수 있음 
    #         'type': 'tool_call'
    #     }
    # ]

    ## 5. tool_calls 값을 사용해 실제 도구 실행하기
    fns = {'get_cluster_load': get_cluster_load} # fns는 도구 이름으로 실행할 도구 객체를 찾는 딕셔너리
    # 함수바인딩후 함수실행  그리고 최종 llm 답변
    for call in ai_msg.tool_calls:
        rs = fns[call['name']].invoke(call['args'])   # get_cluster_load.invoke({'cluster_name': 'prod-a'})
       
        ## 6. 도구 결과를 LLM에게 전달하기
        messages.append(
            ToolMessage(          # ToolMessage: 도구 실행 결과를 담는 메시지
                content=str(rs),
                tool_call_id=call['id'],  # tool_call_id: 어느 도구 호출의 결과인지 표시
            )
        )
        # 모델이 반환한 값	    이후 코드에서 사용하는 목적
        # call['name']	    실행할 도구 선택
        # call['args']	    도구에 전달할 입력값
        # call['id']	    도구 요청과 실행 결과 연결

        ## 이제 messages에는 다음 세 가지가 들어 있음
        # 1. 사용자: prod-a의 사용률을 알려줘
        # 2. AI: get_cluster_load를 prod-a로 호출해줘
        # 3. 도구: CPU 68.5%, 메모리 74.0%
    
    ## 7. 최종 답변 만들기
    final_msg = base_llm.invoke(messages)
    print('최종 답변:', final_msg.content)


    
