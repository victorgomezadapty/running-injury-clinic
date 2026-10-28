# Hito 4 — Variabilidad de etiquetas y registros repetidos

## Por qué esta línea

Una publicación de 2026 ya desarrolló modelos de clasificación transversal del estado actual usando esta misma base RIC y 1.744 corredores. Repetir otro clasificador tendría poca novedad y tampoco resolvería su límite principal: el desenlace sigue siendo estado actual, no riesgo futuro. Este análisis toma otro ángulo: audita cómo varían las etiquetas entre registros del mismo participante y qué incertidumbre temporal existe antes de construir una cohorte.

La publicación de Xiao, Li y Dong comunica rendimiento moderado (AUC 0.790 para random forest), sensibilidad alta y especificidad limitada, además de una brecha entrenamiento–prueba y necesidad de validación externa/subtipos. Se cita y resume; no se reutiliza su figura, texto extenso ni material gráfico. Véase la [publicación original](https://doi.org/10.1186/s13102-026-02026-8).

## Qué hay en los metadatos locales

- 1,832 observaciones de carrera en 1,402 personas.
- 209 personas (14.9% de quienes tienen datos de carrera) tienen más de un registro de carrera.
- Entre esas personas con registros repetidos, 21/209 (10.0%) aparecen con más de una categoría de estado, 22 con más de una categoría de severidad y 25 con más de una categoría de diagnóstico primario.
- Comparando solo la fila más temprana con la más reciente, 20/209 presentan categorías distintas; otra persona tiene variación intermedia aunque las etiquetas de los extremos coincidan.
- 91 filas de carrera (5.0%) tienen timestamps presentes pero distintos entre `datestring` y la fecha del nombre de archivo. Afectan a 91 personas; 2 de las 209 personas repetidas.

La fecha elegida por el proyecto prioriza `datestring` y usa el nombre del archivo cuando la fecha del CSV falta. La comprobación anterior encontró que usar la fecha del nombre de archivo no cambia qué archivo es el primer registro de carrera seleccionado en las 1.402 personas. Eso no convierte los timestamps en visitas clínicas verificadas.

## Estabilidad de categorías entre los registros de cada persona repetida

| Campo | Una categoría | Más de una | Personas con más de una |
| --- | ---: | ---: | ---: |
| injury_status | 188 | 21 | 10.0% |
| severity | 187 | 22 | 10.5% |
| diagnosis | 184 | 25 | 12.0% |

## Estado en el registro más temprano frente al más reciente

El orden usa el timestamp preferido por la auditoría de fuente, con `filename` como desempate. La tabla cuenta personas repetidas; no representa transiciones clínicas confirmadas ni incidencia.

| Registro más temprano ↓ / más reciente → | healthy | injured | discordant | unknown |
| --- | ---: | ---: | ---: | ---: |
| healthy | 89 | 3 | 0 | 5 |
| injured | 9 | 94 | 1 | 0 |
| discordant | 1 | 0 | 5 | 0 |
| unknown | 1 | 0 | 0 | 1 |

## Interpretación y valor diferencial

Estos conteos no indican por sí solos errores: el estado, severidad o diagnóstico pueden cambiar entre registros, los timestamps no están validados como calendario de seguimiento y no se conoce la razón clínica de cada medición. El aporte novedoso y prudente es documentar **sensibilidad del fenotipo a la unidad temporal de análisis**, antes de entrenar modelos o comparar grupos. En concreto, muestra por qué seleccionar una sola fila por persona, declarar qué fecha gobierna esa selección y publicar reglas de conflicto son decisiones metodológicas sustantivas.

La publicación de 2026 ya aborda clasificación transversal. Este proyecto se diferencia con una auditoría reproducible de composición, disponibilidad, velocidad, ambigüedad de etiquetas, registros repetidos y validación biomecánica pendiente; no afirma ser la primera revisión de esta base ni intenta competir en AUC. La siguiente opción analítica sin MATLAB es comparar descriptivamente la selección por registro más temprano frente al más reciente, como escenarios de definición y no como cohorte longitudinal. El cambio de categorías registrado hace que esa sensibilidad temporal sea más informativa que añadir otro clasificador transversal.

## Límites

- La base no está documentada aquí como un protocolo de seguimiento con visitas clínicas uniformes.
- “Más de una etiqueta” significa más de una categoría registrada, no que la persona necesariamente cambió de estado clínico.
- La categorización conservadora usa severidad y campos de lesión reportados; no reemplaza diagnóstico adjudicado.
- No se comparan características biomecánicas por estado ni se estiman asociaciones, causalidad, pronóstico o rendimiento de cribado.
- La validez de ciclos y eventos de marcha sigue pendiente del flujo oficial.

## Reproducibilidad

Regenerar desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe scripts\audit_repeated_record_labels.py
```

El script lee los CSV locales de origen y produce solo tablas agregadas, sin identificadores individuales. Los datos originales y el código oficial se citan conforme a [atribución y licencias](../docs/attribution_and_licensing.md).
