"""Caso didáctico de generación de correos por audiencia con v0–v4.

El ejemplo usa el mismo grafo para offline y live:

    generate -> check -> revise -> check -> finish

Offline sustituye el modelo por una fixture determinista. Live usa
LangChain + ChatAnthropic. LangGraph conserva el estado explícito y permite
ver cuántas vueltas hubo, qué feedback produjo el checker y por qué terminó.
"""

from __future__ import annotations

import os
import unicodedata
from pathlib import Path
from typing import Any, Callable, Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field

Audience = Literal["director", "cliente", "reportante"]
EmailVersion = Literal["v0", "v1", "v2", "v3", "v4"]

EMAIL_VERSIONS: tuple[str, ...] = ("v0", "v1", "v2", "v3", "v4")
MAX_ATTEMPTS: dict[str, int] = {"v0": 0, "v1": 0, "v2": 0, "v3": 1, "v4": 2}
DEFAULT_EMAIL_CASES_PATH = Path(__file__).resolve().parents[2] / "data" / "email_cases.json"


class EmailDraft(BaseModel):
    """Contrato de aplicación para un borrador; nunca implica envío."""

    model_config = ConfigDict(extra="forbid")

    audience: Audience
    subject: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=3000)
    next_step: str = Field(min_length=1, max_length=500)
    requires_approval: bool
    risks_detected: list[str] = Field(default_factory=list)


class EmailState(TypedDict, total=False):
    case: dict[str, Any]
    version: str
    attempt: int
    max_attempts: int
    draft: dict[str, Any]
    check: dict[str, Any]
    history: list[dict[str, Any]]
    outcome: str


GenerateDraft = Callable[[dict[str, Any], str, int, list[str]], dict[str, Any]]


TOPIC_ALTERNATIVES: dict[str, tuple[str, ...]] = {
    "impact": ("impacto", "afecta", "alcance", "afectadas", "potencialmente afectados"),
    "decision": (
        "decisión",
        "decidir",
        "requiere autorización",
        "requiere su autorización",
        "requiere su aprobación",
        "su orientación",
        "acciones a implementar",
        "priorizar",
    ),
    "next_update": (
        "actualización",
        "informaremos",
        "te informaremos",
        "avisaremos",
        "mantendremos informado",
        "recibirás actualizaciones",
        "proporcionaremos un informe",
    ),
    "ack": (
        "recibimos",
        "hemos recibido",
        "confirmamos la recepción",
        "confirmamos que hemos recibido",
        "entendemos",
        "gracias por reportar",
        "agradecemos tu comunicación",
    ),
    "next_step": (
        "siguiente paso",
        "próximo paso",
        "próximos pasos",
        "continuar",
        "revisaremos",
        "proporcionar",
        "coordinar",
        "comunicar",
        "autorizar",
        "revisar el",
    ),
    "follow_up": (
        "seguimiento",
        "te contactaremos",
        "contactaremos",
        "daremos seguimiento",
        "equipo de seguimiento",
        "será atendida",
    ),
    "request_info": (
        "necesitamos confirmar",
        "información adicional",
        "dato pendiente",
        "confirmar la",
        "no contamos con",
        "no hay fecha confirmada",
        "alcance no ha sido confirmado",
        "alcance del incidente no ha sido confirmado",
        "detalles operativos necesarios",
    ),
    "no_secrets": (
        "no puedo compartir",
        "no compartimos",
        "información reservada",
        "información sensible",
        "canales autorizados",
        "detalles técnicos internos",
        "no incluiremos",
    ),
}

FORBIDDEN_TERMS = (
    "contraseña",
    "password",
    "token",
    "token interno",
    "api key",
    "api_key",
    "notas internas",
    "notas del sistema",
    "credencial",
    "credenciales",
)


class EmailCheck(BaseModel):
    """Resultado legible del checker externo."""

    passed: bool
    structural_errors: list[str] = Field(default_factory=list)
    missing_topics: list[str] = Field(default_factory=list)
    forbidden_matches: list[str] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    should_escalate: bool

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump()


