"""Create non-inferential, aggregate descriptions of the fixed 30-runner pilot.

Inputs are the locally processed pilot table and the source feature registry.
Outputs contain no participant identifiers or row-level measurements.
All feature values remain the dataset's source-provided dv_r summaries; this
script does not reconstruct gait or validate touchdown/toe-off events.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PILOT_PATH = ROOT / "data" / "processed" / "pilot_features_wide.csv"
REGISTRY_PATH = ROOT / "reports" / "tables" / "pilot_feature_registry.csv"
SUMMARY_PATH = ROOT / "reports" / "tables" / "pilot_descriptive_summary.csv"
PAIRED_PATH = ROOT / "reports" / "tables" / "pilot_spatiotemporal_paired.csv"
FIGURE_PATH = ROOT / "reports" / "figures" / "pilot_speed_descriptives.png"
REPORT_PATH = ROOT / "reports" / "milestone_02_1_pilot_descriptives.md"

SPATIOTEMPORAL = ("STRIDE_RATE", "STRIDE_LENGTH", "STANCE_TIME", "SWING_TIME")
SIDE_COLORS = {"left": "#2b7a78", "right": "#c05a43"}


def quantile(values: pd.Series, probability: float) -> float:
    return float(values.quantile(probability, interpolation="linear"))


def format_number(value: float, digits: int = 2) -> str:
    return "—" if not np.isfinite(value) else f"{value:.{digits}f}"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not PILOT_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {PILOT_PATH}. Acquire and process the fixed pilot first."
        )
    if not REGISTRY_PATH.is_file():
        raise FileNotFoundError(f"Missing feature registry: {REGISTRY_PATH}")
    pilot = pd.read_csv(PILOT_PATH)
    registry = pd.read_csv(REGISTRY_PATH)
    required = {"participant_id", "injury_status", "speed_m_s", "qc_status"}
    missing = required - set(pilot.columns)
    if missing:
        raise ValueError(f"Pilot table is missing required fields: {sorted(missing)}")
    if len(pilot) != 30 or pilot["participant_id"].nunique() != 30:
        raise ValueError("Expected the fixed 30-person pilot with one row per person.")
    if pilot["injury_status"].value_counts().to_dict() != {
        "healthy": 15,
        "injured": 15,
    }:
        raise ValueError("Pilot labels differ from the fixed 15/15 engineering sample.")
    if not pilot["qc_status"].eq("structural_pass").all():
        raise ValueError("Pilot structural status changed; review before summarizing.")
    if len(registry) != 13 or registry["feature"].duplicated().any():
        raise ValueError("Expected 13 unique features in the pinned registry.")
    return pilot, registry


def build_tables(pilot: pd.DataFrame, registry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, object]] = []
    paired_rows: list[dict[str, object]] = []

    for feature in registry.itertuples(index=False):
        for side in ("left", "right"):
            column = f"{side}__{feature.feature}"
            if column not in pilot:
                raise ValueError(f"Missing expected feature column: {column}")
            values = pd.to_numeric(pilot[column], errors="coerce")
            values = values[np.isfinite(values)]
            summary_rows.append(
                {
                    "feature": feature.feature,
                    "domain": feature.domain,
                    "unit": feature.unit,
                    "phase": feature.phase,
                    "side": side,
                    "n": int(values.size),
                    "median": quantile(values, 0.50) if values.size else np.nan,
                    "q1": quantile(values, 0.25) if values.size else np.nan,
                    "q3": quantile(values, 0.75) if values.size else np.nan,
                    "minimum": float(values.min()) if values.size else np.nan,
                    "maximum": float(values.max()) if values.size else np.nan,
                    "source": "source-provided dv_r summary; not independently reprocessed",
                }
            )

        if feature.feature in SPATIOTEMPORAL:
            paired = pd.DataFrame(
                {
                    "left": pd.to_numeric(pilot[f"left__{feature.feature}"], errors="coerce"),
                    "right": pd.to_numeric(pilot[f"right__{feature.feature}"], errors="coerce"),
                }
            ).dropna()
            difference = paired["left"] - paired["right"]
            paired_rows.append(
                {
                    "feature": feature.feature,
                    "unit": feature.unit,
                    "paired_n": len(paired),
                    "median_left_minus_right": float(difference.median()),
                    "median_absolute_side_difference": float(difference.abs().median()),
                    "q1_absolute_side_difference": float(difference.abs().quantile(0.25)),
                    "q3_absolute_side_difference": float(difference.abs().quantile(0.75)),
                    "interpretation": "descriptive within-person side difference; not a validated asymmetry measure",
                }
            )

    summary = pd.DataFrame(summary_rows)
    paired_summary = pd.DataFrame(paired_rows)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_PATH, index=False, float_format="%.6g")
    paired_summary.to_csv(PAIRED_PATH, index=False, float_format="%.6g")
    return summary, paired_summary


def build_figure(pilot: pd.DataFrame, registry: pd.DataFrame) -> None:
    feature_meta = registry.set_index("feature")
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.4), constrained_layout=True)
    fig.suptitle(
        "Speed and source-provided spatiotemporal summaries · technical pilot (n=30)",
        fontsize=13,
        fontweight="bold",
    )
    x = pd.to_numeric(pilot["speed_m_s"], errors="coerce")

    for axis, feature_name in zip(axes.flat, SPATIOTEMPORAL, strict=True):
        feature = feature_meta.loc[feature_name]
        left = pd.to_numeric(pilot[f"left__{feature_name}"], errors="coerce")
        right = pd.to_numeric(pilot[f"right__{feature_name}"], errors="coerce")
        complete = x.notna() & left.notna() & right.notna()
        for index in np.flatnonzero(complete.to_numpy()):
            axis.plot(
                [x.iloc[index], x.iloc[index]],
                [left.iloc[index], right.iloc[index]],
                color="#9ba5a1",
                alpha=0.36,
                linewidth=0.75,
                zorder=1,
            )
        axis.scatter(
            x[complete], left[complete], s=24, marker="o", color=SIDE_COLORS["left"],
            label="Left", alpha=0.82, zorder=2,
        )
        axis.scatter(
            x[complete], right[complete], s=25, marker="^", color=SIDE_COLORS["right"],
            label="Right", alpha=0.82, zorder=2,
        )
        axis.set_title(feature_name.replace("_", " ").title(), loc="left", fontsize=10)
        axis.set_xlabel("Treadmill speed (m/s)")
        axis.set_ylabel(f"{feature.unit} · source summary")
        axis.grid(axis="both", color="#dfe4e1", linewidth=0.7)
        axis.spines[["top", "right"]].set_visible(False)
        axis.legend(frameon=False, ncol=2, loc="best", fontsize=8)

    fig.text(
        0.5,
        -0.015,
        "Paired side values from 30 deliberately selected participants. Descriptive only; "
        "no injury-group test. Events, cycles and source-summary parity remain unverified.",
        ha="center",
        fontsize=8.5,
        color="#46534e",
    )
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_PATH, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_report(pilot: pd.DataFrame, summary: pd.DataFrame, paired: pd.DataFrame) -> None:
    rows = []
    for feature in summary["feature"].drop_duplicates():
        sides = summary[summary["feature"] == feature].set_index("side")
        unit = str(sides.iloc[0]["unit"])
        rows.append(
            "| {feature} | {unit} | {ln} | {lm} [{lq1}, {lq3}] | {rn} | {rm} [{rq1}, {rq3}] |".format(
                feature=feature,
                unit=unit,
                ln=int(sides.loc["left", "n"]),
                lm=format_number(sides.loc["left", "median"]),
                lq1=format_number(sides.loc["left", "q1"]),
                lq3=format_number(sides.loc["left", "q3"]),
                rn=int(sides.loc["right", "n"]),
                rm=format_number(sides.loc["right", "median"]),
                rq1=format_number(sides.loc["right", "q1"]),
                rq3=format_number(sides.loc["right", "q3"]),
            )
        )

    paired_rows = [
        "| {feature} | {n} | {signed} {unit} | {absolute} {unit} [{q1}, {q3}] |".format(
            feature=row.feature,
            n=int(row.paired_n),
            signed=format_number(row.median_left_minus_right, 3),
            absolute=format_number(row.median_absolute_side_difference, 3),
            q1=format_number(row.q1_absolute_side_difference, 3),
            q3=format_number(row.q3_absolute_side_difference, 3),
            unit=row.unit,
        )
        for row in paired.itertuples(index=False)
    ]

    content = f"""# Hito 2.1 — Descripción exploratoria del piloto disponible

