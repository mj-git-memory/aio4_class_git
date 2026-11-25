# 파라메터 추출 오류, 환각 및 자기교정(Self-Conrrection)
# 모델이 잘못된 타입이나 규칙위반(할인율 0.9 또는 음수금액)을 넘길때 예외를 던져 프로그램이 죽으면
# 사용자 경험이 끊깁니다.
# 대신 도구실행 중 발생한 검증 오류, 파싱오류를 role=tool 메시지로 모델에게 돌려준다
# 모델이 적합한 툴을 다시 찾거나 사용자게에 재입력을 요구하는 자기교정 루프를 만들수 있다

import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
client = OpenAI()


def apply_policy_discount(amount: float, discount_rate: float) -> dict:
    if amount <= 0:
        raise ValueError("금액(amount)은 0보다 커야 합니다.")
    if not (0.0 <= discount_rate <= 0.5):
        raise ValueError(
            f"할인율 {discount_rate}는 정책 허용 범위(0.0~0.5)를 벗어났습니다. "
            "0.0 이상 0.5 이하의 값으로 다시 호출하거나 사용자에게 범위 재입력을 요청하세요."
        )
    return {
        "original_amount": amount,
        "discount_rate": discount_rate,
        "final_amount": round(amount * (1.0 - discount_rate), 2),
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "apply_policy_discount",
            "description": "금액에 할인율(0.0~0.5)을 적용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "원화 금액"},
                    "discount_rate": {"type": "number", "description": "할인율 (0.0~0.5)"},
                },
                "required": ["amount", "discount_rate"],
            },
        },
    }
]

# 50,000원 상품에 할인율 0.8을 적용해줘.
def run_with_self_correction(user_query: str, max_steps: int = 5) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 주문 할인 계산 어시스턴트입니다. "
                "도구 실행 시 오류가 반환되면 원인을 파악해 올바른 인자로 재시도하거나 안내하세요."
            ),
        },
        {"role": "user", "content": user_query},
    ]
    
    for step in range(1, max_steps + 1):
        print('step :',step)
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=messages,
            tools=TOOLS,
        )
        msg = res.choices[0].message
        print('msg.tool_calls :',msg.tool_calls)
        if not msg.tool_calls:
            return msg.content or ""

        messages.append(msg)
        for call in msg.tool_calls:
            try:
                args = json.loads(call.function.arguments)                
                result = apply_policy_discount(**args)
                payload = json.dumps(result, ensure_ascii=False)
                print(f"  [Step {step}] 성공: {call.function.name}({args}) -> {payload}")
            except Exception as exc:
                # 예외를 삼키지 않고 role="tool" 피드백으로 모델에 전달
                payload = json.dumps({"error": str(exc)}, ensure_ascii=False)
                print(f"  [Step {step}] 오류 피드백 전달: {payload}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": payload,
                }
            )

    return "최대 재시도 횟수를 초과했습니다."


if __name__ == "__main__":
    ans = run_with_self_correction("50,000원 상품에 할인율 0.8을 적용해줘.")
    print("\n최종 응답:\n", ans)