"""Audit cohort readiness and prepare a small pilot manifest, entirely offline."""
from pathlib import Path
import json
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.load_metadata import load_metadata, first_observation, NO_INJURY
from src.data.validation import add_quality_flags, build_cohort
from src.data.load_trials import locate_trial
from src.analysis.metadata_summary import markdown_table
from src.analysis.cohort_readiness import group_balance, covariate_availability, label_sensitivity, selected_diagnosis_feasibility, plan_pilot


def main():
    output = ROOT / "reports/tables"
    df = add_quality_flags(load_metadata(ROOT / "data/raw"))
    run = df[df.task.eq("running")]
    first = first_observation(run)
    index = {r["filename"]: r for r in json.loads((ROOT / "data/interim/provenance/ric_data_index.json").read_text()) if r["filename"].endswith(".json")}
    cohort = build_cohort(df, set(index))
    candidate = first_observation(cohort[cohort.candidate_included])
    balance = group_balance(candidate)
    retention, unavailable, reasons = covariate_availability(candidate)
    sensitivity = label_sensitivity(df, set(index))
    diagnosis = selected_diagnosis_feasibility(run, candidate)
    queue = first[first.injury_status.isin(["unknown", "discordant"])].copy()
    queue["later_eligible_record_exists"] = queue.participant_id.isin(set(candidate.participant_id))
    queue["review_reason"] = queue.apply(lambda r: ";".join(reason for flag, reason in [
        (r.severity == "unknown", "missing_or_unrecognized_severity"),
        (r.severity == "no_injury" and r.joint not in NO_INJURY, "no_injury_severity_with_primary_site"),
        (r.severity == "no_injury" and r.diagnosis not in NO_INJURY, "no_injury_severity_with_primary_text"),
        (r.severity == "no_injury" and r.joint_secondary not in NO_INJURY, "no_injury_severity_with_secondary_site"),
        (r.severity == "no_injury" and r.diagnosis_secondary not in NO_INJURY, "no_injury_severity_with_secondary_text"),
    ] if flag), axis=1)
    queue = queue[["participant_id", "filename", "InjDefn", "InjJoint", "SpecInjury", "InjJoint2", "SpecInjury2", "injury_status", "review_reason", "later_eligible_record_exists"]]
    speed = candidate.groupby("injury_status").speed_m_s.agg(["count", "mean", "std", "min", "max"])
    h = candidate.loc[candidate.injury_status.eq("healthy"), "speed_m_s"].astype(float)
    i = candidate.loc[candidate.injury_status.eq("injured"), "speed_m_s"].astype(float)
    lower = max(h.quantile(.05), i.quantile(.05))
    upper = min(h.quantile(.95), i.quantile(.95))
    support = pd.DataFrame([{"injury_status": status, "participants": len(values),
                             "inside_shared_central_range": int(values.between(lower, upper).sum()),
                             "inside_percent": 100 * values.between(lower, upper).mean(),
                             "central_lower_m_s": lower, "central_upper_m_s": upper}
                            for status, values in [("healthy", h), ("injured", i)]])
    pilot = plan_pilot(candidate)
    assert len(pilot) == 30 and pilot.participant_id.nunique() == 30
    pilot["compressed_bytes"] = pilot.archive_member.map(lambda key: index[key]["compressed_size"])
    pilot["uncompressed_bytes"] = pilot.archive_member.map(lambda key: index[key]["size"])
    pilot["already_local"] = pilot.apply(lambda r: locate_trial(ROOT / "data/raw/sample", r.participant_id, r.filename) is not None, axis=1)
    pilot["acquisition_status"] = pilot.already_local.map({True: "already_local_structural_audit_only", False: "planned_not_downloaded"})
    pilot_fields = ["participant_id", "filename", "archive_member", "injury_status", "diagnosis", "diagnosis_secondary", "gender", "speed_m_s", "speed_band", "age_analysis", "adjusted_complete_candidate", "selection_purpose", "compressed_bytes", "uncompressed_bytes", "already_local", "acquisition_status"]
    tables = {"readiness_covariate_balance": balance, "readiness_covariate_retention": retention,
              "readiness_unavailable_covariates": unavailable, "readiness_participant_missingness": reasons,
              "readiness_label_sensitivity": sensitivity, "readiness_diagnosis_feasibility": diagnosis,
              "readiness_injury_review_queue": queue, "readiness_speed_support": support,
              "phase02_pilot_manifest": pilot[pilot_fields]}
    for name, table in tables.items():
        table.to_csv(output / (name + ".csv"), index=False)
    total_expanded = int(retention[retention.covariate_set.eq("expanded_covariates")].available_n.sum())
    total_core = int(retention[retention.covariate_set.eq("core_covariates")].available_n.sum())
    summary = {"candidate_participants": len(candidate), "expanded_complete": total_expanded, "core_complete": total_core,
               "expanded_excluded_percent": 100 * (1 - total_expanded / len(candidate)),
               "first_running_unresolved": len(queue), "later_eligible_records_in_review_queue": int(queue.later_eligible_record_exists.sum()),
               "candidate_speed_healthy_mean": h.mean(), "candidate_speed_injured_mean": i.mean(),
               "pilot_participants": len(pilot), "pilot_already_local": int(pilot.already_local.sum()),
               "pilot_compressed_mb_total": float(pilot.compressed_bytes.sum() / 1e6),
               "pilot_compressed_mb_not_local": float(pilot.loc[~pilot.already_local, "compressed_bytes"].sum() / 1e6),
               "pilot_uncompressed_mb_total": float(pilot.uncompressed_bytes.sum() / 1e6),
               "motion_processed_this_review": False, "primary_cohort_rules_changed": False}
    (output / "readiness_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Descriptive speed and missingness figures; no model or biomechanical comparison.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    bins = [1.1 + .1 * k for k in range(33)]
    axes[0].hist(h, bins=bins, density=True, alpha=.5, label=f"Healthy n={len(h)}", color="#176b87")
    axes[0].hist(i, bins=bins, density=True, alpha=.5, label=f"Injured n={len(i)}", color="#d18448")
    axes[0].set(xlabel="Running speed (m/s)", ylabel="Density", title="Speed distribution in the selected candidate")
    axes[0].legend()
    data = retention[retention.covariate_set.ne("all_candidates")].copy()
    labels = data.injury_status + " / " + data.covariate_set.str.replace("_covariates", "", regex=False)
    bars = axes[1].barh(labels, data.retained_percent, color="#176b87")
    axes[1].bar_label(bars, labels=[f"{v:.1f}%" for v in data.retained_percent], padding=4)
    axes[1].set(xlim=(0, 112), xlabel="Candidates retained (%)", title="Complete covariate availability")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(ROOT / "reports/figures/readiness_balance.png", dpi=160)
    plt.close(fig)
    report = f"""# Qué mejorar y cómo avanzar

Revisión local del Hito 1, 25 de octubre de 2026. Se mantiene la definición primaria de cohorte y no se procesan nuevos datos de movimiento. Ejecutar `python scripts/review_readiness.py` para regenerar esta revisión y la selección propuesta.

## 1. Resolver la comparabilidad antes de interpretar cinemática

En los {len(candidate)} candidatos seleccionados, la velocidad media es {h.mean():.3f} m/s en controles y {i.mean():.3f} m/s en lesionados. La diferencia observada obliga a examinar la velocidad en las futuras comparaciones; no demuestra qué variable causó la diferencia. La siguiente tabla utiliza una observación por participante y los valores disponibles para cada covariable.

{markdown_table(balance)}

SMD = (media lesionados − media controles) / sqrt((varianza lesionados + varianza controles)/2), usando varianzas muestrales. Es un diagnóstico descriptivo de equilibrio entre grupos, no un efecto biomecánico, un umbral clínico ni una prueba de confusión causal. No se ajusta ningún modelo aquí.

Como sensibilidad descriptiva, la intersección de los intervalos percentil 5–95 de velocidad es {lower:.3f}–{upper:.3f} m/s. No se filtra la cohorte con este intervalo ni se propone como rango clínico.

{markdown_table(support)}

![Velocidad y disponibilidad de covariables](figures/readiness_balance.png)

## 2. Evitar pérdidas automáticas por datos faltantes

Exigir todas las covariables ampliadas conserva {total_expanded}/{len(candidate)} candidatos y deja fuera {100 * (1 - total_expanded / len(candidate)):.1f}%. Un conjunto básico conserva {total_core}, pero su elección debe responder a la pregunta científica y no solamente al tamaño disponible.

{markdown_table(retention)}

Conjunto básico: velocidad, edad, género registrado, altura y peso. Ampliado: añade experiencia y nivel deportivo. No se imputa ni se cambia la cohorte; estas son comparaciones de disponibilidad. Preparar análisis básico/ampliado y estudiar selección por faltantes es preferible a asumir que los casos completos representan automáticamente a todos.

{markdown_table(unavailable)}

Cada participante tiene sus motivos de indisponibilidad en `tables/readiness_participant_missingness.csv`. Un dato registrado como desconocido y un valor numérico descartado por plausibilidad también impiden ciertos ajustes; no son lo mismo que una celda fuente vacía.

## 3. Revisar las etiquetas sin inventar diagnósticos

Hay {len(queue)} primeros registros de carrera desconocidos o discordantes. De ellos, {int(queue.later_eligible_record_exists.sum())} participantes tienen otra observación posterior elegible. La cola `tables/readiness_injury_review_queue.csv` conserva los textos originales y motivos de revisión. Resolverla significa revisar reglas y evidencias disponibles; si no hay evidencia suficiente, el estado sigue sin resolverse.

{markdown_table(sensitivity)}

Los escenarios alternativos se calculan únicamente para sensibilidad. `primary_fields_controls` omite la evidencia secundaria para definir controles; `severity_only_exploratory` ignora conflictos entre campos y usa solo severidad. Ninguno sustituye la regla primaria conservadora ni convierte automáticamente una discrepancia en una persona sana. Los cambios de archivo seleccionado muestran que cambiar la regla también puede cambiar qué episodio entra en el análisis.

## 4. Usar tamaños de diagnóstico de la cohorte realmente seleccionada

Los recuentos históricos de cualquier sesión no deben asumirse como el tamaño disponible para una comparación con una sola observación por participante. En esta revisión, los siete diagnósticos mayores conservan sus recuentos al seleccionar el registro, pero disminuyen al exigir covariables ampliadas completas. Esta tabla incluye campos primarios/secundarios, deduplica persona–diagnóstico y mantiene por separado los casos completos ampliados. Las filas no son sumables.

{markdown_table(diagnosis, 12)}

La marca n≥30 es una ayuda de planificación, no un cálculo de potencia. La muestra utilizable podría disminuir tras QC biomecánico. Antes de elegir contrastes, comprobar tamaño efectivo, diagnósticos concurrentes, lado lesionado y distribución de velocidad. No combinar categorías por conveniencia estadística.

## 5. Próximo avance recomendado: piloto técnico de 30 personas

Se prepara `tables/phase02_pilot_manifest.csv`: 15 controles y 15 lesionados, sin repetir participantes. La selección determinista (semilla 42) rota por estratos de género y terciles de velocidad. En lesionados prioriza hasta dos personas por cada uno de los siete diagnósticos con más participantes y n≥30; cuando queda sitio incluye lesión inespecífica. La selección es intencional para probar la ingestión y cobertura de condiciones, no una muestra representativa ni un estudio de diferencias.

La selección propuesta incluye {int(pilot.already_local.sum())} archivos ya locales. Según el índice del ZIP, los 30 miembros suman {pilot.compressed_bytes.sum()/1e6:.1f} MB comprimidos y {pilot.uncompressed_bytes.sum()/1e6:.1f} MB sin comprimir. Los aún no locales suman aproximadamente {pilot.loc[~pilot.already_local, 'compressed_bytes'].sum()/1e6:.1f} MB comprimidos, más cabeceras y solicitudes HTTP. **El manifiesto no descarga ni procesa esos archivos.** Frecuencia de muestreo y cobertura de marcadores aún no se conocen para la mayoría de la selección; deben verificarse durante el piloto.

Entregables del próximo piloto, tras revisar esta propuesta:

1. Adquisición selectiva con límites por lote, integridad y registro de fallos; no cargar todo el dataset en memoria.
2. Lectura de tutoriales oficiales pertinentes y registro de variables disponibles, unidades, signos, lado y definición temporal. Distinguir variables ya calculadas de las que requieren reconstrucción.
3. QC por archivo y por variable: trayectorias, calibración, eventos, ciclos aprovechables y advertencias del procesamiento oficial. No fijar un mínimo de ciclos sin justificarlo con ese flujo y el objetivo analítico.
4. Una tabla de características verificadas con persona, archivo, lado, nombre, valor, unidad, procedencia y estado QC. Elegir un conjunto pequeño e interpretable de cadera, rodilla y tobillo según lo realmente soportado.
5. Validar el piloto antes de ampliar. Las comparaciones ajustadas, curvas completas, fenotipos y clasificación tendrán etapas posteriores explícitas.

## 6. Uso concreto del complemento

BMC–RIC queda como referencia metodológica para compatibilidad entre laboratorios. No añade diagnósticos ni datos de género y no tiene un crosswalk validado a Calgary. Por ahora aporta un contrato de compatibilidad y un esquema de referencia; no aumenta el denominador ni justifica una validación externa independiente. Priorizaría ahora la calidad de la cohorte y el piloto antes de incorporar otra fuente.

## Decisión de avance

El siguiente hito debe producir características biomecánicas verificadas en una muestra pequeña y un informe QC, manteniendo asociaciones, diagnóstico y predicción futura como conceptos distintos. Esta revisión prepara ese trabajo; no declara validada la cinemática ni inicia ML. La definición primaria y los resultados originales del Hito 1 permanecen como referencia.
"""
    (ROOT / "reports/milestone_01_readiness_review.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(diagnosis.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
