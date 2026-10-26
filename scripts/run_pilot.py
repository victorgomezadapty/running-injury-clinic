"""Process the reviewed 30-person pilot offline, one JSON at a time.

Exports existing upstream scalars with checked definitions/units and explicit
quality limitations. Does not reconstruct joint angles or validate gait events.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
import zlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.load_trials import load_trial
from src.data.load_metadata import load_metadata
from src.biomechanics.feature_registry import build_registry, CODE_RELATIVE
from src.biomechanics.pilot_qc import structural_qc, extract_source_features, numeric_scalar
from src.analysis.metadata_summary import markdown_table


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def extract_tutorial_text():
    folder = ROOT / "data/interim/official_tutorials"
    folder.mkdir(parents=True, exist_ok=True)
    sources = []
    for path in sorted((ROOT / "data/raw/official_code/Supplemental_materials/Tutorials").glob("*.mlx")):
        with zipfile.ZipFile(path) as archive:
            document = ET.fromstring(archive.read("matlab/document.xml"))
            text = "\n".join(document.itertext())
        (folder / (path.stem + ".txt")).write_text(text, encoding="utf-8")
        sources.append({"file": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "reviewed_as": "source XML text; MATLAB notebook not executed"})
    if len(sources) < 2:
        raise ValueError("Acquire official tutorials 1–2 before running the pilot")
    return sources


def main():
    registry, placeholders = build_registry(ROOT)
    tutorial_sources = extract_tutorial_text()
    plan_path = ROOT / "reports/tables/phase02_pilot_manifest.csv"
    plan = pd.read_csv(plan_path, dtype={"participant_id": "string", "filename": "string"})
    acquisition = json.loads((ROOT / "data/interim/provenance/pilot_acquisition.json").read_text())
    if acquisition["manifest_sha256"] != sha256_file(plan_path):
        raise ValueError("Pilot manifest changed since acquisition; retain the reviewed version")
    acquired = {(r["participant_id"], r["filename"]): r for r in acquisition["records"]}
    if len(plan) != 30 or plan.participant_id.nunique() != 30:
        raise ValueError("Expected the reviewed 30-person pilot")
    metadata = load_metadata(ROOT / "data/raw")
    metadata = metadata[metadata.task.eq("running")]
    merged = plan.merge(metadata[["participant_id", "filename", "injury_side", "joint", "severity"]], on=["participant_id", "filename"], how="left", validate="one_to_one", indicator=True)
    if not merged._merge.eq("both").all():
        raise ValueError("Pilot contains an observation with no exact metadata link")
    processed, tables = ROOT / "data/processed", ROOT / "reports/tables"
    cache = ROOT / "data/interim/pilot_feature_cache"
    cache.mkdir(parents=True, exist_ok=True)
    schema_payload = {"registry": registry, "placeholder_fields": placeholders,
                      "implementation_sha256": {p: sha256_file(ROOT / p) for p in ["src/data/load_trials.py", "src/biomechanics/feature_registry.py", "src/biomechanics/pilot_qc.py", "scripts/run_pilot.py"]},
                      "metadata_sha256": sha256_file(ROOT / "data/raw/run_data_meta.csv")}
    schema_sha = hashlib.sha256(json.dumps(schema_payload, sort_keys=True).encode()).hexdigest()
    long, trials, geometry, consistency, inventory, provenance, details = [], [], [], [], [], [], []
    for row in merged.itertuples():
        source = acquired.get((row.participant_id, row.filename))
        if not source or source["status"] != "verified":
            raise ValueError("Pilot acquisition is incomplete")
        path = ROOT / source["path"]
        raw_sha = sha256_file(path)
        if raw_sha != source["sha256"]:
            raise ValueError(f"Raw pilot source changed: {path}")
        key = hashlib.sha256(f"{raw_sha}:{schema_sha}:{row.speed_m_s}".encode()).hexdigest()
        cache_path = cache / (key + ".json")
        hit = cache_path.exists()
        if hit:
            result = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            data = load_trial(path)
            qc = structural_qc(data, path)
            qc["audit"]["file"] = path.relative_to(ROOT).as_posix()
            features, temporal = extract_source_features(data, registry, qc["status"], float(row.speed_m_s))
            variables = []
            dv = data.get("dv_r")
            if isinstance(dv, dict):
                for side, values in dv.items():
                    if isinstance(values, dict):
                        for name, value in values.items():
                            variables.append({"side": side, "source_field": name, "numeric_finite_scalar": numeric_scalar(value),
                                              "source_value": value if numeric_scalar(value) else None,
                                              "zero_value": numeric_scalar(value) and value == 0,
                                              "unassigned_in_current_official_code": name in placeholders,
                                              "selected_in_registry": name in {r["feature"] for r in registry}})
            result = json_safe({"qc": qc, "features": features, "temporal": temporal, "variables": variables})
            cache_path.write_text(json.dumps(result, allow_nan=False), encoding="utf-8")
            del data
        identity = {"participant_id": row.participant_id, "filename": row.filename}
        for feature in result["features"]:
            long.append({**identity, "injury_status": row.injury_status, **feature, "source_path": source["path"],
                         "source_sha256": raw_sha, "registry_sha256": schema_sha, "pipeline_cache_key": key})
        qc = result["qc"]
        trial = {**identity, "injury_status": row.injury_status, "gender": row.gender, "speed_m_s": row.speed_m_s,
                 "injury_side_recorded": row.injury_side, "joint_recorded": row.joint, "qc_status": qc["status"],
                 "qc_flags": ";".join(qc["flags"]), "sampling_hz": qc["sampling_hz"], "frames": qc["frames"],
                 "time_span_s": qc["time_span_s"], "tracking_markers": qc["tracking_markers"],
                 "static_anatomical_fields": len(qc["audit"]["static_anatomical"]),
                 "source_feature_slots": len(result["features"]),
                 "provisionally_available_slots": sum(r["provisionally_available"] for r in result["features"]),
                 "temporal_review_sides": sum(r["review_required"] for r in result["temporal"]),
                 "events_qc": qc["events_qc"], "valid_cycle_count": None,
                 "embedded_qc_fields_found": len(qc["audit"]["embedded_qc_fields"]), "cache_hit": hit}
        trials.append(trial)
        geometry += [{**identity, **g} for g in qc["geometry"]]
        consistency += [{**identity, **r} for r in result["temporal"]]
        inventory += [{**identity, **v} for v in result["variables"]]
        provenance.append({**identity, **source, "cache_key": key, "cache_hit": hit})
        details.append({**identity, "qc": qc})
        print(f"Processed {row.participant_id}: {trial['qc_status']}; available {trial['provisionally_available_slots']}/26; cache={hit}", flush=True)
    features, qc_table, variable_table = pd.DataFrame(long), pd.DataFrame(trials), pd.DataFrame(inventory)
    if len(features) != 30 * 2 * len(registry) or features.duplicated(["participant_id", "filename", "side", "feature"]).any():
        raise AssertionError("Feature slot count or participant-side identity failed")
    features.to_csv(processed / "pilot_features_long.csv", index=False)
    features["feature_column"] = features.side + "__" + features.feature
    wide = features.pivot(index=["participant_id", "filename"], columns="feature_column", values="analysis_value").reset_index()
    wide = qc_table.drop(columns=["cache_hit"]).merge(wide, on=["participant_id", "filename"], validate="one_to_one")
    wide.to_csv(processed / "pilot_features_wide.csv", index=False)
    qc_table.to_csv(tables / "pilot_qc_trials.csv", index=False)
    pd.DataFrame(geometry).to_csv(tables / "pilot_qc_geometry.csv", index=False)
    pd.DataFrame(consistency).to_csv(tables / "pilot_temporal_consistency.csv", index=False)
    variable_table.to_csv(tables / "pilot_stored_variable_inventory.csv", index=False)
    pd.DataFrame(provenance).to_csv(tables / "pilot_acquisition_status.csv", index=False)
    pd.DataFrame(registry).to_csv(tables / "pilot_feature_registry.csv", index=False)
    pd.DataFrame(registry).to_csv(ROOT / "handoff/pilot_feature_catalog.csv", index=False)
    coverage = features.groupby(["feature", "unit"], sort=False).agg(expected_slots=("side", "size"), finite_source_values=("value", "count"), available_slots=("provisionally_available", "sum"), zero_source_values=("value", lambda x: int(x.eq(0).sum()))).reset_index()
    coverage.to_csv(tables / "pilot_feature_coverage.csv", index=False)
    (ROOT / "data/interim/pilot_qc_details.json").write_text(json.dumps(json_safe(details), indent=2, allow_nan=False), encoding="utf-8")
    summary = {"participants": len(qc_table), "healthy": int(qc_table.injury_status.eq("healthy").sum()),
               "injured": int(qc_table.injury_status.eq("injured").sum()), "features_per_side": len(registry),
               "expected_bilateral_slots": len(features), "finite_source_values": int(features.value.notna().sum()),
               "provisionally_available_values": int(features.provisionally_available.sum()),
               "structural_pass_trials": int(qc_table.qc_status.eq("structural_pass").sum()),
               "trials_with_temporal_review": int(qc_table.temporal_review_sides.gt(0).sum()),
               "cache_hits": int(qc_table.cache_hit.sum()), "placeholder_names_identified_in_source": len(placeholders),
               "observed_placeholder_records": int(variable_table.unassigned_in_current_official_code.sum()),
               "nonzero_placeholder_records": int((variable_table.unassigned_in_current_official_code & ~variable_table.zero_value).sum()),
               "independently_validated_events_trials": 0, "fully_biomechanically_usable_running_count": None,
               "registry_sha256": schema_sha, "pilot_manifest_sha256": acquisition["manifest_sha256"],
               "official_tutorials": tutorial_sources,
               "method": "source scalar extraction and structural/internal-consistency QC; no joint-angle reconstruction, waveform inference or ML"}
    (tables / "pilot_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Technical quality figures, with no injury-group biomechanical comparisons.
    fig = plt.figure(figsize=(14, 7), layout="constrained")
    grid = fig.add_gridspec(2, 2, width_ratios=[1, 1.8])
    a, b, c = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[:, 1])
    rates = qc_table.sampling_hz.value_counts().sort_index()
    bars = a.bar(rates.index.astype(str), rates.values, color="#176b87")
    a.bar_label(bars, padding=3)
    a.set(xlabel="Source sampling frequency (Hz)", ylabel="Trials", title="Pilot acquisition coverage")
    b.hist(qc_table.time_span_s.dropna(), bins=12, color="#176b87", edgecolor="white")
    b.set(xlabel="Recorded time span (s)", ylabel="Trials", title="Recording duration")
    plot = coverage.iloc[::-1]
    c.barh(plot.feature.str.replace("_", " "), plot.expected_slots, color="#d9e3e8", label="Expected slots")
    c.barh(plot.feature.str.replace("_", " "), plot.available_slots, color="#176b87", label="Provisional source values")
    c.set(xlabel="Left/right feature slots, 30 participants", xlim=(0, 65), title="Source features after technical checks")
    c.legend(loc="upper center", bbox_to_anchor=(.5, -.10), ncol=2, frameon=False)
    for ax in [a, b, c]:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Technical pilot · source-defined values · gait-event validity remains unverified", fontsize=13)
    fig.savefig(ROOT / "reports/figures/pilot_quality_overview.png", dpi=160)
    plt.close(fig)
    report = f"""# Hito 2 — Piloto técnico de características biomecánicas

