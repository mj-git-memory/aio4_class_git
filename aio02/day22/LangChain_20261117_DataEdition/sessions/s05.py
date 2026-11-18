from app.catalog import read_catalog
from app.cli import parser
from app.config import Settings
from app.providers import make_model, friendly_error
from app.pipeline import build_chain, sample_requests
from app.report import save_report

def main():
    p = parser(); p.add_argument("--question"); args = p.parse_args()
    records = read_catalog(args.data); request = sample_requests(records)[0]
    if args.question is not None: request["question"] = args.question
    settings = Settings.read(args.mock); chain = build_chain(make_model(settings), records)

    try:
        answer = chain.invoke(request); row = {**request, "answer": answer, "status": "ok"}
    except Exception as error:
        row = {**request, "error": friendly_error(error), "status": "error"}
        
    save_report(5, records, [row], args.data, settings)
    print(row)

if __name__ == "__main__":
    try: main()
    except Exception as error: raise SystemExit(friendly_error(error))