Este avance usa solamente el piloto técnico local de 30 personas (15 controles y 15 corredores con lesión según metadatos) y los 13 resúmenes bilaterales guardados por la fuente. Es una descripción agregada para entender cobertura, escala y dependencia potencial de velocidad; **no es una comparación clínica de grupos ni una validación biomecánica**.

## Qué muestran estos archivos

- {len(pilot)} personas, una fila por persona; {len(summary)} combinaciones de variable y lado resumidas.
- Cada estadístico procede de `dv_r` en los JSON originales. No recalcula cinemática ni reconstruye ciclos.
- Los 30 ensayos pasaron QC estructural. El recuento de eventos/ciclos utilizables sigue sin establecerse.
- La tabla presenta mediana y rango intercuartílico (Q1–Q3) por lado; las variables angulares conservan signos y convenciones de la fuente.
- El gráfico enlaza los valores izquierdo/derecho de cada participante para cuatro variables espaciotemporales y muestra su velocidad. No identifica participantes ni codifica su estado de lesión.

## Resúmenes por lado

| Variable fuente | Unidad | n izq. | Mediana izq. [Q1, Q3] | n der. | Mediana der. [Q1, Q3] |
| --- | --- | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

## Diferencias pareadas espaciotemporales

Las diferencias izquierda–derecha se muestran solo para variables espaciotemporales con unidad compartida. No se etiquetan como asimetría clínica. Para los ángulos no se calcula un índice bilateral porque la interpretación debe respetar las transformaciones y signos específicos de cada variable en el código fuente.

