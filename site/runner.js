// Hero runner driven by published mean joint-angle curves:
// Fukuchi RK, Fukuchi CA, Duarte M (2017), PeerJ 5:e3298, data CC BY 4.0 (28 runners, treadmill, 2.5 m/s).
// Hip, knee and ankle angles are data. Trunk lean, arm swing, pelvis tilt and the flight lift are drawing choices.
(() => {
  const svg = document.querySelector('.runner-svg');
  const rig = document.querySelector('#rig');
  if (!svg || !rig) return;
  const slider = document.querySelector('#phase-slider');
  const visual = document.querySelector('.hero-visual');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const PELVIS_TILT = 12, FLIGHT_LIFT = 5, GROUND = 298, HIP = [270, 182], THIGH = 60, SHIN = 60, CYCLE_MS = 1500;
  const rad = (d) => d * Math.PI / 180;
  const turn = (x, y, d) => [x * Math.cos(rad(d)) - y * Math.sin(rad(d)), x * Math.sin(rad(d)) + y * Math.cos(rad(d))];
  const state = { gait: null, offsets: null, phase: 0.2, start: null, paused: reduced.matches, dragging: false };
  const sample = (curve, phase) => { const p = ((phase % 1) + 1) % 1 * 100; const lo = Math.floor(p); const hi = Math.min(100, lo + 1); return curve[lo] + (curve[hi] - curve[lo]) * (p - lo); };
  const inStance = (phase) => (((phase % 1) + 1) % 1) * 100 < state.gait.toe_off_pct_median;
  function leg(phase) {
    const g = state.gait;
    const hip = sample(g.hip.mean, phase), knee = sample(g.knee.mean, phase), ankle = sample(g.ankle.mean, phase);
    const thigh = -(hip - PELVIS_TILT), shin = thigh + knee, foot = shin - 14 - ankle;
    const [kx, ky] = turn(0, THIGH, thigh); const k = [HIP[0] + kx, HIP[1] + ky];
    const [ax, ay] = turn(0, SHIN, shin); const a = [k[0] + ax, k[1] + ay];
    const [hx, hy] = turn(-8, 4, foot); const heel = [a[0] + hx, a[1] + hy];
    const [tx, ty] = turn(26, 7, foot); const toe = [a[0] + tx, a[1] + ty];
    return { thigh, k, a, heel, toe, lowest: Math.max(a[1] + 5, toe[1] + 3, heel[1] + 3) };
  }
  function buildOffsets() {
    const raw = Array.from({ length: 101 }, (_, i) => {
      const p = i / 100; const supports = [p, p + 0.5].filter(inStance).map(leg);
      return supports.length ? GROUND - Math.max(...supports.map((s) => s.lowest)) : null;
    });
    return raw.map((v, i) => {
      if (v !== null) return v;
      let b = i; while (raw[b] === null) b = (b + 100) % 101;
      let a = i; while (raw[a] === null) a = (a + 1) % 101;
      const span = ((a - b + 101) % 101) || 1; const s = ((i - b + 101) % 101) / span;
      return raw[b] + (raw[a] - raw[b]) * s - FLIGHT_LIFT * 4 * s * (1 - s);
    });
  }
  const pts = (list) => list.map((p) => p.map((v) => v.toFixed(1)).join(' ')).join(' L');
  const el = (id) => document.getElementById(id);
  function draw() {
    if (!state.gait) return;
    const near = leg(state.phase), far = leg(state.phase + 0.5);
    for (const [id, l] of [['rig-near', near], ['rig-far', far]]) {
      el(id + '-leg').setAttribute('d', `M${pts([HIP, l.k, l.a])}`);
      el(id + '-foot').setAttribute('d', `M${pts([l.heel, l.a, l.toe])}`);
      el(id + '-knee').setAttribute('cx', l.k[0].toFixed(1)); el(id + '-knee').setAttribute('cy', l.k[1].toFixed(1));
      el(id + '-ankle').setAttribute('cx', l.a[0].toFixed(1)); el(id + '-ankle').setAttribute('cy', l.a[1].toFixed(1));
    }
    const shoulder = [HIP[0] + 9, HIP[1] - 66];
    for (const [id, l] of [['rig-near', far], ['rig-far', near]]) {
      const upper = -l.thigh * 0.75; const [ex, ey] = turn(0, 34, upper); const elbow = [shoulder[0] + ex, shoulder[1] + ey];
      const [hx, hy] = turn(0, 30, upper - 88); const hand = [elbow[0] + hx, elbow[1] + hy];
      el(id + '-arm').setAttribute('d', `M${pts([shoulder, elbow, hand])}`);
    }
    const lift = sample(state.offsets, state.phase);
    rig.setAttribute('transform', `translate(0 ${lift.toFixed(1)})`);
    const pct = state.phase * 100, toe = state.gait.toe_off_pct_median;
    const index = pct < toe / 3 ? 0 : pct < 2 * toe / 3 ? 1 : pct < toe ? 2 : 3;
    document.querySelectorAll('[data-phase-point]').forEach((node) => node.classList.toggle('is-active', Number(node.dataset.phasePoint) === Math.min(index, 2) && index < 3));
    if (slider && !state.dragging) slider.value = String(Math.round(pct));
    window.dispatchEvent(new CustomEvent('runner-phase', { detail: { index, pct: Math.round(pct) } }));
  }
  function frame(now) {
    if (!state.paused && !state.dragging) {
      if (state.start === null) state.start = now - state.phase * CYCLE_MS;
      state.phase = ((now - state.start) % CYCLE_MS) / CYCLE_MS;
      draw();
    } else state.start = null;
    requestAnimationFrame(frame);
  }
  slider?.addEventListener('input', () => { state.dragging = true; state.phase = Number(slider.value) / 100; draw(); });
  slider?.addEventListener('change', () => { state.dragging = false; });
  new MutationObserver(() => { state.paused = visual.classList.contains('runner-paused'); }).observe(visual, { attributes: true, attributeFilter: ['class'] });
  fetch('data/gait_reference.json').then((r) => { if (!r.ok) throw new Error(`gait reference HTTP ${r.status}`); return r.json(); }).then((g) => {
    state.gait = g; state.offsets = buildOffsets(); state.paused = visual.classList.contains('runner-paused') || reduced.matches; draw(); requestAnimationFrame(frame);
  }).catch((error) => { console.warn(error); rig.setAttribute('hidden', ''); });
})();
