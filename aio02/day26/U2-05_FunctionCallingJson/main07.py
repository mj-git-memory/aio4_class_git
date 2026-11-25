import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)


def get_shipping_zone(postal_prefix: str) -> dict:
    zones = {"01": "서울 도심권", "13": "수도권 남부", "48": "부산 해운대권"}
    return {"postal_prefix": postal_prefix, "zone": zones.get(postal_prefix[:2], "기타 지역")}


def call_openai_native(prompt: str) -> None:
    client = OpenAI()
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_shipping_zone",
                "description": "우편번호 앞자리로 배송 권역을 조회합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "postal_prefix": {"type": "string", "description": "우편번호 앞 2~5자리"}
                    },
                    "required": ["postal_prefix"],
                },
            },
        }
    ]
    res = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, messages=[{"role": "user", "content": prompt}], tools=tools
    )
    calls = res.choices[0].message.tool_calls or []
    print("[OpenAI SDK] tool_calls:", [(c.function.name, c.function.arguments) for c in calls])


def call_gemini_native(prompt: str) -> None:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[Gemini SDK] google-genai 패키지가 설치되어 있지 않아 예시 스키마만 출력합니다.")
        return

    client = genai.Client()
    fn_decl = types.FunctionDeclaration(
        name="get_shipping_zone",
        description="우편번호 앞자리로 배송 권역을 조회합니다.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "postal_prefix": {"type": "STRING", "description": "우편번호 앞 2~5자리"}
            },
            "required": ["postal_prefix"],
        },
    )
    config = types.GenerateContentConfig(
        temperature=0,
        tools=[types.Tool(function_declarations=[fn_decl])],
    )
    res = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=config,
    )
    calls = res.function_calls or []
    print("[Gemini SDK] function_calls:", [(c.name, dict(c.args or {})) for c in calls])


if __name__ == "__main__":
    q = "우편번호 01450 지역의 배송 권역을 알려줘."
    call_openai_native(q)
    call_gemini_native(q)