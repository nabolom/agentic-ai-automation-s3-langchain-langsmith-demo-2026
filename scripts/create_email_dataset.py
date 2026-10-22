"""Crea el dataset de correo iterativo en LangSmith."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

from s3_langchain_demo.email_loop import load_email_cases  # noqa: E402

DATASET_NAME = "s3-demo-email-loop-6-casos-2026"


def main() -> int:
    if not os.getenv("LANGSMITH_API_KEY", "").strip():
        print("BLOQUEADO: define LANGSMITH_API_KEY en .env local o usa offline.", file=sys.stderr)
        return 2
    try:
        from langsmith import Client
    except ImportError:
        print("BLOQUEADO: instala dependencias con python -m pip install -e .", file=sys.stderr)
        return 2

    try:
        client = Client()
        try:
            dataset = client.read_dataset(dataset_name=DATASET_NAME)
            print(f"El dataset ya existe: {dataset.name} ({dataset.id})")
            return 0
        except Exception:
            pass

        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description="Seis correos sintéticos por audiencia para estudiar v0–v4 y loops acotados.",
        )
        examples = []
        for case in load_email_cases():
            examples.append(
                {
                    "inputs": {"case": case},
                    "outputs": {"expected": case["expected"], "audience": case["audience"]},
                }
            )
        client.create_examples(dataset_id=dataset.id, examples=examples)
        print(f"Dataset creado: {dataset.name} ({dataset.id})")
        return 0
    except Exception as exc:
        print(f"BLOQUEADO: LangSmith no está disponible ({type(exc).__name__}). Usa offline.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
