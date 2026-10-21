"""CLI principal del demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .data import load_cases
from .live import classify_live, validate_environment
from .offline import run_offline, summarize


def _print_offline(rows: list[dict[str, object]], version: str) -> None:
    summary = summarize(rows)
    print(f"Modo offline · {version} · fixture didáctico, no benchmark real")
    print(f"Casos: {summary['cases']} · correctos: {summary['correct']}")
    print("ID   tipo         ruta            escala   correcto")
    print("---  -----------  --------------  -------  --------")
    for row in rows:
        checked = row["checked"]
        print(
            f"{row['id']:<4} {row['kind']:<12} "
            f"{checked['route']:<14} {str(checked['escalate']):<8} "
            f"{str(row['correct']):<8}"
        )
    print(json.dumps(summary, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Demo S3 LangChain + LangSmith")
    sub = parser.add_subparsers(dest="command", required=True)

    offline = sub.add_parser("offline", help="Corre fixtures sin red")
    offline.add_argument("--version", choices=("v0", "v1"), default="v1")
    offline.add_argument("--data", type=Path, default=None)

    live = sub.add_parser("live", help="Llama a Claude y opcionalmente traza en LangSmith")
    live.add_argument("--version", choices=("v0", "v1"), default="v1")
    live.add_argument("--case", default=None, help="ID de caso, por ejemplo E1")
    live.add_argument("--data", type=Path, default=None)

    env = sub.add_parser("env", help="Muestra diagnóstico seguro de variables")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "env":
            print(json.dumps(validate_environment(), indent=2, ensure_ascii=False))
            return 0

        cases = load_cases(args.data)
        if args.command == "offline":
            rows = run_offline(cases, version=args.version)
            _print_offline(rows, args.version)
            return 0

        selected = [case for case in cases if args.case is None or case["id"] == args.case]
        if not selected:
            raise ValueError(f"No encontré el caso {args.case}")
        for case in selected:
            decision, checked = classify_live(case["input"], version=args.version)
            print(json.dumps({
                "id": case["id"],
                "version": args.version,
                "input": case["input"],
                "raw": decision.as_dict(),
                "checked": checked.as_dict(),
            }, ensure_ascii=False, indent=2))
        return 0
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        print(f"BLOQUEADO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        if args.command == "live":
            print(
                "BLOQUEADO: la corrida live falló "
                f"({type(exc).__name__}). Usa offline o revisa tu configuración local.",
                file=sys.stderr,
            )
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
