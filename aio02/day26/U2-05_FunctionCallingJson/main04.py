# 다중 도구 라우팅과 병렬 호출(Parallel Tool Calls)
import json
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(), override=True)
client = OpenAI()


def get_item_price(sku: str) -> dict:
    prices = {"SKU-101": 25000, "SKU-202": 40000, "SKU-303": 15000}
    return {"sku": sku, "price_krw": prices.get(sku.upper(), 20000)}


def get_fx_rate(currency: str = "USD") -> dict:
    rates = {"USD": 1400.0, "JPY": 9.3}
    return {"currency": currency.upper(), "krw_per_unit": rates.get(currency.upper(), 1400.0)}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_item_price",
            "description": "상품 SKU 코드로 단가(원화)를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {"sku": {"type": "string", "description": "상품 코드"}},
                "required": ["sku"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fx_rate",
            "description": "대상 통화(USD, JPY 등)의 원화 환율을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {"currency": {"type": "string", "description": "통화 코드"}},
                "required": ["currency"],
            },
        },
    },
]

TOOL_MAP = {
    "get_item_price": get_item_price,
    "get_fx_rate": get_fx_rate,
}


def run_parallel_demo(query: str) -> str:
    messages = [{"role": "user", "content": query}]
    first = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=messages,
        tools=TOOLS,
        parallel_tool_calls=True,
    )
    msg = first.choices[0].message
    if not msg.tool_calls:
        return msg.content or ""

    print(f"한 턴에 요청된 tool_calls 개수: {len(msg.tool_calls)}")
    messages.append(msg)

    for call in msg.tool_calls:
        fn = TOOL_MAP[call.function.name]
        args = json.loads(call.function.arguments)
        res = fn(**args)
        print(f"  - id={call.id} | {call.function.name}({args}) -> {res}")
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(res, ensure_ascii=False),
            }
        )

    second = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=messages,
        tools=TOOLS,
    )
    return second.choices[0].message.content or ""


if __name__ == "__main__":
    # ans = run_parallel_demo("SKU-101 가격, SKU-202 가격, 그리고 USD 환율을 한꺼번에 알려줘.")
    ans = run_parallel_demo("정수기의 동작원리에 대해서 알려줘")
    print("\n최종 답변:\n", ans)