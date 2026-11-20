"""행동과 관찰을 번갈아 기록한다."""
import argparse
from lesson import MAX_REACT_TURNS, REACT, react, prompt
from s02 import records
from s03 import ask, MODES, RemoteChat


def trace(row, remote, events):
    messages = prompt(REACT, row["question"])
    def chat(history):
        return ask(row, "react", history, remote)
    react(messages, chat, events)
    return messages


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--row", type=int, choices=[0, 3], default=3)
    p.add_argument("--provider", choices=MODES, default="demo")
    args = p.parse_args()
    row = next(r for r in records() if r["row_index"] == args.row)
    remote = None if args.provider == "demo" else RemoteChat(
        args.provider, max_calls=MAX_REACT_TURNS
    )
    events = []
    try:
        messages = trace(row, remote, events)
    finally:
        print("실행 모드", args.provider)
        for label, body in events:
            print(label, body, sep="\n")
