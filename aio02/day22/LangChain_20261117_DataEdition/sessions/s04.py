from langchain_core.output_parsers import StrOutputParser
from app.catalog import read_catalog
from app.cli import parser
from app.config import Settings
from app.providers import make_model, friendly_error
from app.prompts import get_prompt
from app.pipeline import prepare_input, sample_requests
from app.report import save_report

def main():
    p = parser(); p.add_argument("--manual", action="store_true"); args = p.parse_args()
    records = read_catalog(args.data); request = sample_requests(records)[0]
    values = prepare_input(request, records); settings = Settings.read(args.mock)
    model = make_model(settings); prompt = get_prompt(); output_parser = StrOutputParser()
    prompt_value = prompt.invoke(values)
    print(prompt_value); print()
    message = model.invoke(prompt_value)
    print(message); print()
    answer = output_parser.invoke(message)
    print(answer); print()
    chain = prompt | model | output_parser
    print(chain.invoke(values)); print()

    if args.manual:
        prompt_value = prompt.invoke(values)
        message = model.invoke(prompt_value)
        answer = output_parser.invoke(message)
    else:
        chain = prompt | model | output_parser
        answer = chain.invoke(values)
    print(answer)
    save_report(4, records, [{**request, "context": values["context"], "answer": answer,
                            "status": "ok", "execution": "manual" if args.manual else "LCEL"}], args.data, settings)

if __name__ == "__main__":
    try: main()
    except Exception as error: raise SystemExit(friendly_error(error))
