from importlib.metadata import version
from app.catalog import read_catalog, data_info
from app.cli import parser
from app.report import save_report

def main():
    args = parser().parse_args()
    print('args: ', args)
    print('args.data: ', args.data)
    print()
    records = read_catalog(args.data)
    print(records)
    print()
    print("langchain-core", version("langchain-core"))
    print("상품 수:", len(records), "/ 데이터 방식:", data_info(args.data)["acquisition"])
    first = records[0]
    print(first["record_id"], first["title"])
    save_report(1, records, [{"record_id": first["record_id"], "fields": list(first["raw"]),
                            "status": "data_loaded_no_model"}], args.data)

if __name__ == "__main__": main()
