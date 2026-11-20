"""같은 모델로 두 지시문을 실행한다."""
import argparse
import json
from providers import RemoteChat
from s02 import records, variants

MODES = ("demo", "groq", "gemini", "openai")
DEMO_QUESTIONS = {
    "gsm8k-cot-test-0001": (
        "농장에서 오리 12마리가 각각 하루에 달걀을 5개씩 낳습니다. 농장 주인은 전체 달걀 중 20%를 이웃에게 무료로 나누어 주었습니다. "
        "무료로 나누어 준 후 남은 달걀 중 25%는 부화용으로 따로 보관하고, 나머지 달걀은 개당 3달러에 판매했습니다. "
        "달걀 판매로 얻은 총수익은 얼마입니까? 또한 무료로 나누어 준 달걀과 부화용으로 보관한 달걀을 합쳐, 판매하지 않은 달걀은 모두 몇 개입니까?"
    ),
    "gsm8k-main-test-0003": (
        "제임스는 일주일에 3번씩 달리기 훈련을 하며, 한 번 훈련할 때마다 전력 질주를 3회 합니다. "
        "전력 질주 한 번의 거리는 60미터입니다. 제임스가 일주일 동안 달리는 총거리는 몇 미터입니까?"
    ),
}


def scripted(row, strategy, messages):
    if DEMO_QUESTIONS.get(row["id"]) != row["question"]:
        raise ValueError(
            "Demo 대본은 지정된 질문에만 대응합니다. 질문이 바뀌었다면 공급자를 선택하거나 Demo 대본을 갱신하세요."
        )
    if strategy == "react":
        if row["id"] == "gsm8k-cot-test-0001":
            return egg_demo(messages)
        return sprint_demo(messages)
    if row["id"] == "gsm8k-cot-test-0001":
        return "답: 판매 수익 108달러, 판매하지 않은 달걀 24개" if strategy == "direct" else (
            "12 × 5 = 60개\n"
            "60 × 20% = 12개를 무료로 나누어 줍니다.\n"
            "60 - 12 = 48개, 48 × 25% = 12개를 부화용으로 보관합니다.\n"
            "48 - 12 = 36개, 36 × 3 = 108달러입니다.\n"
            "판매하지 않은 달걀은 12 + 12 = 24개입니다.\n"
            "답: 판매 수익 108달러, 판매하지 않은 달걀 24개"
        )
    return "답: 540미터" if strategy == "direct" else "주당 3 × 3 = 9회\n9 × 60 = 540미터\n답: 540미터"


def egg_demo(messages):
    observations = sum(
        message["role"] == "user" and message["content"].startswith("Observation: ")
        for message in messages
    )
    steps = [
        {"action": "multiply", "a": 12, "b": 5},
        {"action": "percent_of", "a": 60, "b": 20},
        {"action": "subtract", "a": 60, "b": 12},
        {"action": "percent_of", "a": 48, "b": 25},
        {"action": "subtract", "a": 48, "b": 12},
        {"action": "multiply", "a": 36, "b": 3},
        {"action": "add", "a": 12, "b": 12},
        {"final": "판매 수익 108달러, 판매하지 않은 달걀 24개"},
    ]
    return json.dumps(steps[observations], ensure_ascii=False)


def sprint_demo(messages):
    last = messages[-1]["content"]
    if not last.startswith("Observation: "):
        return '{"action":"multiply","a":3,"b":3}'
    value = int(last.split(": ")[1])
    if len(messages) == 4:
        return '{"action":"multiply","a":%d,"b":60}' % value
    return '{"final":"%d미터"}' % value


def ask(row, method, messages, remote):
    if remote is None:
        return scripted(row, method, messages)
    return remote(messages)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=MODES, default="demo")
    args = parser.parse_args()
    remote = None if args.provider == "demo" else RemoteChat(args.provider, max_calls=2)
    row = records()[0]
    print("실행 모드", args.provider)
    for method, messages in variants(row).items():
        print(method, ask(row, method, messages, remote), sep="\n")
