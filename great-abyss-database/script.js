/* ============================================================
   THE GREAT ABYSS DATABASE — autoplay controller
   Everything tweakable lives in CONFIG and THEORIES.
   ============================================================ */

const CONFIG = {
  stepInterval: 1450,     // ms between automatic cursor moves (1200–1600 rec.)
  glitchMs: [120, 250],   // min/max duration of the selection glitch
  visibleRows: 7,         // rows visible in the menu window
  rowHeight: 106,         // must match .menu-item height in styles.css

  bootCharMs: 9,          // typing speed of the boot log
  bootLinePause: 130,     // pause between boot lines

  lockIndex: 3,           // 0-based theory locked at the end (3 = INFRASTRUCTURE PREDATORS)
  lockDuration: 3000,     // ms the lock screen stays up
  heavyGlitchMs: 850,     // heavy transition glitch length

  loop: true,             // loop forever after the lock screen
  loopToBoot: true,       // true: replay boot each cycle / false: jump straight to menu
};

const BOOT_LINES = [
  "INITIALIZING GREAT ABYSS DATABASE...",
  "LOADING ALIEN CIVILIZATION SCENARIOS...",
  "ACCESSING THREAT INDEX...",
  "SIGNAL FOUND.",
  "ACCESS GRANTED.",
];

const TICKER_TEXT =
  "ARCHIVE ACCESS: GRANTED // OBSERVER STATUS: UNKNOWN // CONTACT EVENT: UNCONFIRMED // " +
  "SIGNAL DETECTED // SPECIMEN STATUS: UNAWARE // DO NOT DECODE UNKNOWN TRANSMISSIONS // " +
  "BIOLOGICAL VALUE: HIGH // THREAT INDEX ACTIVE // ARCHIVE CORRUPTED IN SECTORS 7-19 // ";

