from app.catalog import read_catalog
from app.cli import parser
from app.pipeline import prepare_input, sample_requests
from app.prompts import get_prompt
from app.report import save_report

def main():
    args = parser().parse_args(); records = read_catalog(args.data)
    request = sample_requests(records)[0]; values = prepare_input(request, records)
    rows = []
    for version in ("weak", "role", "designed"):
        value = get_prompt(version).invoke(values)
        rows.append({**request, "version": version,
                     "messages": [{"role": m.type, "content": m.content} for m in value.to_messages()],
                     "status": "prompt_rendered_no_model"})
    save_report(3, records, rows, args.data)

if __name__ == "__main__": main()
