# Etapa 03 — validación de eventos y ciclos

## Estado

La reejecución oficial quedó preparada para el piloto fijo de 30 archivos, pero **aún no se pudo ejecutar en este entorno**: no se encontró MATLAB ni Octave disponibles en `PATH`. No se declara validación de eventos o ciclos hasta obtener esa ejecución.

La ruta `scripts/validate_official_events.m` vuelve a procesar cada JSON con `gait_kinematics.m` y `gait_steps.m` del suplemento oficial. Guarda los índices de touchdown y toe-off, la matriz de eventos ampliada, las banderas que indican si se usó PCA o el evento de respaldo, los valores discretos regenerados y los recuentos de curvas normalizadas por lado/segmento después del filtro oficial. También compara las 13 variables seleccionadas por lado con los valores almacenados en `dv_r` y conserva SHA-256 de cada JSON de entrada.

## Qué se comprobó antes de intentar la reejecución

- Se adquirieron y verificaron por tamaño/CRC los pequeños recursos oficiales `tutorial_2.mat`, `tutorial_3.mlx`, `tutorial_4.mlx` y `tutorial_4_cache.mat`.
- `tutorial_2.mat` contiene las tablas MATLAB `group_m` y `group_f`, guardadas como objetos opacos para SciPy; no expone una tabla portátil de eventos por archivo.
- `tutorial_4_cache.mat` contiene las tablas de variables discretas de 1.606 registros. No contiene los índices `events`, `eventsflag` ni la lista de ciclos retenidos necesarios para esta validación.
- El código del suplemento llama `gaitClass.mat` como objeto de clasificación MATLAB y utiliza funciones de procesamiento de señales. La ejecución requiere MATLAB, Statistics and Machine Learning Toolbox y Signal Processing Toolbox. La presencia de modelos PCA no sustituye al entorno de ejecución.
- La ejecución oficial construye eventos y filtra el bloque continuo dentro de `gait_steps`; los JSON originales conservan resúmenes, no esas matrices intermedias. Por eso no es válido reconstruir el número real de ciclos a partir de `STRIDE_RATE` y la duración del archivo.

## Ejecución pendiente

En MATLAB con Statistics and Machine Learning Toolbox y Signal Processing Toolbox, ejecutar:

```matlab
projectRoot = 'C:\Users\victo\OneDrive\Documents\Phisiotherapy DATA SCIENCE\SPORTS_REHAB\Running_Injury_Clinic';
addpath(fullfile(projectRoot, 'scripts'));
validate_official_events(projectRoot);
```

El proceso usa el manifiesto inmutable cuyo SHA-256 es `0ebffe1704471632f2f2a947194d813af9a857da175422fe237b88c390035ed4`; no descarga ni modifica los JSON originales. Escribe en `reports/official_reprocessing/`:

- `official_events.csv`: touchdown/toe-off en muestras para cada ciclo retenido y banderas de método.
- `official_trial_summary.csv`: estado por ensayo, etiqueta oficial de marcha, velocidad, filas de eventos y recuento de curvas normalizadas de cadera izquierda/derecha.
- `official_cycle_counts.csv`: recuentos posteriores al filtrado oficial por lado y segmento; diferencia los eventos emparejados de las curvas normalizadas realmente devueltas.
- `official_dv_comparison.csv`: valores discretos almacenados frente a los regenerados por el código oficial.
- `official_reprocessing_results.mat`: matrices completas y procedencia por ensayo.

Una ejecución sin errores permitirá verificar **reproducibilidad del código** y coherencia de los ciclos regenerados con los resúmenes guardados. No validará por sí sola la exactitud clínica de cada evento: para eso harían falta marcas manuales o una referencia externa independiente. Hasta ejecutar el archivo MATLAB, la disponibilidad y número de ciclos utilizables siguen sin determinarse.
