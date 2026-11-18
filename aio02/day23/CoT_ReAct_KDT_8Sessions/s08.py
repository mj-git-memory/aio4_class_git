"""6차시의 실행 기록으로 결과 화면을 만든다."""
import argparse
import json
from html import escape
from pathlib import Path
from lesson import ROOT


def report(path):
    cases = json.loads(path.read_text(encoding="utf-8"))
    parts = []
    for case in cases:
        status = case["status"]
        if status == "완료":
            status = "수치 일치" if case["predicted"] == case["expected"] else "수치 불일치"
        parts.append(f"<section><h2>원본 행 {int(case['row'])} · {escape(case['method'])}</h2>")
        parts.append(f"<p>{escape(case['provider'])} / {escape(case['model'])} · {escape(status)} · 도구 실행 {int(case['tools'])}회</p>")
        fields = [("원본 문제", case["question"]), ("프롬프트", case["instruction"]),
                  *case["events"], ("원본 풀이와 답", case["reference"])]
        for title, body in fields:
            parts.append(f"<h3>{escape(title)}</h3><pre>{escape(body)}</pre>")
        parts.append("</section>")
    source = "https://huggingface.co/datasets/openai/gsm8k/tree/main"
    page = f"""<!doctype html><html lang="ko"><meta charset="utf-8"><title>GSM8K 실행 비교</title>
<style>body{{font:16px/1.6 sans-serif;max-width:760px;margin:2em auto}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}@media print{{section+section{{break-before:page}}}}</style>
<h1>프롬프트별 실행 결과</h1><p>지정 자료 D04 · <a href="{source}">openai/gsm8k</a> · main / test · 원본 행은 0부터 센다.</p>
{''.join(parts)}</html>"""
    target = path.with_suffix(".html")
    target.write_text(page, encoding="utf-8")
    return target


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path)
    args = p.parse_args()
    files = sorted((ROOT / "results").glob("compare_*.json"))
    if args.input is None and not files:
        p.error("먼저 python s06.py를 실행한다.")
    print(report(args.input or files[-1]))
