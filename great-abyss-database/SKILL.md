# SKILL.md — Retro Alien Threat Console Menu

## Objective

Create a reusable animated retro console menu for a YouTube video about alien
civilization theories.

The menu must feel like an old haunted console, a corrupted alien archive, or a
classified threat database from a 90s sci-fi horror game.

The final result should be designed for 1920x1080 screen recording and used as
an intro, transition, or chapter selector in a YouTube video.

The tone should be ominous, analog, degraded, mysterious, and readable.

---

## Core Concept

The interface displays a scrolling list of 12 alien theories on the left.

Each theory is selected automatically one by one.

When a theory is selected, the right panel updates with:

- image
- danger index
- plausibility
- timeframe
- human role
- harvest type
- contact status
- short warning message

The menu should feel like the viewer is accessing forbidden files inside an
alien threat database.

---

## Visual Style

Use this style:

- old console menu
- CRT monitor
- 80s/90s videogame interface
- VHS degradation
- black background
- dirty white, green phosphor, amber, or pale yellow text
- pixel font
- terminal font
- scanlines
- analog flicker
- subtle chromatic aberration
- low FPS jitter
- screen distortion
- corrupted archive feeling

Avoid:

- clean futuristic HUD
- modern dashboard
- corporate UI
- smooth SaaS design
- neon cyberpunk overload
- too many colors
- complex infographic style
- generic AI-looking interface

The design should feel simple, cursed, and functional.

---

## Screen Layout

Use a 16:9 layout optimized for 1920x1080.

### Left Side

A vertical scrolling list of 12 alien theories. Only 6 or 7 items should be
visible at once. The selected item should have a `>` or `►` cursor and flicker
slightly.

```txt
> 01 THE FLESH GARDENERS
  02 SLEEPING GODS
  03 EARTH AS A PENAL COLONY
  04 INFRASTRUCTURE PREDATORS
  05 THE PARASITE CIVILIZATION
  06 EARTH'S ORIGINAL OWNERS
```

### Right Side

A changing threat file panel:

```txt
THREAT FILE 04/12

INFRASTRUCTURE PREDATORS

DANGER INDEX: 94%
PLAUSIBILITY: HIGH
TIMEFRAME: DECADES
HUMAN ROLE: BUILDERS
HARVEST TYPE: COMPUTATIONAL SUBSTRATE
CONTACT STATUS: NOT REQUIRED

WARNING: DO NOT COMPLETE THE MACHINE.
```

Also include a danger bar:

```txt
DANGER [██████████░░] 94%
```

Add a rectangular image frame above or beside the stats. The image should look
like a corrupted archive image, not a clean illustration.

### Bottom Status Bar

Add a bottom ticker or status bar that flickers, blinks, or slowly scrolls:

```txt
ARCHIVE ACCESS: GRANTED // OBSERVER STATUS: UNKNOWN // CONTACT EVENT: UNCONFIRMED
SIGNAL DETECTED // SPECIMEN STATUS: UNAWARE // DO NOT DECODE UNKNOWN TRANSMISSIONS
```

---

## Boot Sequence

Before showing the full menu, include a short boot sequence (1.5–2.5s), then
glitch into the main menu:

```txt
INITIALIZING GREAT ABYSS DATABASE...
LOADING ALIEN CIVILIZATION SCENARIOS...
ACCESSING THREAT INDEX...
SIGNAL FOUND.
ACCESS GRANTED.
```

---

## Animation Rules

The menu must autoplay. Do not require user interaction.

- Start with boot sequence.
- Reveal main interface.
- Move the cursor down automatically every 1.2 to 1.6 seconds.
- Scroll the list vertically as the cursor moves.
- Update the right threat panel when selection changes.
- Trigger a short glitch effect when changing selection.
- Animate the danger bar from 0 to the selected danger percentage.
- Add subtle screen shake or jitter.
- Add CRT scanlines and flicker.
- Loop seamlessly after the 12th theory.

The motion should not feel smooth and modern. It should feel slightly
mechanical, low frame-rate, and analog.

## Timing

- 0.0s–2.0s: boot sequence
- 2.0s–20.0s: menu scrolls through the 12 theories
- 20.0s–23.0s: final selected file locks
- 23.0s–24.0s: heavy glitch transition
- then loop or cut to black

If used as a shorter transition, allow the timing to be adjustable.

---

## Data

Use these exact 12 alien theories (see `script.js` for the canonical array):

01 THE FLESH GARDENERS · 02 SLEEPING GODS · 03 EARTH AS A PENAL COLONY ·
04 INFRASTRUCTURE PREDATORS · 05 THE PARASITE CIVILIZATION ·
06 EARTH'S ORIGINAL OWNERS · 07 THE INVASIVE SPECIES WEAPON ·
08 THE GENETIC RESERVOIR · 09 HELLFORMERS · 10 CIVILIZATIONS MADE OF SIGNAL ·
11 THE HUMAN LIVESTOCK THEORY · 12 REFUGEES FROM A DEAD UNIVERSE

Each entry carries: id, title, danger, plausibility, timeframe, humanRole,
harvestType, contactStatus, image, warning.

---

## Required Files

```txt
/index.html
/styles.css
/script.js
/assets/
```

Use plain HTML, CSS, and JavaScript. No frameworks. The code must be easy to
edit.

## Fonts

- Menu items: Press Start 2P
- Metadata/details: VT323 or Share Tech Mono

## CRT Effects

- Scanlines (repeating-linear-gradient overlay)
- Subtle flicker overlay
- Noise
- Occasional screen distortion
- Effects must be visible but must not make the text unreadable.

## Glitch Rules

When selection changes: briefly distort the selected title, the image, and the
right panel; add a small horizontal offset; show 1 or 2 corrupted text
fragments. The glitch should last between 120ms and 250ms. Do not overuse it —
an old unstable machine, not a TikTok effect.

## Image Style

Each image is displayed inside a degraded archive frame. Low resolution,
monochrome or limited color, CRT degraded, classified-file look, grainy, dark,
slightly pixelated. Use local paths under `assets/`. If images are missing,
show a dark placeholder with text: `IMAGE SIGNAL CORRUPTED`.

## Optional Keyboard Controls

- ArrowDown: next theory
- ArrowUp: previous theory
- Enter: lock selected file (show `FILE SELECTED / ACCESSING SCENARIO...` then
  a stronger glitch)

## Final Lock Screen

After cycling through the list, the system briefly locks onto one file
(configurable in the JavaScript):

```txt
FILE SELECTED:
INFRASTRUCTURE PREDATORS

ACCESSING SCENARIO...
```

Then cut to black or loop.

## UI Copy

Use: ACCESS GRANTED · SIGNAL DETECTED · OBSERVER STATUS: UNKNOWN · SPECIMEN
STATUS: UNAWARE · CONTACT STATUS: UNCONFIRMED · ARCHIVE CORRUPTED · DO NOT
DECODE · DO NOT DISTURB · BIOLOGICAL VALUE: HIGH · THREAT INDEX ACTIVE

Avoid: Welcome · Click here · Loading page · Nice design · Modern interface ·
Dashboard

## Quality Bar

Should look like a haunted retro console menu, an alien threat archive, a
cursed VHS database, an old horror videogame selection screen, a classified
cosmic horror interface. Not a PowerPoint slide, a clean website, a modern
sci-fi dashboard, or a corporate infographic.
