"""Audit record-to-record label variability in the RIC running metadata.

This is a descriptive data-readiness analysis, not a longitudinal injury study.
Dates are not assumed to represent scheduled clinical follow-up, and output
tables contain aggregate counts only (no participant identifiers or row data).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.load_metadata import load_metadata  # noqa: E402


TABLES = ROOT / "reports" / "tables"
SUMMARY_PATH = TABLES / "repeated_record_audit_summary.csv"
ENDPOINT_PATH = TABLES / "repeated_record_status_endpoint_matrix.csv"
STABILITY_PATH = TABLES / "repeated_record_field_stability.csv"
REPORT_PATH = ROOT / "reports" / "milestone_04_repeated_record_audit.md"


def load_running() -> pd.DataFrame:
    data = load_metadata(ROOT / "data" / "raw")
    running = data.loc[data.task.eq("running")].copy()
    if len(running) != 1832 or running.participant_id.nunique() != 1402:
        raise ValueError("Running metadata counts differ from the pinned source snapshot.")
    return running


def audit(running: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    grouped = running.groupby("participant_id", sort=False)
    record_counts = grouped.size()
    repeated_ids = record_counts[record_counts.gt(1)].index
    repeated = running[running.participant_id.isin(repeated_ids)].copy()
    repeated_groups = repeated.groupby("participant_id", sort=False)

    summary = pd.DataFrame(
        [
            {"measure": "running_metadata_records", "n": len(running), "denominator": len(running), "percent": 100.0},
            {"measure": "unique_running_participants", "n": running.participant_id.nunique(), "denominator": running.participant_id.nunique(), "percent": 100.0},
            {"measure": "participants_with_multiple_running_records", "n": len(repeated_ids), "denominator": running.participant_id.nunique(), "percent": 100 * len(repeated_ids) / running.participant_id.nunique()},
            {"measure": "repeated_participants_with_multiple_injury_status_labels", "n": int((repeated_groups.injury_status.nunique() > 1).sum()), "denominator": len(repeated_ids), "percent": 100 * float((repeated_groups.injury_status.nunique() > 1).mean())},
            {"measure": "repeated_participants_with_multiple_severity_labels", "n": int((repeated_groups.severity.nunique() > 1).sum()), "denominator": len(repeated_ids), "percent": 100 * float((repeated_groups.severity.nunique() > 1).mean())},
            {"measure": "repeated_participants_with_multiple_primary_diagnosis_labels", "n": int((repeated_groups.diagnosis.nunique() > 1).sum()), "denominator": len(repeated_ids), "percent": 100 * float((repeated_groups.diagnosis.nunique() > 1).mean())},
            {"measure": "running_records_with_csv_filename_timestamp_disagreement", "n": int(running.timestamp_disagreement.sum()), "denominator": len(running), "percent": 100 * float(running.timestamp_disagreement.mean())},
            {"measure": "participants_with_any_running_timestamp_disagreement", "n": int(running.loc[running.timestamp_disagreement, "participant_id"].nunique()), "denominator": running.participant_id.nunique(), "percent": 100 * running.loc[running.timestamp_disagreement, "participant_id"].nunique() / running.participant_id.nunique()},
            {"measure": "repeated_participants_with_any_running_timestamp_disagreement", "n": int(repeated.loc[repeated.timestamp_disagreement, "participant_id"].nunique()), "denominator": len(repeated_ids), "percent": 100 * repeated.loc[repeated.timestamp_disagreement, "participant_id"].nunique() / len(repeated_ids)},
        ]
    )

    ordered = running.sort_values(
        ["participant_id", "session_time", "filename"],
        na_position="last",
        kind="stable",
    )
    endpoints = ordered.groupby("participant_id", sort=False).agg(
        first_status=("injury_status", "first"),
        latest_status=("injury_status", "last"),
        n_running_records=("filename", "size"),
    )
    endpoints = endpoints[endpoints.n_running_records.gt(1)]
    status_varies = repeated_groups.injury_status.nunique().gt(1)
    endpoint_differs = endpoints.first_status.ne(endpoints.latest_status)
    summary = pd.concat(
        [
            summary,
            pd.DataFrame(
                [
                    {
                        "measure": "repeated_participants_with_different_earliest_latest_status",
                        "n": int(endpoint_differs.sum()),
                        "denominator": len(endpoints),
                        "percent": 100 * float(endpoint_differs.mean()),
                    },
                    {
                        "measure": "repeated_participants_with_intermediate_status_variation_but_matching_endpoints",
                        "n": int((status_varies & ~endpoint_differs).sum()),
                        "denominator": len(endpoints),
                        "percent": 100 * float((status_varies & ~endpoint_differs).mean()),
                    },
                ]
            ),
        ],
        ignore_index=True,
    )
    endpoint_matrix = (
        endpoints.groupby(["first_status", "latest_status"], dropna=False)
        .size()
        .rename("participants")
        .reset_index()
    )
    endpoint_matrix["record_ordering"] = "earliest/latest metadata timestamp; not verified follow-up"

    stability_rows = []
    for field, label in (
        ("injury_status", "source-derived current-status category"),
        ("severity", "source severity category"),
        ("diagnosis", "normalized primary diagnosis category"),
    ):
        category_count = repeated_groups[field].nunique()
        changing = int(category_count.gt(1).sum())
        stability_rows.append(
            {
                "field": field,
                "label_definition": label,
                "repeated_participants": len(repeated_ids),
                "one_category_across_records": int(category_count.eq(1).sum()),
                "multiple_categories_across_records": changing,
                "multiple_category_percent": 100 * changing / len(repeated_ids),
                "interpretation": "record-to-record variability; not proven clinical transition or coding error",
            }
        )
    stability = pd.DataFrame(stability_rows)

    TABLES.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_PATH, index=False, float_format="%.4f")
    endpoint_matrix.to_csv(ENDPOINT_PATH, index=False)
    stability.to_csv(STABILITY_PATH, index=False, float_format="%.4f")
    return summary, endpoint_matrix, stability


def metric(summary: pd.DataFrame, name: str) -> dict[str, float]:
    row = summary.loc[summary.measure.eq(name)].iloc[0]
    return {"n": int(row.n), "denominator": int(row.denominator), "percent": float(row.percent)}


def markdown_matrix(matrix: pd.DataFrame) -> str:
    labels = ["healthy", "injured", "discordant", "unknown"]
    counts = matrix.pivot(index="first_status", columns="latest_status", values="participants").fillna(0)
    counts = counts.reindex(index=labels, columns=labels, fill_value=0).astype(int)
    lines = ["| Registro más temprano ↓ / más reciente → | " + " | ".join(labels) + " |", "| --- | " + " | ".join(["---:"] * len(labels)) + " |"]
    for label in labels:
        lines.append("| " + label + " | " + " | ".join(str(counts.loc[label, col]) for col in labels) + " |")
    return "\n".join(lines)


def write_report(running: pd.DataFrame, summary: pd.DataFrame, matrix: pd.DataFrame, stability: pd.DataFrame) -> None:
    multi = metric(summary, "participants_with_multiple_running_records")
    status = metric(summary, "repeated_participants_with_multiple_injury_status_labels")
    severity = metric(summary, "repeated_participants_with_multiple_severity_labels")
    diagnoses = metric(summary, "repeated_participants_with_multiple_primary_diagnosis_labels")
    timestamp_rows = metric(summary, "running_records_with_csv_filename_timestamp_disagreement")
    timestamp_people = metric(summary, "participants_with_any_running_timestamp_disagreement")
    repeat_timestamp = metric(summary, "repeated_participants_with_any_running_timestamp_disagreement")
    endpoint_changes = metric(summary, "repeated_participants_with_different_earliest_latest_status")
    middle_only = metric(summary, "repeated_participants_with_intermediate_status_variation_but_matching_endpoints")
    middle_wording = (
        "otra persona tiene"
        if middle_only["n"] == 1
        else f"{middle_only['n']} personas tienen"
    )

    stability_rows = []
    for row in stability.itertuples(index=False):
        stability_rows.append(
            f"| {row.field} | {row.one_category_across_records} | {row.multiple_categories_across_records} | {row.multiple_category_percent:.1f}% |"
        )

    report = f"""# Hito 4 — Variabilidad de etiquetas y registros repetidos