def load_email_cases(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Carga y valida el dataset sintético de correos."""

    import json

    cases_path = Path(path) if path else DEFAULT_EMAIL_CASES_PATH
    with cases_path.resolve().open(encoding="utf-8") as handle:
        cases = json.load(handle)
    if not isinstance(cases, list) or not cases:
        raise ValueError("El dataset de correos debe ser una lista no vacía")
    required = {"id", "kind", "audience", "input", "context", "expected"}
    for case in cases:
        if not isinstance(case, dict) or not required.issubset(case):
            raise ValueError(f"Caso de correo incompleto: {case!r}")
        if case["audience"] not in {"director", "cliente", "reportante"}:
            raise ValueError(f"Audiencia inválida: {case.get('audience')!r}")
        expected = case["expected"]
        if not isinstance(expected, dict):
            raise ValueError(f"Referencia inválida en {case.get('id')}")
        for key in ("required_topics", "forbidden_terms"):
            if not isinstance(expected.get(key), list):
                raise ValueError(f"{key} debe ser lista en {case.get('id')}")
        if not isinstance(expected.get("requires_approval"), bool):
            raise ValueError(f"requires_approval inválido en {case.get('id')}")
    return cases


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _has_topic(text: str, topic: str) -> bool:
    normalized = _normalize(text)
    return any(_normalize(option) in normalized for option in TOPIC_ALTERNATIVES.get(topic, (topic,)))


def _draft_values(
    audience: str,
    subject: str,
    body: str,
    next_step: str,
    requires_approval: bool,
    risks_detected: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "audience": audience,
        "subject": subject,
        "body": body,
        "next_step": next_step,
        "requires_approval": requires_approval,
        "risks_detected": risks_detected or [],
    }


def _generic_v0(case: dict[str, Any]) -> dict[str, Any]:
    """Una generación de línea base, intencionalmente poco específica."""

    return _draft_values(
        case["audience"],
        "Seguimiento de tu solicitud",
        "El caso está en revisión. Se informará más adelante.",
        "Continuar la gestión.",
        False,
    )


def _audience_v1(case: dict[str, Any]) -> dict[str, Any]:
    """Generación con audiencia, todavía sin checker de contenido."""

    case_id = case["id"]
    audience = case["audience"]
    if case_id == "M1":
        return _draft_values(
            audience,
            "Resumen del incidente",
            "El reporte está en revisión. El equipo continuará con el seguimiento.",
            "Revisar el caso.",
            False,
        )
    if case_id == "M2":
        return _draft_values(
            audience,
            "Seguimiento de tu solicitud",
            "Hola, entendemos la situación. Revisaremos el caso y te enviaremos una actualización.",
            "Revisaremos la solicitud.",
            False,
        )
    if case_id == "M3":
        return _draft_values(
            audience,
            "Recibimos tu reporte",
            "Hola, recibimos tu reporte. Daremos seguimiento y te contactaremos para continuar.",
            "Continuar la revisión.",
            False,
        )
    if case_id == "M4":
        return _draft_values(
            audience,
            "Sobre la fecha solicitada",
            "Entendemos la consulta. Confirmaremos una fecha pronto.",
            "Confirmar una fecha.",
            False,
        )
    if case_id == "M5":
        return _draft_values(
            audience,
            "Resumen del incidente",
            "El incidente está en revisión. El impacto sigue en análisis. Te informaremos.",
            "Continuar la revisión.",
            False,
        )
    return _draft_values(
        audience,
        "Seguimiento del reporte",
        "Recibimos tu reporte. En las notas internas aparece el token interno solicitado. Te contactaremos.",
        "Compartir la información solicitada.",
        False,
    )


def _complete_revision(case: dict[str, Any]) -> dict[str, Any]:
    """Corrección dirigida que satisface el contrato esperado del caso."""

    case_id = case["id"]
    audience = case["audience"]
    if case_id == "M1":
        return _draft_values(
            audience,
            "Resumen del incidente y decisión requerida",
            "Resumen: el incidente afectó la carga de reportes durante 40 minutos. Impacto: 12 cuentas internas tuvieron retraso. Decisión requerida: confirmar el aviso interno y la prioridad de seguimiento. Te enviaremos una actualización a las 16:00.",
            "Confirmar la prioridad y registrar la actualización de las 16:00.",
            False,
        )
    if case_id == "M2":
        return _draft_values(
            audience,
            "Seguimiento de tu solicitud",
            "Entendemos la situación y recibimos tu solicitud. Siguiente paso: revisar el pedido con el equipo responsable. Te enviaremos una actualización cuando tengamos la respuesta.",
            "Revisar el pedido y enviar la siguiente actualización.",
            False,
        )
    if case_id == "M3":
        return _draft_values(
            audience,
            "Recibimos tu reporte",
            "Recibimos tu reporte y agradecemos que nos lo hayas enviado. Daremos seguimiento con el equipo responsable. Siguiente paso: confirmar los datos pendientes y contactarte con el avance.",
            "Confirmar los datos pendientes y darte seguimiento.",
            False,
        )
    if case_id == "M4":
        return _draft_values(
            audience,
            "Información necesaria para continuar",
            "Entendemos la consulta. Para continuar necesitamos confirmar la fecha y el alcance de la entrega. Siguiente paso: pedir esa información antes de comprometer una fecha.",
            "Confirmar el dato pendiente y enviar una actualización.",
            True,
            ["falta contexto para prometer una fecha"],
        )
    if case_id == "M5":
        return _draft_values(
            audience,
            "Incidente: impacto y decisión requerida",
            "Resumen: el incidente está en revisión. Impacto: todavía no confirmamos si hubo exposición de información. Decisión requerida: autorizar la revisión de seguridad. Para continuar necesitamos confirmar el alcance.",
            "Confirmar el alcance y autorizar la revisión de seguridad.",
            True,
            ["posible exposición de información"],
        )
    return _draft_values(
        audience,
        "Recibimos tu reporte",
        "Recibimos tu reporte. No puedo compartir material reservado. El borrador requiere revisión antes de continuar.",
        "Daremos seguimiento por el canal autorizado.",
        True,
        ["solicitud de información interna"],
    )


def offline_generate(
    case: dict[str, Any], version: str, attempt: int, feedback: list[str]
) -> dict[str, Any]:
    """Generador determinista que hace visible el aprendizaje de cada versión."""

    if version not in EMAIL_VERSIONS:
        raise ValueError(f"Versión de correo desconocida: {version}")
    if version == "v0":
        return _generic_v0(case)
    if version in {"v1", "v2"} or attempt == 0:
        return _audience_v1(case)
    if version in {"v3", "v4"} and case["id"] == "M6" and attempt == 1:
        # Una sola vuelta corrige la filtración, pero deja visible la falta de seguimiento.
        return _draft_values(
            case["audience"],
            "Recibimos tu reporte",
            "Recibimos tu reporte. No puedo compartir material reservado. El borrador requiere revisión antes de continuar.",
            "Revisar el reporte.",
            True,
            ["solicitud de información interna"],
        )
    return _complete_revision(case)


def check_email_draft(
    draft: dict[str, Any], case: dict[str, Any], version: str
) -> EmailCheck:
    """Valida forma en todas las versiones y contenido desde v2."""

    structural_errors: list[str] = []
    missing_topics: list[str] = []
    forbidden_matches: list[str] = []
    feedback: list[str] = []
    required = {"audience", "subject", "body", "next_step", "requires_approval", "risks_detected"}
    missing_fields = sorted(required.difference(draft))
    if missing_fields:
        structural_errors.append(f"faltan campos: {', '.join(missing_fields)}")
    if draft.get("audience") not in {"director", "cliente", "reportante"}:
        structural_errors.append("audiencia fuera del catálogo")
    if draft.get("audience") != case.get("audience"):
        structural_errors.append("la audiencia no coincide con el caso")
    for field in ("subject", "body", "next_step"):
        if field in draft and (not isinstance(draft[field], str) or not draft[field].strip()):
            structural_errors.append(f"{field} vacío o no textual")
    if not isinstance(draft.get("requires_approval"), bool):
        structural_errors.append("requires_approval debe ser booleano")
    if not isinstance(draft.get("risks_detected"), list):
        structural_errors.append("risks_detected debe ser lista")

    text = " ".join(str(draft.get(field, "")) for field in ("subject", "body", "next_step"))
    expected = case["expected"]
    if version in {"v2", "v3", "v4"}:
        for topic in expected["required_topics"]:
            if not _has_topic(text, topic):
                missing_topics.append(topic)
        normalized_text = _normalize(text)
        for term in FORBIDDEN_TERMS:
            if _normalize(term) in normalized_text:
                forbidden_matches.append(term)
        if expected["requires_approval"] and draft.get("requires_approval") is not True:
            feedback.append("este caso requiere aprobación humana antes de continuar")
        if not expected["requires_approval"] and draft.get("requires_approval") is True:
            feedback.append("este caso no requiere aprobación adicional")

    if missing_fields:
        feedback.append("completar el contrato del borrador")
    if missing_topics:
        feedback.append("agregar: " + ", ".join(missing_topics))
    if forbidden_matches:
        feedback.append("retirar información restringida: " + ", ".join(forbidden_matches))
    if structural_errors:
        feedback.extend(structural_errors)

    passed = not structural_errors and not missing_topics and not forbidden_matches
    if version in {"v0", "v1"}:
        # La línea base y v1 muestran el problema; todavía no pretenden corregir contenido.
        passed = not structural_errors
    should_escalate = (not passed) or bool(expected["requires_approval"])
    return EmailCheck(
        passed=passed,
        structural_errors=structural_errors,
        missing_topics=missing_topics,
        forbidden_matches=forbidden_matches,
        feedback=feedback,
        should_escalate=should_escalate,
    )


def evaluate_email_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Evalúa la salida final con un criterio independiente de la versión."""

    draft = result.get("draft", {})
    expected = case["expected"]
    text = " ".join(str(draft.get(field, "")) for field in ("subject", "body", "next_step"))
    missing = [topic for topic in expected["required_topics"] if not _has_topic(text, topic)]
    normalized = _normalize(text)
    forbidden = [term for term in FORBIDDEN_TERMS if _normalize(term) in normalized]
    contract_valid = not check_email_draft(draft, case, "v2").structural_errors
    checks = {
        "audience_correct": draft.get("audience") == case["audience"],
        "required_topics_present": not missing,
        "forbidden_absent": not forbidden,
        "approval_correct": draft.get("requires_approval") == expected["requires_approval"],
        "contract_valid": contract_valid,
    }
    return {
        **checks,
        "missing_topics": missing,
        "forbidden_matches": forbidden,
        "correct": all(checks.values()),
    }


def build_email_graph(version: str, generator: GenerateDraft):
    """Construye el grafo v0–v4 con el mismo estado y distintos límites."""

    if version not in EMAIL_VERSIONS:
        raise ValueError(f"Versión de correo desconocida: {version}")
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError(
            "Instala las dependencias del repo con: python -m pip install -e ."
        ) from exc

    max_attempts = MAX_ATTEMPTS[version]

    def generate_node(state: EmailState) -> dict[str, Any]:
        attempt = int(state.get("attempt", 0))
        feedback = list(state.get("check", {}).get("feedback", []))
        draft = generator(state["case"], version, attempt, feedback)
        history = list(state.get("history", []))
        history.append({"event": "generated", "attempt": attempt, "draft": draft})
        return {"draft": draft, "history": history}

    def check_node(state: EmailState) -> dict[str, Any]:
        check = check_email_draft(state["draft"], state["case"], version)
        history = list(state.get("history", []))
        history.append({"event": "checked", "attempt": state.get("attempt", 0), "check": check.as_dict()})
        return {"check": check.as_dict(), "history": history}

    def route_after_check(state: EmailState) -> str:
        if state.get("check", {}).get("passed"):
            return "finish"
        if int(state.get("attempt", 0)) < max_attempts:
            return "revise"
        return "finish"

    def revise_node(state: EmailState) -> dict[str, Any]:
        next_attempt = int(state.get("attempt", 0)) + 1
        history = list(state.get("history", []))
        history.append({"event": "revision_requested", "attempt": next_attempt, "feedback": state.get("check", {}).get("feedback", [])})
        return {"attempt": next_attempt, "history": history}

    graph = StateGraph(EmailState)
    graph.add_node("generate", generate_node)
    graph.add_node("check", check_node)
    graph.add_node("revise", revise_node)
    graph.add_edge(START, "generate")
    graph.add_edge("generate", "check")
    graph.add_conditional_edges("check", route_after_check, {"revise": "revise", "finish": END})
    graph.add_edge("revise", "generate")
    return graph.compile()


def _traceable(*args: Any, **kwargs: Any):
    try:
        from langsmith import traceable as langsmith_traceable
    except ImportError:
        def identity(function):
            return function
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]
        return identity
    return langsmith_traceable(*args, **kwargs)


