// Builds presentation/FYP_Presentation.pptx — mid-semester checkpoint 1 deck (15 slides, 16:9).
//
//   cd presentation/deck && npm install && node build_deck.js
//   (first, once: uv run presentation/deck/make_concepts.py  — writes the concept sketches into figures/)
//
// Story: antenna basics → how an antenna is judged → our structure (CPW-fed monopole) → metasurface idea →
// objectives → literature → method → work done (CST results) → next steps → conclusion.
// The slides carry visuals and keywords; the spoken detail is in presentation/SPEAKER_SCRIPT.md.
// CST screenshots are cropped into .cache/ at build time; files in figures/ are never modified.
"use strict";

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const md = require("react-icons/md");
const JSZip = require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));

const ROOT = path.resolve(__dirname, "..", "..");
const FIGS = path.join(ROOT, "figures");
const CACHE = path.join(__dirname, ".cache");
const OUT = path.join(ROOT, "presentation", "FYP_Presentation.pptx");

// ----------------------------------------------------------------------------------------- theme
const THEME = {
  name: "Copper and Navy",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1F2328", lt1: "FFFFFF", dk2: "17324D", lt2: "F2F4F7",
    accent1: "B8651B", accent2: "2E7D5B", accent3: "C0392B", accent4: "3B6EA5", accent5: "E9D8C4", accent6: "8A94A6",
    hlink: "3B6EA5", folHlink: "6B4E9B",
  },
};
const C = {
  ink: "1F2328", navy: "17324D", copper: "B8651B", green: "2E7D5B", red: "C0392B", blue: "3B6EA5",
  grey: "8A94A6", line: "D5D9E0", card: "F2F4F7", copperTint: "F7EDE3", greenTint: "E6F2EC", redTint: "F9E7E5",
  navyTint: "E7EDF4", white: "FFFFFF", fr4: "6E8B3D", cu: "C27C3A", muted: "5B6472",
};
const HEAD = THEME.headFontFace;
const BODY = THEME.bodyFontFace;

const W = 13.333, H = 7.5, MX = 0.6;
const TOP = 1.6, BOTTOM = 6.8;   // content area
const FOOTER = "Wideband MIMO Antenna with Metasurface  ·  Dept. of ECE, NIT Silchar";

// ----------------------------------------------------------------------------------------- facts
// From the CST plots in figures/ (CST markers where shown; otherwise read off the curve, ±0.05 GHz).
const F = {
  band: "2.16 – 15.73 GHz",
  bandWidth: "about 13.6 GHz wide",
  resonances: "2.7 · 4.8 · 9.2 · 14.3 GHz",
  gap: "2\u00A0mm",
  msBand: "about 2.0 → 18 GHz",
  msGaps: [[3.0, 3.4, "−6.6 dB"], [4.5, 4.7, "−9.7 dB"], [5.1, 5.6, "−8.8 dB"]],
};

// References in the order the slides cite them (IEEE style). Kept in step with report/literature.py.
const REFS = [
  "N. P. Agrawall, G. Kumar, and K. P. Ray, “Wide-band planar monopole antennas,” IEEE Trans. Antennas Propag., vol. 46, no. 2, pp. 294–295, Feb. 1998.",
  "M. S. Sharawi, “Printed multi-band MIMO antenna systems and their performance metrics,” IEEE Antennas Propag. Mag., vol. 55, no. 5, pp. 218–232, Oct. 2013.",
  "C. A. Balanis, Antenna Theory: Analysis and Design, 4th ed. Hoboken, NJ, USA: Wiley, 2016.",
  "R. N. Simons, Coplanar Waveguide Circuits, Components, and Systems. New York, NY, USA: Wiley, 2001.",
  "C. L. Holloway et al., “An overview of the theory and applications of metasurfaces,” IEEE Antennas Propag. Mag., vol. 54, no. 2, pp. 10–35, Apr. 2012.",
  "J. B. Pendry, A. J. Holden, D. J. Robbins, and W. J. Stewart, “Magnetism from conductors and enhanced nonlinear phenomena,” IEEE Trans. Microw. Theory Techn., vol. 47, no. 11, pp. 2075–2084, Nov. 1999.",
  "A. J. A. Al-Gburi et al., “High gain of UWB planar antenna utilising FSS reflector for UWB applications,” Comput. Mater. Contin., vol. 70, no. 1, pp. 1425–1436, 2022.",
  "M. Hussain et al., “Bandwidth and gain enhancement of a CPW antenna using frequency selective surface for UWB applications,” Micromachines, vol. 14, no. 3, Art. no. 591, 2023.",
  "B. Hammache et al., “Gain enhancement of compact CPW-fed ultra-wideband antenna using an FSS reflector,” Microw. Opt. Technol. Lett., vol. 66, no. 10, Art. no. e34344, 2024.",
  "G. Sen, A. Banerjee, M. Kumar, and S. Das, “An ultra-wideband monopole antenna with a gain enhanced performance using a novel split-ring meta-surface reflector,” Microw. Opt. Technol. Lett., vol. 59, no. 6, pp. 1296–1300, 2017.",
  "M. M. Hasan et al., “Gain and isolation enhancement of a wideband MIMO antenna using metasurface for 5G sub-6 GHz communication systems,” Sci. Rep., vol. 12, Art. no. 9433, 2022.",
];

// ----------------------------------------------------------------------------------------- helpers
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: HEAD, bodyFontFace: BODY };
pres.title = "Wideband MIMO Antenna with Metasurface — Mid-Semester Evaluation";
pres.author = "Chanswarang Boro, Nishit Baishya, Anushka Dam, Sanjana";
pres.subject = "B.Tech project, Dept. of ECE, NIT Silchar";

pres.defineSlideMaster({
  title: "COVER",
  background: { color: C.white },
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.white },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: MX, y: 0.38, w: 9.0, h: 0.32, fontFace: BODY, fontSize: 13,
      bold: true, color: C.copper, charSpacing: 1.5, margin: 0, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.68, w: W - 2 * MX, h: 0.75, fontFace: HEAD,
      fontSize: 34, bold: true, color: C.navy, margin: 0, valign: "middle", align: "left" }, text: "" } },
    { text: { text: FOOTER, options: { x: MX, y: 7.02, w: 9, h: 0.28, fontFace: BODY, fontSize: 10, color: C.grey, margin: 0 } } },
  ],
  slideNumber: { x: W - MX - 0.6, y: 7.02, w: 0.6, h: 0.28, fontFace: BODY, fontSize: 10, color: C.grey, align: "right", margin: 0 },
});

/** "S_{11} below −10 dB" → text runs with real subscripts; **bold** spans too. */
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|_\{[^}]*\})/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push({ text: text.slice(last, m.index), options: { ...base } });
    const tok = m[0];
    if (tok.startsWith("**")) out.push(...runs(tok.slice(2, -2), { ...base, bold: true }));
    else out.push({ text: tok.slice(2, -1), options: { ...base, subscript: true } });
    last = m.index + tok.length;
  }
  if (last < text.length) out.push({ text: text.slice(last), options: { ...base } });
  return out;
}

/** Paragraph list → runs with breaks. items: string | {t, bullet, color, size, bold, after} */
function paras(items, base = {}) {
  const out = [];
  items.forEach((it, i) => {
    const o = typeof it === "string" ? { t: it } : it;
    const r = runs(o.t, { ...base, ...(o.color ? { color: o.color } : {}), ...(o.size ? { fontSize: o.size } : {}),
      ...(o.bold ? { bold: true } : {}) });
    const pOpts = { breakLine: i < items.length - 1, paraSpaceAfter: o.after ?? base.paraSpaceAfter ?? 6 };
    if (o.bullet !== false && base.bullet) pOpts.bullet = base.bullet === true ? true : base.bullet;
    if (o.bullet && o.bullet !== true) pOpts.bullet = o.bullet;
    r.forEach((run, k) => {
      if (k === 0) Object.assign(run.options, { bullet: pOpts.bullet });
      if (k === r.length - 1) Object.assign(run.options, { breakLine: pOpts.breakLine, paraSpaceAfter: pOpts.paraSpaceAfter });
    });
    out.push(...r);
  });
  return out;
}

