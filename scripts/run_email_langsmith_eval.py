"""Corre una versión live del loop de correo sobre el dataset LangSmith."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

if os.getenv("LANGSMITH_EMAIL_LOOP_PROJECT"):
    os.environ["LANGSMITH_PROJECT"] = os.environ["LANGSMITH_EMAIL_LOOP_PROJECT"]

from s3_langchain_demo.email_loop import run_email_case  # noqa: E402

DATASET_NAME = "s3-demo-email-loop-6-casos-2026"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=("v0", "v4"), default="v4")
    args = parser.parse_args()
    if not os.getenv("ANTHROPIC_API_KEY", "").strip() or not os.getenv("LANGSMITH_API_KEY", "").strip():
        print("BLOQUEADO: este script necesita ANTHROPIC_API_KEY y LANGSMITH_API_KEY; usa offline si no están.", file=sys.stderr)
        return 2
    try:
        from langsmith import Client
    except ImportError:
        print("BLOQUEADO: instala dependencias con python -m pip install -e .", file=sys.stderr)
        return 2

    def target(inputs: dict) -> dict:
        result = run_email_case(inputs["case"], args.version, mode="live")
        return {
            "case_id": result["case_id"],
            "version": result["version"],
            "draft": result["draft"],
            "check": result["check"],
            "evaluation": result["evaluation"],
            "history": result["history"],
            "outcome": result["outcome"],
        }

    def contract_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        evaluation = outputs.get("evaluation", {})
        return {
            "key": "email_contract",
            "score": 1 if evaluation.get("contract_valid") else 0,
            "comment": "La salida conserva el contrato estructurado.",
        }

    def content_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        evaluation = outputs.get("evaluation", {})
        return {
            "key": "email_content",
            "score": 1 if evaluation.get("required_topics_present") and evaluation.get("forbidden_absent") else 0,
            "comment": f"missing={evaluation.get('missing_topics', [])}; forbidden={evaluation.get('forbidden_matches', [])}",
        }

    def escalation_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        evaluation = outputs.get("evaluation", {})
        return {
            "key": "email_escalation",
            "score": 1 if evaluation.get("approval_correct") else 0,
            "comment": "La aprobación requerida coincide con la referencia.",
        }

    try:
        client = Client()
        results = client.evaluate(
            target,
            data=DATASET_NAME,
            evaluators=[contract_evaluator, content_evaluator, escalation_evaluator],
            experiment_prefix=f"s3-email-loop-{args.version}",
            max_concurrency=1,
        )
        print(results)
        return 0
    except Exception as exc:
        print(f"BLOQUEADO: la evaluación LangSmith falló ({type(exc).__name__}). Usa offline.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
