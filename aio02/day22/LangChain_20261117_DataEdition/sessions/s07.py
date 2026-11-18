import hashlib
import time
from langchain_core.output_parsers import StrOutputParser
from app.catalog import read_catalog
from app.cli import parser
from app.config import Settings
from app.providers import make_model, friendly_error
from app.pipeline import prepare_input, sample_requests
from app.prompts import get_prompt
from app.report import save_report

def main():
    p = parser(); p.add_argument("--repeats", type=int, default=1, choices=[1,2,3]); args = p.parse_args()
    records = read_catalog(args.data); settings = Settings.read(args.mock); model = make_model(settings)
    rows = []; stop = False
    for repeat in range(args.repeats):
        versions = ["weak", "role", "designed"]
        versions = versions[repeat:] + versions[:repeat]
        for request in sample_requests(records):
            values = prepare_input(request, records)
            for version in versions:
                started = time.perf_counter(); row = {**request, "version": version, "repeat": repeat+1,
                  "context_hash": hashlib.sha256(values["context"].encode()).hexdigest()[:12],
                  "question_hash": hashlib.sha256(values["question"].encode()).hexdigest()[:12],
                  "prompt_hash": hashlib.sha256(get_prompt(version).invoke(values).to_string().encode()).hexdigest()[:12]}
                try:
                    message = (get_prompt(version) | model).invoke(values)
                    print(message)
                    # answer = StrOutputParser().invoke(message)
                    # row.update(status="ok", answer=answer, characters=len(answer),
                            #    within_500_chars=len(answer)<=500, usage=message.usage_metadata)
                except Exception as error:
                    row.update(status="error", error=friendly_error(error))
                    stop = getattr(error, "status_code", None) == 429
                row["elapsed_seconds"] = round(time.perf_counter()-started,4); rows.append(row)
                if stop: break
            if stop: break
        if stop: break
    save_report(7, records, rows, args.data, settings,
                notes=["같은 상품·질문·모델을 사용합니다. 문자 수는 의미 품질 점수가 아닙니다."])
    print("기록 수:", len(rows))

if __name__ == "__main__":
    try: main()
    except Exception as error: raise SystemExit(friendly_error(error))
