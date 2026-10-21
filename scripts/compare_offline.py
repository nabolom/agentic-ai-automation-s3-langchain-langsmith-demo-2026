"""Compara los fixtures v0 y v1 sin red."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from s3_langchain_demo.data import load_cases  # noqa: E402
from s3_langchain_demo.offline import run_offline, summarize  # noqa: E402


def main() -> int:
    cases = load_cases()
    v0 = {row["id"]: row for row in run_offline(cases, "v0")}
    v1 = {row["id"]: row for row in run_offline(cases, "v1")}
    print("Comparación sintética: no es benchmark de un modelo real")
    print("ID   v0 correcto   v1 correcto   lectura")
    print("---  ------------  ------------   -------")
    for case in cases:
        before = v0[case["id"]]
        after = v1[case["id"]]
        if before["correct"] and after["correct"]:
            reading = "sin cambio"
        elif not before["correct"] and after["correct"]:
            reading = "mejora del fixture"
        elif before["correct"] and not after["correct"]:
            reading = "regresión del fixture"
        else:
            reading = "sin resolver"
        print(f"{case['id']:<4} {str(before['correct']):<13} {str(after['correct']):<13} {reading}")
    print(f"v0={summarize(v0.values())}")
    print(f"v1={summarize(v1.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