function text(slide, items, x, y, w, h, o = {}) {
  const base = { fontFace: o.fontFace || BODY, fontSize: o.size || 16, color: o.color || C.ink, bold: o.bold || false,
    bullet: o.bullet, paraSpaceAfter: o.after };
  const arr = typeof items === "string" ? runs(items, base) : paras(items, base);
  slide.addText(arr, { x, y, w, h, margin: o.margin ?? 0, valign: o.valign || "top", align: o.align || "left",
    isTextBox: true, lineSpacingMultiple: o.lineSpacing || 1.0, fit: "none", objectName: o.name });
}

function rect(slide, x, y, w, h, fill, o = {}) {
  slide.addShape(o.round === false ? pres.shapes.RECTANGLE : pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: o.radius ?? 0.12,
    fill: fill ? { color: fill, transparency: o.transparency || 0 } : { type: "none" },
    line: o.line ? { color: o.line, width: o.lineWidth || 1, dashType: o.dash ? "dash" : "solid" } : { type: "none" },
    objectName: o.name,
  });
}

function line(slide, x1, y1, x2, y2, color, o = {}) {
  slide.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.max(Math.abs(x2 - x1), 0.0001), h: Math.max(Math.abs(y2 - y1), 0.0001),
    flipH: x2 < x1, flipV: y2 < y1,
    line: { color, width: o.width || 1.5, dashType: o.dash ? "dash" : "solid", endArrowType: o.arrow ? "triangle" : undefined,
      beginArrowType: o.both ? "triangle" : undefined },
  });
}

const iconCache = new Map();
async function icon(name, color, px = 256) {
  const key = `${name}-${color}-${px}`;
  if (iconCache.has(key)) return iconCache.get(key);
  const Comp = md[name];
  if (!Comp) throw new Error(`icon ${name} not found in react-icons/md`);
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: `#${color}`, size: px }));
  const buf = await sharp(Buffer.from(svg)).resize(px, px).png().toBuffer();
  const data = "image/png;base64," + buf.toString("base64");
  iconCache.set(key, data);
  return data;
}

/** Icon in a filled circle — the deck's visual motif. */
async function badge(slide, name, x, y, d, bg = C.navy, fg = C.white) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { type: "none" } });
  const pad = d * 0.22;
  slide.addImage({ data: await icon(name, fg), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}

function numberBadge(slide, n, x, y, d, bg = C.navy, fg = C.white, o = {}) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: bg ? { color: bg } : { type: "none" },
    line: o.line ? { color: o.line, width: 1.5, dashType: o.dash ? "dash" : "solid" } : { type: "none" } });
  slide.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: BODY, fontSize: o.size || 18,
    bold: true, color: fg, margin: 0, isTextBox: true });
}

/** Crop figures/<name> into .cache and return {path, w, h} in pixels. */
async function cropped(name, crop) {
  const src = path.join(FIGS, name);
  if (!crop) {
    const meta = await sharp(src).metadata();
    return { path: src, w: meta.width, h: meta.height };
  }
  const [l, t, r, b] = crop;
  const out = path.join(CACHE, `${path.parse(name).name}_${l}_${t}_${r}_${b}.png`);
  await sharp(src).extract({ left: l, top: t, width: r - l, height: b - t }).png().toFile(out);
  return { path: out, w: r - l, h: b - t };
}

/** Place an image fitted inside (x, y, w, h); returns the placed box. */
async function image(slide, name, x, y, w, h, o = {}) {
  const im = await cropped(name, o.crop);
  const s = Math.min(w / im.w, h / im.h);
  const pw = im.w * s, ph = im.h * s;
  const px = x + (o.align === "left" ? 0 : o.align === "right" ? w - pw : (w - pw) / 2);
  const py = y + (o.valign === "top" ? 0 : (h - ph) / 2);
  slide.addImage({ path: im.path, x: px, y: py, w: pw, h: ph, objectName: name });
  if (o.border) rect(slide, px, py, pw, ph, null, { line: C.line, round: false });
  return { x: px, y: py, w: pw, h: ph, scale: s };
}

// CST 1D plots: 2288 × 959 px, frame found with numpy (left, right, top, bottom) and the axis ranges printed on them.
const PLOTS = {
  "cst_initial_ground_s11.png": { frame: [71, 2253, 96, 889], y: [0, -50] },
  "cst_single_Lg_best.png": { frame: [71, 2067, 96, 889], y: [20, -50] },
  "cst_single_R_best.png": { frame: [71, 2078, 96, 889], y: [0, -45] },
  "cst_single_final_s11_bandwidth.png": { frame: [100, 2168, 96, 889], y: [0, -35] },
  "cst_single_final_s11.png": { frame: [71, 2168, 96, 889], y: [0, -35] },
  "cst_single_ms_s11.png": { frame: [71, 2168, 96, 889], y: [5, -30] },
};
const CROP_TOP = 64; // drops the "S-Parameters [Magnitude in dB]" title

/** Place a CST plot (title and outside legend cropped) and return mappers from (GHz, dB) to slide inches. */
async function cstPlot(slide, name, x, y, w, h, o = {}) {
  const p = PLOTS[name];
  const [L, R, T, B] = p.frame;
  const crop = [0, CROP_TOP, Math.min(R + 10, 2288), 959];
  const box = await image(slide, name, x, y, w, h, { crop, align: o.align || "center", valign: o.valign });
  const s = box.scale;
  const fx = (f) => box.x + (L - crop[0]) * s + (f / 18) * (R - L) * s;
  const fy = (db) => box.y + (T - crop[1]) * s + ((p.y[0] - db) / (p.y[0] - p.y[1])) * (B - T) * s;
  return { box, fx, fy, top: fy(p.y[0]), bottom: fy(p.y[1]) };
}

/** Translucent band over a plot between two frequencies (full plot height). */
function band(slide, plot, f1, f2, color, transparency = 82) {
  slide.addShape(pres.shapes.RECTANGLE, { x: plot.fx(f1), y: plot.top, w: plot.fx(f2) - plot.fx(f1), h: plot.bottom - plot.top,
    fill: { color, transparency }, line: { type: "none" } });
}

function chip(slide, label, x, y, w, h, o = {}) {
  rect(slide, x, y, w, h, o.fill || C.card, { radius: 0.1, line: o.line });
  text(slide, label, x + 0.15, y, w - 0.3, h, { size: o.size || 15, color: o.color || C.ink, valign: "middle",
    align: o.align || "left", bold: o.bold });
}

function contentSlide(kicker, title, notes) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  if (kicker) s.addText(kicker.toUpperCase(), { placeholder: "kicker" });
  s.addText(runs(title), { placeholder: "title" });
  if (notes) s.addNotes(notes.replace(/\s+/g, " ").trim());
  return s;
}