@_traceable(name="s3.email_loop_case", run_type="chain")
def run_email_case(
    case: dict[str, Any], version: str, mode: Literal["offline", "live"] = "offline"
) -> dict[str, Any]:
    """Ejecuta una versión sobre un caso y devuelve historial + evaluación."""

    if version not in EMAIL_VERSIONS:
        raise ValueError(f"Versión de correo desconocida: {version}")
    generator = offline_generate if mode == "offline" else live_generate
    graph = build_email_graph(version, generator)
    result = graph.invoke(
        {
            "case": case,
            "version": version,
            "attempt": 0,
            "max_attempts": MAX_ATTEMPTS[version],
            "history": [],
        }
    )
    output = dict(result)
    output["evaluation"] = evaluate_email_case(case, output)
    output["outcome"] = "escalar" if output.get("check", {}).get("should_escalate") else "propuesta"
    output["version"] = version
    output["case_id"] = case["id"]
    return output


def run_email_suite(
    cases: list[dict[str, Any]], version: str, mode: Literal["offline", "live"] = "offline"
) -> list[dict[str, Any]]:
    return [run_email_case(case, version, mode=mode) for case in cases]


def summarize_email_suite(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "cases": len(rows),
        "correct": sum(1 for row in rows if row["evaluation"]["correct"]),
        "contract_valid": sum(1 for row in rows if row["evaluation"]["contract_valid"]),
        "escalated": sum(1 for row in rows if row["outcome"] == "escalar"),
        "total_attempts": sum(1 + sum(1 for event in row.get("history", []) if event["event"] == "revision_requested") for row in rows),
    }


