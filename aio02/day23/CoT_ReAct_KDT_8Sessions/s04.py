"""계산 요청 한 줄을 검사하고 실행한다."""
import argparse
import json
from lesson import calculate


def execute(reply):
    step = json.loads(reply)
    if not isinstance(step, dict) or set(step) != {"action", "a", "b"}:
        raise ValueError("계산 요청에는 action, a, b가 필요하다.")
    return calculate(step["action"], step["a"], step["b"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--action", default="subtract")
    p.add_argument("--a", type=int, default=16)
    p.add_argument("--b", type=int, default=3)
    args = p.parse_args()
    reply = json.dumps(vars(args))
    print(reply)
    print("Observation:", execute(reply))
