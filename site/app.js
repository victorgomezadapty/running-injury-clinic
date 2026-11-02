const copy = {
  es: {
    skip:"Saltar al contenido",navStudy:"El estudio",navEvidence:"Evidencia",navMethods:"Métodos",navReproduce:"Reproducir",
    eyebrow:"REHABILITACIÓN DEPORTIVA · RENDIMIENTO HUMANO",heroTitle:"Cuando una persona se lesiona al correr, ¿qué nos dice su movimiento?",heroLead:"Una lectura prudente de la biomecánica de carrera y del estado actual de lesión: qué permiten afirmar los datos y dónde están sus límites.",explore:"Explorar el estudio",viewCode:"Ver código reproducible",scopeStamp:"Fenotipado transversal · no predice lesiones futuras",motionLab:"LABORATORIO DE MOVIMIENTO / 01",phaseLabel:"FASE ILUSTRATIVA",illustrationNote:"Ilustración conceptual · no representa ondas ni eventos de participantes",datasetSource:"RUNNING INJURY CLINIC KINEMATIC DATASET · FIGSHARE v1",
    snapshot:"EL DATASET",snapshotCopy:"Un archivo público amplio; un piloto técnico deliberadamente pequeño.",people:"personas en el dataset fuente",runningPeople:"con observaciones de carrera",pilotPeople:"personas en el piloto técnico",eventPending:"VALIDACIÓN DE EVENTOS PENDIENTE",fullQc:"Aún no se ha establecido un recuento completo de ciclos utilizables.",sectionQuestion:"DEL MOVIMIENTO AL FENOTIPO",studyEyebrow:"PREGUNTA DE INVESTIGACIÓN",studyTitle:"¿Qué patrones de carrera se asocian con el estado <em>actual</em> de lesión?",studyLead:"El proyecto organiza etiquetas de lesión reportadas y cinemática en cinta en un flujo transparente a nivel de participante. Empieza con resúmenes proporcionados por la fuente y una auditoría técnica reproducible.",studyLimit:"El piloto describe disponibilidad y calidad estructural. Todavía no estima asociaciones biomecánicas entre grupos.",
    cohortEyebrow:"QUIÉN ENTRA EN EL ANÁLISIS",cohortTitle:"Una etiqueta actual no cuenta toda la historia clínica.",cohortCopy:"La cohorte candidata usa reglas explícitas de estado y disponibilidad. No equivale a una cohorte clínica revisada independientemente.",candidateLabel:"COHORTE CANDIDATA",candidateMeans:"1.257 participantes",candidateText:"353 con estado saludable y 904 con estado lesionado bajo las reglas conservadoras de metadatos.",comparisonLabel:"PILOTO TÉCNICO",comparisonValue:"30 participantes",outcomeLabel:"DESENLACE",outcomeValue:"Estado actual reportado",unitLabel:"UNIDAD",unitValue:"Participante; sesiones y ensayos agrupados",healthy:"Saludable",injured:"Lesionado",cohortCaption:"Los conteos describen elegibilidad por metadatos; no son el tamaño de una muestra biomecánica con ciclos validados.",designLabel:"DISEÑO",designValue:"Asociación transversal",sourceLabel:"FUENTE PÚBLICA",sourceText:"participantes únicos en registros de carrera y caminata",pilotLabel:"PILOTO TÉCNICO",pilotText:"15 + 15 archivos para revisar integridad, cobertura de variables y calidad técnica",eventGate:"validación de eventos/ciclos pendiente",
    confounder:"UNA DECISIÓN DE DISEÑO IMPORTANTE",speedTitle:"La velocidad cambia la pregunta.",speedCopy:"Antes de comparar biomecánica, considera a qué velocidad corría cada participante. En la cohorte candidata, la velocidad media difiere entre grupos. Un pequeño estudio experimental también observó cambios asociados a la velocidad en cinemática y cinética de miembros inferiores. La diferencia justifica evaluar ajuste y solapamiento; no demuestra que la velocidad causara la diferencia entre grupos.",readSpeed:"Leer el estudio sobre velocidad",chartNote:"Medias descriptivas de metadatos; no inferencia biomecánica.",sectionMethod:"DE LA FUENTE A LA TRAZABILIDAD",kaggleButton:"Paquete del piloto en Kaggle",
    methodsEyebrow:"MÉTODO EN CAPAS",methodsTitle:"Primero preservar. Después verificar. Luego interpretar.",methodsLead:"Cada etapa conserva trazabilidad entre fuente, selección, valores reportados y decisiones de calidad.",method1Title:"Fijar una fuente reproducible",method1Text:"Dataset Figshare v1, manifiestos con hash y adquisición acotada; sin reescribir originales.",method2Title:"Definir la cohorte antes de analizar",method2Text:"Reglas publicadas para estado actual, observaciones de carrera, velocidad y disponibilidad.",method3Title:"Auditar la estructura del piloto",method3Text:"Comprobar JSON, trayectorias finitas, frecuencia de muestreo y consistencia sin corregir silenciosamente la fuente.",method4Title:"Validar eventos y ciclos",method4Text:"Reejecutar MATLAB oficial y comparar touchdown/toe-off, ciclos normalizados retenidos y resúmenes regenerados antes de ampliar la cohorte.",method4Tag:"EJECUCIÓN MATLAB PENDIENTE",pilotResults:"COMPROBACIONES TÉCNICAS DEL PILOTO · N = 30",sourceScalars:"RESÚMENES DE LA FUENTE",structuralPass:"Archivos que superan comprobaciones estructurales",featureSlots:"Valores bilaterales finitos en el registro seleccionado",validatedCycles:"Registros de eventos/ciclos validados independientemente",pilotResultNote:"Las comprobaciones estructurales no verifican la temporización de eventos ni la validez clínica. Los 780 valores son resúmenes de la fuente.",
    evidenceEyebrow:"QUÉ DICE LA LITERATURA",evidenceTitle:"¿Por qué fenotipar con cuidado?",evidenceLead:"La evidencia es mixta, las definiciones varían y la población importa. El argumento más sólido para este proyecto es formular preguntas específicas y reproducibles, no buscar un marcador universal.",evidenceSynthesis:"REVISIÓN SISTEMÁTICA · 82 ESTUDIOS",evidence1Title:"Una sola medida de marcha no explica las lesiones.",evidence1Text:"Lopes y colaboradores encontraron asociación agrupada solo para la aducción máxima de cadera; el resultado dependía de una pequeña fracción de estudios. También señalaron definiciones y métodos inconsistentes.",evidencePopulation:"LA POBLACIÓN CAMBIA LA SEÑAL",evidence2Title:"Los resultados no se transfieren automáticamente.",evidence2Text:"Una revisión de estudios prospectivos encontró patrones distintos según sexo y nivel competitivo. La evidencia agrupada disponible fue específica para ciertas poblaciones, como corredoras recreativas.",evidenceProspective:"COHORTE PROSPECTIVA · 52 SEMANAS",evidence3Title:"El diagnóstico y el tiempo cambian la pregunta.",evidence3Text:"En 224 corredores recreativos sin lesión, algunos factores basales se asociaron con lesiones diagnosticadas médicamente durante el seguimiento. Este diseño responde algo distinto a comparar el estado actual.",evidenceConfounder:"BIOMECÁNICA · VELOCIDAD",evidence4Title:"Comparar condiciones equivalentes.",evidence4Text:"Cambios experimentales en la velocidad alteran la cinemática y la cinética máximas de cadera, rodilla y tobillo. La velocidad debe formar parte del diseño e interpretación.",evidenceFeasibility:"FACTIBILIDAD · MEDIDAS DE CAMPO",evidence5Title:"Los estudios pequeños sirven si se etiquetan con rigor.",evidence5Text:"Un estudio de sprint de 2025 combinó IMU y medidas de fuerza-velocidad con vigilancia, pero registró solo dos lesiones prospectivas. Se presenta como factibilidad, no como predicción.",discussionTake:"Implicación para el proyecto:",discussionText:"informar definiciones diagnósticas, velocidad, datos faltantes y controles de calidad de eventos antes de estimar asociaciones. Las diferencias exploratorias son hipótesis, no recomendaciones de cribado.",fullReview:"Revisión bibliográfica y estrategia de búsqueda →",
    limitsEyebrow:"LÍMITES DE INTERPRETACIÓN",limitsTitle:"Qué puede decir este proyecto y qué no.",canTitle:"Puede respaldar",can1:"Una descripción auditable de la cohorte candidata y la calidad de datos.",can2:"Asociaciones cuidadosamente definidas y ajustadas por velocidad tras validar eventos.",can3:"Un punto de partida reproducible para hipótesis específicas por diagnóstico.",cannotTitle:"No puede demostrar",cannot1:"Que un patrón de movimiento cause una lesión o prediga lesiones futuras.",cannot2:"Un umbral de cribado validado, diagnóstico clínico o recomendación terapéutica.",cannot3:"Validación externa independiente con un dataset relacionado sin correspondencia verificada de participantes.",
    reproEyebrow:"MÉTODOS ABIERTOS · ATRIBUCIÓN",reproTitle:"Preparado para verificar, citar y ampliar.",reproText:"El archivo original es grande. El repositorio usa adquisición acotada con hashes y un manifiesto fijo. No copia trayectorias brutas de participantes a GitHub. Empieza por la fuente y la guía de reproducción.",repoButton:"Abrir repositorio GitHub",sourceButton:"Dataset original Figshare",licenseTitle:"Dos licencias para dos tipos de material.",licenseText:"El dataset fuente usa CC BY 4.0; sus scripts MATLAB suministrados usan MIT. El código de este proyecto usa MIT. Los valores derivados conservan atribución y una nota explícita de adaptación.",licenseLink:"Detalles de atribución →",reproStack:"RUTA DE REPRODUCCIÓN",matlabGate:"validate_official_events(projectRoot)",pending:"PENDIENTE",immutable:"ENTRADAS BRUTAS · INMUTABLES",reproGateNote:"No ampliar la cohorte hasta ejecutar y revisar el procesador oficial de eventos y ciclos.",footerLine:"Rehabilitación deportiva, ciencia del movimiento y datos reproducibles.",portfolioLink:"Más proyectos en el portafolio de Víctor",footerResearch:"Prototipo de investigación",allReferences:"Bibliografía completa",backTop:"Volver arriba ↑"
  }
};
copy.es.pilotReport = "Abrir los descriptivos agregados del piloto ↗";

