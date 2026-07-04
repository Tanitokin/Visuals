# THE GREAT ABYSS DATABASE

Retro haunted alien-threat console menu for
**"The Most Terrifying Alien Civilization Scenarios That Might Actually Be Real Vol. 2"**.

**Single self-contained `index.html`** — CSS, JS and the three retro fonts are
inlined, and the corrupted-archive image placeholders are generated at
runtime. Double-click `index.html` in Chrome and it works, no server needed.

Flow: start screen (`CLICK TO INITIALIZE DATABASE`, unlocks audio) → boot
sequence → cursor scans the 12 theory files → locks on one file → heavy
glitch → loops forever. Designed for 1920x1080 screen recording (the stage is
a fixed 1920x1080 canvas scaled to fit the window — record fullscreen at
1080p for a pixel-perfect capture).

## Edit

Everything lives in `index.html`:

- **Timings, lock file, loop behavior** → `CONFIG` at the top of the `<script>`
  (`stepInterval`, `lockIndex`, `lockDuration`, `loop`, `loopToBoot`, …).
- **Sound files and volumes** → the `AUDIO` object right below `CONFIG`.
- **The 12 theories** → the `theories` array.
- **Boot lines** → `BOOT_LINES`.
- **Colors / fonts / effect intensity** → `:root` variables and the `.fx`
  overlays in the `<style>` block.

## Images

Drop real archive images into `assets/` next to `index.html`, using the exact
filenames from the `theories` array (e.g. `assets/flesh-gardeners.png`).
Until then each file shows a generated corrupted-archive placeholder with the
theory name.

## Audio

Optional — the menu is fully silent (and error-free) until you add the files.
See `assets/audio/README.md` for the five expected filenames and volumes.
Audio starts after the initial click (browsers block autoplay audio).

## Controls

- **Click / `Space`** — initialize (start screen)
- `↓` / `↑` — next / previous theory (pauses autoplay)
- `Enter` — lock the current file (stronger glitch)
- `Space` — pause / resume autoplay
- `M` (or click the corner toggle) — audio on / off

See `SKILL.md` for the full design spec.