// ========================================================================================= slides
async function sTitle() {
  const s = pres.addSlide({ masterName: "COVER" });
  s.addImage({ path: path.join(FIGS, "nits_logo.png"), x: MX, y: 0.45, w: 0.95, h: 0.95 });
  text(s, "B.TECH PROJECT  ·  MID-SEMESTER EVALUATION", MX + 1.15, 0.62, 7, 0.3, { size: 13, color: C.copper, bold: true });
  text(s, "Dept. of Electronics & Communication Engineering, NIT Silchar", MX + 1.15, 0.92, 7.2, 0.3, { size: 13, color: C.muted });
  text(s, [{ t: "Wideband MIMO Antenna", after: 0 }, { t: "with Metasurface", after: 0 }], MX, 1.75, 7.6, 1.6,
    { fontFace: HEAD, size: 44, bold: true, color: C.navy, lineSpacing: 0.95 });
  text(s, "Checkpoint 1 — a CPW-fed wideband antenna with a split-ring metasurface reflector", MX, 3.45, 7.2, 0.7,
    { size: 18, color: C.muted });
  // team and guides
  rect(s, MX, 4.45, 3.55, 2.25, C.card);
  text(s, [{ t: "Presented by", bold: true, color: C.copper, size: 14, after: 6 },
    { t: "Chanswarang Boro  (2314143)", after: 2 }, { t: "Nishit Baishya  (2314088)", after: 2 },
    { t: "Anushka Dam  (2314115)", after: 2 }, { t: "Sanjana  (2314060)", after: 0 }],
  MX + 0.25, 4.62, 3.2, 2.0, { size: 15 });
  rect(s, MX + 3.75, 4.45, 3.55, 2.25, C.card);
  text(s, [{ t: "Under the guidance of", bold: true, color: C.copper, size: 14, after: 6 },
    { t: "**Dr. Ujjal Chakraborty**", after: 0 }, { t: "Associate Professor, ECE", size: 14, color: C.muted, after: 10 },
    { t: "Co-guide", bold: true, color: C.copper, size: 14, after: 4 },
    { t: "**Mr. Sovan Bhattacharya**", after: 0 }, { t: "PhD Scholar, ECE", size: 14, color: C.muted, after: 0 }],
  MX + 4.0, 4.62, 3.2, 2.0, { size: 15 });
  text(s, "B.Tech 7th Semester  ·  Session 2026–27  ·  October 2026", MX, 6.88, 7.3, 0.3, { size: 12, color: C.grey });
  // hero: metasurface behind, antenna in front
  rect(s, 8.35, 0.75, 4.4, 4.4, C.card, { radius: 0.15 });
  await image(s, "cst_metasurface_top.png", 8.6, 1.0, 3.9, 3.9);
  rect(s, 9.13, 3.05, 3.6, 3.6, C.white, { radius: 0.15, line: C.line });
  await image(s, "cst_final_antenna.png", 9.33, 3.25, 3.2, 3.2);
  text(s, "our antenna (front)  +  split-ring metasurface (behind)", 8.35, 6.75, 4.6, 0.3, { size: 11, color: C.grey, align: "center" });
  s.addNotes("Introduce the project and the team. This is checkpoint 1: one wideband antenna, optimised, with a metasurface added behind it. MIMO comes in Phase II.");
}

async function sAntenna() {
  const s = contentSlide("Basics", "What is an antenna?",
    `An antenna turns the electrical signal in a cable into radio waves, and catches radio waves and turns them back into
    a signal. Phones, Wi-Fi routers and GPS all use one. Its size depends on the wavelength: higher frequency means a
    shorter wave and a smaller antenna.`);
  // flow: transmitter → cable → antenna ~~~ waves ~~~ antenna → receiver
  const y = 2.05, d = 1.2;
  const nodes = [
    ["MdRouter", "Transmitter", 0.9], ["MdSettingsInputAntenna", "Antenna", 3.75],
    ["MdSettingsInputAntenna", "Antenna", 8.4], ["MdSmartphone", "Receiver", 11.25],
  ];
  for (const [ic, lab, x] of nodes) {
    await badge(s, ic, x, y, d, ic === "MdSettingsInputAntenna" ? C.copper : C.navy);
    text(s, lab, x - 0.4, y + d + 0.1, d + 0.8, 0.35, { size: 15, bold: true, align: "center" });
  }
  line(s, 0.9 + d + 0.1, y + d / 2, 3.75 - 0.1, y + d / 2, C.navy, { width: 2.5 });
  text(s, "signal in a cable", 2.2, y + d / 2 - 0.42, 1.5, 0.35, { size: 12, color: C.muted, align: "center" });
  line(s, 8.4 + d + 0.1, y + d / 2, 11.25 - 0.1, y + d / 2, C.navy, { width: 2.5 });
  text(s, "signal in a cable", 9.65, y + d / 2 - 0.42, 1.5, 0.35, { size: 12, color: C.muted, align: "center" });
  // radio waves between the antennas
  for (let k = 0; k < 5; k++) {
    const cx = 5.35 + k * 0.62;
    s.addShape(pres.shapes.ARC, { x: cx, y: y + 0.1, w: 0.5, h: 1.0, angleRange: [300, 60],
      line: { color: C.blue, width: 2.5 }, fill: { type: "none" } });
  }
  text(s, "radio waves through the air", 4.95, y + d + 0.1, 3.4, 0.35, { size: 15, bold: true, color: C.blue, align: "center" });
  text(s, "transmit:  signal → wave", 3.15, y - 0.55, 2.4, 0.35, { size: 13, color: C.copper, align: "center" });
  text(s, "receive:  wave → signal", 7.8, y - 0.55, 2.4, 0.35, { size: 13, color: C.copper, align: "center" });
  // three cards
  const cards = [
    ["MdSwapHoriz", "A converter", "Electrical signal ↔ radio wave, in both directions"],
    ["MdWifiTethering", "Everywhere", "Phones, Wi-Fi routers, GPS, radar"],
    ["MdStraighten", "Size follows wavelength", "Higher frequency → shorter wave → smaller antenna"],
  ];
  const cw = (W - 2 * MX - 0.6) / 3;
  for (let i = 0; i < 3; i++) {
    const x = MX + i * (cw + 0.3), cy = 4.35;
    rect(s, x, cy, cw, 2.2, C.card);
    await badge(s, cards[i][0], x + 0.3, cy + 0.32, 0.75, C.navy);
    text(s, cards[i][1], x + 1.25, cy + 0.32, cw - 1.45, 0.75, { size: 19, bold: true, color: C.navy, valign: "middle" });
    text(s, cards[i][2], x + 0.3, cy + 1.25, cw - 0.6, 0.8, { size: 16 });
  }
}

async function sJudge() {
  const s = contentSlide("Basics", "How do we judge an antenna?",
    `Two questions. First, matching: how much of the power we feed in bounces back. That is S11. Below minus 10 dB means
    less than 10 percent comes back, and the frequency range where that holds is the bandwidth. Second, gain and the
    radiation pattern: how strongly and in which direction the antenna sends its power. A plain monopole sends equally to
    the front and the back; a reflector behind it folds the back lobe forward, which raises the gain.`);
  const cw = (W - 2 * MX - 0.35) / 2;
  for (const [i, ic, head, sub] of [[0, "MdShowChart", "Matching  —  S_{11}", "how much power bounces back"],
    [1, "MdRadar", "Gain & radiation pattern", "how strongly, and in which direction"]]) {
    const x = MX + i * (cw + 0.35);
    rect(s, x, TOP, cw, 5.15, C.card);
    await badge(s, ic, x + 0.3, TOP + 0.25, 0.7, i === 0 ? C.navy : C.copper);
    text(s, head, x + 1.15, TOP + 0.2, cw - 1.4, 0.45, { size: 20, bold: true, color: C.navy });
    text(s, sub, x + 1.15, TOP + 0.62, cw - 1.4, 0.35, { size: 15, color: C.muted });
  }
  await image(s, "concept_s11.png", MX + 0.25, TOP + 1.15, cw - 0.5, 3.0);
  text(s, "Below −10 dB  →  less than 10 % reflected  →  good match", MX + 0.3, TOP + 4.3, cw - 0.6, 0.65,
    { size: 15, bold: true, color: C.green, align: "center", valign: "middle" });
  const x2 = MX + cw + 0.35;
  await image(s, "concept_pattern.png", x2 + 0.25, TOP + 1.1, 3.1, 3.95);
  text(s, [
    { t: "**Gain** (dBi): power in the best direction, compared with an antenna that radiates equally everywhere", after: 10 },
    { t: "A monopole sends **front and back** → part of the power is wasted", after: 10 },
    { t: "A reflector behind it sends more power **forward** → higher gain", after: 0 },
  ], x2 + 3.45, TOP + 1.3, cw - 3.7, 3.7, { size: 15, valign: "middle" });
  text(s, "concept sketches, not our results", x2 + 0.3, TOP + 4.75, cw - 0.6, 0.3, { size: 11, color: C.grey, align: "right" });
}

