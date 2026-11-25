"""임시 SQLite DB로 단일 SQL Tool과 조회 전용 제한을 검증합니다."""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import custom_tools as tools


class CustomToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory(prefix="tool_test_", dir=tools.ROOT)
        cls.path = Path(cls.temp.name) / "test.sqlite3"
        cls.environment = patch.dict(os.environ, {"SQLITE_DB_PATH": str(cls.path)})
        cls.environment.start()
        tools.initialize_database()

    @classmethod
    def tearDownClass(cls):
        cls.environment.stop()
        assert Path(cls.temp.name).resolve().parent == tools.ROOT
        cls.temp.cleanup()

    def test_exact_counts_and_relationships(self):
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0], 100)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM card_transactions").fetchone()[0], 1000)
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT COUNT(DISTINCT corporate_card_id) FROM card_transactions").fetchone()[0], 100)

    def test_reinitialization_preserves_data(self):
        before = tools.query_database("SELECT SUM(amount_krw) AS total FROM card_transactions")
        self.assertFalse(tools.initialize_database()["created"])
        self.assertEqual(before, tools.query_database("SELECT SUM(amount_krw) AS total FROM card_transactions"))

    def test_only_dynamic_sql_tool_is_registered(self):
        self.assertEqual(set(tools.TOOL_REGISTRY), {"query_database"})
        self.assertEqual([item["name"] for item in tools.TOOL_DEFINITIONS], ["query_database"])

    def test_arbitrary_columns_filters_and_bound_values(self):
        sql = "SELECT employee_id, name, department FROM employees WHERE employee_id = ?"
        result = tools.query_database(sql, ["E001"])
        self.assertEqual(result["status"], "success")
        row = json.loads(json.dumps(result, ensure_ascii=False))["data"]["rows"][0]
        self.assertEqual(set(row), {"employee_id", "name", "department"})
        self.assertEqual(row["employee_id"], "E001")
        self.assertEqual(tools.query_database(sql, ["E999"])["data"]["rows"], [])
        self.assertEqual(tools.query_database(sql, ["' OR 1=1 --"])["data"]["rows"], [])

    def test_query_reads_live_database(self):
        select = "SELECT department FROM employees WHERE employee_id=?"
        original = tools.query_database(select, ["E001"])["data"]["rows"][0]["department"]
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute("UPDATE employees SET department=? WHERE employee_id=?", ("검증부서", "E001"))
            connection.commit()
        try:
            self.assertEqual(tools.query_database(select, ["E001"])["data"]["rows"][0]["department"], "검증부서")
        finally:
            with closing(sqlite3.connect(self.path)) as connection:
                connection.execute("UPDATE employees SET department=? WHERE employee_id=?", (original, "E001"))
                connection.commit()

    def test_join_aggregation_and_cte(self):
        sql = """WITH usage AS (
            SELECT e.department, t.amount_krw FROM employees e
            JOIN card_transactions t ON e.corporate_card_id=t.corporate_card_id
        ) SELECT department, COUNT(*) AS count, SUM(amount_krw) AS total
          FROM usage GROUP BY department ORDER BY total DESC"""
        result = tools.query_database(sql)
        self.assertEqual(result["status"], "success")
        rows = result["data"]["rows"]
        self.assertEqual(sum(row["count"] for row in rows), 1000)
        self.assertEqual([row["total"] for row in rows], sorted([row["total"] for row in rows], reverse=True))

    def test_bound_dates_and_card_owner_join(self):
        sql = """SELECT COUNT(*) AS count, COALESCE(SUM(t.amount_krw),0) AS total
            FROM employees e JOIN card_transactions t ON e.corporate_card_id=t.corporate_card_id
            WHERE e.name=? AND t.used_at BETWEEN ? AND ?"""
        result = tools.query_database(sql, ["김가온", "2026-11-01", "2026-11-30"])
        self.assertEqual(result["data"]["rows"], [{"count": 3, "total": 423500}])
        self.assertEqual(tools.query_database(sql, ["김가온", "2030-01-01", "2030-01-31"])["data"]["rows"],
                         [{"count": 0, "total": 0}])

    def test_numeric_parameters_preserve_aggregate_comparisons(self):
        sql = "SELECT corporate_card_id, SUM(amount_krw) AS total FROM card_transactions GROUP BY corporate_card_id HAVING SUM(amount_krw)>=?"
        numeric = tools.query_database(sql, [1000000])
        self.assertEqual(numeric["status"], "success")
        self.assertTrue(numeric["data"]["rows"])
        self.assertTrue(all(row["total"] >= 1000000 for row in numeric["data"]["rows"]))
        via_tool = tools.execute_tool("query_database", json.dumps({"sql": sql, "parameters": [1000000]}))
        self.assertEqual(numeric, via_tool)

    def test_read_only_other_tables_and_multi_statement_denied(self):
        for sql in (
            "DELETE FROM employees", "UPDATE employees SET annual_salary_krw=1",
            "INSERT INTO employees SELECT * FROM employees", "DROP TABLE employees",
            "CREATE TABLE other (id)", "ATTACH DATABASE ':memory:' AS other",
            "PRAGMA writable_schema=ON", "SELECT * FROM sqlite_master",
            "SELECT load_extension('anything')", "SELECT * FROM employees; DELETE FROM employees",
            "/* harmless */ DELETE FROM card_transactions RETURNING *",
            "WITH ids AS (SELECT employee_id FROM employees) DELETE FROM employees WHERE employee_id IN ids",
        ):
            with self.subTest(sql=sql):
                self.assertNotEqual(tools.query_database(sql)["status"], "success")
        self.assertEqual(tools.query_database("SELECT COUNT(*) AS count FROM employees")["data"]["rows"][0]["count"], 100)
        self.assertEqual(tools.query_database("SELECT COUNT(*) AS count FROM card_transactions")["data"]["rows"][0]["count"], 1000)

    def test_foreign_key_rejects_orphan_card(self):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute("PRAGMA foreign_keys=ON")
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("INSERT INTO card_transactions VALUES ('bad','missing','2026-11-01','m','c',1,'d')")

    def test_query_limits_and_invalid_inputs(self):
        result = tools.query_database("SELECT * FROM card_transactions", row_limit=5)
        self.assertEqual(result["data"]["returned_count"], 5)
        self.assertTrue(result["data"]["truncated"])
        for kwargs in ({"sql": ""}, {"sql": None}, {"sql": "SELECT 1", "row_limit": 201},
                       {"sql": "SELECT 1", "row_limit": 0}, {"sql": "SELECT 1", "row_limit": True},
                       {"sql": "SELECT 1", "parameters": {}}, {"sql": "SELECT ?", "parameters": [[]]}):
            self.assertEqual(tools.query_database(**kwargs)["status"], "invalid_input")
        self.assertEqual(tools.query_database("SELECT e.name,e.name FROM employees e")["status"], "invalid_input")

    def test_execution_budget_interrupts_excessive_query(self):
        with patch("custom_tools.time.monotonic", side_effect=[0, 3]):
            result = tools.query_database("""SELECT COUNT(*) AS count FROM card_transactions a
                CROSS JOIN card_transactions b CROSS JOIN card_transactions c""")
        self.assertEqual(result["status"], "error")
        self.assertIn("interrupted", result["error"])

    def test_tool_arguments_and_null_defaults(self):
        self.assertEqual(tools.execute_tool("unknown", "{}")["status"], "invalid_input")
        for raw in ("not json", "[]", '{"sql": null}', '{"sql":"SELECT 1","extra":1}'):
            self.assertEqual(tools.execute_tool("query_database", raw)["status"], "invalid_input")
        result = tools.execute_tool("query_database", '{"sql":"SELECT COUNT(*) AS count FROM employees","parameters":null,"row_limit":null}')
        self.assertEqual(result["data"]["rows"], [{"count": 100}])

    def test_missing_database_does_not_create_file(self):
        missing = self.path.with_name("missing.sqlite3")
        with patch.dict(os.environ, {"SQLITE_DB_PATH": str(missing)}):
            self.assertEqual(tools.query_database("SELECT * FROM employees")["status"], "error")
        self.assertFalse(missing.exists())

    def test_cli_sql_and_parameters(self):
        for args, expected_code in (
            (["--init-db"], 0),
            (["--sql", "SELECT name FROM employees WHERE employee_id=?", "--parameters", '["E001"]'], 0),
            (["--sql", "SELECT COUNT(*) AS count FROM employees"], 0),
            (["--sql", "DELETE FROM employees"], 1),
        ):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, "-X", "utf8", str(tools.ROOT / "custom_tools.py"), *args],
                                        capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, expected_code, result.stderr)
                self.assertIsInstance(json.loads(result.stdout), dict)


if __name__ == "__main__":
    unittest.main()