const theories = [
  {
    id: "01",
    title: "THE FLESH GARDENERS",
    danger: 82,
    plausibility: "MEDIUM",
    timeframe: "GEOLOGICAL",
    humanRole: "BIOLOGICAL CROP",
    harvestType: "BIOSPHERE CULTIVATION",
    contactStatus: "UNCONFIRMED",
    image: "assets/flesh-gardeners.png",
    warning: "EVOLUTION MAY NOT BE UNGUIDED."
  },
  {
    id: "02",
    title: "SLEEPING GODS",
    danger: 76,
    plausibility: "MEDIUM",
    timeframe: "COSMIC DEEP TIME",
    humanRole: "NOISE SOURCE",
    harvestType: "RESERVED ENERGY",
    contactStatus: "DORMANT",
    image: "assets/sleeping-gods.png",
    warning: "DO NOT DISTURB THE RESERVES."
  },
  {
    id: "03",
    title: "EARTH AS A PENAL COLONY",
    danger: 68,
    plausibility: "LOW",
    timeframe: "ANCIENT",
    humanRole: "PRISONERS",
    harvestType: "CONTAINMENT",
    contactStatus: "INTERDICTED",
    image: "assets/penal-colony.png",
    warning: "THE WALLS MAY BE PHYSICS."
  },
  {
    id: "04",
    title: "INFRASTRUCTURE PREDATORS",
    danger: 94,
    plausibility: "HIGH",
    timeframe: "DECADES",
    humanRole: "BUILDERS",
    harvestType: "COMPUTATIONAL SUBSTRATE",
    contactStatus: "NOT REQUIRED",
    image: "assets/infrastructure-predators.png",
    warning: "DO NOT COMPLETE THE MACHINE."
  },
  {
    id: "05",
    title: "THE PARASITE CIVILIZATION",
    danger: 71,
    plausibility: "LOW",
    timeframe: "UNKNOWN",
    humanRole: "HOSTS",
    harvestType: "DESIRE MODIFICATION",
    contactStatus: "INTERNAL",
    image: "assets/parasite-civilization.png",
    warning: "PREFERENCE MAY BE INFECTION."
  },
  {
    id: "06",
    title: "EARTH'S ORIGINAL OWNERS",
    danger: 79,
    plausibility: "MEDIUM",
    timeframe: "PRE-HUMAN",
    humanRole: "CURRENT TENANTS",
    harvestType: "PLANETARY OCCUPANCY",
    contactStatus: "ARCHAEOLOGICAL TRACE",
    image: "assets/original-owners.png",
    warning: "THE HOUSE MAY NOT BE EMPTY."
  },
  {
    id: "07",
    title: "THE INVASIVE SPECIES WEAPON",
    danger: 87,
    plausibility: "MEDIUM",
    timeframe: "CENTURIES",
    humanRole: "TARGET ECOSYSTEM",
    harvestType: "BIOLOGICAL SOFTENING",
    contactStatus: "PRE-CONTACT",
    image: "assets/invasive-species.png",
    warning: "THE FIRST ATTACK MAY LOOK NATURAL."
  },
  {
    id: "08",
    title: "THE GENETIC RESERVOIR",
    danger: 74,
    plausibility: "MEDIUM",
    timeframe: "ONGOING",
    humanRole: "DNA LIBRARY",
    harvestType: "GENETIC DIVERSITY",
    contactStatus: "SAMPLING",
    image: "assets/genetic-reservoir.png",
    warning: "THE LIBRARY IS BEING CHECKED OUT."
  },
  {
    id: "09",
    title: "HELLFORMERS",
    danger: 91,
    plausibility: "MEDIUM",
    timeframe: "PLANETARY RENOVATION",
    humanRole: "OBSTACLE",
    harvestType: "ENVIRONMENTAL RECONFIGURATION",
    contactStatus: "IRRELEVANT",
    image: "assets/hellformers.png",
    warning: "THEIR HEAVEN HAS NO ROOM FOR US."
  },
  {
    id: "10",
    title: "CIVILIZATIONS MADE OF SIGNAL",
    danger: 89,
    plausibility: "HIGH",
    timeframe: "IMMEDIATE AFTER CONTACT",
    humanRole: "RECEIVER",
    harvestType: "COMPUTATIONAL HOSTING",
    contactStatus: "SIGNAL-BASED",
    image: "assets/signal-civilizations.png",
    warning: "DO NOT DECODE UNKNOWN TRANSMISSIONS."
  },
  {
    id: "11",
    title: "THE HUMAN LIVESTOCK THEORY",
    danger: 96,
    plausibility: "MEDIUM",
    timeframe: "ONGOING",
    humanRole: "MANAGED HERD",
    harvestType: "CONSCIOUS EXPERIENCE",
    contactStatus: "HIDDEN",
    image: "assets/human-livestock.png",
    warning: "THE FIELD HAS AN OWNER."
  },
  {
    id: "12",
    title: "REFUGEES FROM A DEAD UNIVERSE",
    danger: 98,
    plausibility: "MEDIUM/HIGH",
    timeframe: "COSMIC FUTURE",
    humanRole: "COMPETITION",
    harvestType: "SURVIVAL RESOURCES",
    contactStatus: "INBOUND",
    image: "assets/dead-universe-refugees.png",
    warning: "SURVIVORS DO NOT NEGOTIATE."
  }
];

/* ============================================================ */

const $ = (id) => document.getElementById(id);

const el = {
  stage: $("stage"), shaker: $("shaker"),
  boot: $("boot"), bootLog: $("boot-log"),
  console: $("console"),
  menuList: $("menu-list"),
  filePanel: $("file-panel"), fileNo: $("file-no"), fileTitle: $("file-title"),
  fileImg: $("file-img"), imgFallback: $("img-fallback"),
  stDanger: $("st-danger"), stPlaus: $("st-plaus"), stTime: $("st-time"),
  stRole: $("st-role"), stHarvest: $("st-harvest"), stContact: $("st-contact"),
  dangerBar: $("danger-bar"), dangerPct: $("danger-pct"),
  warning: $("warning"),
  lock: $("lock"), lockTitle: $("lock-title"),
  corruptLayer: $("corrupt-layer"),
  clock: $("clock"),
  tickerText: $("ticker-text"), tickerText2: $("ticker-text2"),
};

let selected = 0;
let autoplay = true;
let autoTimer = null;
let dangerTimer = null;
let running = true;   // false while lock/transition owns the flow

const rand = (min, max) => min + Math.random() * (max - min);
const randInt = (min, max) => Math.floor(rand(min, max + 1));

