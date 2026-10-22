# Ejemplo: loop de correos por audiencia, v0 → v4

Este ejemplo toma un reporte sintético y produce un borrador de correo para una audiencia concreta:

- director(a);
- cliente;
- persona que reporta.

El correo nunca se envía. El resultado es una propuesta que puede aprobarse, corregirse o escalarse.

## La escalera didáctica

| Versión | Qué cambia | Vueltas |
|---|---|---:|
| `v0` | generación general, sin política explícita de audiencia | 0 |
| `v1` | política de audiencia en el prompt | 0 |
| `v2` | contrato estructurado y checker de contenido/riesgo | 0 |
| `v3` | feedback específico y una regeneración | 1 |
| `v4` | loop operativo con no-progreso, aprobación y límite | 2 |

Todas las versiones corren sobre los mismos seis casos.

## Flujo del grafo

```text
START
  ↓
generate
  ↓
check ── pasa ───────────────→ END
  │
  ├─ falla y quedan vueltas ─→ revise → generate
  │
  └─ falla sin vueltas ──────→ END
```

El estado registra el borrador, el feedback del checker, el número de vuelta y la razón de cierre. La implementación usa LangGraph; la generación live usa LangChain y `ChatAnthropic`.

## Ejecutar offline

Desde la raíz del repo:

```bash
python -m pip install -e .
python scripts/run_email_loop.py --mode offline --version all
python scripts/run_email_loop.py --mode offline --version v4 --case M6 --json
```

La salida permite revisar por versión:

- casos correctos;
- contrato válido;
- casos escalados;
- número total de intentos;
- historial de generación, checker y revisión.

Los resultados offline son fixtures de enseñanza. No son un benchmark de Claude.

## Ejecutar live

La clase usa live solo para comparar una corrida v0 y una v4 con datos sintéticos:

```bash
cp .env.example .env
python scripts/run_email_loop.py --mode live --version v0 --case M2
python scripts/run_email_loop.py --mode live --version v4 --case M6
```

Variables necesarias:

```text
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=s3-demo-email-loop-live
```

No se conectan Gmail, Outlook, CRM ni buzones. LangSmith recibe casos sintéticos y borradores no enviados.

## Crear y evaluar en LangSmith

```bash
python scripts/create_email_dataset.py
python scripts/run_email_langsmith_eval.py --version v0
python scripts/run_email_langsmith_eval.py --version v4
```

Los evaluadores separados miden:

- contrato estructurado;
- temas obligatorios y ausencia de información restringida;
- coincidencia de `requires_approval`.

La comparación se hace sobre el mismo dataset. LangSmith permite abrir una fila, revisar la trace y ver las vueltas del grafo.

## Qué observar en clase

1. En `v0`, el correo suena genérico y no responde a la audiencia.
2. En `v1`, cambia el tono y la estructura, pero todavía pueden pasar promesas o faltar información.
3. En `v2`, el checker convierte esos problemas en feedback y escalamiento.
4. En `v3`, una vuelta corrige el problema principal.
5. En `v4`, el caso adversarial necesita una segunda vuelta; el grafo termina por aprobación o escalamiento y no sigue intentando indefinidamente.

## Archivos

- `src/s3_langchain_demo/email_loop.py`: estado, grafo, generadores, checker y evaluador.
- `data/email_cases.json`: seis casos sintéticos.
- `scripts/run_email_loop.py`: runner offline/live.
- `scripts/create_email_dataset.py`: dataset de LangSmith.
- `scripts/run_email_langsmith_eval.py`: evaluación live de v0/v4.
- `tests/test_email_loop.py`: pruebas sin red y mock live.
- `docs/EMAIL-LOOP.md`: explicación para la sesión.