async function sIntro() {
  const s = contentSlide("Introduction & problem statement", "Why wideband, why MIMO — and what is the problem?",
    `Wideband means one antenna serves many services. MIMO means several antennas on one device, for more data and a
    more reliable link. Printed monopoles are small, cheap and wideband — but they radiate equally front and back, so the
    gain is low. A plain metal sheet behind them only helps if it is far away, which makes the antenna thick. So our
    question is how to raise the gain while keeping the antenna thin and wideband.`);
  const cards = [
    ["MdGraphicEq", "Wideband", "One antenna covers many services (about 2–15 GHz)"],
    ["MdHub", "MIMO", "Several antennas on one device → more data, more reliable link"],
    ["MdMemory", "Printed monopole", "Small, cheap, easy to make and naturally wideband"],
  ];
  const cw = (W - 2 * MX - 0.6) / 3;
  for (let i = 0; i < 3; i++) {
    const x = MX + i * (cw + 0.3);
    rect(s, x, TOP, cw, 1.95, C.card);
    await badge(s, cards[i][0], x + 0.3, TOP + 0.3, 0.75, C.navy);
    text(s, cards[i][1], x + 1.25, TOP + 0.3, cw - 1.45, 0.75, { size: 20, bold: true, color: C.navy, valign: "middle" });
    text(s, cards[i][2], x + 0.3, TOP + 1.18, cw - 0.6, 0.7, { size: 15 });
  }
  // problem
  const py = TOP + 2.3;
  rect(s, MX, py, 7.4, 2.85, C.redTint);
  await badge(s, "MdWarningAmber", MX + 0.3, py + 0.3, 0.75, C.red);
  text(s, "The problem", MX + 1.25, py + 0.3, 5, 0.75, { size: 20, bold: true, color: C.red, valign: "middle" });
  text(s, [
    { t: "A printed monopole radiates **to the front and the back** → part of the power goes the wrong way → **low gain**", after: 10 },
    { t: "A plain metal sheet behind it must sit **about a quarter-wavelength away** → the antenna becomes **thick**", after: 0 },
  ], MX + 0.35, py + 1.2, 6.8, 1.6, { size: 16, bullet: true });
  // question
  rect(s, MX + 7.7, py, W - 2 * MX - 7.7, 2.85, C.navy);
  await badge(s, "MdLightbulbOutline", MX + 8.0, py + 0.3, 0.75, C.copper);
  text(s, "Our question", MX + 8.95, py + 0.3, 3, 0.75, { size: 20, bold: true, color: C.white, valign: "middle" });
  text(s, "How can we raise the gain and still keep the antenna thin and wideband?", MX + 8.0, py + 1.2, 4.1, 1.5,
    { fontFace: HEAD, size: 20, color: C.white });
  text(s, "[1]–[3]", W - MX - 1.5, BOTTOM + 0.0, 1.5, 0.22, { size: 10, color: C.grey, align: "right" });
}

async function sOurAntenna() {
  const s = contentSlide("Our structure", "Our antenna: a CPW-fed printed monopole",
    `This is our optimised antenna. The ten-sided patch is the part that radiates. It is fed by a coplanar waveguide:
    the signal line runs between two ground planes on the same side of the board, and the back of the board is bare.
    We chose FR-4 because it is cheap and easy to fabricate; a near-circular decagon because smooth current paths give
    several resonances that merge into one wide band; and CPW because it needs only one copper layer, no vias, and it is
    easy to attach a connector.`);
  // antenna with callouts (image 928 × 928 px)
  const ax = MX, ay = TOP, ad = 3.75;
  rect(s, ax, ay, 5.75, 5.2, C.card);
  const im = await image(s, "cst_final_antenna.png", ax + 0.3, ay + 0.3, ad, ad);
  const P = (px, py) => [im.x + (px / 928) * im.w, im.y + (py / 928) * im.h];
  const tip = (px, py, col) => {
    const [tx, ty] = P(px, py);
    s.addShape(pres.shapes.OVAL, { x: tx - 0.07, y: ty - 0.07, w: 0.14, h: 0.14, fill: { color: col }, line: { color: C.white, width: 1 } });
    return [tx, ty];
  };
  const lx = im.x + im.w + 0.3;
  let [tx, ty] = tip(640, 230, C.copper);
  line(s, tx, ty, lx - 0.05, ty, C.copper, { width: 1.5 });
  text(s, "Decagon patch", lx, ty - 0.2, 1.4, 0.4, { size: 15, bold: true, color: C.copper, valign: "middle" });
  [tx, ty] = tip(820, 760, C.navy);
  line(s, tx, ty, lx - 0.05, ty, C.navy, { width: 1.5 });
  text(s, "Ground", lx, ty - 0.2, 1.4, 0.4, { size: 15, bold: true, color: C.navy, valign: "middle" });
  [tx, ty] = tip(463, 900, C.navy);
  line(s, tx, ty, tx, im.y + im.h + 0.28, C.navy, { width: 1.5 });
  text(s, "Signal line", tx - 0.8, im.y + im.h + 0.3, 1.6, 0.35, { size: 15, bold: true, color: C.navy, align: "center" });
  text(s, "FR-4 board · 50 × 50 × 1.6 mm · copper", ax, ay + 4.75, 5.75, 0.3, { size: 13, color: C.muted, align: "center" });
  // CPW cross-section
  const cx = 6.75, cy = TOP - 0.05, cwid = W - MX - cx;
  text(s, "CPW feed — cross-section", cx, cy, cwid, 0.35, { size: 16, bold: true, color: C.navy });
  const sy = cy + 0.85;
  rect(s, cx, sy, cwid, 0.4, C.fr4, { round: false });
  const g = 0.22, sig = 0.75, gw = (cwid - sig - 2 * g) / 2;
  const strips = [[cx, gw, "ground"], [cx + gw + g, sig, "signal"], [cx + gw + g + sig + g, gw, "ground"]];
  for (const [x, w, lab] of strips) {
    rect(s, x, sy - 0.1, w, 0.1, C.cu, { round: false });
    text(s, lab, x, sy - 0.45, w, 0.3, { size: 14, bold: true, align: "center", color: lab === "signal" ? C.copper : C.navy });
  }
  text(s, "FR-4 substrate (1.6 mm)", cx, sy + 0.06, cwid, 0.3, { size: 12, color: C.white, align: "center", bold: true });
  text(s, "back of the board: no metal", cx, sy + 0.45, cwid, 0.3, { size: 12, color: C.muted, align: "center" });
  // why cards
  const why = [
    ["MdLayers", "Why printed on FR-4?", "Cheap, light and easy to fabricate"],
    ["MdHexagon", "Why a decagon patch?", "Close to a circle → smooth current paths → several resonances merge into one wide band"],
    ["MdCable", "Why a CPW feed?", "Signal and ground on one side → one copper layer, no vias, easy connector, wideband"],
  ];
  let wy = sy + 0.9;
  for (const [ic, head, body] of why) {
    rect(s, cx, wy, cwid, 1.02, C.card);
    await badge(s, ic, cx + 0.22, wy + 0.17, 0.66, C.copper);
    text(s, head, cx + 1.08, wy + 0.08, cwid - 1.2, 0.38, { size: 16, bold: true, color: C.navy });
    text(s, body, cx + 1.08, wy + 0.44, cwid - 1.2, 0.56, { size: 14 });
    wy += 1.1;
  }
  text(s, "[1], [3], [4]", W - MX - 1.5, BOTTOM + 0.0, 1.5, 0.22, { size: 10, color: C.grey, align: "right" });
}

