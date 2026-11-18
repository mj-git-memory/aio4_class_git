import html
import json
from pathlib import Path
from datetime import datetime, timezone
from app.config import ROOT
from app.catalog import data_info


def save_report(session, records, result_rows, data_path, settings=None, notes=None):
    """실제 실행 결과를 HTML과 JSON으로 저장한다. 모델을 여기서 호출하지 않는다."""
    info = data_info(data_path)
    provider = settings.provider if settings else "not_called"
    model = settings.model if settings else "not_called"
    mode = "모의 모델 · 실제 추론 아님" if provider == "mock" else ("모델 호출 없음" if settings is None else "원격 모델 설정 · 항목별 실행 상태 확인")
    dataset_mode = "공개 가공 표본 · 원본 API 직접 수집 아님" if info["acquisition"] == "public_derived_file" else info["acquisition"]
    payload = {"topic_id": "U2-01", "session": session, "created_at": datetime.now(timezone.utc).isoformat(),
               "data": info, "dataset_mode": dataset_mode, "provider": provider, "model": model,
               "model_mode": mode, "temperature": settings.temperature if settings else None,
               "max_output": settings.max_output if settings else None, "notes": notes or [], "rows": result_rows}
    folder = ROOT / "reports"; folder.mkdir(exist_ok=True)
    stem = f"s{session:02d}_report"
    (folder / (stem + ".json")).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    def esc(x): return html.escape(str(x))
    items = []
    for row in result_rows:
        product = next((p for p in records if p["record_id"] == row.get("record_id")), None)
        raw = product["raw"] if product else {}
        items.append('<article><h2>' + esc(row.get("record_id", "데이터")) + ' · ' + esc(row.get("version", "결과")) + '</h2>'
          + '<div class="cols"><section><h3>상품 원문</h3><pre>'
          + esc(json.dumps(raw, ensure_ascii=False, indent=2)) + '</pre></section>'
          + '<section><h3>입력·메시지·실행 결과</h3><pre>'
          + esc(json.dumps(row, ensure_ascii=False, indent=2)) + '</pre></section></div></article>')
    text = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>U2-01 결과 화면</title><style>'
    text += 'body{font-family:"Malgun Gothic",sans-serif;background:#edf3fb;color:#17324f;margin:0;line-height:1.7}main{max-width:1220px;margin:30px auto;padding:32px;background:white;border-radius:16px}h1{font-size:28px}.badge{display:inline-block;padding:7px 13px;background:#dcebed;border-radius:6px;margin:4px;font-weight:bold;font-size:13px}.warn{background:#fff0cd}.meta{font-size:13px;color:#52677e}article{border:1px solid #d6e0ee;border-radius:12px;padding:20px;margin:20px 0}.cols{display:grid;grid-template-columns:1fr 1fr;gap:25px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.8 Consolas,monospace;background:#f5f8fc;padding:15px;border-radius:7px}h3{font-size:16px}@media(max-width:800px){.cols{grid-template-columns:1fr}main{margin:0;padding:20px}}@media print{body{background:white}main{margin:0;max-width:none}article{break-inside:avoid}}'
    text += '</style><main><p>2026-11-17 · LangChain · 제공 자료 활용 실습</p><h1>U2-01 / ' + str(session) + '차시 실행 결과</h1>'
    text += '<div class="badge warn">' + esc(dataset_mode) + '</div><div class="badge">' + esc(mode) + '</div>'
    text += '<p class="meta">데이터: ' + esc(info['file']) + ' / 공급자: ' + esc(provider) + ' / 모델: ' + esc(model) + '</p>'
    text += '<p class="meta">출처: ' + esc(info['source_url']) + '<br>SHA256: ' + esc(info['sha256']) + '</p>'
    text += '<p class="meta">캡처: 데이터 출처·표본 id·입력·결과·실행 모드를 포함해 저장합니다. 기관 승인 화면이 아닙니다.</p>'
    text += ''.join('<p>'+esc(note)+'</p>' for note in (notes or [])) + ''.join(items) + '</main></html>'
    path = folder / (stem + '.html'); path.write_text(text, encoding='utf-8')
    print('결과 화면:', path)
    return path
