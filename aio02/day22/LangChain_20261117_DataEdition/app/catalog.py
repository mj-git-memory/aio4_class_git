import json
import hashlib
from pathlib import Path
from app.config import ROOT

DEFAULT_DATA = ROOT / "data/products_public_derived.json"

def read_catalog(path=DEFAULT_DATA):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or not data:
        raise ValueError("상품 데이터는 비어 있지 않은 JSON 배열이어야 합니다.")
    if len(data) > 1000:
        raise ValueError("수업 데이터는 최대 1000개 상품으로 제한합니다.")
    records = []
    for index, row in enumerate(data, 1):
        if not isinstance(row, dict):
            raise ValueError(f"{index}번째 상품은 JSON 객체여야 합니다.")
        for key in ("title", "category", "description"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"{index}번째 상품의 {key}가 누락/잘못되었습니다.")
        # API id가 없으면 출처 파일의 행 번호를 사용한다. 두 종류를 혼동하지 않는다.
        record_id = "api-" + str(row["id"]) if "id" in row else f"row-{index:03d}"
        records.append({"record_id": record_id, "source_row": index, "raw": row,
                        "title": row["title"].strip(), "category": row["category"].strip(),
                        "description": row["description"].strip()})
    ids = [x["record_id"] for x in records]
    if len(ids) != len(set(ids)):
        raise ValueError("record_id가 중복됩니다.")
    return records

def find_product(records, record_id):
    for row in records:
        if row["record_id"] == record_id:
            return row
    raise ValueError("상품을 찾지 못했습니다: " + str(record_id))

def product_context(product):
    # 통화·재고·배송·보증처럼 확인하지 못한 사실은 맥락에 추가하지 않는다.
    fields = {k: product[k] for k in ("record_id", "title", "category", "description")}
    return json.dumps(fields, ensure_ascii=False, indent=2)

def data_info(path=DEFAULT_DATA):
    path = Path(path)
    meta_path = ROOT / "data/dataset_source.json" if path.resolve() == DEFAULT_DATA.resolve() else path.with_suffix(".source.json")
    info = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"acquisition": "imported_unverified", "source_url": "사용자가 지정한 로컬 파일"}
    return {**info, "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
