# S3 — Demo LangChain + LangSmith: observar, evaluar y decidir

Repositorio didáctico independiente del Mentor para la Sesión 3 de **Agentic AI Automation 2026**.

La demo usa un caso sintético de **clasificar y rutear solicitudes**. El objetivo no es construir un agente grande. Es aprender a:

1. distinguir workflow, agente, retry y loop;
2. observar una corrida con LangSmith;
3. convertir casos en un dataset evaluable;
4. usar un checker determinista antes de introducir un LLM-as-judge;
5. comparar `v0 → un cambio → v1` sobre los mismos casos;
6. decidir si hace falta un loop o basta un flujo con verificación y escalamiento humano.

## Importante: no toca los repositorios del curso

Este repo es una superficie de demostración. No reemplaza:

- `agentic-ai-automation-preflight-2026`;
- `agentic-ai-automation-mentor-agent-2026`;
- el repo privado de facilitación.

La demo usa únicamente datos sintéticos. Nunca subas API keys, datos de clientes ni información real.

## Dos modos

### Modo offline — recomendado para empezar

No llama a Anthropic ni a LangSmith. Usa fixtures deterministas para practicar el razonamiento y comprobar que el repo funciona:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -e .
python -m s3_langchain_demo offline --version v0
python -m s3_langchain_demo offline --version v1
python -m unittest discover -s tests -v
```

El modo offline es una simulación pedagógica. Sus resultados sirven para verificar el contrato del ejercicio, no para afirmar el desempeño de un modelo real.

### Modo live — LangChain + Claude + LangSmith

Requiere dos credenciales separadas:

- `ANTHROPIC_API_KEY` para llamar a Claude vía API;
- `LANGSMITH_API_KEY` para enviar traces y evaluaciones.

No son la misma cosa que el acceso de Claude Code. Cárgalas únicamente en variables de entorno o en un `.env` local que permanece fuera de Git.

```bash
cp .env.example .env
# Edita .env solo en tu equipo; no lo subas.

python -m s3_langchain_demo live --version v0 --case E1
python -m s3_langchain_demo live --version v1 --case E1
```

Para enviar traces a un proyecto propio de LangSmith, usa en `.env`:

```text
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=s3-demo-triage-live
```

## Recorrido pedagógico sugerido

1. Ejecuta offline y lee la tabla completa.
2. Abre `docs/CONCEPTOS.md` y explica qué diferencia hay entre trace y evaluación.
3. Configura LangSmith solo cuando el grupo entienda el contrato.
4. Ejecuta un caso live y abre su trace.
5. Crea el dataset en LangSmith con `python scripts/create_dataset.py`.
6. Corre `python scripts/run_langsmith_eval.py --version v0`.
7. Corre la versión `v1` con el único cambio descrito en `docs/DEMO.md`.
8. Compara los experimentos y pregunta qué cambió y qué no.
9. Vuelve al Mentor y elige la estación A–E de S3.

## Estructura

```text
data/cases.json                 seis casos sintéticos
src/s3_langchain_demo/           código ejecutable
scripts/create_dataset.py        crea dataset en LangSmith
scripts/run_langsmith_eval.py   corre evaluación live
scripts/compare_offline.py      compara fixtures offline
docs/CONCEPTOS.md                explicación no técnica
docs/DEMO.md                     guion de la demo
docs/PASO-A-PASO.md              recorrido del facilitador

tests/                           pruebas sin red ni credenciales
```

## Seguridad

- No hay claves en el repositorio.
- `offline` no hace llamadas de red.
- El dataset es sintético.
- El modo live es opcional.
- Si LangSmith falla, usa el modo offline o el fallback de capturas/tabla.

## Referencias oficiales

- [ChatAnthropic en LangChain](https://docs.langchain.com/oss/python/integrations/chat/anthropic)
- [Structured output en LangChain](https://docs.langchain.com/oss/python/langchain/structured-output)
- [Tracing de LangChain con LangSmith](https://docs.langchain.com/langsmith/trace-with-langchain)
- [Conceptos de evaluación en LangSmith](https://docs.langchain.com/langsmith/evaluation-concepts)
- [Comparar experimentos en LangSmith](https://docs.langchain.com/langsmith/compare-experiment-results)
