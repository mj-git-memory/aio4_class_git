"""같은 문제와 모델에서 세 방식의 실행 기록을 모은다."""
import argparse
from datetime import datetime
import json
import re
from lesson import MAX_REACT_TURNS, ROOT, REACT
from s02 import records, variants
from s03 import MODES, RemoteChat, ask
from s05 import trace


NUMBER = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?")
ANSWER_MARKER = re.compile(r"(?:최종\s*)?(?:정답|답)\s*[:：]?", re.IGNORECASE)


def answer_numbers(text):
    if not text.strip():
        return []
    markers = list(ANSWER_MARKER.finditer(text))
    answer = text[markers[-1].end():] if markers else text.strip().splitlines()[-1]
    return [float(match.replace(",", "")) for match in NUMBER.findall(answer)]


def display_number(values):
    if not values:
        return None
    return values[0] if len(values) == 1 else values


def compare(row, remote, provider):
    cases = []
    templates = variants(row)
    for method in ("direct", "cot", "react"):
        events = []
        call_count = remote.calls if remote else 0
        expected = row["answer"].split("####")[-1].strip()
        expected_numbers = answer_numbers(expected)
        instruction = REACT if method == "react" else templates[method][0]["content"]
        case = dict(row=row["row_index"], question=row["question"], method=method,
                    provider=provider, model=remote.model if remote else "교사 대본",
                    instruction=instruction, events=events, status="실행 중",
                    predicted=None, expected=expected, expected_numbers=expected_numbers,
                    correct=None)
        try:
            if method == "react":
                trace(row, remote, events)
                reply = json.loads(events[-1][1])["final"]
            else:
                reply = ask(row, method, templates[method], remote)
                events.append(("모델 응답", reply))
            predicted_numbers = answer_numbers(reply)
            case["predicted"] = display_number(predicted_numbers)
            if not predicted_numbers:
                case["status"] = "답 형식 확인"
            elif not expected_numbers:
                case["status"] = "기준 답 형식 확인"
            else:
                case["correct"] = predicted_numbers == expected_numbers
                case["status"] = "정답 일치" if case["correct"] else "정답 불일치"
        except (ValueError, RuntimeError) as exc:
            case["status"] = "실행 중단"
            events.append(("오류", str(exc)))
        case["reference"] = row["answer"]
        case["tools"] = sum(label == "계산 도구 · 반환값" for label, _ in events)
        case["api_requests"] = remote.calls - call_count if remote else 0
        cases.append(case)
    return cases


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=MODES, default="demo")
    args = p.parse_args()
    rows = records()
    remote = None if args.provider == "demo" else RemoteChat(
        args.provider, max_calls=len(rows) * (MAX_REACT_TURNS + 2)
    )
    cases = []
    for row in rows:
        cases.extend(compare(row, remote, args.provider))
    directory = ROOT / "results"
    directory.mkdir(exist_ok=True)
    path = directory / f"compare_{datetime.now():%Y%m%d_%H%M%S_%f}.json"
    path.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in cases:
        print(item["row"], item["method"], item["status"], item["predicted"],
              "API", item["api_requests"], "도구", item["tools"])
    print(path)
