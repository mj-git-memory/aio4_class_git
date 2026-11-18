"""같은 모델로 두 지시문을 실행한다."""
import argparse
from providers import RemoteChat
from s02 import records, variants
from lesson import demo

MODES = ("demo", "groq", "gemini", "openai")


def scripted(row, strategy, messages):
    if strategy == "react":
        if row["row_index"] == 0:
            return demo(messages)
        return sprint_demo(messages)
    if row["row_index"] == 0:
        return "답: 18달러" if strategy == "direct" else "16 − 3 − 4 = 9개\n9 × 2 = 18달러\n답: 18달러"
    return "답: 540미터" if strategy == "direct" else "주당 3 × 3 = 9회\n9 × 60 = 540미터\n답: 540미터"


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
