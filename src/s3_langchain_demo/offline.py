"""Fixture offline para practicar la lectura de v0 y v1 sin red."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .evaluator import score_decision, validate_decision
from .models import Decision

# Fixture didáctico, no benchmark de un modelo real.
OFFLINE_FIXTURES: dict[str, dict[str, Decision]] = {
    "v0": {
        "E1": Decision("soporte", "alta", "Cuenta existente.", False),
        "E2": Decision("ventas", "alta", "Pregunta comercial.", False),
        "E3": Decision("soporte", "media", "Hay una cuenta relacionada.", False),
        "E4": Decision("soporte", "alta", "Consulta de pedido.", False),
        "E5": Decision("soporte", "media", "Solicitud de cuenta.", False),
        "E6": Decision("humano", "baja", "Solicitud no confiable.", True),
    },
    "v1": {
        "E1": Decision("soporte", "alta", "Acceso a cuenta.", False),
        "E2": Decision("ventas", "alta", "Solicitud de precios.", False),
        "E3": Decision("facturacion", "alta", "Corrección de factura.", False),
        "E4": Decision("soporte", "alta", "Estado de pedido.", False),
        "E5": Decision("humano", "baja", "Cancelación y devolución requieren revisión.", True),
        "E6": Decision("humano", "baja", "La instrucción intenta saltarse el contrato.", True),
    },
}


def run_offline(cases: Iterable[dict[str, Any]], version: str = "v1") -> list[dict[str, Any]]:
    """Ejecuta el fixture y devuelve una fila por caso."""

    if version not in OFFLINE_FIXTURES:
        raise ValueError(f"Versión offline desconocida: {version}")

    rows: list[dict[str, Any]] = []
    for case in cases:
        case_id = case["id"]
        decision = OFFLINE_FIXTURES[version].get(case_id)
        if decision is None:
            raise ValueError(f"No existe fixture para {case_id} en {version}")
        checked = validate_decision(decision)
        score = score_decision(checked.as_dict(), case["expected"])
        rows.append(
            {
                "id": case_id,
                "kind": case["kind"],
                "input": case["input"],
                "raw": decision.as_dict(),
                "checked": checked.as_dict(),
                **score,
            }
        )
    return rows


def summarize(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    rows_list = list(rows)
    return {
        "cases": len(rows_list),
        "correct": sum(1 for row in rows_list if row["correct"]),
        "route_correct": sum(1 for row in rows_list if row["route_correct"]),
        "escalation_correct": sum(1 for row in rows_list if row["escalation_correct"]),
    }
