"""원본 API를 한 번 요청하거나 사용자가 저장한 JSON을 가져온다."""
import argparse
import json
import shutil
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from app.catalog import read_catalog
from app.config import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-file", type=Path)
    args = parser.parse_args()
    target = ROOT / "data/products_live.json"
    if args.import_file:
        read_catalog(args.import_file)
        target.write_bytes(args.import_file.read_bytes())
        mode, origin = "imported_file_origin_not_independently_verified", str(args.import_file.name)
    else:
        origin = "https://fakestoreapi.com/products"
        try:
            with urllib.request.urlopen(origin, timeout=20) as response:
                content = response.read(2_000_001)
            if len(content) > 2_000_000:
                raise ValueError("응답 크기가 수업용 상한 2MB를 넘었습니다.")
            data = json.loads(content)
            temp = ROOT / "data/products_download_check.json"
            temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            read_catalog(temp)
            temp.replace(target)
            mode = "direct_api_download"
        except Exception as error:
            raise SystemExit(f"API 수집 미완료 ({type(error).__name__}). 브라우저에서 정상 응답을 저장한 경우 --import-file로 가져오세요. 보안 확인을 우회하지 않습니다.")
    meta = {"resource_id": "D01", "source_url": origin, "original_api": "https://fakestoreapi.com/products",
            "acquisition": mode, "checked_on": datetime.now(timezone.utc).isoformat(),
            "record_count": len(read_catalog(target)), "limitation": "현재 실행 환경에서 검증한 취득 방식만 기록"}
    target.with_suffix('.source.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print('저장:', target)

if __name__ == '__main__':
    main()
