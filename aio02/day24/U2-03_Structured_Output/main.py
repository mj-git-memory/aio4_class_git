"""U2-03 | 실제 원본을 읽고 생성 결과를 검증한다."""
import argparse
import csv
import hashlib
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, ValidationError

ROOT = Path(__file__).resolve().parent
FILES = {"bank": "bank.csv", "product": "fakestore_products.json"}
SOURCES = {
    "bank": "https://archive.ics.uci.edu/dataset/222/bank+marketing",
    "product": "https://fakestoreapi.com/products",
}
MODELS = {"groq": "openai/gpt-oss-20b", "openai": "gpt-4o-mini", "gemini": "gemini-3.5-flash"}
RULES = {
    "bank": "전화 접촉 기록을 정규화하라. duration은 초 단위 duration_s, campaign은 contacts, "
            "poutcome은 previous_result에 넣고 unknown은 null로 바꿔라. 그 외 값은 그대로 옮겨라.",
    "product": "상품 카탈로그를 정규화하라. title, category, price를 각각 원문 그대로 옮겨라. 통화 변환이나 반올림을 하지 마라.",
}


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Contact(Contract):
    duration_s: int
    contacts: int
    previous_result: Literal["success", "failure", "other"] | None


class Product(Contract):
    title: str
    category: str
    price: float


TYPES = {"bank": Contact, "product": Product}


def read_rows(dataset):
    path = ROOT / "data" / FILES[dataset]
    if dataset == "product" and not path.exists():
        req = Request(SOURCES[dataset], headers={"Accept": "application/json"})
        with urlopen(req, timeout=30) as response:
            payload = response.read()
        rows = json.loads(payload)
        if not isinstance(rows, list) or not rows:
            raise ValueError("상품 원본은 비어 있지 않은 JSON 배열이어야 합니다.")
        for item in rows:
            reference(dataset, project(dataset, item))
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            stream.write(payload)
            temporary = Path(stream.name)
        temporary.replace(path)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        if dataset == "bank":
            return list(csv.DictReader(stream, delimiter=";"))
        return json.load(stream)


def project(dataset, source):
    keys = ("duration", "campaign", "poutcome") if dataset == "bank" else ("title", "category", "price")
    return {key: source[key] for key in keys}


def reference(dataset, row):
    if dataset == "product":
        return Product.model_validate(row)
    return Contact(duration_s=int(row["duration"]), contacts=int(row["campaign"]),
                   previous_result=None if row["poutcome"] == "unknown" else row["poutcome"])


def diagnose(row):
    base = reference("bank", row).model_dump()
    missing = base.copy()
    del missing["previous_result"]
    cases = {"원본 변환": base, "필수 키 누락": missing,
             "숫자 문자열": {**base, "duration_s": str(base["duration_s"])},
             "허용 목록 밖": {**base, "previous_result": "unknown"},
             "추가 키": {**base, "y": "yes"}, "다른 정수": {**base, "contacts": base["contacts"] + 1}}
    result = {}
    for name, value in cases.items():
        try:
            parsed = Contact.model_validate(value)
            result[name] = "통과" if parsed.model_dump() == base else "형식 통과 / 원본 불일치"
        except ValidationError as exc:
            result[name] = [(e["loc"], e["type"]) for e in exc.errors()]
    return result


def call_api(provider, prompt, schema_type, mode, report):
    key = os.getenv(provider.upper() + "_API_KEY")
    if not key:
        raise ValueError(provider.upper() + "_API_KEY 설정 필요")
    model = os.getenv(provider.upper() + "_MODEL") or MODELS[provider]
    event = {"provider": provider, "requested_model": model}
    report["attempts"].append(event)
    schema = schema_type.model_json_schema()
    if mode == "chain":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=model, api_key=key, max_retries=0, timeout=60)
        chain = llm.with_structured_output(schema_type, method="json_schema", strict=True, include_raw=True)
        reply = chain.invoke(prompt)
        raw = reply["raw"]
        event["actual_model"] = raw.response_metadata.get("model_name", model)
        report["finish"] = raw.response_metadata.get("finish_reason")
        report["raw"] = raw.content
        if raw.additional_kwargs.get("refusal") or report["finish"] != "stop" or reply["parsing_error"] or reply["parsed"] is None:
            raise ValueError("거절·중단 또는 파싱 실패: " + str(report["finish"]))
        return reply["parsed"].model_dump_json()
    if provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {"x-goog-api-key": key}
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        if mode == "strict":
            body["generationConfig"] = {"responseMimeType": "application/json", "responseJsonSchema": schema}
    else:
        base = "https://api.groq.com/openai/v1" if provider == "groq" else "https://api.openai.com/v1"
        url = base + "/chat/completions"
        headers = {"Authorization": "Bearer " + key}
        body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        if mode == "strict":
            body["response_format"] = {"type": "json_schema", "json_schema": {
                "name": schema_type.__name__, "strict": True, "schema": schema}}
    req = Request(url, data=json.dumps(body).encode(), headers={**headers, "Content-Type": "application/json"})
    with urlopen(req, timeout=60) as response:
        data = json.load(response)
    event["actual_model"] = data.get("modelVersion") or data.get("model") or model
    if provider == "gemini":
        candidate = next(iter(data.get("candidates", [])), {})
        report["finish"] = candidate.get("finishReason") or data.get("promptFeedback", {}).get("blockReason")
        content = "".join(p.get("text", "") for p in candidate.get("content", {}).get("parts", []) if not p.get("thought"))
        complete = report["finish"] == "STOP"
    else:
        choice = data["choices"][0]
        report["finish"] = choice["finish_reason"]
        msg = choice["message"]
        content = msg.get("content")
        complete = report["finish"] == "stop" and not msg.get("refusal")
    report["raw"] = content
    if not complete or not content:
        raise ValueError(f"거절·중단·빈 응답 (종료 사유 {report['finish']})")
    return content


