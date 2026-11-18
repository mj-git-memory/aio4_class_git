"""같은 질문에 정답 지시와 풀이 예시를 각각 결합한다."""
import argparse
import json
from lesson import ROOT, COT, prompt

DIRECT = "최종 답을 '답: 숫자 단위' 한 줄로 작성한다."
WORKED = COT + "\n마지막 줄은 '답: 숫자 단위'로 작성한다. 예: 답: 3자루"


def records():
    return json.loads((ROOT / "data/problems.json").read_text(encoding="utf-8"))


def variants(row):
    return {name: prompt(instruction, row["question"])
            for name, instruction in [("direct", DIRECT), ("cot", WORKED)]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", choices=[0, 3], type=int, default=0)
    args = parser.parse_args()
    row = next(r for r in records() if r["row_index"] == args.row)
    for name, messages in variants(row).items():
        print(name)
        for message in messages:
            print(message["role"], message["content"], sep="\n")
