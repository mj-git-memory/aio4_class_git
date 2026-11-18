import csv
import json
from pathlib import Path
from app.catalog import read_catalog
from app.cli import parser
from app.config import ROOT, Settings
from app.providers import make_model, friendly_error
from app.pipeline import build_chain, sample_requests
from app.report import save_report

def main():
    p = parser(); p.add_argument("--input", type=Path); p.add_argument("--limit", type=int, default=3, choices=range(1,6)); args=p.parse_args()
    records=read_catalog(args.data)
    if args.input:
        with args.input.open(encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f)
            if not reader.fieldnames or not {"record_id","question"}<=set(reader.fieldnames):
                raise ValueError("CSV 헤더는 record_id,question을 포함해야 합니다.")
            requests=[]
            for i,row in enumerate(reader):
                if i>=args.limit: break
                requests.append(row)
    else: requests=sample_requests(records)[:args.limit]
    settings=Settings.read(args.mock); chain=build_chain(make_model(settings),records); rows=[]
    for request in requests:
        try: row={**request,"answer":chain.invoke(request),"status":"ok"}
        except Exception as error:
            row={**request,"error":friendly_error(error),"status":"error"}; rows.append(row)
            if getattr(error,"status_code",None)==429: break
            continue
        rows.append(row)
    out=ROOT/"outputs/drafts.jsonl"; out.parent.mkdir(exist_ok=True)
    out.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in rows),encoding="utf-8")
    save_report(8,records,rows,args.data,settings)
    print("성공",sum(x["status"]=="ok" for x in rows),"/ 오류",sum(x["status"]=="error" for x in rows))
    print("데이터 결과:",out)

if __name__=="__main__":
    try: main()
    except Exception as error: raise SystemExit(friendly_error(error))
