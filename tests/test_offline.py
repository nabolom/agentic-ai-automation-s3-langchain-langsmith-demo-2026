import json
import unittest
from pathlib import Path

from s3_langchain_demo.data import load_cases
from s3_langchain_demo.evaluator import score_decision, validate_decision
from s3_langchain_demo.offline import run_offline, summarize


class OfflineContractTests(unittest.TestCase):
    def test_dataset_has_six_cases_with_required_mix(self):
        cases = load_cases()
        self.assertEqual(len(cases), 6)
        self.assertEqual([case["kind"] for case in cases].count("tipico"), 4)
        self.assertEqual([case["kind"] for case in cases].count("limite"), 1)
        self.assertEqual([case["kind"] for case in cases].count("adversarial"), 1)

    def test_v0_and_v1_fixture_scores_are_explicit(self):
        cases = load_cases()
        v0 = run_offline(cases, "v0")
        v1 = run_offline(cases, "v1")
        self.assertEqual(summarize(v0)["correct"], 4)
        self.assertEqual(summarize(v1)["correct"], 6)

    def test_low_confidence_cannot_disable_escalation(self):
        result = validate_decision({
            "route": "soporte",
            "confidence": "baja",
            "reason": "No estoy seguro.",
            "escalate": False,
        })
        self.assertTrue(result.accepted)
        self.assertTrue(result.escalate)

    def test_invalid_route_is_rejected_and_sent_to_human(self):
        result = validate_decision({
            "route": "reembolso_automatico",
            "confidence": "alta",
            "reason": "No existe esa ruta.",
            "escalate": False,
        })
        self.assertFalse(result.accepted)
        self.assertEqual(result.route, "humano")
        self.assertTrue(result.escalate)
        self.assertTrue(result.errors)

    def test_score_compares_route_and_escalation(self):
        score = score_decision(
            {"route": "humano", "escalate": True},
            {"route": "humano", "escalate": True},
        )
        self.assertEqual(score, {
            "route_correct": True,
            "escalation_correct": True,
            "correct": True,
        })


if __name__ == "__main__":
    unittest.main()
