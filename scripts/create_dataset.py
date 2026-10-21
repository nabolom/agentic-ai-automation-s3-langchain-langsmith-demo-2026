"""Crea el dataset de seis casos en LangSmith.

Ejecutar solo después de configurar LANGSMITH_API_KEY. No imprime la clave.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from s3_langchain_demo.data import load_cases  # noqa: E402

DATASET_NAME = "s3-demo-triage-6-casos-2026"


def main() -> int:
    if not os.getenv("LANGSMITH_API_KEY", "").strip():
        print("BLOQUEADO: define LANGSMITH_API_KEY en tu entorno/.env", file=sys.stderr)
        return 2
    try:
        from langsmith import Client
    except ImportError:
        print("BLOQUEADO: instala dependencias con python -m pip install -e .", file=sys.stderr)
        return 2

    client = Client()
    try:
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
        print(f"El dataset ya existe: {dataset.name} ({dataset.id})")
        return 0
    except Exception:
        pass

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Casos sintéticos para S3: 4 típicos, 1 límite y 1 adversarial.",
    )
    examples = []
    for case in load_cases():
        examples.append({
            "inputs": {"request": case["input"], "case_id": case["id"]},
            "outputs": case["expected"],
        })
    client.create_examples(dataset_id=dataset.id, examples=examples)
    print(f"Dataset creado: {dataset.name} ({dataset.id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