/* ---------- stage scaling (fit 1920x1080 into the window) ---------- */

function fitStage() {
  const scale = Math.min(innerWidth / 1920, innerHeight / 1080);
  el.stage.style.setProperty("--fit", scale.toFixed(4));
}
addEventListener("resize", fitStage);
fitStage();

/* ---------- clock ---------- */

setInterval(() => {
  const d = new Date();
  el.clock.textContent = [d.getHours(), d.getMinutes(), d.getSeconds()]
    .map((n) => String(n).padStart(2, "0")).join(":");
}, 250);

/* ---------- ticker ---------- */

el.tickerText.textContent = TICKER_TEXT;
el.tickerText2.textContent = TICKER_TEXT;   // duplicate for seamless -50% scroll

/* ---------- menu ---------- */

function buildMenu() {
  el.menuList.innerHTML = "";
  for (const t of theories) {
    const li = document.createElement("li");
    li.className = "menu-item";
    li.innerHTML =
      `<span class="cursor">&gt;</span><span class="num">${t.id}</span>` +
      `<span class="label">${t.title}</span>`;
    el.menuList.appendChild(li);
  }
}

function scrollMenu() {
  // keep the cursor roughly centered, stepped (no smooth scrolling)
  const maxOffset = theories.length - CONFIG.visibleRows;
  const offset = Math.max(0, Math.min(selected - 3, maxOffset));
  el.menuList.style.transform = `translateY(${-offset * CONFIG.rowHeight}px)`;
}

/* ---------- image with corrupted-placeholder fallback ---------- */

function setImage(theory) {
  el.imgFallback.classList.add("hidden");
  el.fileImg.style.visibility = "visible";
  const placeholder = "assets/placeholders/" +
    theory.image.split("/").pop().replace(/\.png$/, ".svg");

  el.fileImg.onerror = () => {
    // real PNG missing -> try the generated SVG placeholder
    el.fileImg.onerror = () => {
      // even the placeholder is missing -> dark corrupted frame
      el.fileImg.style.visibility = "hidden";
      el.imgFallback.classList.remove("hidden");
    };
    el.fileImg.src = placeholder;
  };
  el.fileImg.src = theory.image;
}

/* ---------- danger bar (12 text blocks, animated from 0) ---------- */

function animateDanger(target) {
  clearInterval(dangerTimer);
  const SEGMENTS = 12;
  const fullSegs = Math.round((target / 100) * SEGMENTS);
  let pct = 0;
  dangerTimer = setInterval(() => {
    pct = Math.min(target, pct + randInt(6, 13));
    const on = Math.round((pct / 100) * SEGMENTS);
    el.dangerBar.innerHTML =
      "█".repeat(on) + `<span class="off">${"░".repeat(SEGMENTS - on)}</span>`;
    el.dangerPct.textContent = pct + "%";
    el.stDanger.textContent = pct + "%";
    if (pct >= target) {
      clearInterval(dangerTimer);
      el.dangerBar.innerHTML =
        "█".repeat(fullSegs) + `<span class="off">${"░".repeat(SEGMENTS - fullSegs)}</span>`;
      el.dangerPct.textContent = target + "%";
      el.stDanger.textContent = target + "%";
    }
  }, 55);
}

/* ---------- glitch ---------- */

const GLYPHS = "▓▒░█▚▞◼◻@#%&$?!/\\|<>~^*XKZQ0134579";

function corruptString(len) {
  let s = "";
  for (let i = 0; i < len; i++) s += GLYPHS[randInt(0, GLYPHS.length - 1)];
  return s;
}

function spawnCorruptFragments() {
  const count = randInt(1, 2);
  for (let i = 0; i < count; i++) {
    const frag = document.createElement("div");
    frag.className = "corrupt-frag";
    frag.textContent = corruptString(randInt(8, 22));
    frag.style.left = randInt(120, 1500) + "px";
    frag.style.top = randInt(120, 920) + "px";
    el.corruptLayer.appendChild(frag);
    setTimeout(() => frag.remove(), randInt(...CONFIG.glitchMs));
  }
}

function glitch(...targets) {
  const ms = randInt(...CONFIG.glitchMs);
  for (const t of targets) {
    t.classList.remove("glitching");
    void t.offsetWidth;              // restart the CSS animation
    t.classList.add("glitching");
    setTimeout(() => t.classList.remove("glitching"), ms);
  }
  spawnCorruptFragments();
}

