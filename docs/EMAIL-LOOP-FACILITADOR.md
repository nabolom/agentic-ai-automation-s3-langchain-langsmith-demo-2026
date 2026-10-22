# Guion de facilitación — correo iterativo v0–v4

## Duración sugerida: 30 minutos

### Minutos 0–3 — Encuadre

Di:

> “Vamos a seguir un mismo correo en cinco versiones. No vamos a decidir cuál versión es ‘la inteligente’. Vamos a mirar qué problema aparece, qué cambio hacemos y cómo sabemos si la siguiente vuelta ayudó.”

Aclara:

- los datos son sintéticos;
- los correos son borradores;
- no se conecta ningún buzón;
- offline es la parte reproducible;
- live se usa para observar una corrida, no para inventar una estadística.

### Minutos 3–8 — La línea base

Corre:

```bash
python scripts/run_email_loop.py --mode offline --version v0
```

Pregunta:

> “¿Qué le falta a un correo que sirve igual para dirección, cliente y reportante?”

Escucha: nivel de detalle, responsabilidad, decisión, tono, seguimiento y riesgo.

### Minutos 8–12 — Audiencia

Corre v1:

```bash
python scripts/run_email_loop.py --mode offline --version v1
```

Abre `M1`, `M2` y `M3`. Pregunta:

> “¿Qué cambió porque ahora conocimos la audiencia?”

Después muestra `M4` y pregunta:

> “¿Qué nos hace falta antes de prometer una fecha?”

### Minutos 12–16 — Contrato y checker

Corre v2:

```bash
python scripts/run_email_loop.py --mode offline --version v2 --case M6 --json
```

Lee los eventos `checked` y el feedback. Di:

> “El checker no reescribe el correo. Identifica el problema y deja una instrucción concreta para la siguiente vuelta.”

Pregunta:

> “¿Qué parte podría revisar un programa? ¿Qué parte requeriría una persona?”

### Minutos 16–21 — Una vuelta

Corre v3 para `M6`:

```bash
python scripts/run_email_loop.py --mode offline --version v3 --case M6 --json
```

Cuenta los eventos:

```text
generated → checked → revision_requested → generated → checked
```

Pregunta:

> “¿Qué se corrigió y qué quedó pendiente?”

Explica que una vuelta tiene valor porque recibe feedback; repetir la misma petición no constituye una mejora.

### Minutos 21–25 — Dos vueltas y paradas

Corre v4:

```bash
python scripts/run_email_loop.py --mode offline --version v4 --case M6 --json
```

Muestra que una segunda vuelta agrega seguimiento y que el caso todavía requiere aprobación. Di:

> “El grafo no decide enviar. Decide que el borrador está listo para revisión o que debe escalarse.”

Pregunta:

> “¿Qué habría ocurrido si el segundo intento repitiera el mismo error?”

Respuesta esperada: detener por no-progreso o escalar.

### Minutos 25–30 — LangSmith y live

Muestra el dataset `s3-demo-email-loop-6-casos-2026` y una trace preparada. Después, si hay credenciales y tiempo, corre un solo caso live v0 y un solo caso live v4:

```bash
python scripts/run_email_loop.py --mode live --version v0 --case M2
python scripts/run_email_loop.py --mode live --version v4 --case M6
```

Di:

> “Aquí el proveedor puede variar. Por eso seguimos usando la misma suite y el mismo checker. La trace muestra el recorrido; la evaluación nos ayuda a comparar casos.”

## Preguntas que conviene hacer

- “¿Qué cambió en la entrada?”
- “¿Qué cambió en el prompt?”
- “¿Qué cambió en el contrato?”
- “¿Qué cambió en el checker?”
- “¿Qué vuelta reparó qué defecto?”
- “¿Qué caso todavía necesita aprobación?”
- “¿Dónde se detiene el proceso?”
- “¿Qué evidencia guardarías para S4?”

## Fallbacks

### Si LangSmith no abre

Usa `--json` y lee el historial local. Di:

> “La UI ayuda a explorar. El aprendizaje de hoy también queda en este historial reproducible.”

### Si Anthropic no responde

Continúa offline y muestra una trace preparada etiquetada como material de demostración.

### Si el grupo pregunta por enviar el correo

Responde:

> “Ese es otro problema. Aquí solo estamos diseñando el borrador, el checker y la aprobación. Un envío real necesitaría permisos, registro y recuperación.”

### Si una persona quiere usar datos reales

Responde:

> “Para esta demo no. Usa una versión sintética del caso. Los datos reales se incorporan después de revisar autorización y exposición.”

## Cierre

Pide estas cinco líneas:

```text
Mi audiencia:
Mi caso límite:
Mi checker:
Mi límite de vueltas:
Mi condición de escalamiento:
```