Sports Rehabilitation & Human Performance · Running Biomechanics & Injury Phenotyping

Se adquirieron y revisaron {len(qc_table)} JSON de la selección previamente definida: {summary['healthy']} controles y {summary['injured']} corredores con lesión según la regla de metadatos. La muestra es intencional para comprobar el procesamiento; no estima prevalencia ni diferencias clínicas entre grupos. Se utiliza una observación por participante y se mantiene la identidad persona–archivo–lado.

## Resultado del piloto

{markdown_table(pd.DataFrame([{'metric': k, 'value': summary[k]} for k in ['participants', 'features_per_side', 'expected_bilateral_slots', 'finite_source_values', 'provisionally_available_values', 'structural_pass_trials', 'trials_with_temporal_review', 'placeholder_names_identified_in_source', 'observed_placeholder_records', 'nonzero_placeholder_records', 'independently_validated_events_trials']]))}

Los {len(registry)} tipos de características producen 26 columnas bilaterales, además de identificadores y campos QC. Los valores finitos de la tabla larga se conservan como los entrega `dv_r`, incluso si requieren revisión. `analysis_value` enmascara campos ausentes/no finitos, tiempos o tasas no positivos, ángulos exactamente cero pendientes de revisión, observaciones con alertas estructurales y lados con una alerta de coherencia temporal. Un cero angular no se declara automáticamente un error: se retiene y queda pendiente de revisión.

