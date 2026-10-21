# Conceptos que vamos a observar

## LangChain no es el agente

En este repo, LangChain es la capa que conecta el modelo, el esquema de salida y la ejecución de la función. No decide por sí solo si el sistema debe ser un agente ni si necesita un loop.

La demo es deliberadamente pequeña:

```text
solicitud → modelo clasificador → salida estructurada → checker → ruta/humano
```

El orden está fijado por el programa. Por eso es un workflow con una llamada de IA; no necesitamos convertirlo artificialmente en un agente autónomo.

## LangSmith no es el evaluador

LangSmith registra traces y organiza evaluaciones. La calidad depende de los casos, las referencias y los evaluadores que definimos.

- Una **trace** ayuda a reconstruir una corrida.
- Un **dataset** contiene ejemplos que queremos volver a probar.
- Un **evaluator** expresa el criterio.
- Un **experiment** registra qué pasó cuando una versión corrió sobre el dataset.

## Por qué el checker es determinista

Una ruta debe pertenecer a un catálogo. Un campo obligatorio debe existir. Confianza baja debe escalar. Esas reglas se pueden expresar en código y deben hacerlo antes de pedirle a otro modelo una opinión.

Esto permite preguntar en clase:

> ¿La salida es correcta o solo está bien escrita?

Un JSON válido no implica que la decisión de negocio sea correcta.

## Retry versus loop

Un retry vuelve a intentar, normalmente porque hubo un error transitorio. Un loop agrega una condición de progreso:

```text
trabajo → verificar → cambiar → volver a verificar
```

Si el sistema repite la misma acción sin una señal de progreso, solo está consumiendo presupuesto.

## v0 y v1

La versión offline `v0` tiene dos errores pedagógicos intencionales: confunde una factura con soporte y trata una cancelación/devolución como soporte. `v1` cambia el criterio de routing y escala el caso límite.

Estos resultados son fixtures didácticos. No representan una medición de Claude ni una promesa de mejora en producción. En modo live, los resultados pueden variar y deben leerse desde sus traces y casos.
