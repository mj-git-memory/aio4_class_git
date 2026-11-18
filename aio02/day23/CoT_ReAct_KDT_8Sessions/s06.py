"""같은 문제와 모델에서 세 방식의 실행 기록을 모은다."""
import argparse
from datetime import datetime
import json
import re
from lesson import ROOT, REACT
from s02 import records, variants
from s03 import MODES, RemoteChat, ask
from s05 import trace


def number(text):
    if not text.strip():
        return None
    last_line = text.strip().splitlines()[-1]
    match = re.fullmatch(r"(?:답:\s*)?(-?\d+(?:\.\d+)?)\s*(?:달러|미터|m|USD)?[.]?", last_line)
    return float(match[1]) if match else None


def compare(row, remote, provider):
    cases = []
    templates = variants(row)
    for method in ("direct", "cot", "react"):
        events = []
        instruction = REACT if method == "react" else templates[method][0]["content"]
        case = dict(row=row["row_index"], question=row["question"], method=method,
                    provider=provider, model=remote.model if remote else "교사 대본",
                    instruction=instruction, events=events, status="완료", predicted=None)
        try:
            if method == "react":
                trace(row, remote, events)
                reply = json.loads(events[-1][1])["final"]
                # 수업용 규약: 설명 뒤에 수량과 단위가 오는 답도 허용한다.
                suffix = re.search(r"(-?\d+(?:\.\d+)?)\s*(달러|미터|m|USD)(?:이다)?[.]?$", reply.strip())
                value = number(suffix[1] + suffix[2]) if suffix else number(reply)
            else:
                reply = ask(row, method, templates[method], remote)
                events.append(("모델 응답", reply))
                value = number(reply)
            case["predicted"] = value
            if value is None:
                case["status"] = "답 형식 확인"
        except (ValueError, RuntimeError) as exc:
            case["status"] = "실행 중단"
            events.append(("오류", str(exc)))
        case["reference"] = row["answer"]
        case["expected"] = float(row["answer"].split("####")[-1].strip())
        case["tools"] = sum(label == "계산 도구 · 반환값" for label, _ in events)
        cases.append(case)
    return cases


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=MODES, default="demo")
    args = p.parse_args()
    remote = None if args.provider == "demo" else RemoteChat(args.provider, max_calls=14)
    cases = []
    for row in records():
        cases.extend(compare(row, remote, args.provider))
    directory = ROOT / "results"
    directory.mkdir(exist_ok=True)
    path = directory / f"compare_{datetime.now():%Y%m%d_%H%M%S_%f}.json"
    path.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in cases:
        print(item["row"], item["method"], item["status"], item["predicted"], item["tools"])
    print(path)
