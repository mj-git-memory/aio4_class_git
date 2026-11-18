from app.catalog import read_catalog
from app.cli import parser
from app.config import Settings
from app.providers import make_model, friendly_error
from app.pipeline import build_chain, sample_requests
from app.report import save_report

def main():
    p = parser(); p.add_argument("--stream", action="store_true"); args = p.parse_args()
    records = read_catalog(args.data); inputs = sample_requests(records)
    settings = Settings.read(args.mock); chain = build_chain(make_model(settings), records)
    if args.stream:
        chunks = []
        for chunk in chain.stream(inputs[0]):
            print(chunk, end="", flush=True); chunks.append(chunk)
        print(); rows = [{**inputs[0], "answer": "".join(chunks), "status": "ok", "execution": "stream"}]
    else:
        outputs = chain.batch(inputs, config={"max_concurrency": 1}, return_exceptions=True)
        rows = [{**request, **({"status": "error", "error": friendly_error(output)} if isinstance(output, Exception)
                 else {"status": "ok", "answer": output}), "execution": "batch"} for request, output in zip(inputs, outputs)]
    save_report(6, records, rows, args.data, settings)

if __name__ == "__main__":
    try: main()
    except Exception as error: raise SystemExit(friendly_error(error))