// design-pass: ES copy aligned with the English meaning, and keys for strings that were English-only.
Object.assign(copy.es, {
  studyLimit:"El dataset es transversal. No muestra que un patrón de movimiento causara una lesión, no predice lesiones futuras y no diagnostica a ningún corredor.",
  unitValue:"Un registro seleccionado por persona",
  comparisonLabel:"COMPARACIÓN CLAVE",comparisonValue:"Estado de lesión, con la velocidad a la vista",
  cohortEyebrow:"LA SELECCIÓN, NO TODO EL ARCHIVO",cohortTitle:"Una cohorte con reglas que se pueden revisar.",
  cohortCopy:"Los conteos de candidatos salen de los metadatos y son provisionales. No son la muestra final biomecánicamente utilizable.",
  candidateLabel:"CANDIDATOS DE CARRERA",candidateText:"primer registro elegible por participante, con estado resuelto y metadatos utilizables",
  cohortCaption:"Conteos reproducidos desde los metadatos fijados de Figshare v1 y la regla conservadora documentada. Candidato no equivale a inclusión final.",
  candidateMeans:"COHORTE CANDIDATA · VELOCIDAD MEDIA",
  chartNote:"Solo control de balance de metadatos · no se ha hecho ninguna prueba biomecánica entre grupos.",
  heroLead:"Una lectura prudente de la biomecánica de carrera y del estado actual de lesión, pensada para mostrar qué permiten afirmar los datos y dónde se detienen.",
  motionLab:"ESTUDIO DE MOVIMIENTO / 01",phaseLabel:"FASE DEL CICLO",curveStamp:"FUKUCHI 2017 · 2,5 m/s",
  illustrationNote:"Cadera, rodilla y tobillo siguen curvas medias publicadas de 28 corredores (Fukuchi et al., 2017, CC BY 4.0). Tronco y brazos son ilustrativos. No es un registro de participantes RIC.",
  runnerTitle:"Corredor animado con curvas articulares publicadas",
  runnerDesc:"Cadera, rodilla y tobillo siguen las curvas medias de 28 corredores en cinta a 2,5 m/s (Fukuchi et al., 2017). Tronco, brazos y altura de vuelo son ilustrativos. No es un registro de participantes de Running Injury Clinic.",
  ptTouch:"CONTACTO",ptStance:"APOYO MEDIO",ptToe:"DESPEGUE",
  metaAudit:"auditoría de metadatos",pilotSplit:"15 sanos · 15 lesionados",
  idxQuestion:"01 / PREGUNTA",idxProcess:"04 / PROCESO",
  sourceFoot:"2.506 archivos JSON · 1.832 registros de carrera",healthyN:"353 sanos",injuredN:"904 lesionados",
  tag1:"FUENTE · SHA-256",tag2:"POR PERSONA · SENSIBILIDAD",tag3:"ESTRUCTURA · CONTROL TÉCNICO",
  auditLink:"Leer la auditoría de registros repetidos y etiquetas ↗",cohortLink:"Cohorte prospectiva de 52 semanas",
  xiaoLabel:"MISMO DATASET · ML TRANSVERSAL",xiaoTitle:"Ya hay un clasificador publicado con esta fuente.",
  xiaoText:"Xiao et al. (2026) comunicaron un ROC-AUC de 0,790 con random forest, sensibilidad alta y especificidad limitada. Nuestro ángulo complementario audita etiquetas de registros repetidos y el momento de cada cohorte antes de modelar.",
  gateStack:"PYTHON · CONTROL MATLAB",checksums:"HASHES · MANIFIESTO · CÓDIGO FUENTE",
  evidenceLead:"La evidencia es mixta, las definiciones varían y la población importa. El argumento más sólido para este proyecto no es un marcador universal de lesión. Es una forma transparente de hacer preguntas más concretas y reproducibles.",
  limitsTitle:"Qué puede decir este proyecto y qué no.",
  idxBalance:"02 / NUEVO ANÁLISIS",vBalance:"BALANCE ANTES DE LA BIOMECÁNICA",balEyebrow:"NUEVO ANÁLISIS · BALANCE DE COVARIABLES",
  balTitle:"La velocidad y la edad separan más a los grupos que el tamaño corporal o la experiencia.",
  balLead:"Diferencia de medias estandarizada (lesionados menos sanos) en la cohorte candidata de 1.257 personas. En estudios observacionales se suele considerar equilibrado un |SMD| menor de 0,1. Es un control de diseño, no un resultado biomecánico.",
  smdLeft:"Mayor en sanos",smdRight:"Mayor en lesionados",
  smdNote:"Líneas discontinuas: ±0,1. Los años corriendo faltan en 286 candidatos (lo informaron 242 sanos y 729 lesionados).",
  ovEyebrow:"SOLAPAMIENTO DE VELOCIDAD",
  ovText:"El 82 % de los sanos y el 80 % de los lesionados corren dentro de la ventana común de 2,21 a 3,07 m/s (la intersección de los percentiles 5 a 95 de cada grupo). Comparar a igual velocidad es factible dentro de esa ventana.",
  idxLabels:"03 / NUEVO ANÁLISIS",vLabels:"UNA PERSONA, VARIOS REGISTROS",labEyebrow:"NUEVO ANÁLISIS · ESTABILIDAD DE ETIQUETAS",
  labTitle:"Una etiqueta actual es una foto fija.",
  labLead:"209 de 1.402 corredores (14,9 %) tienen más de un registro de carrera. Al comparar el registro más antiguo con el más reciente de cada persona, 20 de ellos (9,6 %) tienen otro estado. El orden sigue las fechas de los metadatos, no un seguimiento clínico verificado.",
  mxRows:"Registro más antiguo ↓",mxCols:"Registro más reciente →",
  labWhy:"El proyecto conserva el primer registro elegible de cada persona. Si se usara el último, 20 corredores repetidos tendrían otra etiqueta. Eso justifica análisis de sensibilidad sobre la regla de etiquetado antes de comparar grupos.",
  auditLink2:"Auditoría completa de registros repetidos",
  speedAria:"Velocidad media de la cohorte candidata: sanos 2,74 metros por segundo, lesionados 2,55 metros por segundo"
});
copy.en = {};
document.querySelectorAll('[data-i18n]').forEach((element) => { if (!(element.dataset.i18n in copy.en)) copy.en[element.dataset.i18n] = element.innerHTML; });
document.querySelectorAll('[data-i18n-aria]').forEach((element) => { copy.en[element.dataset.i18nAria] = element.getAttribute('aria-label'); });
copy.en.illustrationNote = "Hip, knee and ankle follow published mean curves of 28 runners (Fukuchi et al., 2017, CC BY 4.0). Trunk and arms are illustrative. Not a RIC participant recording.";
copy.en.phaseLabel = "CYCLE PHASE";
const fmtNum = (lang, value, dec = 0) => new Intl.NumberFormat(lang === 'es' ? 'es-ES' : 'en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec, useGrouping: true }).format(value);

const languageButton = document.querySelector('.language-toggle');
const langParam = new URLSearchParams(location.search).get('lang');
let language = langParam === 'en' || langParam === 'es' ? langParam : (localStorage.getItem('running-clinic-language') || 'en');
function setLanguage(next) {
  language = next;
  document.documentElement.lang = next;
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const value = copy[next]?.[element.dataset.i18n];
    if (value !== undefined) element.innerHTML = value;
  });
  document.querySelectorAll('[data-i18n-aria]').forEach((element) => { const value = copy[next]?.[element.dataset.i18nAria]; if (value) element.setAttribute('aria-label', value); });
  document.querySelectorAll('[data-num]').forEach((element) => { element.textContent = fmtNum(next, Number(element.dataset.num), Number(element.dataset.dec || 0)); });
  document.title = next === 'es' ? 'Running Injury Clinic · Biomecánica y fenotipado de lesiones' : 'Running Injury Clinic · Biomechanics and injury phenotyping';
  document.querySelector('.hero-visual')?.setAttribute('aria-label', next === 'es' ? 'Corredor animado con curvas articulares medias publicadas; no es un registro de participantes' : 'Runner animated with published mean joint-angle curves; not a participant recording');
  languageButton.textContent = next === 'en' ? 'ES' : 'EN';
  languageButton.setAttribute('aria-pressed', String(next === 'es'));
  languageButton.setAttribute('aria-label', next === 'en' ? 'Switch language to Spanish' : 'Cambiar el idioma a inglés');
  document.querySelector('.main-nav')?.setAttribute('aria-label', next === 'en' ? 'Main navigation' : 'Navegación principal');
  document.querySelector('.metrics-band')?.setAttribute('aria-label', next === 'en' ? 'Project snapshot' : 'Resumen del proyecto');
  phaseSlider?.setAttribute('aria-label', next === 'en' ? 'Scrub the running cycle' : 'Recorrer el ciclo de carrera');
  const paused = playButton?.classList.contains('is-paused');
  playButton?.setAttribute('aria-label', next === 'en' ? (paused ? 'Play animation' : 'Pause animation') : (paused ? 'Reproducir animación' : 'Pausar animación'));
  localStorage.setItem('running-clinic-language', next);
  updatePhase(Number(phaseSlider.value));
  renderExtras();
}
languageButton?.addEventListener('click', () => setLanguage(language === 'en' ? 'es' : 'en'));

