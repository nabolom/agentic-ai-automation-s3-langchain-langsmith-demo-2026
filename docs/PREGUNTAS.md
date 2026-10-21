# Preguntas para después de la demo

## Si preguntan: “¿Esto ya es un agente?”

Respuesta sugerida:

> “Es un workflow con una decisión de IA y una verificación. No necesito llamarlo agente para que sea útil. La etiqueta importa menos que poder explicar el camino, la salida y el límite.”

## “¿Por qué no dejamos que Claude decida todo?”

> “Porque algunas reglas son explícitas, baratas y riesgosas de delegar. La IA puede interpretar; el checker puede bloquear una salida inválida.”

## “¿Por qué el JSON válido no basta?”

> “Porque la forma puede ser correcta y la ruta equivocada. Por eso medimos schema, ruta y escalamiento por separado.”

## “¿Qué aporta LangChain?”

> “Nos da una forma estándar de representar la llamada al modelo, el structured output y la composición del flujo. No reemplaza el diseño del proceso.”

## “¿Qué aporta LangSmith?”

> “Nos permite inspeccionar traces y organizar evaluaciones. No conoce por sí solo la verdad de tu proceso.”

## “¿Por qué no usar LLM-as-judge desde el inicio?”

> “Porque primero queremos un criterio que podamos explicar con código. Si el problema es ruta permitida, un `if` es más transparente que otro modelo.”

## “¿Cuál es la diferencia entre trace y experiment?”

> “La trace explica una operación concreta. El experimento reúne los resultados de una versión sobre varios ejemplos.”

## “¿Qué caso pondrías en un dataset?”

> “Uno que represente una decisión importante, una frontera o una falla que no quiero volver a perder.”

## “¿Cuándo hago un loop?”

> “Cuando hay trabajo, verificación, un cambio observable y una condición explícita para terminar. Si no, probablemente basta un checker o un flujo de una pasada.”

## “¿Qué hago si mi proyecto ya está más avanzado?”

> “No regreses. Usa la demo como auditoría: busca una trace, un dataset, un evaluador, una comparación y una condición de parada. Después ve a la estación D o E.”

## “¿Qué hago si todavía no tengo proyecto?”

> “Usa esta demo como caso común, pero no la confundas con tu proyecto. Después elige Ruta 2 o Ruta 3 en el Mentor.”