async function sMetasurface() {
  const s = contentSlide("Our structure", "Our idea: a metasurface reflector",
    `A metasurface is a thin board printed with many small, repeated metal cells. Each of our cells has two split rings:
    a ring with a small cut behaves like a tiny resonant circuit, and two rings of different size give two resonances.
    The board has solid copper on the back and sits only 2 millimetres behind the antenna. The copper reflects the
    backward wave and the rings shift how it reflects, so that it can add to the forward wave instead of cancelling it.
    Whether the gain really rises is what our next simulation will show.`);
  // array + cell zoom
  rect(s, MX, TOP, 6.0, 4.15, C.card);
  const arr = await image(s, "cst_metasurface_top.png", MX + 0.25, TOP + 0.25, 3.45, 3.3);
  text(s, "6 × 5 cells (top view)", MX + 0.25, arr.y + arr.h + 0.08, 3.45, 0.3, { size: 13, color: C.muted, align: "center" });
  const cell = await image(s, "cst_metasurface_cell.png", MX + 3.95, TOP + 0.45, 1.8, 1.8, { border: true });
  // highlight the zoomed cell on the array (top-left cell)
  const cs = arr.w / 1060;
  rect(s, arr.x + 10 * cs, arr.y + 10 * cs, 162 * cs, 162 * cs, null, { line: C.copper, lineWidth: 2, round: false });
  line(s, arr.x + 172 * cs, arr.y + 10 * cs, cell.x, cell.y, C.copper, { width: 1.25, dash: true });
  text(s, [{ t: "One cell:", bold: true, color: C.copper, after: 2 }, { t: "two split rings", after: 2 },
    { t: "(outer + inner)", after: 2 }, { t: "small cut = “split”", after: 0 }],
  MX + 3.95, cell.y + cell.h + 0.15, 1.9, 1.2, { size: 13 });
  // side view (native)
  const vx = 7.0, vw = 5.7;
  text(s, "Side view (not to scale)", vx, TOP, vw, 0.35, { size: 16, bold: true, color: C.navy });
  const aY = TOP + 1.3, mY = TOP + 2.6;
  rect(s, vx + 0.4, aY, 3.6, 0.22, C.fr4, { round: false });
  rect(s, vx + 1.4, aY - 0.06, 1.6, 0.06, C.cu, { round: false });
  text(s, "antenna", vx + 4.1, aY - 0.06, 1.4, 0.32, { size: 13, bold: true });
  rect(s, vx + 0.4, mY, 3.6, 0.22, C.fr4, { round: false });
  for (let k = 0; k < 8; k++) rect(s, vx + 0.5 + k * 0.44, mY - 0.05, 0.3, 0.05, C.cu, { round: false });
  rect(s, vx + 0.4, mY + 0.22, 3.6, 0.06, C.cu, { round: false });
  text(s, "metasurface", vx + 4.1, mY - 0.1, 1.6, 0.32, { size: 13, bold: true });
  text(s, "copper back", vx + 4.1, mY + 0.16, 1.6, 0.3, { size: 12, color: C.muted });
  // gap dimension
  line(s, vx + 0.15, aY + 0.22, vx + 0.15, mY - 0.05, C.ink, { width: 1.25, arrow: true, both: true });
  text(s, F.gap, vx - 0.75, (aY + mY) / 2 - 0.05, 0.85, 0.3, { size: 14, bold: true, color: C.copper, align: "right" });
  // waves
  line(s, vx + 1.9, aY - 0.12, vx + 1.9, aY - 0.75, C.blue, { width: 2.5, arrow: true });
  line(s, vx + 2.6, aY + 0.3, vx + 2.6, mY - 0.12, C.red, { width: 2.5, arrow: true });
  line(s, vx + 3.1, mY - 0.12, vx + 3.1, aY - 0.75, C.blue, { width: 2.5, arrow: true, dash: true });
  text(s, "forward", vx + 0.7, aY - 0.7, 1.15, 0.3, { size: 12, color: C.blue, align: "right" });
  text(s, "backward", vx + 1.45, (aY + mY) / 2 - 0.05, 1.1, 0.3, { size: 12, color: C.red, align: "right" });
  text(s, "reflected, adds forward", vx + 3.2, aY - 0.7, 2.4, 0.3, { size: 12, color: C.blue });
  // three points
  const pts = [
    ["MdGridOn", "Thin board with repeated small metal cells"],
    ["MdSensors", "Split ring = tiny resonator → two rings, two resonances"],
    ["MdTrendingUp", `Placed only ${F.gap} behind → can stay thin`],
  ];
  let py = TOP + 3.35;
  for (const [ic, t] of pts) {
    await badge(s, ic, vx, py, 0.5, C.navy);
    text(s, t, vx + 0.65, py - 0.02, vw - 0.65, 0.55, { size: 15, valign: "middle" });
    py += 0.62;
  }
  chip(s, "Goal: send the backward wave forward → **more gain** (to be confirmed by the gain simulation)",
    MX, TOP + 4.35, 6.0, 0.8, { fill: C.copperTint, size: 15 });
  text(s, "[5], [6]", W - MX - 1.5, BOTTOM + 0.0, 1.5, 0.22, { size: 10, color: C.grey, align: "right" });
}

async function sObjectives() {
  const s = contentSlide("Objectives", "Four objectives",
    `First, design a compact CPW-fed wideband antenna for about 2 to 15 GHz. Second, optimise it in CST: the ground
    position first, then the patch size. Third, add the split-ring metasurface behind it to raise the gain while keeping
    it thin. Fourth, in Phase II, build the MIMO version, fabricate it and measure it.`);
  const obj = [
    ["MdDesignServices", "Design", "A compact CPW-fed wideband antenna covering about 2–15 GHz"],
    ["MdTune", "Optimise", "Ground position, then patch size, in CST, for S_{11} below −10 dB"],
    ["MdGridOn", "Metasurface", "Split rings behind the antenna to raise the gain while keeping it thin"],
    ["MdHub", "Extend & test", "Phase II: MIMO version, fabrication and measurement"],
  ];
  const cw = (W - 2 * MX - 0.9) / 4;
  for (let i = 0; i < 4; i++) {
    const x = MX + i * (cw + 0.3), y = TOP + 0.35;
    rect(s, x, y, cw, 3.6, i === 3 ? C.white : C.card, { line: i === 3 ? C.line : undefined, dash: i === 3 });
    numberBadge(s, i + 1, x + 0.3, y + 0.3, 0.6, i === 3 ? C.grey : C.copper, C.white, { size: 20 });
    await badge(s, obj[i][0], x + cw - 1.05, y + 0.25, 0.75, C.navy);
    text(s, obj[i][1], x + 0.3, y + 1.35, cw - 0.6, 0.5, { size: 21, bold: true, color: C.navy });
    text(s, obj[i][2], x + 0.3, y + 1.95, cw - 0.6, 1.5, { size: 17 });
  }
  text(s, "Objectives 1–3: this phase   ·   Objective 4: Phase II", MX, TOP + 4.25, W - 2 * MX, 0.35,
    { size: 14, color: C.muted, align: "center" });
}