def generate(provider, mode, dataset, row, report):
    cls = TYPES[dataset]
    prompt = "\n".join([RULES[dataset], "JSON 객체 하나만 출력하라.",
                        "출력 명세 " + json.dumps(cls.model_json_schema(), ensure_ascii=False),
                        "입력 " + json.dumps(row, ensure_ascii=False)])
    report["prompt"] = prompt
    try:
        raw = call_api(provider, prompt, cls, mode, report)
    except HTTPError as exc:
        report["attempts"][-1]["http_status"] = exc.code
        if exc.code != 429 or provider not in ("groq", "gemini"):
            raise
        report["fallback"] = f"{provider} HTTP 429 → OpenAI"
        raw = call_api("openai", prompt, cls, mode, report)
    parsed = cls.model_validate_json(raw)
    report["parsed"] = parsed.model_dump()
    report["schema_ok"] = True
    if parsed != reference(dataset, row):
        raise ValueError("원본 대조 실패")
    report["source_ok"] = True


def write_report(report):
    folder = ROOT / "runs"
    folder.mkdir(exist_ok=True)
    stem = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    data = json.dumps(report, indent=2, ensure_ascii=False)
    (folder / (stem + ".json")).write_text(data, encoding="utf-8")
    blocks = []
    for key, value in report.items():
        printable = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
        blocks.append(f"<h2>{html.escape(key)}</h2><pre>{html.escape(printable)}</pre>")
    page = "<meta charset=utf-8><style>body{font:15px sans-serif;max-width:850px;margin:3em auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef4f3;padding:1em}h2{font-size:17px}</style><h1>구조화 출력 실행 기록</h1>"
    path = folder / (stem + ".html")
    path.write_text(page + "".join(blocks), encoding="utf-8")
    print(data, path, sep="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["inspect", "schema", "diagnose", "plain", "strict", "chain"])
    parser.add_argument("--dataset", choices=FILES, default="bank")
    parser.add_argument("--provider", choices=MODELS, default="groq")
    parser.add_argument("--row", type=int, default=1)
    args = parser.parse_args()
    if args.mode == "chain" and args.provider != "openai":
        parser.error("chain은 --provider openai로 실행하세요.")
    if args.mode == "diagnose" and args.dataset != "bank":
        parser.error("diagnose는 bank 전용입니다.")
    names = {"bank": "Bank Marketing Dataset", "product": "Fake Store API Data (JSON)"}
    report = {"mode": args.mode, "dataset_name": names[args.dataset], "source": SOURCES[args.dataset]}
    try:
        rows = read_rows(args.dataset)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report.update(status="error", error=str(exc))
        write_report(report)
        return 1
    if not 1 <= args.row <= len(rows):
        parser.error(f"--row 범위는 1~{len(rows)}입니다.")
    row = project(args.dataset, rows[args.row - 1])
    path = ROOT / "data" / FILES[args.dataset]
    report.update({"file": path.name,
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "row": args.row, "input": row})
    try:
        if args.mode == "schema":
            report["schema"] = TYPES[args.dataset].model_json_schema()
        elif args.mode == "diagnose":
            report["validation"] = diagnose(row)
        elif args.mode != "inspect":
            report["attempts"] = []
            generate(args.provider, args.mode, args.dataset, row, report)
        report["status"] = "ok"
    except Exception as exc:
        report.update(status="error", error=f"{type(exc).__name__}: {exc}")
    write_report(report)
    return int(report["status"] == "error")


if __name__ == "__main__":
    raise SystemExit(main())
