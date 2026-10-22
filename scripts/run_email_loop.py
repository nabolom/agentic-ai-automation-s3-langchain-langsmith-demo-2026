"""Corre el caso de correos v0–v4 sobre la misma suite."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

if os.getenv("LANGSMITH_EMAIL_LOOP_PROJECT"):
    os.environ["LANGSMITH_PROJECT"] = os.environ["LANGSMITH_EMAIL_LOOP_PROJECT"]

from s3_langchain_demo.email_loop import (  # noqa: E402
    EMAIL_VERSIONS,
    load_email_cases,
    run_email_suite,
    summarize_email_suite,
)


def _print_rows(rows: list[dict], version: str, mode: str) -> None:
    summary = summarize_email_suite(rows)
    print(f"Modo {mode} · {version} · borradores sintéticos, ningún correo se envía")
    print(
        f"Casos: {summary['cases']} · correctos: {summary['correct']} · "
        f"contrato: {summary['contract_valid']} · escalados: {summary['escalated']} · "
        f"intentos: {summary['total_attempts']}"
    )
    print("ID   audiencia    tipo          vueltas  resultado  correcto")
    print("---  -----------  ------------  -------  ---------  --------")
    for row in rows:
        revisions = sum(1 for event in row.get("history", []) if event["event"] == "revision_requested")
        print(
            f"{row['case_id']:<4} {row['case']['audience']:<12} {row['case']['kind']:<13} "
            f"{revisions + 1:<8} {row['outcome']:<10} {str(row['evaluation']['correct']):<8}"
        )
    print(json.dumps({"version": version, "mode": mode, **summary}, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Demo S3: loop de correos por audiencia")
    parser.add_argument("--mode", choices=("offline", "live"), default="offline")
    parser.add_argument("--version", choices=(*EMAIL_VERSIONS, "all"), default="all")
    parser.add_argument("--case", default=None, help="ID de caso, por ejemplo M6")
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Imprime el historial completo")
    args = parser.parse_args(argv)

    if args.mode == "live" and args.version not in {"v0", "v4"}:
        print("BLOQUEADO: el live docente está limitado a v0 y v4; v1–v3 se estudian offline.", file=sys.stderr)
        return 2

    try:
        cases = load_email_cases(args.data)
        if args.case:
            cases = [case for case in cases if case["id"] == args.case]
            if not cases:
                raise ValueError(f"No encontré el caso {args.case}")
        versions = list(EMAIL_VERSIONS) if args.version == "all" else [args.version]
        for version in versions:
            rows = run_email_suite(cases, version, mode=args.mode)
            if args.json:
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                _print_rows(rows, version, args.mode)
        return 0
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        print(f"BLOQUEADO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"BLOQUEADO: la corrida de correo falló ({type(exc).__name__}). Usa offline.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
