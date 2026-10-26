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

const languageButton = document.querySelector('.language-toggle');
let language = localStorage.getItem('running-clinic-language') || 'en';
function setLanguage(next) {
  language = next;
  document.documentElement.lang = next;
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const value = copy[next]?.[element.dataset.i18n];
    if (value) element.innerHTML = value;
  });
  languageButton.textContent = next === 'en' ? 'ES' : 'EN';
  languageButton.setAttribute('aria-pressed', String(next === 'es'));
  languageButton.setAttribute('aria-label', next === 'en' ? 'Cambiar idioma a español' : 'Change language to English');
  document.querySelector('.main-nav')?.setAttribute('aria-label', next === 'en' ? 'Navegación principal' : 'Main navigation');
  document.querySelector('.metrics-band')?.setAttribute('aria-label', next === 'en' ? 'Resumen del proyecto' : 'Project snapshot');
  phaseSlider?.setAttribute('aria-label', next === 'en' ? 'Explora el ciclo de marcha ilustrativo' : 'Explore the illustrative gait cycle');
  const paused = playButton?.classList.contains('is-paused');
  playButton?.setAttribute('aria-label', next === 'en' ? (paused ? 'Reproducir ilustración' : 'Pausar ilustración') : (paused ? 'Play illustration' : 'Pause illustration'));
  localStorage.setItem('running-clinic-language', next);
  updatePhase(Number(phaseSlider.value));
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
const phaseNames = { en: ['Loading response', 'Mid-stance', 'Propulsion', 'Swing'], es: ['Respuesta a la carga', 'Apoyo medio', 'Propulsión', 'Balanceo'] };
function updatePhase(value) {
  if (!phaseSlider) return;
  const phase = Math.min(3, Math.floor(value / 25));
  phaseName.textContent = phaseNames[language][phase];
  phaseNumber.textContent = `0${phase + 1}—04`;
  phaseSlider.style.setProperty('--progress', `${value}%`);
  phaseSlider.setAttribute('aria-valuetext', phaseNames[language][phase]);
}
phaseSlider?.addEventListener('input', () => updatePhase(Number(phaseSlider.value)));
const playButton = document.querySelector('.play-toggle');
playButton?.addEventListener('click', () => {
  const paused = playButton.classList.toggle('is-paused');
  document.querySelector('.hero-visual')?.classList.toggle('runner-paused', paused);
  playButton.setAttribute('aria-pressed', String(!paused));
  playButton.setAttribute('aria-label', paused ? (language === 'en' ? 'Play illustration' : 'Reproducir ilustración') : (language === 'en' ? 'Pause illustration' : 'Pausar ilustración'));
});

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
