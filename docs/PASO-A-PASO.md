# Paso a paso — Demo LangChain + LangSmith

## Parte A — Tú como facilitador(a)

### Paso 0. Clona el repo

Si el repo ya es público:

```bash
git clone https://github.com/nabolom/agentic-ai-automation-s3-langchain-langsmith-demo-2026.git
cd agentic-ai-automation-s3-langchain-langsmith-demo-2026
```

Comprueba que estás en el repo correcto:

```bash
pwd
git remote -v
git status --short
```

### Paso 1. Crea un entorno Python

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, no cambies políticas globales para la clase. Ejecuta directamente:

```powershell
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Paso 2. Instala el repo

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Verifica que el modo offline funciona:

```bash
python -m s3_langchain_demo env
python -m s3_langchain_demo offline --version v0
python -m s3_langchain_demo offline --version v1
python scripts/compare_offline.py
python -m unittest discover -s tests -v
```

Debes ver seis casos. La fixture didáctica marca `v0` con 4/6 y `v1` con 6/6. No lo presentes como desempeño real del modelo.

### Paso 3. Crea cuentas y claves fuera del repo

Necesitas:

1. Una cuenta de Claude Console con una API key de Anthropic.
2. Una cuenta/workspace de LangSmith con una API key de LangSmith.

No pegues esas claves en el README, el chat ni el repositorio. Usa `.env` local:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edita `.env`:

```text
ANTHROPIC_API_KEY=tu_clave_local
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=tu_clave_local_de_langsmith
LANGSMITH_PROJECT=s3-demo-triage-live
```

El archivo `.env` está ignorado por Git. Confirma que Git no lo ve:

```bash
git status --short
```

### Paso 4. Prueba una corrida live

Empieza con un solo caso:

```bash
python -m s3_langchain_demo live --version v1 --case E1
```

Si falla, lee el mensaje `BLOQUEADO`. No uses otra clave ni pegues una clave en el repositorio. Verifica:

```bash
python -m s3_langchain_demo env
```

La salida solo muestra si hay variables presentes; nunca imprime sus valores.

### Paso 5. Lee la trace

Abre LangSmith y entra al proyecto `s3-demo-triage-live`.

Busca la corrida de `E1` y pregunta:

- ¿qué recibió la función?
- ¿qué recibió Claude?
- ¿qué objeto estructurado devolvió?
- ¿qué hizo el checker?
- ¿qué se devolvió a la ruta final?

### Paso 6. Crea el dataset

Con las claves cargadas:

```bash
python scripts/create_dataset.py
```

El script crea el dataset `s3-demo-triage-6-casos-2026` con los seis casos.

### Paso 7. Corre v0 y v1

```bash
python scripts/run_langsmith_eval.py --version v0
python scripts/run_langsmith_eval.py --version v1
```

El primer experimento puede tardar. Usa `max_concurrency=1` para que la demo sea más legible y no dispare llamadas simultáneas innecesarias.

### Paso 8. Compara

En LangSmith:

1. abre el dataset;
2. selecciona los experimentos `s3-demo-v0` y `s3-demo-v1`;
3. abre la vista de comparación;
4. revisa cada fila;
5. abre una trace de un caso que cambió;
6. comprueba si hubo regresiones.

Tu frase clave:

> “No me interesa solo el promedio. Quiero saber qué casos cambiaron y qué evidencia explica el cambio.”

### Paso 9. Cierra con Mentor

No copies el repo de demo dentro del Mentor. Regresa al proyecto personal y elige:

- A: completar casos/línea base;
- B: diagnosticar una falla;
- C: definir checker o cuatro paradas;
- D: extender con costo, estado o recuperación;
- E: puente a S4.

## Parte B — Recorrido para Aprendedores(as)

### Paso 1. Comprueba el entorno

```bash
python --version
python -m pip --version
git --version
```

### Paso 2. Clona y entra

```bash
git clone https://github.com/nabolom/agentic-ai-automation-s3-langchain-langsmith-demo-2026.git
cd agentic-ai-automation-s3-langchain-langsmith-demo-2026
```

### Paso 3. Instala y prueba offline

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
python -m s3_langchain_demo offline --version v0
```

Si Windows bloquea la activación, no cambies políticas globales. Ejecuta directamente:

```powershell
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m s3_langchain_demo offline --version v0
```

### Paso 4. Decide si necesitas live

No necesitas una API key para completar el razonamiento. Puedes estudiar `offline`, `docs/CONCEPTOS.md` y `docs/DEMO.md`.

Si tu facilitador te indica usar live, crea `.env` local y configura tus propias claves. No las compartas.

### Paso 5. Ejecuta un solo caso

```bash
python -m s3_langchain_demo live --version v1 --case E1
```

### Paso 6. Registra evidencia

En tu repo personal o en tu hoja de clase escribe:

- qué caso corriste;
- qué salida esperabas;
- qué trace observaste;
- qué checker actuó;
- qué cambió entre v0 y v1;
- si necesitas loop o basta no-loop.

### Paso 7. Vuelve al Mentor

La demo no sustituye tu proyecto. Lleva la pregunta y la evidencia al Mentor:

> “Mi caso es ____. Observé ____. Mi hipótesis de capa es ____. Mi siguiente paso es ____.”

## Fallback si algo falla

### Sin Python o sin instalación

Usa la tabla de `data/cases.json` y la salida del deck. Marca el modo como `BLOQUEADO`; no inventes una trace.

### Sin API key de Anthropic

Usa offline. La clase conserva el concepto de contrato, checker y evaluación.

### Sin API key de LangSmith

Ejecuta live solo como llamada local si tu proveedor está disponible, o usa offline. No hay que crear una cuenta para entender la teoría.

### Sin conexión

Usa:

```bash
python -m s3_langchain_demo offline --version v0
python -m s3_langchain_demo offline --version v1
```

### Error de proveedor o modelo

No cambies cinco cosas a la vez. Guarda el mensaje de error sin secretos, marca qué paso está bloqueado y vuelve al caso sintético.
