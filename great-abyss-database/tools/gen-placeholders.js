// Generates 12 corrupted-archive SVG placeholders for the Great Abyss Database.
const fs = require("fs");
const path = require("path");

const OUT = require("path").join(__dirname, "..", "assets", "placeholders");

const theories = [
  ["01", "THE FLESH GARDENERS", "flesh-gardeners"],
  ["02", "SLEEPING GODS", "sleeping-gods"],
  ["03", "EARTH AS A PENAL COLONY", "penal-colony"],
  ["04", "INFRASTRUCTURE PREDATORS", "infrastructure-predators"],
  ["05", "THE PARASITE CIVILIZATION", "parasite-civilization"],
  ["06", "EARTH'S ORIGINAL OWNERS", "original-owners"],
  ["07", "THE INVASIVE SPECIES WEAPON", "invasive-species"],
  ["08", "THE GENETIC RESERVOIR", "genetic-reservoir"],
  ["09", "HELLFORMERS", "hellformers"],
  ["10", "CIVILIZATIONS MADE OF SIGNAL", "signal-civilizations"],
  ["11", "THE HUMAN LIVESTOCK THEORY", "human-livestock"],
  ["12", "REFUGEES FROM A DEAD UNIVERSE", "dead-universe-refugees"],
];

// wrap a title into lines of <= 14 chars
function wrap(title) {
  const words = title.split(" ");
  const lines = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > 14 && cur) { lines.push(cur); cur = w; }
    else cur = (cur + " " + w).trim();
  }
  if (cur) lines.push(cur);
  return lines;
}

function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/'/g, "&#39;"); }

// deterministic pseudo-random per index
function prng(seed) {
  let s = seed * 2654435761 % 4294967296;
  return () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296;
}

function makeSvg(id, title, idx) {
  const rnd = prng(idx + 7);
  const lines = wrap(title);
  const seed = idx * 13 + 5;
  const lineH = 74;
  const startY = 400 - ((lines.length - 1) * lineH) / 2;

  const titleText = lines.map((l, i) =>
    `<text x="400" y="${startY + i * lineH}" text-anchor="middle" font-family="monospace" font-size="52" font-weight="bold" fill="#9dff8a" opacity="0.9" letter-spacing="4">${esc(l)}</text>`
  ).join("\n  ");

  // ghost echo of the title (chromatic aberration feel)
  const ghostText = lines.map((l, i) =>
    `<text x="404" y="${startY + i * lineH + 2}" text-anchor="middle" font-family="monospace" font-size="52" font-weight="bold" fill="#ff4d3a" opacity="0.22" letter-spacing="4">${esc(l)}</text>`
  ).join("\n  ");

  // random horizontal tear bars
  let tears = "";
  for (let i = 0; i < 6; i++) {
    const y = Math.floor(rnd() * 780);
    const h = 3 + Math.floor(rnd() * 14);
    const op = (0.06 + rnd() * 0.22).toFixed(2);
    const shade = rnd() > 0.5 ? "#9dff8a" : "#000000";
    tears += `<rect x="0" y="${y}" width="800" height="${h}" fill="${shade}" opacity="${op}"/>\n  `;
  }

  // dropout blocks (missing data)
  let blocks = "";
  for (let i = 0; i < 5; i++) {
    const x = Math.floor(rnd() * 700);
    const y = Math.floor(rnd() * 700);
    const w = 30 + Math.floor(rnd() * 130);
    const h = 8 + Math.floor(rnd() * 30);
    blocks += `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#000" opacity="0.85"/>\n  `;
  }

  const hexRow = Array.from({ length: 8 }, () =>
    Math.floor(rnd() * 256).toString(16).padStart(2, "0").toUpperCase()).join(" ");

  return `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
  <defs>
    <filter id="noise">
      <feTurbulence type="fractalNoise" baseFrequency="0.82" numOctaves="3" seed="${seed}" stitchTiles="stitch"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.10  0 0 0 0 0.55  0 0 0 0 0.12  0 0 0 0.55 0"/>
    </filter>
    <filter id="coarse">
      <feTurbulence type="turbulence" baseFrequency="0.012 0.09" numOctaves="2" seed="${seed + 3}"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.06  0 0 0 0 0.32  0 0 0 0 0.08  0 0 0 0.5 0"/>
    </filter>
  </defs>

  <rect width="800" height="800" fill="#040604"/>
  <rect width="800" height="800" filter="url(#coarse)" opacity="0.5"/>
  <rect width="800" height="800" filter="url(#noise)" opacity="0.35"/>

  <ellipse cx="400" cy="400" rx="330" ry="330" fill="#12240f" opacity="0.75"/>

  ${tears}${blocks}
  ${ghostText}
  ${titleText}

  <!-- scanlines -->
  <g opacity="0.3">
    ${Array.from({ length: 100 }, (_, i) => `<rect x="0" y="${i * 8}" width="800" height="2" fill="#000" opacity="0.55"/>`).join("")}
  </g>

  <!-- classified frame -->
  <rect x="14" y="14" width="772" height="772" fill="none" stroke="#4c7a45" stroke-width="3" stroke-dasharray="26 12"/>
  <path d="M14 84 V14 H84 M716 14 H786 V84 M786 716 V786 H716 M84 786 H14 V716" fill="none" stroke="#9dff8a" stroke-width="6"/>

  <text x="34" y="58" font-family="monospace" font-size="26" fill="#9dff8a" opacity="0.85" letter-spacing="3">FILE ${id}//12</text>
  <text x="766" y="58" text-anchor="end" font-family="monospace" font-size="26" fill="#ff4d3a" opacity="0.8" letter-spacing="3">CLASSIFIED</text>
  <text x="34" y="740" font-family="monospace" font-size="22" fill="#4c7a45" letter-spacing="2">${hexRow}</text>
  <text x="34" y="772" font-family="monospace" font-size="24" fill="#ffb64a" opacity="0.85" letter-spacing="3">ARCHIVE SIGNAL DEGRADED // DO NOT DECODE</text>
</svg>
`;
}

fs.mkdirSync(OUT, { recursive: true });
for (let i = 0; i < theories.length; i++) {
  const [id, title, slug] = theories[i];
  fs.writeFileSync(path.join(OUT, slug + ".svg"), makeSvg(id, title, i));
  console.log("wrote", slug + ".svg");
}
