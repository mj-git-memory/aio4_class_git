"""의도 분석 구조/보완/모의 API 검증. 실제 Gemini 의미 분류는 --test-intents로 별도 확인합니다."""

from copy import deepcopy
from datetime import date
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from openai import OpenAI
import httpx2

import custom_tools
from intent_analysis import analyze_intent, compare_intent, intent_test_cases, parse_reference_date, relative_period_rules, run_intent_suite
from main import AgentClient


class IntentTests(unittest.TestCase):
    def setUp(self):
        self.reference = date(2026, 11, 19)
        self.payload = {
            "intent": "card_usage", "scope": "individual", "summary": "직원의 카드 사용내역 조회",
            "subjects": [{"employee_id": "E001", "employee_name": None, "card_id": None}],
            "period": {"original_expression": None, "start_date": None, "end_date": None},
            "requested_fields": ["transactions"], "analysis_tasks": [], "constraints": [],
            "needs_clarification": False, "clarification_questions": [], "unsupported_reasons": [],
        }

    def analyze(self, question="E001의 카드 사용내역을 알려줘", payload=None):
        agent = SimpleNamespace(name="gemini", generate=Mock(return_value=json.dumps(payload or self.payload)))
        result = analyze_intent(agent, question, self.reference)
        return result, agent

    def test_linked_card_plan_preserves_original_and_does_not_execute_tools(self):
        with patch.object(custom_tools, "query_database", side_effect=AssertionError("Tool 실행 금지")):
            result, agent = self.analyze()
        self.assertEqual(result["candidate_tools"], ["query_database"])
        self.assertEqual(result["original_question"], "E001의 카드 사용내역을 알려줘")
        self.assertEqual(result["review_status"], "ready_for_review")
        self.assertFalse(result["tool_execution"])
        self.assertFalse(result["openai_called"])
        request = json.loads(agent.generate.call_args.args[0])
        self.assertEqual(request["reference_date"], "2026-11-19")
        self.assertIn("response_schema", agent.generate.call_args.kwargs)
        self.assertNotIn("85000000", agent.generate.call_args.args[0])

    def test_direct_card_requires_no_employee_id(self):
        self.payload["subjects"] = [{"employee_id": None, "employee_name": None, "card_id": "CARD-1002"}]
        result, _ = self.analyze("CARD-1002 사용내역")
        self.assertEqual(result["candidate_tools"], ["query_database"])
        self.assertFalse(result["analysis"]["needs_clarification"])

    def test_name_only_can_use_database_search(self):
        self.payload["subjects"] = [{"employee_id": None, "employee_name": "김민준", "card_id": None}]
        result, _ = self.analyze("김민준의 카드 사용내역")
        self.assertEqual(result["review_status"], "ready_for_review")
        self.assertEqual(result["candidate_tools"], ["query_database"])

    def test_no_subject_and_employee_info_from_card_need_clarification(self):
        for subjects, intent in [([], "card_usage")]:
            payload = deepcopy(self.payload)
            payload.update(subjects=subjects, intent=intent)
            result, _ = self.analyze("CARD-1002 사용자의 정보", payload)
            self.assertEqual(result["review_status"], "needs_clarification")

    def test_group_queries_need_no_individual_identifier(self):
        self.payload.update(scope="group", subjects=[])
        result, _ = self.analyze("개발팀 전체 카드 사용액 합계")
        self.assertEqual(result["review_status"], "ready_for_review")
        self.assertEqual(result["candidate_tools"], ["query_database"])

    def test_hallucinated_or_partial_ids_are_rejected(self):
        for question in ("김민준의 카드 사용내역", "E0012의 카드 사용내역"):
            with self.subTest(question=question), self.assertRaises(RuntimeError):
                self.analyze(question)

    def test_invalid_or_unjustified_dates_require_clarification(self):
        for period in [
            {"original_expression": "지정 기간", "start_date": "2026-11-31", "end_date": None},
            {"original_expression": "지정 기간", "start_date": "2026-11-30", "end_date": "2026-11-01"},
            {"original_expression": None, "start_date": "2026-11-01", "end_date": None},
        ]:
            with self.subTest(period=period):
                self.payload["period"] = period
                result, _ = self.analyze("E001의 지정 기간 카드 내역")
                self.assertEqual(result["review_status"], "needs_clarification")
                self.assertIsNone(result["analysis"]["period"]["start_date"])

    def test_unmentioned_period_expression_is_rejected(self):
        self.payload["period"]["original_expression"] = "이번 달"
        with self.assertRaises(RuntimeError):
            self.analyze()

    def test_general_and_unsupported_have_no_candidate_tools(self):
        for intent in ("general", "unsupported"):
            self.payload.update(intent=intent, subjects=[])
            result, _ = self.analyze("법인카드 설명")
            self.assertEqual(result["candidate_tools"], [])
            self.assertEqual(result["review_status"], "unsupported" if intent == "unsupported" else "ready_for_review")

    def test_malformed_schema_and_unknown_fields_are_rejected(self):
        for raw in ("not json", "{}", json.dumps({**self.payload, "extra": 1}),
                    json.dumps({**self.payload, "needs_clarification": "false"})):
            agent = SimpleNamespace(name="gemini", generate=Mock(return_value=raw))
            with self.subTest(raw=raw), self.assertRaises(RuntimeError):
                analyze_intent(agent, "E001", self.reference)

    def test_non_gemini_and_empty_question_do_not_call_model(self):
        for name, question in (("openai", "E001"), ("gemini", " ")):
            agent = SimpleNamespace(name=name, generate=Mock())
            with self.assertRaises(ValueError):
                analyze_intent(agent, question, self.reference)
            agent.generate.assert_not_called()

    def test_reference_date_validation(self):
        self.assertEqual(parse_reference_date("2026-11-19"), self.reference)
        for value in ("20261119", "2026-02-30", "bad"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_reference_date(value)

    def test_calendar_policy_corrects_month_and_keeps_model_period(self):
        self.payload["period"] = {"original_expression": "이번 달", "start_date": "2026-11-01", "end_date": "2026-11-19"}
        result, _ = self.analyze("E001의 이번 달 사용액")
        self.assertEqual(result["analysis"]["period"]["end_date"], "2026-11-30")
        self.assertEqual(result["model_period"]["end_date"], "2026-11-19")
        self.assertTrue(result["normalization_notes"])

    def test_explicit_today_limit_is_preserved(self):
        self.payload["period"] = {"original_expression": "이번 달", "start_date": "2026-11-01", "end_date": "2026-11-30"}
        result, _ = self.analyze("E001의 이번 달 사용액을 오늘까지 알려줘")
        self.assertEqual(result["analysis"]["period"]["end_date"], "2026-11-19")

    def test_relative_calendar_leap_and_year_boundaries(self):
        self.assertEqual(relative_period_rules(date(2028, 2, 10))["이번달"], ["2028-02-01", "2028-02-29"])
        self.assertEqual(relative_period_rules(date(2026, 1, 1))["지난달"], ["2025-12-01", "2025-12-31"])

    def test_suite_preserves_previous_results_on_api_failure(self):
        import httpx2
        from openai import RateLimitError
        result, _ = self.analyze()
        error = RateLimitError("private detail", response=httpx2.Response(429, request=httpx2.Request("POST", "https://offline.invalid")), body=None)
        with patch("intent_analysis.analyze_intent", side_effect=[result, error]):
            report = run_intent_suite(SimpleNamespace(), self.reference)
        self.assertEqual(report["attempted"], 2)
        self.assertEqual(report["skipped"], 6)
        self.assertNotIn("private detail", json.dumps(report))

    def test_comparison_reports_mismatches_and_dynamic_month(self):
        result, _ = self.analyze()
        self.assertEqual(compare_intent(result, {"intent": "card_usage"}), [])
        self.assertEqual(compare_intent(result, {"intent": "general"}), ["intent"])
        month = intent_test_cases(date(2028, 2, 10))[1]["expected"]
        self.assertEqual(month["end_date"], "2028-02-29")

    def test_schema_is_translated_for_both_sdk_apis(self):
        for api in ("responses", "chat_completions"):
            captured = []
            def handler(request):
                body = json.loads(request.content)
                captured.append(body)
                text = json.dumps(self.payload)
                if api == "responses":
                    payload = {"id": "r", "object": "response", "created_at": 0, "model": "m", "status": "completed",
                               "output": [{"type": "message", "id": "msg", "role": "assistant", "status": "completed",
                                           "content": [{"type": "output_text", "text": text, "annotations": []}]}]}
                else:
                    payload = {"id": "c", "object": "chat.completion", "created": 0, "model": "m",
                               "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": text}}]}
                return httpx2.Response(200, json=payload)
            with OpenAI(api_key="offline", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                result = analyze_intent(AgentClient("gemini", "m", api, client), "E001의 카드 사용내역", self.reference)
                self.assertEqual(result["analysis"]["intent"], "card_usage")
            body = captured[0]
            schema_format = body["text"]["format"] if api == "responses" else body["response_format"]["json_schema"]
            self.assertTrue(schema_format["strict"])
            self.assertIn("schema", schema_format)
            self.assertNotIn("tools", body)


if __name__ == "__main__":
    unittest.main()
