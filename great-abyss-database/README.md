# THE GREAT ABYSS DATABASE

Retro haunted alien-threat console menu for
**"The Most Terrifying Alien Civilization Scenarios That Might Actually Be Real Vol. 2"**.

Plain HTML/CSS/JS, no frameworks. Autoplays: boot sequence → cursor scans the
12 theory files → locks on one file → heavy glitch → loops forever.
Designed for 1920x1080 screen recording (the stage is a fixed 1920x1080 canvas
scaled to fit the window — record fullscreen at 1080p for a pixel-perfect capture).

## Run

```bash
cd great-abyss-database
python3 -m http.server 8123      # any static server works
# open http://localhost:8123
```

(A server is needed because the page loads local fonts/images; opening
`index.html` directly via file:// also works in most browsers.)

## Edit

- **Timings, lock file, loop behavior** → `CONFIG` at the top of `script.js`
  (`stepInterval`, `lockIndex`, `lockDuration`, `loop`, `loopToBoot`, …).
- **The 12 theories** → the `theories` array in `script.js`.
- **Boot lines / ticker copy** → `BOOT_LINES` and `TICKER_TEXT` in `script.js`.
- **Colors / fonts / effect intensity** → `:root` variables and the `.fx`
  overlays in `styles.css`.

## Images

Drop your real archive images into `assets/` using the exact filenames from
the `theories` array (e.g. `assets/flesh-gardeners.png`). Until then the page
automatically falls back to the generated corrupted-archive SVGs in
`assets/placeholders/`, and if even those are missing it shows a dark
`IMAGE SIGNAL CORRUPTED` frame. Regenerate the placeholders with:

```bash
node tools/gen-placeholders.js
```

## Keyboard (optional — autoplay needs no input)

- `↓` / `↑` — next / previous theory (pauses autoplay)
- `Enter` — lock the current file (stronger glitch)
- `Space` — pause / resume autoplay

See `SKILL.md` for the full design spec.