async function sLiterature() {
  const s = contentSlide("Literature review", "Reflectors add gain, but sit 9–20 mm away",
    `We reviewed ten papers; here are the closest five. Reflectors behind wideband antennas raise the gain by about 4 to
    6 dB. But as the chart shows, most of them sit 9 to 20 millimetres behind the antenna. Our metasurface sits only 2
    millimetres behind. A gap this thin over a band as wide as 2 to 15 GHz is rarely reported — that is our research gap.`);
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy }, align: "left" } });
  const row = (cells, hl) => cells.map((t, j) => ({ text: t, options: {
    bold: hl || j === 0, color: hl ? C.copper : C.ink, fill: { color: hl ? C.copperTint : C.white } } }));
  const rows = [
    [hdr("Work"), hdr("Reflector behind the antenna"), hdr("Gap"), hdr("Peak gain")],
    row(["Al-Gburi 2022 [7]", "19 × 19 loop FSS", "10 mm*", "6.7 → 11.5 dBi"]),
    row(["Hussain 2023 [8]", "5 × 5 ring-frame FSS", "9 mm", "6.5 → 10.5 dBi"]),
    row(["Hammache 2024 [9]", "7 × 7 FSS", "20 mm", "2.2 → 8.4 dBi"]),
    row(["Sen 2017 [10]", "double split-ring metasurface", "—", "≈ +5.5 dB"]),
    row(["Hasan 2022 [11]", "10 × 10 split-ring MS (MIMO)", "12 mm", "5.4 → 8.3 dBi"]),
    row(["This work", "6 × 5 double split-ring MS", F.gap, "being simulated"], true),
  ];
  s.addTable(rows, { x: MX, y: TOP, w: 7.35, colW: [1.95, 2.85, 0.9, 1.65], fontFace: BODY, fontSize: 14,
    rowH: 0.5, valign: "middle", margin: [0, 0.08, 0, 0.08], border: { type: "solid", pt: 0.75, color: C.line } });
  text(s, "FSS = frequency selective surface · MS = metasurface · * total height · — not given in the abstract",
    MX, TOP + 3.6, 7.35, 0.3, { size: 11, color: C.grey });
  // gap chart
  const labels = ["This work", "Hussain 2023", "Al-Gburi 2022*", "Hasan 2022", "Hammache 2024"];
  const values = [2, 9, 10, 12, 20];
  s.addChart(pres.charts.BAR, [{ name: "Gap (mm)", labels, values }], {
    x: 8.2, y: TOP - 0.05, w: W - MX - 8.2, h: 3.85, barDir: "bar", catAxisOrientation: "maxMin",
    chartColors: [C.copper, C.grey, C.grey, C.grey, C.grey], barGapWidthPct: 45,
    showTitle: true, title: "Reflector gap behind the antenna (mm)", titleFontFace: BODY, titleFontSize: 14, titleColor: C.navy,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontFace: BODY, dataLabelFontSize: 13, dataLabelColor: C.ink,
    dataLabelFormatCode: "0", catAxisLabelFontFace: BODY, catAxisLabelFontSize: 13, catAxisLabelColor: C.ink,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false,
    valAxisMaxVal: 24, valAxisMinVal: 0,
  });
  // research gap
  const gy = TOP + 4.05;
  rect(s, MX, gy, W - 2 * MX, 1.15, C.navy);
  await badge(s, "MdFlag", MX + 0.3, gy + 0.22, 0.7, C.copper);
  text(s, [{ t: "Research gap", bold: true, color: "F3C9A1", size: 15, after: 2 },
    { t: `A metasurface only a few mm behind an antenna that works from about 2 to 15 GHz is rarely reported → our aim: ${F.gap}, then MIMO`, after: 0 }],
  MX + 1.2, gy + 0.12, W - 2 * MX - 1.45, 0.95, { size: 16, color: C.white, valign: "middle" });
}

async function sMethod() {
  const s = contentSlide("Proposed methodology", "Eight steps — six done, two to go",
    `We work in eight steps. Steps one to six are done: the initial antenna, the ground sweep, the patch-size sweep, the
    optimised antenna, the metasurface design and the S11 with the metasurface. Step seven, the gain plots, is what
    remains in this phase; step eight is Phase II. All simulations run in CST Studio Suite 2019, and we change one
    dimension at a time and keep the value with the best S11.`);
  const steps = [
    ["Initial antenna\nin CST", "done"], ["Ground position\nsweep", "done"], ["Patch size\nsweep", "done"],
    ["Optimised\nantenna", "done"], ["Metasurface\ndesign", "done"], ["Antenna +\nmetasurface", "done"],
    ["Gain vs\nfrequency", "doing"], ["Phase II: MIMO\n& testing", "planned"],
  ];
  const n = steps.length, d = 0.72, y = TOP + 0.45;
  const x0 = MX + 0.45, dx = (W - 2 * MX - 0.9 - d) / (n - 1);
  line(s, x0 + d / 2, y + d / 2, x0 + (n - 2) * dx + d / 2, y + d / 2, C.navy, { width: 3 });
  line(s, x0 + (n - 2) * dx + d / 2, y + d / 2, x0 + (n - 1) * dx + d / 2, y + d / 2, C.grey, { width: 2, dash: true });
  for (let i = 0; i < n; i++) {
    const x = x0 + i * dx, st = steps[i][1];
    if (st === "done") numberBadge(s, i + 1, x, y, d, C.navy, C.white, { size: 20 });
    else if (st === "doing") numberBadge(s, i + 1, x, y, d, C.copper, C.white, { size: 20 });
    else numberBadge(s, i + 1, x, y, d, C.white, C.grey, { line: C.grey, dash: true, size: 20 });
    text(s, steps[i][0], x + d / 2 - 0.74, y + d + 0.15, 1.48, 0.95,
      { size: 14, align: "center", color: st === "planned" ? C.muted : C.ink, bold: st === "doing" });
  }
  // legend
  const ly = y + d + 1.25;
  const leg = [["Done", C.navy, null], ["Remaining (this phase)", C.copper, null], ["Planned (Phase II)", C.white, C.grey]];
  let lx = MX + 2.4;
  for (const [lab, fill, ln] of leg) {
    s.addShape(pres.shapes.OVAL, { x: lx, y: ly + 0.05, w: 0.26, h: 0.26, fill: { color: fill },
      line: ln ? { color: ln, width: 1.25, dashType: "dash" } : { type: "none" } });
    text(s, lab, lx + 0.38, ly, 2.6, 0.36, { size: 14, valign: "middle" });
    lx += 3.1;
  }
  // tools
  const tools = [
    ["MdComputer", "Simulation tool", "CST Studio Suite 2019, frequency-domain solver, 0–18 GHz"],
    ["MdLayers", "Material", "FR-4 board (1.6 mm) with copper conductors"],
    ["MdTune", "Method", "Change one dimension at a time; keep the value with the best S_{11}"],
  ];
  const cw = (W - 2 * MX - 0.6) / 3, ty = TOP + 3.25;
  for (let i = 0; i < 3; i++) {
    const x = MX + i * (cw + 0.3);
    rect(s, x, ty, cw, 1.85, C.card);
    await badge(s, tools[i][0], x + 0.3, ty + 0.3, 0.68, C.copper);
    text(s, tools[i][1], x + 1.15, ty + 0.3, cw - 1.35, 0.68, { size: 18, bold: true, color: C.navy, valign: "middle" });
    text(s, tools[i][2], x + 0.3, ty + 1.08, cw - 0.6, 0.7, { size: 15 });
  }
}

