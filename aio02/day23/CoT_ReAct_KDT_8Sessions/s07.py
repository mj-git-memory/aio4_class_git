"""고정 응답을 넣어 형식 오류와 반복 종료를 재현한다."""
from lesson import REACT, react, prompt
from s02 import records

CASES = {
    "잘못된 JSON": "계산하겠습니다.",
    "연산명 오류": '{"action":"minus","a":16,"b":3}',
    "자료형 오류": '{"action":"subtract","a":"16","b":3}',
    "반복 상한": '{"action":"subtract","a":16,"b":3}',
    "수정한 최종 응답": '{"final":"18달러"}',
}


def replay(reply, question):
    events = []
    try:
        react(prompt(REACT, question), lambda history: reply, events)
        status = "종료"
    except ValueError as exc:
        status = str(exc)
    observations = [text for title, text in events if title == "계산 도구 · 반환값"]
    return status, observations


if __name__ == "__main__":
    for label, reply in CASES.items():
        status, observations = replay(reply, records()[0]["question"])
        print(label, status, observations, sep=" | ")
