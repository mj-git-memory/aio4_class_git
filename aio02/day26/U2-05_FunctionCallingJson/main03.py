# Function Calling JSON Schema

import json
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(), override=True)
client = OpenAI()

def estimate_cloud_cost(instance_size:str, hours:int, region:str="ap-northeast-2")->dict:
    hourly_rates = {'small':0.05,'medium':0.15,"large":0.40}
    rate = hourly_rates.get(instance_size, 0.15)
    return {
        'instance_size':instance_size,
        'hours':hours,
        'region':region,
        'estimated_usd':round(rate*hours,2)
    }

# 모호한 스키마 vs 명시적 단위,설명 스키마 비교
WEAK_SHEMA=[
    {
        'type':'function',
        'function':{
            'name':'estimate_cloud_cost',
            'description':'비용계산',
            'parameters':{
                'type':'object',
                'properties':{
                    'instance_size':{'type':'string'},
                    'hours':{'type':'integer'},
                    'region':{'type':'string'},
                },
                'required':['instance_size','hours']            
            },            
        },
    },
]

# 명시적 스키마 (Clear Schema)
CLEAR_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "estimate_cloud_cost",
            "description": (
                "클라우드 서버 인스턴스의 예상 사용 비용을 계산합니다. "
                "서버 인스턴스 크기, 사용 시간(hours), AWS 리전(region)을 입력받아 "
                "시간당 요금과 사용 시간을 기준으로 예상 비용(USD)을 계산합니다. "
                "비용 계산이 필요한 질문에 사용하세요."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "instance_size": {
                        "type": "string",
                        "enum": ["small", "medium", "large"],
                        "description": (
                            "클라우드 서버 인스턴스 크기입니다. "
                            "small은 시간당 $0.05, medium은 $0.15, "
                            "large는 $0.40입니다. "                            
                        )
                    },
                    "hours": {
                        "type": "integer",
                        "minimum": 1,
                        "description": (
                            "클라우드 서버를 사용할 시간입니다. "
                            "단위는 시간(hours)이며 1 이상의 정수로 입력합니다. "
                            "예를 들어 3시간 사용은 3으로 입력합니다."
                        )
                    },
                    "region": {
                        "type": "string",
                        "enum": [
                            "ap-northeast-2",
                            "us-east-1",
                            "us-west-2",
                            "eu-west-1"
                        ],
                        "default": "ap-northeast-2",
                        "description": (
                            "클라우드 서버를 생성할 리전 코드입니다. "
                            "ap-northeast-2는 서울 리전입니다. "
                            "사용자가 리전을 지정하지 않으면 "
                            "ap-northeast-2를 사용합니다."
                        )
                    }
                },
                "required": ["instance_size", "hours"]
            }
        }
    }
]

def test_schema(label:str, schema:list, prompt:str)->None:
    res = client.chat.completions.create(
        model='gpt-4o-mini',
        temperature=0,
        messages=[{'role':'user','content':prompt}],
        tools=schema
    )
    msg = res.choices[0].message
    raw_rags = msg.tool_calls[0].function.arguments if msg.tool_calls else "{}"
    print(f'{label}추출 인자 : {raw_rags}')

if __name__ == "__main__":
    prompt = "서울 리전에서 소형 서버를 2일 동안 돌리면 비용이 얼마인가요?"
    test_schema('모호한 스키마',WEAK_SHEMA,prompt)
    test_schema('명시적 스키마',CLEAR_SCHEMA,prompt)