async function sInitial() {
  const s = contentSlide("", "Starting point: the initial antenna is poorly matched",
    `This is where we started: the decagon patch with the ground edge far away, at minus 20 millimetres. The S11 stays
    above minus 10 dB from 2 to 7.7 GHz — shaded red — with only a few narrow dips below the line higher up. So the
    antenna is not usable yet. The first thing to fix is the ground position.`);
  rect(s, MX, TOP, 3.75, 4.35, C.card);
  await image(s, "cst_initial_antenna.png", MX + 0.25, TOP + 0.25, 3.25, 3.25);
  text(s, "Initial design: ground far from the patch (L_{g} = −20 mm)", MX + 0.2, TOP + 3.6, 3.35, 0.65,
    { size: 14, color: C.muted, align: "center" });
  const px = MX + 4.05, pw = W - MX - px;
  text(s, "S_{11} of the initial antenna", px, TOP - 0.05, pw, 0.35, { size: 16, bold: true, color: C.navy });
  const p = await cstPlot(s, "cst_initial_ground_s11.png", px, TOP + 0.35, pw, 3.85, { valign: "top" });
  band(s, p, 2.0, 7.7, C.red, 84);
  text(s, "poor match: 2 – 7.7 GHz", p.fx(2.0), p.fy(-38) - 0.05, p.fx(7.7) - p.fx(2.0), 0.35,
    { size: 14, bold: true, color: C.red, align: "center" });
  chip(s, "S_{11} stays **above −10 dB from 2 to 7.7 GHz**; only a few narrow dips below it higher up → **not usable yet**",
    MX, TOP + 4.55, W - 2 * MX, 0.7, { fill: C.redTint, size: 16 });
}

async function sOptimise() {
  const s = contentSlide("", "Optimisation: ground position first, then patch size",
    `Step one: we moved the ground edge towards the patch in ten steps, from minus 20 to minus 7 millimetres. A closer
    ground couples more strongly to the patch and fixes the low-frequency match; only minus 7 millimetres, the blue
    curve, stays below minus 10 dB across the band. Step two: with the ground fixed, we changed the patch radius from 4
    to 15 millimetres. Small patches leave big unmatched regions; the 15 millimetre patch, brown, joins all the
    resonances into one band. A bigger patch also sits closer to the ground, which helps too.`);
  const cw = (W - 2 * MX - 0.35) / 2;
  const items = [
    ["cst_single_Lg_best.png", "Step 1 · Ground position", "10 positions: L_{g} = −20 → −7 mm", "Best: L_{g} = −7 mm", C.blue, "MdTune"],
    ["cst_single_R_best.png", "Step 2 · Patch size", "13 sizes: R = 4 → 15 mm", "Best: R = 15 mm", "A0522D", "MdHexagon"],
  ];
  for (let i = 0; i < 2; i++) {
    const [name, head, range, best, col, ic] = items[i];
    const x = MX + i * (cw + 0.35);
    rect(s, x, TOP, cw, 5.2, C.card);
    await badge(s, ic, x + 0.25, TOP + 0.2, 0.6, C.navy);
    text(s, head, x + 1.0, TOP + 0.2, cw - 1.2, 0.6, { size: 19, bold: true, color: C.navy, valign: "middle" });
    await cstPlot(s, name, x + 0.15, TOP + 0.95, cw - 0.3, 2.65);
    // legend: best vs others
    const ly = TOP + 3.75;
    line(s, x + 0.35, ly + 0.17, x + 0.85, ly + 0.17, col, { width: 3.5 });
    text(s, best, x + 0.95, ly, 2.4, 0.36, { size: 15, bold: true, color: col === "A0522D" ? "8B4513" : C.blue, valign: "middle" });
    line(s, x + 3.35, ly + 0.17, x + 3.85, ly + 0.17, "B0B6C0", { width: 2 });
    text(s, "other values", x + 3.95, ly, 1.7, 0.36, { size: 15, color: C.muted, valign: "middle" });
    text(s, range, x + 0.35, ly + 0.5, cw - 0.7, 0.36, { size: 15 });
    text(s, i === 0 ? "Closer ground → stronger coupling → better low-band match"
      : "Bigger patch → resonances join into one band", x + 0.35, ly + 0.88, cw - 0.7, 0.36, { size: 15, bold: true });
  }
}

async function sOptimised() {
  const s = contentSlide("", "Optimised antenna: matched from 2.16 to 15.73 GHz",
    `This is the optimised antenna: the 15 millimetre decagon with the ground edge at minus 7 millimetres. S11 stays
    below minus 10 dB from 2.16 to 15.73 GHz — one band about 13.6 GHz wide, with four resonances. It covers our 2 to 15
    GHz target. One honest note: near 6.5 and 12.2 GHz the curve only just stays below the line.`);
  rect(s, MX, TOP, 3.75, 5.2, C.card);
  await image(s, "cst_final_antenna.png", MX + 0.3, TOP + 0.25, 3.15, 3.15);
  const dims = [["Board", "FR-4, 50 × 50 × 1.6 mm"], ["Patch", "decagon, R = 15 mm"], ["Ground edge", "L_{g} = −7 mm"]];
  let dy = TOP + 3.6;
  for (const [k, v] of dims) {
    text(s, k, MX + 0.3, dy, 1.25, 0.4, { size: 14, bold: true, color: C.navy, valign: "middle" });
    text(s, v, MX + 1.5, dy, 2.2, 0.4, { size: 14, valign: "middle" });
    dy += 0.48;
  }
  const px = MX + 4.05, pw = W - MX - px;
  const p = await cstPlot(s, "cst_single_final_s11_bandwidth.png", px, TOP, pw, 3.45, { valign: "top" });
  band(s, p, 2.1615, 15.734, C.green, 85);
  // stat
  const sy = TOP + 3.6;
  text(s, F.band, px, sy, 4.6, 0.85, { fontFace: HEAD, size: 40, bold: true, color: C.copper, valign: "middle" });
  text(s, "S_{11} below −10 dB (green band)", px, sy + 0.85, 4.6, 0.4, { size: 16, color: C.muted });
  const facts = [["MdStraighten", F.bandWidth], ["MdGraphicEq", `resonances: ${F.resonances}`], ["MdCheckCircle", "covers the 2–15 GHz target"]];
  let fy = sy + 0.05;
  for (const [ic, t] of facts) {
    await badge(s, ic, px + 4.7, fy, 0.42, C.navy);
    text(s, t, px + 5.25, fy - 0.02, pw - 5.25, 0.46, { size: 15, valign: "middle" });
    fy += 0.53;
  }
}

async function sMsResult() {
  const s = contentSlide("", "Metasurface added: wider band, three small gaps",
    `Top: the antenna alone. Bottom: the same antenna with the metasurface 2 millimetres behind it, on the same
    frequency axis. The band now starts lower, at about 2 GHz, and stays matched up to 18 GHz — the end of our
    simulation. But there are three narrow regions, shaded red, where S11 rises above minus 10 dB, the worst being minus
    6.6 dB near 3.1 GHz. At such a small gap the metasurface also changes the antenna's input match, so it needs tuning.
    We do not have the gain result yet; that is the next simulation.`);
  const pw = 6.75, ph = 2.25;
  text(s, "Antenna alone", MX, TOP - 0.1, pw, 0.32, { size: 15, bold: true, color: C.navy });
  const a = await cstPlot(s, "cst_single_final_s11.png", MX, TOP + 0.22, pw, ph, { align: "left", valign: "top" });
  band(s, a, 2.1615, 15.734, C.green, 85);
  const y2 = a.box.y + a.box.h + 0.15;
  text(s, `Antenna + metasurface (${F.gap} gap)`, MX, y2, pw, 0.32, { size: 15, bold: true, color: C.navy });
  const b = await cstPlot(s, "cst_single_ms_s11.png", MX, y2 + 0.32, pw, ph, { align: "left", valign: "top" });
  band(s, b, 2.0, 18, C.green, 88);
  for (const [f1, f2] of F.msGaps) band(s, b, f1, f2, C.red, 55);
  // findings — start right after the (height-limited) plots
  const x = Math.max(a.box.x + a.box.w, b.box.x + b.box.w) + 0.45, w = W - MX - x;
  const rows = [
    ["MdCheckCircle", C.green, "Wider band", F.msBand, C.greenTint],
    ["MdWarningAmber", C.red, "3 narrow gaps", "3.0–3.4 · 4.5–4.7 · 5.1–5.6 GHz\n(worst −6.6 dB near 3.1 GHz)", C.redTint],
    ["MdBuild", C.copper, "Next: tune", "air gap, ring size and ground position", C.copperTint],
  ];
  let ry = TOP;
  for (const [ic, col, head, body, tint] of rows) {
    rect(s, x, ry, w, 1.5, tint);
    await badge(s, ic, x + 0.25, ry + 0.25, 0.62, col);
    text(s, head, x + 1.05, ry + 0.2, w - 1.2, 0.45, { size: 19, bold: true, color: col });
    text(s, body, x + 1.05, ry + 0.65, w - 1.2, 0.8, { size: 15 });
    ry += 1.65;
  }
  text(s, "18 GHz is the end of the simulated range · gain not simulated yet", x, ry + 0.02, w, 0.3,
    { size: 12, color: C.grey });
}