const menuButton = document.querySelector('.menu-toggle');
const mobileNav = document.querySelector('#mobile-nav');
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  mobileNav.hidden = !open;
});
mobileNav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  mobileNav.hidden = true;
  menuButton?.setAttribute('aria-expanded', 'false');
}));

const phaseSlider = document.querySelector('#phase-slider');
const phaseName = document.querySelector('#phase-name');
const phaseNumber = document.querySelector('#phase-number');
const phaseNames = { en: ['Loading response', 'Mid-stance', 'Propulsion', 'Swing and flight'], es: ['Respuesta a la carga', 'Apoyo medio', 'Propulsión', 'Oscilación y vuelo'] };
let runnerPhase = null;
window.addEventListener('runner-phase', (event) => { if (runnerPhase !== event.detail.index) { runnerPhase = event.detail.index; updatePhase(event.detail.pct); } });
function updatePhase(value) {
  if (!phaseSlider) return;
  const phase = runnerPhase ?? (value < 12.3 ? 0 : value < 24.7 ? 1 : value < 37 ? 2 : 3);
  phaseName.textContent = phaseNames[language][phase];
  phaseNumber.textContent = `0${phase + 1} / 04`;
  phaseSlider.style.setProperty('--progress', `${value}%`);
  phaseSlider.setAttribute('aria-valuetext', phaseNames[language][phase]);
}
phaseSlider?.addEventListener('input', () => updatePhase(Number(phaseSlider.value)));
const playButton = document.querySelector('.play-toggle');
playButton?.addEventListener('click', () => {
  const paused = playButton.classList.toggle('is-paused');
  document.querySelector('.hero-visual')?.classList.toggle('runner-paused', paused);
  playButton.setAttribute('aria-pressed', String(!paused));
  playButton.setAttribute('aria-label', paused ? (language === 'en' ? 'Play animation' : 'Reproducir animación') : (language === 'en' ? 'Pause animation' : 'Pausar animación'));
});

