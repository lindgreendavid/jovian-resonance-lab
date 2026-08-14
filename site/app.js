"use strict";

const colors = { Io: "#75d6d1", Europa: "#eeb66b", Ganymede: "#caa27c", Callisto: "#ce7658" };
const radii = { Io: 0.18, Europa: 0.31, Ganymede: 0.49, Callisto: 0.75 };
let animationData;
let results;
let frame = 0;
let playing = false;
let speed = 1;
let raf = 0;

function jdToDate(jd) {
  const unix = (jd - 2440587.5) * 86400000;
  return new Date(unix).toISOString().slice(0, 16).replace("T", " ");
}

function fitCanvas(canvas) {
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(1, Math.round(rect.width * ratio));
  const height = Math.max(1, Math.round(rect.height * ratio));
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }
  return { width, height, ratio };
}

function drawOrbit() {
  if (!animationData) return;
  const canvas = document.querySelector("#orbit-canvas");
  const ctx = canvas.getContext("2d");
  const { width, height, ratio } = fitCanvas(canvas);
  const cx = width / 2;
  const cy = height / 2;
  const extent = Math.min(width, height) * 0.47;
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "rgba(117,214,209,.18)";
  ctx.lineWidth = ratio;
  Object.values(radii).forEach((radius) => {
    ctx.beginPath(); ctx.arc(cx, cy, extent * radius, 0, Math.PI * 2); ctx.stroke();
  });
  const gradient = ctx.createRadialGradient(cx - 8 * ratio, cy - 8 * ratio, 2, cx, cy, 30 * ratio);
  gradient.addColorStop(0, "#fff0b3"); gradient.addColorStop(.45, "#eeb66b"); gradient.addColorStop(1, "#9a442b");
  ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(cx, cy, 28 * ratio, 0, Math.PI * 2); ctx.fill();
  Object.entries(animationData.moons).forEach(([name, positions]) => {
    const [x, y] = positions[frame];
    const angle = Math.atan2(y, x);
    const displayRadius = extent * radii[name];
    const mx = cx + Math.cos(angle) * displayRadius;
    const my = cy + Math.sin(angle) * displayRadius;
    ctx.fillStyle = colors[name]; ctx.beginPath(); ctx.arc(mx, my, (name === "Ganymede" ? 7 : 5) * ratio, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#eaf3f5"; ctx.font = `${11 * ratio}px system-ui`; ctx.fillText(name, mx + 9 * ratio, my - 8 * ratio);
  });
  document.querySelector("#epoch").textContent = `${jdToDate(animationData.epochs_jd_tdb[frame])} TDB`;
  document.querySelector("#time-slider").value = frame;
}

function tick() {
  if (!playing || !animationData) return;
  frame = (frame + speed) % animationData.epochs_jd_tdb.length;
  drawOrbit();
  raf = window.setTimeout(() => requestAnimationFrame(tick), 55);
}

function drawResidualChart(canvas, series, reference, minimumScale = 5) {
  const ctx = canvas.getContext("2d");
  const { width, height, ratio } = fitCanvas(canvas);
  const pad = { x: 52 * ratio, y: 38 * ratio };
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "rgba(168,189,194,.22)"; ctx.fillStyle = "#a8bdc2"; ctx.font = `${11 * ratio}px system-ui`;
  [0, .25, .5, .75, 1].forEach((fraction) => { const y = pad.y + fraction * (height - 2 * pad.y); ctx.beginPath(); ctx.moveTo(pad.x, y); ctx.lineTo(width - pad.x, y); ctx.stroke(); });
  const residual = series.map((value, index) => ((value - reference[index] + 540) % 360) - 180);
  const max = Math.max(minimumScale, ...residual.map(Math.abs));
  const plot = (values, color, lineWidth) => { ctx.strokeStyle = color; ctx.lineWidth = lineWidth * ratio; ctx.beginPath(); values.forEach((value, index) => { const x = pad.x + index / (values.length - 1) * (width - 2 * pad.x); const y = height / 2 - value / max * (height / 2 - pad.y); if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke(); };
  plot(new Array(residual.length).fill(0), "#eaf3f5", 1);
  plot(residual, "#75d6d1", 2);
  ctx.fillText(`+${max.toFixed(0)}°`, 5 * ratio, pad.y); ctx.fillText("0°", 18 * ratio, height / 2); ctx.fillText(`−${max.toFixed(0)}°`, 5 * ratio, height - pad.y);
}

function drawChart(model) {
  if (!results) return;
  drawResidualChart(
    document.querySelector("#trace-chart"),
    results.chart[model],
    results.chart.reference,
  );
}

function chooseModel(model) {
  document.querySelectorAll("[data-model]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.model === model)));
  document.querySelector("#model-name").textContent = model;
  document.querySelector("#max-error").textContent = `${results.models[model].maximum_absolute_residual_degrees.toFixed(2)}°`;
  const notes = { K2: "Independent two-body motion loses the observed three-body phase relationship.", G3: "Mutual forces recover much of the structure, but the phase remains displaced.", G4: "Adding Callisto slightly improves this interval over G3; that contrast was not a separate gate.", G4J2: "G4J2 replicates the frozen ordering at the common 0.0025-day validation step." };
  document.querySelector("#chart-description").textContent = notes[model];
  drawChart(model);
}

function chooseStep(step) {
  document.querySelectorAll("[data-step]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.step === step)));
  const labels = { G4J2_coarse: "0.005 day", G4J2: "0.0025 day", G4J2_fine: "0.00125 day" };
  const metrics = { G4J2_coarse: results.coarse_reference, G4J2: results.models.G4J2, G4J2_fine: results.fine_reference };
  const descriptions = {
    G4J2_coarse: "The coarse trace is included to estimate convergence; it is not the common validation step.",
    G4J2: "The medium trace is the common-step G4J2 model used in the frozen ordering comparison.",
    G4J2_fine: "The finest trace passes the frozen 1° reference-adequacy gate.",
  };
  document.querySelector("#step-name").textContent = labels[step];
  document.querySelector("#step-rmse").textContent = `${metrics[step].circular_rmse_degrees.toFixed(3)}°`;
  document.querySelector("#convergence-description").textContent = descriptions[step];
  drawResidualChart(
    document.querySelector("#convergence-chart"),
    results.chart[step],
    results.chart.reference,
    0.75,
  );
}

async function init() {
  try {
    [animationData, results] = await Promise.all([fetch("data/animation-v0.1.json").then((r) => r.json()), fetch("data/results-v1.0.json").then((r) => r.json())]);
    document.querySelector("#time-slider").max = animationData.epochs_jd_tdb.length - 1;
    document.querySelector("#mean-angle").textContent = `${results.reference.circular_mean_degrees.toFixed(3)}°`;
    drawOrbit(); chooseModel("G4J2"); chooseStep("G4J2_fine");
  } catch (error) {
    document.querySelector("#epoch").textContent = "Data unavailable";
    console.error(error);
  }
}

document.querySelector("#time-slider").addEventListener("input", (event) => { frame = Number(event.target.value); drawOrbit(); });
document.querySelector("#play").addEventListener("click", (event) => { playing = !playing; event.currentTarget.setAttribute("aria-pressed", String(playing)); event.currentTarget.textContent = playing ? "Pause" : "Play"; if (playing) tick(); else window.clearTimeout(raf); });
document.querySelector("#slower").addEventListener("click", () => { speed = Math.max(1, speed - 1); document.querySelector("#speed").textContent = `Speed: ${speed} sample${speed === 1 ? "" : "s"} per frame`; });
document.querySelector("#faster").addEventListener("click", () => { speed = Math.min(8, speed + 1); document.querySelector("#speed").textContent = `Speed: ${speed} samples per frame`; });
document.querySelectorAll("[data-model]").forEach((button) => button.addEventListener("click", () => chooseModel(button.dataset.model)));
document.querySelectorAll("[data-step]").forEach((button) => button.addEventListener("click", () => chooseStep(button.dataset.step)));
window.addEventListener("resize", () => { drawOrbit(); drawChart(document.querySelector("[data-model][aria-pressed=true]").dataset.model); drawResidualChart(document.querySelector("#convergence-chart"), results.chart[document.querySelector("[data-step][aria-pressed=true]").dataset.step], results.chart.reference, 0.75); });
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) playing = false;
init();
