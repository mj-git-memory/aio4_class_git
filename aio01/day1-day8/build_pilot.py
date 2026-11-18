"""실제 템플릿과 CSS로 서버 없이 열 수 있는 UI 확인용 HTML을 만든다."""

from html import escape
from pathlib import Path
from string import Template

BASE = Path(__file__).resolve().parent


def build_pilot():
    template = Template((BASE / "templates" / "index.html").read_text(encoding="utf-8"))
    samples = [
        ("서연", "오늘도 작은 걸음을 남기고 갑니다.\n이 공간에 좋은 이야기들이 가득 쌓이길 바라요.", "2026-10-23T14:20+09:00", "2026.10.23 · 14:20 KST"),
        ("지우", "잠깐 들렀는데 마음이 편안해지네요. 반갑습니다!", "2026-10-23T13:45+09:00", "2026.10.23 · 13:45 KST"),
        ("민서", "새로운 시작을 응원해요. 다음에 또 인사하러 올게요.", "2026-10-23T11:10+09:00", "2026.10.23 · 11:10 KST"),
    ]
    cards = []
    for name, message, stamp, label in samples:
        cards.append(
            '<article class="entry"><header>'
            f'<h3>{escape(name)}</h3><time datetime="{stamp}">{label}</time>'
            f'</header><p>{escape(message)}</p>'
            '<a class="edit-link" href="#write-title">수정</a></article>'
        )
    html = template.substitute(
        notice="", name="", message="", total=3, entries="".join(cards),
        pagination='<span aria-current="page">1 / 1</span>',
        form_title="안부 남기기", form_action="/entries",
        password_hint="숫자 4자리 · 수정할 때 필요해요",
        password_attributes='minlength="4" maxlength="4" pattern="[0-9]{4}" inputmode="numeric"',
        password_autocomplete="new-password", submit_label="방명록 남기기 ↗", cancel_link="",
    )
    css = (BASE / "static" / "style.css").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="/static/style.css">', f"<style>\n{css}\n</style>")
    html = html.replace("<title>작은 방명록</title>", "<title>작은 방명록 · UI 파일럿</title>")
    html = html.replace("<main>", '<main>\n    <aside class="pilot-banner">UI 파일럿 · 아래 글은 예시입니다. 입력·버튼은 실제 DB에 저장되지 않습니다.</aside>')
    # 정적 파일에서 Enter나 버튼으로 POST가 발생하지 않도록 폼을 제거한다.
    html = html.replace('<form action="/entries" method="post" accept-charset="UTF-8">', '<div class="pilot-form">')
    html = html.replace("</form>", "</div>").replace('type="submit"', 'type="button"')
    output = BASE / "pilot.html"
    output.write_text(html, encoding="utf-8")
    return output


if __name__ == "__main__":
    print(build_pilot())