## Por qué esta línea

Una publicación de 2026 ya desarrolló modelos de clasificación transversal del estado actual usando esta misma base RIC y 1.744 corredores. Repetir otro clasificador tendría poca novedad y tampoco resolvería su límite principal: el desenlace sigue siendo estado actual, no riesgo futuro. Este análisis toma otro ángulo: audita cómo varían las etiquetas entre registros del mismo participante y qué incertidumbre temporal existe antes de construir una cohorte.

La publicación de Xiao, Li y Dong comunica rendimiento moderado (AUC 0.790 para random forest), sensibilidad alta y especificidad limitada, además de una brecha entrenamiento–prueba y necesidad de validación externa/subtipos. Se cita y resume; no se reutiliza su figura, texto extenso ni material gráfico. Véase la [publicación original](https://doi.org/10.1186/s13102-026-02026-8).

## Qué hay en los metadatos locales

- {len(running):,} observaciones de carrera en {running.participant_id.nunique():,} personas.
- {multi['n']} personas ({multi['percent']:.1f}% de quienes tienen datos de carrera) tienen más de un registro de carrera.
- Entre esas personas con registros repetidos, {status['n']}/{status['denominator']} ({status['percent']:.1f}%) aparecen con más de una categoría de estado, {severity['n']} con más de una categoría de severidad y {diagnoses['n']} con más de una categoría de diagnóstico primario.
- Comparando solo la fila más temprana con la más reciente, {endpoint_changes['n']}/{endpoint_changes['denominator']} presentan categorías distintas; {middle_wording} variación intermedia aunque las etiquetas de los extremos coincidan.
- {timestamp_rows['n']} filas de carrera ({timestamp_rows['percent']:.1f}%) tienen timestamps presentes pero distintos entre `datestring` y la fecha del nombre de archivo. Afectan a {timestamp_people['n']} personas; {repeat_timestamp['n']} de las {repeat_timestamp['denominator']} personas repetidas.

La fecha elegida por el proyecto prioriza `datestring` y usa el nombre del archivo cuando la fecha del CSV falta. La comprobación anterior encontró que usar la fecha del nombre de archivo no cambia qué archivo es el primer registro de carrera seleccionado en las 1.402 personas. Eso no convierte los timestamps en visitas clínicas verificadas.

## Estabilidad de categorías entre los registros de cada persona repetida

| Campo | Una categoría | Más de una | Personas con más de una |
| --- | ---: | ---: | ---: |
{chr(10).join(stability_rows)}

## Estado en el registro más temprano frente al más reciente

El orden usa el timestamp preferido por la auditoría de fuente, con `filename` como desempate. La tabla cuenta personas repetidas; no representa transiciones clínicas confirmadas ni incidencia.

{markdown_matrix(matrix)}

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
.venv\\Scripts\\python.exe scripts\\audit_repeated_record_labels.py
```

El script lee los CSV locales de origen y produce solo tablas agregadas, sin identificadores individuales. Los datos originales y el código oficial se citan conforme a [atribución y licencias](../docs/attribution_and_licensing.md).
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    running = load_running()
    summary, matrix, stability = audit(running)
    write_report(running, summary, matrix, stability)
    for path in (SUMMARY_PATH, ENDPOINT_PATH, STABILITY_PATH, REPORT_PATH):
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