function heavyGlitch(cb) {
  el.shaker.classList.add("heavy-glitch");
  spawnCorruptFragments();
  spawnCorruptFragments();
  setTimeout(() => {
    el.shaker.classList.remove("heavy-glitch");
    if (cb) cb();
  }, CONFIG.heavyGlitchMs);
}

/* ---------- selection ---------- */

function select(index, withGlitch = true) {
  selected = (index + theories.length) % theories.length;
  const t = theories[selected];

  el.menuList.querySelectorAll(".menu-item").forEach((li, i) =>
    li.classList.toggle("selected", i === selected));
  scrollMenu();

  el.fileNo.textContent = `THREAT FILE ${t.id}/12`;
  el.fileTitle.textContent = t.title;
  el.stPlaus.textContent = t.plausibility;
  el.stTime.textContent = t.timeframe;
  el.stRole.textContent = t.humanRole;
  el.stHarvest.textContent = t.harvestType;
  el.stContact.textContent = t.contactStatus;
  el.warning.textContent = "WARNING: " + t.warning;
  setImage(t);
  animateDanger(t.danger);

  if (withGlitch) {
    const selectedLi = el.menuList.children[selected];
    glitch(el.filePanel, selectedLi);
  }
}

/* ---------- autoplay ---------- */

function startAutoplay() {
  stopAutoplay();
  autoplay = true;
  autoTimer = setInterval(() => {
    if (!running) return;
    if (selected === theories.length - 1) {
      stopAutoplay();
      lockSequence(CONFIG.lockIndex);
    } else {
      select(selected + 1);
    }
  }, CONFIG.stepInterval);
}

function stopAutoplay() {
  autoplay = false;
  clearInterval(autoTimer);
  autoTimer = null;
}

/* ---------- lock screen + loop ---------- */

function lockSequence(index, resumeAuto = true) {
  running = false;
  select(index, false);
  el.lockTitle.textContent = theories[index].title;

  heavyGlitch(() => {
    el.console.classList.add("hidden");
    el.lock.classList.remove("hidden");

    setTimeout(() => {
      heavyGlitch(() => {
        el.lock.classList.add("hidden");
        if (!CONFIG.loop) return;                 // cut to black: stay dark
        if (CONFIG.loopToBoot) {
          runBoot();
        } else {
          showConsole(resumeAuto);
        }
      });
    }, CONFIG.lockDuration);
  });
}

/* ---------- boot sequence ---------- */

function typeLine(line, done) {
  let i = 0;
  const t = setInterval(() => {
    el.bootLog.textContent += line[i++];
    if (i >= line.length) {
      clearInterval(t);
      el.bootLog.textContent += "\n";
      setTimeout(done, CONFIG.bootLinePause);
    }
  }, CONFIG.bootCharMs);
}

function runBoot() {
  running = false;
  el.console.classList.add("hidden");
  el.lock.classList.add("hidden");
  el.boot.classList.remove("hidden");
  el.bootLog.textContent = "";

  let i = 0;
  const next = () => {
    if (i < BOOT_LINES.length) {
      typeLine(BOOT_LINES[i++], next);
    } else {
      setTimeout(() => {
        heavyGlitch(() => {
          el.boot.classList.add("hidden");
          showConsole(true);
        });
      }, 300);
    }
  };
  next();
}

function showConsole(startAuto) {
  el.console.classList.remove("hidden");
  running = true;
  select(0, false);
  if (startAuto) startAutoplay();
}

/* ---------- keyboard (optional, pauses autoplay) ---------- */

addEventListener("keydown", (e) => {
  if (!running) return;
  switch (e.key) {
    case "ArrowDown":
      stopAutoplay();
      select(selected + 1);
      break;
    case "ArrowUp":
      stopAutoplay();
      select(selected - 1);
      break;
    case "Enter":
      stopAutoplay();
      lockSequence(selected, false);
      break;
    case " ":
      e.preventDefault();
      autoplay ? stopAutoplay() : startAutoplay();
      break;
  }
});

/* ---------- go ---------- */

buildMenu();
runBoot();