**El piloto verifica adquisición, esquema, vínculo con metadatos, definiciones/unidades documentadas y consistencia técnica. No equivale a una validación biomecánica completa.** El número de observaciones con eventos/ciclos plenamente validados continúa sin establecerse.

![Calidad del piloto](figures/pilot_quality_overview.png)

## Qué características están documentadas

{markdown_table(pd.DataFrame(registry)[['feature', 'domain', 'unit', 'phase', 'source_line_start', 'source_line_end']])}

El catálogo completo, con expresiones exactas y SHA-256 del código, está en `tables/pilot_feature_registry.csv` y `../handoff/pilot_feature_catalog.csv`. Se revisaron los tutoriales oficiales 1 y 2, además de `gait_steps.m` y `gait_kinematics.m`; sus originales permanecen intactos y las copias de texto extraídas están en `data/interim/official_tutorials/`.

## Hallazgos metodológicos que cambian cómo interpretar los datos

1. La normalización oficial de estas curvas va de touchdown a toe-off: 101 puntos de **apoyo**, no de todo el ciclo. La flexión máxima de rodilla usa los primeros 70 puntos; la aducción máxima de cadera, los primeros 60. No se sustituyen por picos globales.
2. `STRIDE_RATE` representa zancadas/minuto por lado. Aunque el tutorial usa nombres temporales terminados en `_hz`, sus etiquetas y la fórmula `60*hz/diff(TD)` confirman la unidad. No se trata como pasos/minuto o Hz.
3. Los ángulos salen en grados del código de cinemática. Se preservan los signos originales; por ejemplo, la definición de flexión de rodilla incluye un signo negativo. No se aplica valor absoluto ni una conversión automática de rotación interna/externa.
4. La matriz oficial se inicializa en cero y deja {len(placeholders)} nombres de campo sin asignación en el código revisado. Esos campos no entran en la selección; un cero reservado no es una medición normal. La coincidencia con el código actual no demuestra qué versión produjo cada JSON histórico.
5. Los valores exportados son los resúmenes originales, no máximos recalculados de marcadores ni valores individuales de cada ciclo. Los eventos retenidos, sus advertencias y el número válido de ciclos no aparecen como salidas verificadas en estos JSON.

