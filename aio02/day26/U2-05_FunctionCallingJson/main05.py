# Pydantic / Python 타입힌트 기반 자동 스키마 변환
# Pydantic BasseModel Field(description=...) 를 정의해서 model_json_schema()로 표준
# JSON Schema 생성하거나 또는 @tool(args_schema=...) / bind_tools(...) 연결해서
# 타입검증과 스키마를 동시에 만족

# 직접작성한 dict 스키마dhk @tool /pydantic 이 만든 스키마 가 같은 JSON Schema형태를 api에게 넘긴다

import json
from typing import Literal
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class DiscountInput(BaseModel):
    amount: float = Field(...,gt=0,description="할인 전 원화 금액(0보다 커야 함)")
    discount_rate: float = Field(..., ge=0.0,le=0.5,description="할인율(0.0~0.5사이)")
    rounding: Literal["floor","round","ceil"] = Field(default="round",description="소수점 처리 방식")

@tool(args_schema=DiscountInput)
def calc_discounted_price(amount:float, discount_rate:float, rounding:str = 'round')->float:
    '''원화 금액에 허용범위(0.0~0.5)내 할인율 을 적용합니다.'''
    raw = amount * (1.0 - discount_rate)
    if rounding == 'floor':
        return float(int(raw))
    elif rounding == 'ceil':
        return float(int(raw) + 1 if raw > int(raw) else 0 )
    else:
        return float(round(raw))
        
if __name__ == "__main__":
    print(" === pydantic model_json_schema() ===")
    print(json.dumps(DiscountInput.model_json_schema(),indent=2,ensure_ascii=False))

    print("\n=== @tool(args_schema=DiscountInput)가 생성한 tool_call_schema ===")
    print(json.dumps(calc_discounted_price.tool_call_schema.model_json_schema(), indent=2,
               ensure_ascii=False))

    print("\n실제 도구 실행 테스트")
    calc_discounted_price.invoke({"amount":50000,"discount_rate":0.2})