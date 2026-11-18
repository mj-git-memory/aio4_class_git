"""실제 DB나 접속정보 없이 설정 로딩만 검사합니다."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import db_config


class ConfigTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "config.json"
        env = patch.dict("os.environ", {}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        config_path = patch.object(db_config, "CONFIG_PATH", self.path)
        config_path.start()
        self.addCleanup(config_path.stop)

    def test_local_file_and_password_override(self):
        self.path.write_text(json.dumps({
            "host": "local.example", "user": "test-user", "password": "file-secret"
        }))
        with patch.dict("os.environ", {"PGPASSWORD": "env-secret"}):
            config = db_config.load_db_config()
        self.assertEqual(config["host"], "local.example")
        self.assertEqual(config["password"], "env-secret")

    def test_render_without_file(self):
        with patch.dict("os.environ", {
            "PGHOST": "render.example", "PGPORT": "6543", "PGDATABASE": "postgres",
            "PGUSER": "test-user", "PGPASSWORD": "env-secret"
        }):
            config = db_config.load_db_config()
        self.assertEqual(config["host"], "render.example")
        self.assertEqual(config["port"], 6543)

    def test_missing_settings(self):
        with self.assertRaisesRegex(ValueError, "접속정보가 부족"):
            db_config.load_db_config()

    def test_invalid_port_does_not_print_password(self):
        with patch.dict("os.environ", {
            "PGHOST": "test.example", "PGUSER": "test-user",
            "PGPASSWORD": "env-secret", "PGPORT": "invalid"
        }):
            with self.assertRaises(ValueError) as caught:
                db_config.load_db_config()
        self.assertNotIn("env-secret", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