async function sNext() {
  const s = contentSlide("Challenges & future work", "What were the challenges, and what comes next",
    `Our challenges: long simulation times for the full model; a few glitches in the sweep curves near 4 and 6 GHz from
    too few frequency points, which we will re-run; a thin matching margin near 6.5 and 12.2 GHz; and the mismatch gaps
    the metasurface introduced. Next, in this phase: the gain-versus-frequency plots with and without the metasurface,
    and tuning. Then Phase II: a four-port MIMO antenna with the metasurface, isolation and correlation checks,
    fabrication and measurement.`);
  // challenges
  const cx = MX, cw = 5.3;
  text(s, "Challenges", cx, TOP - 0.05, cw, 0.4, { size: 20, bold: true, color: C.navy });
  const ch = [
    ["MdTimer", "Long run times", "antenna + metasurface needs a large mesh"],
    ["MdShowChart", "Sweep glitches", "jumps near 4 and 6 GHz from too few frequency points → re-run"],
    ["MdStraighten", "Thin margin", "only just below −10 dB near 6.5 and 12.2 GHz"],
    ["MdWarningAmber", "Metasurface detuning", "three narrow mismatch gaps, 3.0–5.6 GHz"],
  ];
  let y = TOP + 0.5;
  for (const [ic, head, body] of ch) {
    await badge(s, ic, cx, y, 0.6, C.red);
    text(s, [{ t: head, bold: true, color: C.ink, after: 0 }, { t: body, color: C.muted, size: 14, after: 0 }],
      cx + 0.78, y - 0.05, cw - 0.8, 0.95, { size: 16 });
    y += 1.12;
  }
  // future
  const fx = MX + 5.75, fw = W - MX - fx, colw = (fw - 0.3) / 2;
  const groups = [
    ["Remaining in this phase", C.copper, C.copperTint, ["Gain vs frequency: antenna alone", "Gain vs frequency: antenna + metasurface", "Tune the metasurface to close the gaps"]],
    ["Phase II", C.navy, C.navyTint, ["4-port MIMO (elements turned 90°) + metasurface", "Isolation and correlation (ECC) between ports", "Fabricate on FR-4 and measure"]],
  ];
  for (let g = 0; g < 2; g++) {
    const [head, col, tint, list] = groups[g];
    const x = fx + g * (colw + 0.3);
    rect(s, x, TOP, colw, 3.75, tint);
    text(s, head, x + 0.25, TOP + 0.18, colw - 0.5, 0.4, { size: 18, bold: true, color: col });
    let iy = TOP + 0.8;
    for (let k = 0; k < list.length; k++) {
      numberBadge(s, g * 3 + k + 1, x + 0.25, iy, 0.42, col, C.white, { size: 14 });
      text(s, list[k], x + 0.8, iy - 0.06, colw - 1.0, 0.85, { size: 15 });
      iy += 0.95;
    }
  }
  // expected outcomes
  const oy = TOP + 3.95;
  text(s, "Expected outcomes", fx, oy, fw, 0.36, { size: 17, bold: true, color: C.navy });
  const outs = ["Thin wideband antenna with higher gain", "Compact MIMO antenna, good isolation", "Tested prototype vs simulation"];
  const ow = (fw - 0.3) / 3;
  for (let k = 0; k < 3; k++) chip(s, outs[k], fx + k * (ow + 0.15), oy + 0.42, ow, 0.85, { size: 14, align: "center" });
}

async function sConclusion() {
  const s = contentSlide("Conclusion", "Conclusion",
    `To conclude: the single wideband antenna is designed and matched from 2.16 to 15.73 GHz. The split-ring
    metasurface is designed and simulated with it: the band widens, with three narrow gaps that need tuning. Next come
    the gain plots with and without the metasurface, and then the MIMO antenna. Thank you — we are happy to take
    questions.`);
  const cards = [
    ["MdCheckCircle", C.green, "Antenna done", "CPW-fed decagon matched from **2.16–15.73 GHz**"],
    ["MdGridOn", C.copper, "Metasurface added", `6 × 5 split rings, ${F.gap} behind: wider band, 3 gaps to tune`],
    ["MdEast", C.navy, "Next", "Gain plots with and without the metasurface → MIMO antenna"],
  ];
  const cw = (W - 2 * MX - 0.6) / 3;
  for (let i = 0; i < 3; i++) {
    const x = MX + i * (cw + 0.3);
    rect(s, x, TOP, cw, 1.95, C.card);
    await badge(s, cards[i][0], x + 0.3, TOP + 0.3, 0.7, cards[i][1]);
    text(s, cards[i][2], x + 1.2, TOP + 0.3, cw - 1.4, 0.7, { size: 20, bold: true, color: C.navy, valign: "middle" });
    text(s, cards[i][3], x + 0.3, TOP + 1.1, cw - 0.6, 0.8, { size: 15 });
  }
  text(s, "References", MX, TOP + 2.2, 4, 0.35, { size: 16, bold: true, color: C.navy });
  const half = Math.ceil(REFS.length / 2);
  const colw = (W - 2 * MX - 0.4) / 2;
  for (let c = 0; c < 2; c++) {
    const list = REFS.slice(c * half, (c + 1) * half).map((r, k) => ({ t: `[${c * half + k + 1}] ${r}`, after: 3 }));
    text(s, list, MX + c * (colw + 0.4), TOP + 2.6, colw, 2.65, { size: 10, color: C.muted });
  }
}

// ========================================================================================= build
async function applyThemeColors(file) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const part = "ppt/theme/theme1.xml";
  const slots = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"];
  const scheme = `<a:clrScheme name="${THEME.name}">` + slots.map((k) => `<a:${k}><a:srgbClr val="${THEME.colors[k]}"/></a:${k}>`).join("") + "</a:clrScheme>";
  const xml = (await zip.file(part).async("string")).replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, scheme);
  zip.file(part, xml);
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

async function main() {
  fs.mkdirSync(CACHE, { recursive: true });
  const slides = [sTitle, sAntenna, sJudge, sIntro, sOurAntenna, sMetasurface, sObjectives, sLiterature, sMethod,
    sInitial, sOptimise, sOptimised, sMsResult, sNext, sConclusion];
  for (const fn of slides) await fn();
  await pres.writeFile({ fileName: OUT });
  await applyThemeColors(OUT);
  console.log(`Wrote ${path.relative(ROOT, OUT)} (${slides.length} slides)`);
}

main().catch((e) => { console.error(e); process.exit(1); });
