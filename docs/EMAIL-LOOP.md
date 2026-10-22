# S3 — Demo de correo iterativo en LangChain y LangSmith

## Propósito

Esta demo permite explicar una idea concreta: la calidad de un sistema mejora cuando cada corrida deja casos, feedback y decisiones que se pueden volver a probar.

El caso genera borradores de correo para tres audiencias. La sesión no enseña a enviar correo. Enseña a observar, evaluar y detener un flujo que produce texto.

## El caso

La entrada es un reporte sintético. La audiencia se conoce antes de generar el borrador. El sistema recibe también un contexto permitido. La salida tiene asunto, cuerpo, siguiente paso, aprobación requerida y riesgos detectados.

La persona que facilita debe repetir una frase:

> “El borrador puede ser útil y aun así necesitar aprobación. Que el contrato pase no autoriza el envío.”

## Qué representa cada versión

### v0 — Una generación general

El modelo recibe el reporte y produce un correo genérico. No sabe qué necesita un director, un cliente o quien reportó el problema. El resultado sirve como línea base.

Pregunta para la sala:

> “¿Qué información se pierde cuando tratamos a las tres audiencias como si fueran la misma?”

### v1 — Política de audiencia

El prompt especifica qué debe contener cada correo. La salida puede mejorar aunque todavía no exista un checker que la detenga.

Pregunta:

> “¿Qué puede seguir mal aunque el prompt explique la audiencia?”

### v2 — Contrato y checker

La salida deja de ser texto libre. Tiene un formato que el programa puede revisar. El checker busca campos, temas, información restringida y aprobación.

Pregunta:

> “¿Qué problema puede detectar el checker y cuál necesita el criterio de una persona?”

### v3 — Corrección dirigida

Cuando falla el checker, devuelve feedback concreto. El grafo puede regenerar una vez. La vuelta tiene sentido porque el segundo intento recibe información distinta.

Pregunta:

> “¿Qué cambió entre una vuelta y la siguiente?”

### v4 — Loop operativo

El grafo permite hasta dos vueltas. También detecta que una vuelta no progresa y escala casos de riesgo. El sistema tiene una forma explícita de terminar.

Pregunta:

> “¿Qué nos impide dejar que siga intentando hasta que nos guste el texto?”

## Orden de la demo

1. Ejecutar los cinco modos offline.
2. Abrir el caso `M6`, que solicita información interna.
3. Comparar el historial de v3 y v4.
4. Mostrar el dataset de LangSmith.
5. Ejecutar una corrida live v0 con un caso típico.
6. Ejecutar una corrida live v4 con el caso adversarial.
7. Abrir la trace y ubicar `generate`, `check`, `revise` y el cierre.
8. Comparar los resultados sin afirmar que una corrida live es un benchmark.

## Qué decir mientras se ve la trace

- “Aquí está la entrada sintética.”
- “Aquí aparece la primera propuesta.”
- “El checker encontró esta observación.”
- “Esta es la vuelta de corrección.”
- “Ahora el grafo termina porque el borrador pasa o porque requiere aprobación.”
- “La segunda vuelta no es gratuita: tiene un límite y deja evidencia.”

## Qué revisar en LangSmith

En el proyecto de correo busca:

- input del caso;
- audiencia;
- versión;
- número de intento;
- salida estructurada;
- feedback del checker;
- eventos de revisión;
- resultado final;
- evaluaciones por caso.

La trace responde qué ocurrió. El dataset permite volver a ejecutar la misma pregunta. El evaluador permite comparar versiones.

## Los seis casos

- `M1`: dirección necesita impacto, decisión y actualización.
- `M2`: cliente necesita reconocimiento, siguiente paso y actualización.
- `M3`: reportante necesita confirmación, seguimiento y siguiente paso.
- `M4`: cliente pide una fecha que todavía no está confirmada.
- `M5`: dirección recibe un incidente con alcance todavía incierto.
- `M6`: reportante intenta obtener token y notas internas.

## Qué no decir

No digas:

- que v4 “resuelve” la redacción de correos en general;
- que una tasa de seis casos representa una operación real;
- que una salida estructurada es automáticamente correcta;
- que el loop debe existir en todos los flujos;
- que el live y el offline tienen que dar el mismo resultado;
- que el correo se envía.

## Cierre

Pide que cada persona escriba:

```text
Caso que quiero conservar:
Falla que quiero volver a probar:
Checker que puedo escribir:
Límite de vueltas:
Cuándo entra una persona:
```

El puente a S4 es directo: permisos, observabilidad, recuperación y handoff.
