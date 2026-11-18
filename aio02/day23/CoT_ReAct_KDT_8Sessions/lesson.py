"""두 프롬프트를 같은 문제에 적용하고 메시지와 계산 결과를 기록한다."""
import argparse
import json
from datetime import datetime
from html import escape
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from providers import RemoteChat

ROOT = Path(__file__).resolve().parent
COT = """예시처럼 계산식과 단위를 사용해 한국어로 풀이하고 마지막 줄에 답을 쓴다.
예시 문제: 연필 10자루 중 4자루를 쓰고 나머지를 두 명에게 똑같이 나눈다.
예시 풀이: 남은 연필은 10 - 4 = 6자루이다. 한 명의 몫은 6 ÷ 2 = 3자루이다.
예시 답: 3자루"""
REACT = """문제를 풀 때 계산 도구를 사용한다. 한 번에 JSON 객체 하나만 출력한다.
계산 요청 예: {"action":"subtract","a":10,"b":4}
사용 가능한 action은 add, subtract, multiply이다. a와 b에는 정수를 쓴다.
직전 계산 결과는 Observation 메시지로 전달된다. 다음 계산에는 그 값을 사용한다.
답을 구하면 {"final":"단위가 있는 한국어 답"} 형식으로 마친다."""


def prompt(system, question):
    template = ChatPromptTemplate.from_messages([
        ("system", "{instruction}"), ("human", "{question}")
    ])
    value = template.invoke({"instruction": system, "question": question})
    instruction, problem = value.to_messages()
    return [{"role": "system", "content": instruction.content},
            {"role": "user", "content": problem.content}]


def calculate(action, a, b):
    if type(a) is not int or type(b) is not int:
        raise ValueError("a와 b에는 정수를 입력한다.")
    if action == "add":
        return a + b
    if action == "subtract":
        return a - b
    if action == "multiply":
        return a * b
    raise ValueError(f"지원하지 않는 연산: {action}")


def react(messages, chat, events):
    for _ in range(5):
        reply = chat(messages)
        events.append(("ReAct · 모델 응답", reply))
        messages.append({"role": "assistant", "content": reply})
        step = json.loads(reply)
        if isinstance(step, dict) and set(step) == {"final"} and isinstance(step["final"], str):
            return
        if not isinstance(step, dict) or set(step) != {"action", "a", "b"}:
            raise ValueError("action, a, b 또는 final 필드를 확인한다.")
        value = calculate(step["action"], step["a"], step["b"])
        observation = f"Observation: {value}"
        events.append(("계산 도구 · 반환값", observation))
        messages.append({"role": "user", "content": observation})
    raise ValueError("다섯 번의 응답 안에 최종 답이 없어 종료했다.")


def demo(messages):
    if messages[0]["content"] == COT:
        return "판매량은 16 - 3 - 4 = 9개이다. 하루 판매액은 9 × 2 = 18달러이다.\n답: 18달러"
    last = messages[-1]["content"]
    if last.startswith("Observation: "):
        number = int(last.split(": ")[1])
        count = sum(m["content"].startswith("Observation: ") for m in messages)
        if count == 1:
            return json.dumps({"action": "subtract", "a": number, "b": 4})
        if count == 2:
            return json.dumps({"action": "multiply", "a": number, "b": 2})
        return json.dumps({"final": f"하루 판매액은 {number}달러이다."}, ensure_ascii=False)
    return '{"action":"subtract","a":16,"b":3}'


def save(events, mode, row):
    directory = ROOT / "results"
    directory.mkdir(exist_ok=True)
    path = directory / f"{mode}_{datetime.now():%Y%m%d_%H%M%S_%f}.html"
    sections = "".join(f"<h3>{escape(title)}</h3><pre>{escape(body)}</pre>" for title, body in events)
    source = "https://huggingface.co/datasets/openai/gsm8k/tree/main"
    path.write_text(f"""<!doctype html><html lang="ko"><meta charset="utf-8"><title>1차시 실행 기록</title>
<style>body{{font:16px/1.6 sans-serif;max-width:760px;margin:3em auto}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}h3{{break-after:avoid}}</style>
<h1>1차시 실행 기록</h1><p>{escape(mode)} · {escape(row['id'])}</p>
<p>지정 데이터 D04 · <a href="{source}">openai/gsm8k</a> · main / test · 원본 행 0 (첫 번째)</p>
{sections}</html>""", encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["demo", "groq", "gemini", "openai"], default="demo")
    mode = parser.parse_args().provider
    row = json.loads((ROOT / "data/problem.json").read_text(encoding="utf-8"))
    question = row["question"]
    events = [("문제 원문", question)]
    try:
        chat = demo if mode == "demo" else RemoteChat(mode, max_calls=6)
        label = "교사용 대본 · 로컬 계산" if mode == "demo" else f"{mode} · {chat.model}"
        events.append(("실행 방식", label))
        events.append(("CoT · 작성한 프롬프트", COT))
        events.append(("CoT · 모델 응답", chat(prompt(COT, question))))
        events.append(("ReAct · 작성한 프롬프트", REACT))
        react(prompt(REACT, question), chat, events)
        events.append(("원본 풀이와 정답", row["answer"]))
    except (ValueError, RuntimeError) as exc:
        events.append(("실행 중단", str(exc)))
        raise SystemExit(str(exc)) from None
    finally:
        for title, body in events:
            print(title, body, sep="\n")
        print(save(events, mode, row))


if __name__ == "__main__":
    main()
