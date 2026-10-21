"""Carga de fixtures de la demo."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ExpectedDecision

DEFAULT_CASES_PATH = Path(__file__).resolve().parents[2] / "data" / "cases.json"


def load_cases(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Carga y valida mínimamente los casos sintéticos."""

    cases_path = Path(path) if path else DEFAULT_CASES_PATH
    with cases_path.resolve().open(encoding="utf-8") as handle:
        cases = json.load(handle)

    if not isinstance(cases, list) or not cases:
        raise ValueError("El dataset debe ser una lista no vacía")

    required = {"id", "kind", "input", "expected"}
    for case in cases:
        if not required.issubset(case):
            raise ValueError(f"Caso incompleto: {case!r}")
        ExpectedDecision.from_mapping(case["expected"])
    return cases
