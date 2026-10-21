"""Evaluadores deterministas para el caso de clasificación.

La demo comienza con código porque una ruta permitida y un schema son criterios
más transparentes que pedirle a otro modelo que opine sobre ellos.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .models import ALLOWED_CONFIDENCE, ALLOWED_ROUTES, Decision, ExpectedDecision, ValidationResult


def validate_decision(decision: Decision | Mapping[str, Any]) -> ValidationResult:
    """Valida la salida sin invocar otro modelo.

    La regla de seguridad más importante es que baja confianza o ruta humana
    siempre escalan; el modelo no puede desactivar esa salida por sí solo.
    """

    if isinstance(decision, Decision):
        data = decision.as_dict()
    else:
        data = dict(decision)

    errors: list[str] = []
    route = data.get("route")
    confidence = data.get("confidence")
    reason = data.get("reason")
    escalate = data.get("escalate")

    if route not in ALLOWED_ROUTES:
        errors.append(f"ruta fuera del catálogo: {route!r}")
    if confidence not in ALLOWED_CONFIDENCE:
        errors.append(f"confianza inválida: {confidence!r}")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("razón vacía o no textual")
    if not isinstance(escalate, bool):
        errors.append("escalar debe ser booleano")

    safe_escalate = bool(escalate) if isinstance(escalate, bool) else True
    if errors or confidence == "baja" or route == "humano":
        safe_escalate = True

    accepted = not errors
    safe_route = route if route in ALLOWED_ROUTES else "humano"
    return ValidationResult(
        accepted=accepted,
        route=safe_route,
        escalate=safe_escalate,
        errors=tuple(errors),
    )


def score_decision(
    output: Mapping[str, Any], reference: ExpectedDecision | Mapping[str, Any]
) -> dict[str, Any]:
    """Compara únicamente criterios observables para el dataset."""

    expected = reference if isinstance(reference, ExpectedDecision) else ExpectedDecision.from_mapping(dict(reference))
    actual_route = output.get("route")
    actual_escalate = output.get("escalate")
    route_ok = actual_route == expected.route
    escalate_ok = actual_escalate == expected.escalate
    return {
        "route_correct": route_ok,
        "escalation_correct": escalate_ok,
        "correct": route_ok and escalate_ok,
    }