| Variable | Pares | Mediana izq. − der. | Diferencia absoluta mediana [Q1, Q3] |
| --- | ---: | ---: | ---: |
{chr(10).join(paired_rows)}

## Relación descriptiva con velocidad

![Relación entre velocidad y resúmenes espaciotemporales](figures/pilot_speed_descriptives.png)

La figura ayuda a ver si la velocidad acompaña cambios en zancada, apoyo o balanceo dentro de este piloto pequeño. Los dos lados de cada persona son observaciones emparejadas; no deben contarse como 60 personas. La selección 15/15 y las diferencias de velocidad del marco de cohorte limitan cualquier lectura conjunta. No se ajustan modelos, no se calculan valores p y no se formula una conclusión sobre lesión.

## Qué puede y qué no puede concluirse

Este análisis permite describir qué valores fuente están disponibles y planear una siguiente comprobación. No confirma que los eventos touchdown/toe-off o los ciclos retenidos sean correctos; tampoco garantiza que los resúmenes fueran producidos por la misma versión de código que se inspeccionó. Por ello no establece diferencias por lesión, fenotipos, umbrales clínicos o riesgo futuro.

La prioridad científica sigue siendo ejecutar el flujo oficial y comparar eventos, ciclos retenidos y resúmenes en los mismos archivos. Después, si el QC lo permite, se podrá decidir qué parte de la cohorte tiene cobertura biomecánica suficiente.

## Reproducibilidad y atribución

Regenerar este informe y sus tablas/figura desde la raíz del repositorio:

```powershell
.venv\\Scripts\\python.exe scripts\\summarize_pilot_descriptives.py
```

Los datos y definiciones de origen corresponden a Ferber et al., *Running Injury Clinic Kinematic Dataset*, v1 (2024), DOI [10.25452/figshare.plus.24255795.v1](https://doi.org/10.25452/figshare.plus.24255795.v1), CC BY 4.0. Los valores son resúmenes derivados del dataset y se mantienen atribuidos; no se vuelven a publicar filas ni identificadores en esta descripción agregada. Véase la [revisión metodológica del piloto](milestone_02_pilot_summary.md) y el [estado de la validación oficial pendiente](milestone_03_official_events_validation.md).

### Archivos generados

- `reports/tables/pilot_descriptive_summary.csv`
- `reports/tables/pilot_spatiotemporal_paired.csv`
- `reports/figures/pilot_speed_descriptives.png`
"""
    REPORT_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    pilot, registry = load_inputs()
    summary, paired = build_tables(pilot, registry)
    build_figure(pilot, registry)
    write_report(pilot, summary, paired)
    print(f"Wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"Wrote {PAIRED_PATH.relative_to(ROOT)}")
    print(f"Wrote {FIGURE_PATH.relative_to(ROOT)}")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