## Calidad por archivo y trazabilidad

{markdown_table(qc_table[['participant_id', 'qc_status', 'sampling_hz', 'time_span_s', 'provisionally_available_slots', 'temporal_review_sides']])}

Cada archivo se comprueba contra la adquisición mediante SHA-256; la adquisición valida además tamaño y CRC del miembro ZIP. Se examinan marcadores requeridos, formas, frames, frecuencia, valores no finitos/cero, vectores estáticos, pares anatómicos coincidentes y geometría no colineal de clusters. La variación de distancias entre marcadores rígidos se describe mediante MAD relativa; 5% es un disparador técnico de revisión, no un umbral clínico validado. La coherencia entre duración de apoyo/balanceo, tasa de zancada, longitud y velocidad se revisa también al 5%; medianas agregadas pueden no obedecer exactamente las identidades. No se corrigen los originales para hacerlas coincidir.

La caché por archivo incorpora SHA-256 del JSON, código de extracción/QC, definiciones oficiales, metadatos y velocidad vinculada. Permite repetir la exportación sin volver a parsear trayectorias, invalidándose cuando cambian sus dependencias. Los JSON se procesan secuencialmente y los archivos completos del dataset no se descargan.

## Archivos entregados

- [Tabla larga con valores originales, unidades y QC](../data/processed/pilot_features_long.csv).
- [Matriz bilateral con valores provisionalmente disponibles](../data/processed/pilot_features_wide.csv).
- [QC por archivo](tables/pilot_qc_trials.csv), [coherencia temporal](tables/pilot_temporal_consistency.csv) y [geometría de clusters](tables/pilot_qc_geometry.csv).
- [Inventario completo de campos almacenados](tables/pilot_stored_variable_inventory.csv) y [cobertura de la selección](tables/pilot_feature_coverage.csv).
- [Procedencia de la adquisición y caché](tables/pilot_acquisition_status.csv).

## Qué falta antes de ampliar o comparar grupos

Ejecutar el procesamiento oficial en un entorno MATLAB compatible, o validar una implementación equivalente contra salidas oficiales, es necesario para verificar reconstrucción, eventos, advertencias y ciclos aprovechables. Los tutoriales se inspeccionaron, no se ejecutaron en MATLAB. No se inventa un número de ciclos a partir de tasa × duración ni se declara completado ese QC.

Mantener las observaciones con advertencias en una cola de revisión y definir la política de ciclos/variables con evidencia. Después, revisar velocidad/edad y datos faltantes antes de comparaciones ajustadas con tamaños de efecto e incertidumbre. Esta muestra técnica no sustenta inferencia de diferencias entre diagnósticos, fenotipos clínicos, diagnóstico automático o predicción futura. BMC–RIC permanece separado y no valida la independencia del piloto.

No se ha reconstruido cinemática, ajustado modelos de lesión, realizado clustering ni llevado a cabo inferencia de curvas. El siguiente paso recomendado es la validación de eventos y paridad con el procesamiento oficial, antes de procesar la cohorte completa.
"""
    (ROOT / "reports/milestone_02_pilot_summary.md").write_text(report, encoding="utf-8")
    (ROOT / "handoff/pilot_findings.md").write_text(
        "# Technical pilot handoff\n\n" + markdown_table(pd.DataFrame([{"metric": k, "value": summary[k]} for k in ["participants", "features_per_side", "finite_source_values", "provisionally_available_values", "structural_pass_trials", "observed_placeholder_records", "independently_validated_events_trials"]])) +
        "\n\nValues are existing upstream dv_r scalars, preserved without sign changes. Definitions and units are checked against official source code; events, usable cycles and independent reconstruction parity remain unverified. See ../reports/milestone_02_pilot_summary.md, pilot_feature_catalog.csv and ../docs/official_processing_review.md.\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
