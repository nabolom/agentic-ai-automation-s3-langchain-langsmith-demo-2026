"""Contratos pequeños y explícitos para la demo.

El modo offline usa dataclasses para no depender de red. El modo live usa
estos valores como contrato de aplicación y puede añadir validación Pydantic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ALLOWED_ROUTES = ("soporte", "ventas", "facturacion", "humano")
ALLOWED_CONFIDENCE = ("baja", "media", "alta")


@dataclass(frozen=True)
class ExpectedDecision:
    """Salida esperada curada por la persona que conoce el proceso."""

    route: str
    escalate: bool

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ExpectedDecision":
        return cls(route=str(value["route"]), escalate=bool(value["escalate"]))


@dataclass(frozen=True)
class Decision:
    """Salida del modelo o del fixture, antes del checker final."""

    route: str
    confidence: str
    reason: str
    escalate: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "confidence": self.confidence,
            "reason": self.reason,
            "escalate": self.escalate,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Resultado del checker externo."""

    accepted: bool
    route: str
    escalate: bool
    errors: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "route": self.route,
            "escalate": self.escalate,
            "errors": list(self.errors),
        }