let extras = null;
const STATUS = { healthy: ['Sano', 'Healthy'], injured: ['Lesionado', 'Injured'], discordant: ['Discordante', 'Discordant'], unknown: ['Desconocido', 'Unknown'] };
const COVARIATES = { speed_m_s: ['Velocidad en cinta', 'Treadmill speed', 'm/s', 2], age_analysis: ['Edad', 'Age', '', 1], Height_analysis: ['Estatura', 'Height', 'cm', 1], Weight_analysis: ['Peso', 'Weight', 'kg', 1], YrsRunning_analysis: ['Años corriendo', 'Years running', '', 1] };
function node(tag, cls, text) { const el = document.createElement(tag); if (cls) el.className = cls; if (text !== undefined) el.textContent = text; return el; }
function renderExtras() {
  if (!extras) return;
  const L = (es, en) => (language === 'es' ? es : en);
  const smd = document.querySelector('#smd-chart');
  if (smd) {
    smd.replaceChildren();
    const max = 0.6;
    for (const row of extras.covariate_balance) {
      const meta = COVARIATES[row.variable] || [row.variable, row.variable, '', 1];
      const line = node('div', 'smd-row' + (Math.abs(row.smd) >= 0.1 ? ' is-imbalanced' : ''));
      const label = node('div', 'smd-label'); label.append(node('strong', '', L(meta[0], meta[1])), node('span', '', `${L('Sanos', 'Healthy')} ${fmtNum(language, row.healthy_mean, meta[3])} · ${L('Lesionados', 'Injured')} ${fmtNum(language, row.injured_mean, meta[3])}${meta[2] ? ' ' + meta[2] : ''}`));
      const track = node('div', 'smd-track'); const bar = node('i', 'smd-bar ' + (row.smd < 0 ? 'neg' : 'pos'));
      const width = Math.min(50, Math.abs(row.smd) / max * 50); bar.style.width = `${width}%`; bar.style.left = row.smd < 0 ? `${50 - width}%` : '50%';
      track.append(node('span', 'smd-zero'), node('span', 'smd-tick minus'), node('span', 'smd-tick plus'), bar);
      line.append(label, track, node('b', 'smd-value', `${row.smd > 0 ? '+' : row.smd < 0 ? '−' : ''}${fmtNum(language, Math.abs(row.smd), 2)}`));
      smd.append(line);
    }
  }
  const overlap = document.querySelector('#overlap-bars');
  if (overlap) {
    overlap.replaceChildren();
    for (const row of extras.speed_support) {
      const item = node('div', 'overlap-row ov-' + row.status);
      const head = node('div', 'overlap-head'); head.append(node('span', '', L(STATUS[row.status][0] + 's', STATUS[row.status][1])), node('strong', '', `${fmtNum(language, row.inside_percent, 0)}${language === 'es' ? ' %' : '%'}`));
      const track = node('div', 'overlap-track'); const fill = node('i'); fill.style.width = `${row.inside_percent}%`; track.append(fill);
      item.append(head, track, node('small', '', `${fmtNum(language, row.inside)} ${L('de', 'of')} ${fmtNum(language, row.participants)}`));
      overlap.append(item);
    }
  }
  const matrix = document.querySelector('#status-matrix');
  if (matrix) {
    matrix.replaceChildren();
    const order = ['healthy', 'injured', 'discordant', 'unknown'];
    const value = (a, b) => (extras.status_endpoints.find((r) => r.first === a && r.latest === b) || { participants: 0 }).participants;
    const head = node('div', 'mx-row mx-headrow'); head.setAttribute('role', 'row'); head.append(node('span', 'mx-corner'));
    for (const b of order) { const c = node('span', 'mx-col', L(STATUS[b][0], STATUS[b][1])); c.setAttribute('role', 'columnheader'); head.append(c); }
    matrix.append(head);
    for (const a of order) {
      const row = node('div', 'mx-row'); row.setAttribute('role', 'row');
      const h = node('span', 'mx-rowhead', L(STATUS[a][0], STATUS[a][1])); h.setAttribute('role', 'rowheader'); row.append(h);
      for (const b of order) {
        const v = value(a, b); const cell = node('span', 'mx-cell' + (a === b ? ' same' : v ? ' changed' : ' empty'), v ? fmtNum(language, v) : '0'); cell.setAttribute('role', 'cell');
        cell.setAttribute('aria-label', `${L(STATUS[a][0], STATUS[a][1])} → ${L(STATUS[b][0], STATUS[b][1])}: ${v}`); row.append(cell);
      }
      matrix.append(row);
    }
  }
  const stability = document.querySelector('#stability-list');
  if (stability) {
    stability.replaceChildren();
    const s = extras.repeated_summary;
    for (const [key, es, en] of [['repeated_participants_with_multiple_injury_status_labels', 'con más de un estado', 'with more than one status'], ['repeated_participants_with_multiple_severity_labels', 'con más de una severidad', 'with more than one severity'], ['repeated_participants_with_multiple_primary_diagnosis_labels', 'con más de un diagnóstico principal', 'with more than one primary diagnosis']]) {
      const item = node('div', 'stability-item'); item.append(node('strong', '', `${fmtNum(language, s[key].n)} / ${fmtNum(language, s[key].denominator)}`), node('span', '', L(es, en))); stability.append(item);
    }
  }
}
fetch('data/extras.json').then((r) => { if (!r.ok) throw new Error(`extras HTTP ${r.status}`); return r.json(); }).then((data) => { extras = data; renderExtras(); }).catch((error) => console.warn(error));

