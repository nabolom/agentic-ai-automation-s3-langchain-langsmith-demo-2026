import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from s3_langchain_demo.email_loop import (
    EMAIL_VERSIONS,
    load_email_cases,
    run_email_case,
    run_email_suite,
    summarize_email_suite,
)


class EmailLoopOfflineTests(unittest.TestCase):
    def test_dataset_has_three_audiences_and_six_cases(self):
        cases = load_email_cases()
        self.assertEqual(len(cases), 6)
        self.assertEqual({case["audience"] for case in cases}, {"director", "cliente", "reportante"})
        self.assertEqual([case["kind"] for case in cases].count("tipico"), 3)
        self.assertEqual([case["kind"] for case in cases].count("ambiguo"), 1)
        self.assertEqual([case["kind"] for case in cases].count("limite"), 1)
        self.assertEqual([case["kind"] for case in cases].count("adversarial"), 1)

    def test_versions_are_cumulative_and_same_suite(self):
        cases = load_email_cases()
        summaries = {version: summarize_email_suite(run_email_suite(cases, version)) for version in EMAIL_VERSIONS}
        self.assertEqual([summaries[v]["cases"] for v in EMAIL_VERSIONS], [6] * 5)
        self.assertEqual([summaries[v]["correct"] for v in EMAIL_VERSIONS], [0, 2, 2, 5, 6])
        self.assertEqual(summaries["v0"]["total_attempts"], 6)
        self.assertEqual(summaries["v3"]["total_attempts"], 10)
        self.assertEqual(summaries["v4"]["total_attempts"], 11)

    def test_v3_stops_after_one_revision_and_v4_uses_two_for_adversarial_case(self):
        case = next(case for case in load_email_cases() if case["id"] == "M6")
        v3 = run_email_case(case, "v3")
        v4 = run_email_case(case, "v4")
        self.assertEqual(sum(event["event"] == "revision_requested" for event in v3["history"]), 1)
        self.assertFalse(v3["evaluation"]["correct"])
        self.assertEqual(sum(event["event"] == "revision_requested" for event in v4["history"]), 2)
        self.assertTrue(v4["evaluation"]["correct"])
        self.assertTrue(v4["draft"]["requires_approval"])
        self.assertTrue(v4["evaluation"]["forbidden_absent"])

    def test_v4_never_sends_and_escalates_risky_cases(self):
        rows = run_email_suite(load_email_cases(), "v4")
        risky = {row["case_id"]: row for row in rows if row["case_id"] in {"M4", "M5", "M6"}}
        self.assertEqual(set(risky), {"M4", "M5", "M6"})
        self.assertTrue(all(row["outcome"] == "escalar" for row in risky.values()))
        self.assertTrue(all("send" not in row for row in risky.values()))


class EmailLoopLiveMockTests(unittest.TestCase):
    def test_live_v4_uses_structured_output_without_network(self):
        fake = SimpleNamespace(
            model_dump=lambda: {
                "audience": "cliente",
                "subject": "Seguimiento",
                "body": "Entendemos la situación. Siguiente paso: revisar el caso. Te enviaremos una actualización.",
                "next_step": "Revisar el caso.",
                "requires_approval": False,
                "risks_detected": [],
            }
        )
        case = next(case for case in load_email_cases() if case["id"] == "M2")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-only-placeholder", "LANGSMITH_TRACING": "false"}, clear=False):
            with patch("langchain_anthropic.ChatAnthropic") as chat:
                structured = chat.return_value.with_structured_output.return_value
                structured.invoke.return_value = fake
                result = run_email_case(case, "v4", mode="live")
        chat.assert_called_once()
        chat.return_value.with_structured_output.assert_called_once()
        self.assertEqual(result["draft"]["audience"], "cliente")
        self.assertTrue(result["evaluation"]["correct"])


if __name__ == "__main__":
    unittest.main()
