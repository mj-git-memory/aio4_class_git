"""실제 임시 SQLite와 모의 API로 Tool Calling 및 Gemini → OpenAI 순서를 검증합니다."""
from datetime import date
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import httpx2
from openai import OpenAI

import custom_tools as tools
from main import AgentClient, Settings, ToolExecutionIncomplete, generate_final_answer, run_pipeline


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory(prefix="pipeline_test_", dir=tools.ROOT)
        cls.environment = patch.dict(os.environ, {"SQLITE_DB_PATH": str(Path(cls.temp.name) / "test.sqlite3")})
        cls.environment.start()
        tools.initialize_database()

    @classmethod
    def tearDownClass(cls):
        cls.environment.stop()
        assert Path(cls.temp.name).resolve().parent == tools.ROOT
        cls.temp.cleanup()

    def test_actual_sdk_tool_loop_for_both_apis(self):
        for api in ("responses", "chat_completions"):
            with self.subTest(api=api):
                captured = []
                def handler(request):
                    body = json.loads(request.content)
                    captured.append(body)
                    number = len(captured)
                    name = "query_database"
                    args = {"sql": "SELECT corporate_card_id FROM employees WHERE employee_id=?", "parameters": ["E001"]} if number == 1 else {
                        "sql": "SELECT COUNT(*) AS count FROM card_transactions WHERE corporate_card_id=?", "parameters": ["CARD-1001"]}
                    if number == 2:
                        if api == "responses":
                            prior = body["input"][-1]
                            self.assertEqual(prior["call_id"], "call1")
                            self.assertTrue(any(item.get("type") == "reasoning" for item in body["input"]))
                            self.assertEqual(json.loads(prior["output"])["data"]["rows"][0]["corporate_card_id"], "CARD-1001")
                        else:
                            prior = body["messages"][-1]
                            self.assertEqual(prior["tool_call_id"], "call1")
                            self.assertEqual(body["messages"][-2]["tool_calls"][0]["extra_content"]["google"]["thought_signature"], "opaque")
                            self.assertEqual(json.loads(prior["content"])["data"]["rows"][0]["corporate_card_id"], "CARD-1001")
                    if api == "responses":
                        output = [{"type": "function_call", "id": f"fc{number}", "call_id": f"call{number}",
                                   "name": name, "arguments": json.dumps(args)}]
                        if number == 1:
                            output.insert(0, {"type": "reasoning", "id": "rs1", "summary": [], "encrypted_content": "opaque"})
                        if number == 3:
                            output = [{"type": "message", "id": "msg", "role": "assistant", "status": "completed",
                                       "content": [{"type": "output_text", "text": "조회 결과 카드 사용내역은 10건입니다.", "annotations": []}]}]
                        payload = {"id": f"r{number}", "object": "response", "created_at": 0, "model": "m", "status": "completed", "output": output}
                    else:
                        message = {"role": "assistant", "content": None, "tool_calls": [
                            {"id": f"call{number}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)},
                             "extra_content": {"google": {"thought_signature": "opaque"}}}]}
                        if number == 3:
                            message = {"role": "assistant", "content": "조회 결과 카드 사용내역은 10건입니다."}
                        payload = {"id": f"c{number}", "object": "chat.completion", "created": 0, "model": "m",
                                   "choices": [{"index": 0, "finish_reason": "stop" if number == 3 else "tool_calls", "message": message}]}
                    return httpx2.Response(200, json=payload)
                with OpenAI(api_key="offline", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                    agent = AgentClient("gemini" if api == "chat_completions" else "openai", "m", api, client)
                    trace = []
                    text = agent.run_with_tools("E001 카드 사용내역", instructions="조회", max_rounds=3, trace=trace)
                self.assertIn("10건", text)
                self.assertEqual([record["tool"] for record in trace], ["query_database", "query_database"])
                self.assertEqual(trace[1]["result"]["data"]["rows"][0]["count"], 10)
                definition = captured[0]["tools"][0]
                self.assertEqual(len(captured[0]["tools"]), 1)
                self.assertEqual(definition.get("name") or definition["function"]["name"], "query_database")
                self.assertEqual(captured[0]["tool_choice"], "required")
                if api == "responses":
                    self.assertEqual(captured[0]["include"], ["reasoning.encrypted_content"])

    def test_unqueried_answer_is_not_accepted(self):
        def handler(request):
            return httpx2.Response(200, json={"id": "c", "object": "chat.completion", "created": 0, "model": "m",
                "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "추측한 답"}}]})
        with OpenAI(api_key="offline", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            with self.assertRaises(ToolExecutionIncomplete):
                AgentClient("gemini", "m", "chat_completions", client).run_with_tools("질문", instructions="조회", max_rounds=1, trace=[])

    def test_tool_round_limit(self):
        captured = []
        def handler(request):
            captured.append(json.loads(request.content))
            return httpx2.Response(200, json={"id": "c", "object": "chat.completion", "created": 0, "model": "m",
                "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {"role": "assistant", "content": None,
                    "tool_calls": [{"id": "id", "type": "function", "function": {"name": "query_database", "arguments": '{"sql":"SELECT employee_id FROM employees"}'}}]}}]})
        trace = []
        with OpenAI(api_key="offline", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            with self.assertRaises(ToolExecutionIncomplete):
                AgentClient("gemini", "m", "chat_completions", client).run_with_tools("조회", instructions="조회", max_rounds=1, trace=trace)
        self.assertEqual(len(trace), 1)
        self.assertEqual(captured[-1]["tool_choice"], "none")

    def pipeline_mocks(self, *, failure=False, review="ready_for_review",
                       finalizer_failure=False, intent_kind="card_usage", missing_openai=False):
        events = []
        def collect(context, **kwargs):
            events.append("tools")
            kwargs["trace"].append({
                "agent": "gemini", "round": 1, "tool": "query_database",
                "arguments": '{"sql":"SELECT COUNT(*) AS count FROM card_transactions"}',
                "result": {"status": "success", "data": {"rows": [{"count": 1000}]}, "error": None},
            })
            if failure:
                raise ToolExecutionIncomplete("실행 실패")
            return "조회 완료"

        def final_answer(*args, **kwargs):
            events.append("answer")
            if finalizer_failure:
                raise RuntimeError("private response detail")
            return "OpenAI 최종 답변"

        gemini = SimpleNamespace(client=Mock(), run_with_tools=Mock(side_effect=collect))
        openai = SimpleNamespace(client=Mock(), generate=Mock(side_effect=final_answer))
        intent = {
            "reference_date": "2026-11-19", "review_status": review,
            "analysis": {"intent": intent_kind, "clarification_questions": ["대상 확인"],
                         "unsupported_reasons": []},
        }
        def analyze(*args):
            events.append("intent")
            return intent

        def create(settings, *, names):
            if names == ("openai",) and missing_openai:
                raise ValueError("필수 환경 변수 누락: OPENAI_MODEL")
            return {name: gemini if name == "gemini" else openai for name in names}

        with patch("main.create_agents", side_effect=create) as factory, \
             patch("intent_analysis.analyze_intent", side_effect=analyze):
            result = run_pipeline(
                "질문", Settings(10, 3), date(2026, 11, 19), answer_instructions="표로 답하세요.",
            )
        return result, factory, gemini, openai, events

    def test_pipeline_order_is_intent_tools_then_openai_answer(self):
        result, factory, gemini, openai, events = self.pipeline_mocks()
        self.assertEqual(events, ["intent", "tools", "answer"])
        self.assertEqual(result["executor"], "gemini")
        self.assertEqual(result["answer_generator"], "openai")
        self.assertEqual(result["answer"], "OpenAI 최종 답변")
        self.assertTrue(result["openai_called"])
        self.assertEqual([call.kwargs["names"] for call in factory.call_args_list],
                         [("gemini",), ("openai",)])
        gemini.client.close.assert_called_once()
        openai.client.close.assert_called_once()

    def test_handoff_contains_original_and_exact_database_results(self):
        result, factory, gemini, openai, events = self.pipeline_mocks()
        payload = json.loads(openai.generate.call_args.args[0])
        self.assertEqual(payload["original_question"], "질문")
        self.assertEqual(payload["intent"], result["intent"]["analysis"])
        self.assertEqual(payload["database_results"][0]["result"], result["tool_trace"][0]["result"])
        self.assertNotIn("조회 완료", openai.generate.call_args.args[0])
        self.assertIn("표로 답하세요.", openai.generate.call_args.kwargs["instructions"])

    def test_failed_gemini_query_does_not_call_openai(self):
        result, factory, gemini, openai, events = self.pipeline_mocks(failure=True)
        self.assertEqual(result["status"], "retrieval_failed")
        self.assertEqual(events, ["intent", "tools"])
        self.assertTrue(result["tool_trace"])
        self.assertIsNone(result["answer"])
        self.assertFalse(result["openai_called"])
        self.assertEqual(factory.call_count, 1)
        openai.generate.assert_not_called()

    def test_clarification_does_not_execute_tools_or_call_openai(self):
        result, factory, gemini, openai, events = self.pipeline_mocks(review="needs_clarification")
        self.assertEqual(result["answer"], "대상 확인")
        self.assertEqual(events, ["intent"])
        self.assertFalse(result["tool_execution"])
        self.assertFalse(result["openai_called"])
        self.assertEqual(factory.call_count, 1)

    def test_general_question_skips_tools(self):
        result, factory, gemini, openai, events = self.pipeline_mocks(intent_kind="general")
        self.assertEqual(events, ["intent", "answer"])
        self.assertFalse(result["tool_execution"])
        self.assertIsNone(result["executor"])
        self.assertEqual(result["answer_generator"], "openai")

    def test_final_answer_failure_preserves_evidence(self):
        result, factory, gemini, openai, events = self.pipeline_mocks(finalizer_failure=True)
        self.assertEqual(result["status"], "answer_generation_failed")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["tool_trace"])
        self.assertTrue(result["openai_called"])
        self.assertNotIn("private response detail", json.dumps(result))

    def test_missing_openai_configuration_preserves_evidence(self):
        result, factory, gemini, openai, events = self.pipeline_mocks(missing_openai=True)
        self.assertEqual(result["status"], "answer_generation_failed")
        self.assertTrue(result["tool_trace"])
        self.assertFalse(result["openai_called"])
        self.assertIsNone(result["answer"])

    def test_no_evidence_does_not_call_finalizer_for_company_data(self):
        agent = SimpleNamespace(generate=Mock())
        with self.assertRaises(ToolExecutionIncomplete):
            generate_final_answer(agent, "사용액", {"analysis": {"intent": "card_usage"}}, [])
        agent.generate.assert_not_called()

    def test_default_cli_and_explicit_pipeline_use_same_flow(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from main import main
        for options in ([], ["--pipeline"], ["--json"]):
            with self.subTest(options=options):
                output = StringIO()
                result = {"status": "success", "answer": "최종 답변", "tool_trace": []}
                with patch("main.load_settings", return_value=Settings(10, 3)), \
                     patch("main.run_pipeline", return_value=result) as pipeline, \
                     redirect_stdout(output):
                    status = main(["--question", "질문", "--reference-date", "2026-11-19", *options])
                self.assertEqual(status, 0)
                pipeline.assert_called_once()
                self.assertEqual(pipeline.call_args.args[:1], ("질문",))
                if "--json" in options:
                    self.assertEqual(json.loads(output.getvalue()), result)
                else:
                    self.assertEqual(output.getvalue().strip(), "최종 답변")

    def test_cli_reports_query_failure_and_returns_nonzero(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from main import main
        output = StringIO()
        result = {"status": "retrieval_failed", "answer": None, "tool_trace": []}
        with patch("main.load_settings", return_value=Settings(10, 3)), \
             patch("main.run_pipeline", return_value=result), redirect_stdout(output):
            status = main(["--question", "질문"])
        self.assertEqual(status, 1)
        self.assertIn("DB 조회", output.getvalue())

    def test_empty_question_does_not_start_pipeline(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from main import main
        with patch("main.run_pipeline") as pipeline, redirect_stdout(StringIO()):
            self.assertEqual(main(["--question", " "]), 1)
        pipeline.assert_not_called()


if __name__ == "__main__":
    unittest.main()
