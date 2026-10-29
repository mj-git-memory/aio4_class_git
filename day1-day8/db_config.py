"""로컬 config.json과 배포 환경변수에서 PostgreSQL 접속정보를 읽습니다."""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().with_name("config.json")


def load_db_config():
    config = {}
    if CONFIG_PATH.is_file():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    # 환경변수가 로컬 파일보다 우선합니다. Render에서는 파일 없이 설정합니다.
    config = {
        "host": os.environ.get("PGHOST", config.get("host")),
        "port": os.environ.get("PGPORT", config.get("port", 5432)),
        "dbname": os.environ.get("PGDATABASE", config.get("dbname", config.get("database", "postgres"))),
        "user": os.environ.get("PGUSER", config.get("user")),
        "password": os.environ.get("PGPASSWORD", config.get("password")),
    }
    missing = [key for key, value in config.items() if value is None or value == ""]
    if missing:
        raise ValueError(
            "DB 접속정보가 부족합니다: " + ", ".join(missing)
            + ". 로컬 config.json 또는 PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD를 설정하세요."
        )
    try:
        config["port"] = int(config["port"])
        if not 1 <= config["port"] <= 65535:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("DB port는 1~65535 사이의 정수여야 합니다.") from None
    return config