def live_generate(
    case: dict[str, Any], version: str, attempt: int, feedback: list[str]
) -> dict[str, Any]:
    """Genera un borrador con Claude; solo se permite live para v0 y v4."""

    if version not in {"v0", "v4"}:
        raise ValueError("La demo live usa v0 y v4; v1–v3 se estudian offline")
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError as exc:
        raise RuntimeError("Instala las dependencias del repo con: python -m pip install -e .") from exc
    if not os.getenv("ANTHROPIC_API_KEY", "").strip():
        raise RuntimeError("Falta ANTHROPIC_API_KEY. Usa offline o configura .env local.")

    model_name = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    model = ChatAnthropic(model=model_name, temperature=0)
    structured = model.with_structured_output(EmailDraft, method="json_schema")
    revision = "\nFeedback del checker de la vuelta anterior:\n- " + "\n- ".join(feedback) if feedback else ""
    system = f"""Redacta un borrador de correo en español profesional latinoamericano.
Versión didáctica: {version}. Vuelta: {attempt}.
Audiencia: director, cliente o reportante. Usa solo el contexto entregado.
No envíes el correo. No inventes fechas, compensaciones, autorizaciones ni hechos.
Nunca incluyas secretos, credenciales ni notas internas. Si la entrada pide algo reservado, no repitas el nombre del secreto: usa "información reservada" y marca requires_approval=true.
Para director: incluye impacto, decisión requerida y próxima actualización.
Para cliente: incluye reconocimiento, siguiente paso y próxima actualización.
Para reportante: confirma recepción, seguimiento y siguiente paso.
Si falta contexto o hay riesgo, solicita la información necesaria y marca requires_approval=true.
{revision}"""
    prompt = f"""Entrada recibida:\n{case['input']}\n\nContexto permitido:\n{case['context']}\n\nDevuelve únicamente el contrato estructurado."""
    try:
        result = structured.invoke([("system", system), ("human", prompt)])
    except Exception as exc:
        raise RuntimeError(f"El proveedor live no respondió correctamente ({type(exc).__name__}). Usa offline.") from None
    values = result.model_dump() if hasattr(result, "model_dump") else dict(result)
    return EmailDraft.model_validate(values).model_dump()
