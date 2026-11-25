import json
from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import tool

load_dotenv(find_dotenv())


@tool
def calc_sla_penalty(planned_hours:int, actual_hours:int, hourly_rate:int=10000) -> dict : 
    '''예정 처리 시간(planned_hours) 대비 실제 소요 시간(actual_hours) 초과분에 대한 SLA 패널티 계산'''
    delay_hours = max(0, actual_hours-planned_hours)
    penalty_krw = delay_hours*hourly_rate
    return {
        'planned_hours' : planned_hours,
        'actual_hours' : actual_hours,
        'delay_hours' : delay_hours,
        'penalty_krw': penalty_krw,
    }

if __name__ == '__main__' :
    print('@tool 변환 결과')
    print('도구 이름: ', calc_sla_penalty.name)
    # 도구 이름: name='calc_sla_penalty' description='예정 처리 시간(planned_hours) 대비 실제 소요 시간(actual_hours) 초과분에 대한 SLA 패널티 계산' args_schema=<class 'langchain_core.utils.pydantic.calc_sla_penalty'> func=<function calc_sla_penalty at 0x1036fb240>
    print('도구 설명: ', calc_sla_penalty.description)
    print('자동생성 JSON Schema: ')
    print(json.dumps(calc_sla_penalty.args_schema.model_json_schema(),
                    #  indent=2,  # 들여쓰기 
                     ensure_ascii=False)
                     )
    # {"description": "예정 처리 시간(planned_hours) 대비 실제 소요 시간(actual_hours) 초과분에 대한 SLA 패널티 계산", "properties": {"planned_hours": {"title": "Planned Hours", "type": "integer"}, "actual_hours": {"title": "Actual Hours", "type": "integer"}, "hourly_rate": {"default": 10000, "title": "Hourly Rate", "type": "integer"}}, "required": ["planned_hours", "actual_hours"], "title": "calc_sla_penalty", "type": "object"}
    print(f'type : {type(json.dumps(calc_sla_penalty.args_schema.model_json_schema(),
                    #  indent=2,  # 들여쓰기 
                     ensure_ascii=False))}'
                     )
    # type : <class 'str'>
    print('---')
    print(calc_sla_penalty.args_schema) # <class 'langchain_core.utils.pydantic.calc_sla_penalty'>
    print(f'type : {type(calc_sla_penalty.args_schema)}') # type : <class 'pydantic._internal._model_construction.ModelMetaclass'>
    print('---')
    print(calc_sla_penalty.args_schema.model_json_schema())
    # {'description': '예정 처리 시간(planned_hours) 대비 실제 소요 시간(actual_hours) 초과분에 대한 SLA 패널티 계산', 'properties': {'planned_hours': {'title': 'Planned Hours', 'type': 'integer'}, 'actual_hours': {'title': 'Actual Hours', 'type': 'integer'}, 'hourly_rate': {'default': 10000, 'title': 'Hourly Rate', 'type': 'integer'}}, 'required': ['planned_hours', 'actual_hours'], 'title': 'calc_sla_penalty', 'type': 'object'}
    print(f'type : {type(calc_sla_penalty.args_schema.model_json_schema())}') 
    # type : <class 'dict'>

    # calc_sla_penalty.args_schema.model_json_schema() -> 도구에 전달할 입력값의 규칙을 JSON Schema 형태의 파이썬 딕셔너리로 반환하는 코드
    # def calc_sla_penalty(
    #     planned_hours: int,
    #     actual_hours: int,
    #     hourly_rate: int = 10000
    # ) -> dict:
    ## -> 변환되는 스키마 : 
    # {
    #     "properties": {                   # properties: 입력으로 받을 매개변수와 각각의 규칙
    #         "planned_hours": {
    #         "title": "Planned Hours",
    #         "type": "integer"
    #         },
    #         "actual_hours": {
    #         "title": "Actual Hours",
    #         "type": "integer"
    #         },
    #         "hourly_rate": {
    #         "default": 10000,             # hourly_rate를 생략하면 사용할 기본값
    #         "title": "Hourly Rate",
    #         "type": "integer"
    #         }
    #     },
    #     "required": [                     # required: 반드시 전달해야 하는 값
    #         "planned_hours",
    #         "actual_hours"
    #     ],
    #     "title": "calc_sla_penalty",
    #     "type": "object"
    # }

# calc_sla_penalty                      # @tool이 변환한 도구 객체
# calc_sla_penalty.args_schema          # 도구의 입력 규칙을 정의한 Pydantic 모델
# calc_sla_penalty.args_schema.model_json_schema()   # 입력 규칙을 JSON Schema 딕셔너리로 변환

# print(json.dumps(calc_sla_penalty.args_schema.model_json_schema(),
#                 #  indent=2,  # 들여쓰기 
#                  ensure_ascii=False)
#                  )
## 이 호출 자체가 화면에 출력하거나 패널티를 계산하지는 않음
# 바깥의 json.dumps(...)가 딕셔너리를 보기 좋은 JSON 문자열로 만들고, print(...)가 화면에 출력
## -> LLM은 이 스키마를 보고 “이 도구를 호출하려면 어떤 이름의 값을 어떤 타입으로 전달해야 하는지” 알 수 있음