setLanguage(language);
const revealTargets = document.querySelectorAll('.section, .cohort-section, .speed-section, .methods-section, .evidence-section, .limits-section, .reproduce-section, .metrics-band');
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  revealTargets.forEach((target) => target.classList.add('reveal'));
  const observer = new IntersectionObserver((entries, activeObserver) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        activeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealTargets.forEach((target) => observer.observe(target));
}
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.querySelector('.hero-visual')?.classList.add('runner-paused');
  playButton?.classList.add('is-paused');
  playButton?.setAttribute('aria-pressed', 'false');
}

// design-pass: on narrow screens the new-analysis sections start collapsed behind an accessible toggle.
(() => {
  const labels = { es: ['Ver el análisis', 'Ocultar el análisis'], en: ['Show the analysis', 'Hide the analysis'] };
  const lang = () => (document.documentElement.lang || 'es').slice(0, 2) === 'en' ? 'en' : 'es';
  const toggles = [];
  document.querySelectorAll('[data-collapse-after]').forEach((marker, index) => {
    const section = marker.closest('section');
    if (!section || section.querySelector('.collapse-body')) return;
    const body = document.createElement('div');
    body.className = 'collapse-body';
    body.id = `${section.id || 'analysis'}-body-${index}`;
    while (marker.nextSibling) body.appendChild(marker.nextSibling);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'collapse-toggle';
    button.setAttribute('aria-controls', body.id);
    button.setAttribute('aria-expanded', 'false');
    button.innerHTML = '<span class="collapse-label"></span><span class="collapse-icon" aria-hidden="true">+</span>';
    marker.after(button, body);
    section.classList.add('is-collapsible');
    button.addEventListener('click', () => {
      const open = !section.classList.contains('is-open');
      section.classList.toggle('is-open', open);
      button.setAttribute('aria-expanded', String(open));
      paint();
      if (open) window.dispatchEvent(new Event('resize'));
    });
    toggles.push([section, button]);
  });
  function paint() {
    for (const [section, button] of toggles) {
      const open = section.classList.contains('is-open');
      button.querySelector('.collapse-label').textContent = labels[lang()][open ? 1 : 0];
      button.querySelector('.collapse-icon').textContent = open ? '−' : '+';
    }
  }
  paint();
  new MutationObserver(paint).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
