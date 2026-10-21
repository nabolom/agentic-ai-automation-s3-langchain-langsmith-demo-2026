"""Corre v0 o v1 sobre el dataset de LangSmith.

La función objetivo llama a Claude mediante LangChain. El evaluador compara
ruta y escalamiento contra las referencias curadas, sin usar LLM-as-judge.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from s3_langchain_demo.evaluator import score_decision  # noqa: E402
from s3_langchain_demo.live import classify_live  # noqa: E402

DATASET_NAME = "s3-demo-triage-6-casos-2026"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=("v0", "v1"), default="v1")
    args = parser.parse_args()

    try:
        from langsmith import Client
    except ImportError:
        print("BLOQUEADO: instala dependencias con python -m pip install -e .", file=sys.stderr)
        return 2

    def target(inputs: dict) -> dict:
        decision, checked = classify_live(inputs["request"], version=args.version)
        # Se conserva raw para poder leer la traza; el criterio mide la salida segura.
        return {
            "route": checked.route,
            "escalate": checked.escalate,
            "raw": decision.as_dict(),
        }

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        score = score_decision(outputs, reference_outputs)
        return {
            "key": "triage_correct",
            "score": 1 if score["correct"] else 0,
            "comment": (
                f"route_correct={score['route_correct']}; "
                f"escalation_correct={score['escalation_correct']}"
            ),
        }

    client = Client()
    results = client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[evaluator],
        experiment_prefix=f"s3-demo-{args.version}",
        max_concurrency=1,
    )
    print(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
