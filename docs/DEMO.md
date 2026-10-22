# Guion de la demo S3

## 1. Encadre — 2 minutos

Di:

> “Voy a usar LangChain para ejecutar un flujo pequeño y LangSmith para observarlo y evaluarlo. La herramienta no decide qué es un buen sistema; nos ayuda a ver qué ocurrió y a comparar casos.”

Aclara:

- los datos son sintéticos;
- nadie necesita crear una cuenta para entender la demo;
- no se proyectan API keys;
- si la conexión falla, se puede continuar offline.

## 2. Caso normal — 5 minutos

Ejecuta `E1` o `E2` en modo live y abre la trace.

Pregunta:

1. ¿Qué input recibió el sistema?
2. ¿Qué input exacto recibió el modelo?
3. ¿Qué salida estructurada devolvió?
4. ¿Qué verificó el checker?
5. ¿Qué ruta final se tomó?

No empieces por la puntuación. Primero reconstruye la operación.

La corrida debe aparecer dentro de la trace de aplicación `s3.classify_live`. En su salida busca la decisión cruda y el resultado del checker; la llamada de LangChain al modelo debe quedar como paso anidado cuando el tracing esté activado.

## 3. Caso fallido — 5 minutos

Ejecuta `E3`, `E5` o `E6` con `v0`.

Pregunta:

- ¿La falla está en el contexto?
- ¿La solicitud llegó al componente correcto?
- ¿La salida cumplió el contrato?
- ¿El checker dejó pasar algo que debió bloquear?
- ¿Qué evidencia necesitaríamos antes de culpar al modelo?

## 4. Dataset — 3 minutos

Muestra que los seis casos están separados en:

- 4 típicos;
- 1 límite;
- 1 adversarial.

Explica que una falla observada puede convertirse en un caso recurrente, pero la referencia esperada debe ser revisada por alguien que conoce el proceso.

## 5. Evaluación — 5 minutos

Ejecuta `run_langsmith_eval.py --version v0`.

Muestra:

- dataset;
- target;
- evaluator determinista;
- resultado por caso;
- trace asociada.

Aclara que una tasa resume; no diagnostica por sí sola.

## 6. v1 — 5 minutos

Ejecuta la versión v1 sobre los mismos casos. El cambio conceptual es:

- el routing conoce la ruta de facturación;
- cancelación/devolución escala a una persona;
- una salida fuera de catálogo no avanza.

Compara los dos experimentos. Pregunta:

> “¿Qué podemos atribuir al único cambio y qué no?”

## 7. Cierre — 3 minutos

Di:

> “La trace explica una corrida. La evaluación compara varias. El loop solo aparece si hay una segunda vuelta real, una señal de progreso, un presupuesto, una detección de no-progreso y un escalamiento.”

Conecta con las estaciones A–E del deck de S3.

## 8. Caso principal de S3: correo iterativo v0–v4

Para mostrar cómo la evidencia cambia el sistema, usa el caso de correos por audiencia de `docs/EMAIL-LOOP-FACILITADOR.md`.

La secuencia recomendada es:

```bash
python scripts/run_email_loop.py --mode offline --version all
python scripts/run_email_loop.py --mode offline --version v3 --case M6 --json
python scripts/run_email_loop.py --mode offline --version v4 --case M6 --json
```

Explica la progresión en voz alta:

- `v0`: generación general;
- `v1`: política por audiencia;
- `v2`: contrato y checker;
- `v3`: una corrección dirigida;
- `v4`: hasta dos vueltas, no-progreso y escalamiento.

La misma suite de seis casos se conserva en todas las versiones. La comparación debe mirar cada correo, no únicamente el porcentaje. En live, limita la demostración a un caso v0 y uno v4 con datos sintéticos:

```bash
python scripts/run_email_loop.py --mode live --version v0 --case M2
python scripts/run_email_loop.py --mode live --version v4 --case M6
```

El resultado siempre es un borrador. No se conecta ningún buzón ni se envía correo.
