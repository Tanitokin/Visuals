# Green-CRT terminal template (Manim CE)

A reusable "WORST CITIES / archive-terminal" style: neon-green phosphor UI on a
dark CRT, pixel/terminal fonts, scanlines + glow + subtle flicker, segmented
loading bars, blinking cursors, and synthesized mechanical SFX + CRT hum.

## Files

| File | What it is |
|------|------------|
| `crt_style.py` | **The toolkit.** Palette, fonts, helpers, CRT ambience, segmented bar, `CRTScene` base class. Import this. |
| `template_scene.py` | **Minimal starter.** Copy it to begin a new scene (`CRTTemplate`). |
| `boot.py` | Reference: a boot / loading screen (`WorstCitiesBoot`). |
| `worst_cities.py` | Reference: a ranked countdown menu with covers (`WorstCities`). |
| `assets/fonts/` | Fonts (VT323, Press Start 2P, Oxanium, Xolonium, TESLA, Share Tech Mono…). |
| `assets/audio/` | Synthesized SFX + `crt_hum.wav` background. |
| `assets/covers/` | Per-item cover images (used by `worst_cities.py`). |

## Quick start

```python
from crt_style import *

class MyScene(CRTScene):
    def construct(self):
        self.start_crt()                       # bg + clock + scanlines + hum
        title = left(self.txt("MY TITLE", 64, GREEN_BRT), -6.55, 2.3)
        self.play(FadeIn(title))
        self.wait(1)
```

Render: `./.venv/bin/manim -pqh --fps 30 my_scene.py MyScene`

## What `CRTScene` gives you

- `self.start_crt()` — dark-green bg, a running `self.clock` (for blinks/animation),
  scanlines, a drifting glow band, a subtle brightness flicker, and the CRT hum.
- `self.txt(s, size, color, font)` — terminal text (defaults to VT323 / green).
- `self.blink(period, duty)` — bool for blinking cursors/highlights.
- `self.flash(op, color)` — quick full-screen flash (e.g. on ACCESS GRANTED).

## Toolkit helpers (in `crt_style`)

- `left(mob, x, y)` / `right(mob, x, y)` — edge-aligned placement.
- `neon(mob, color, widths, ops)` — soft glow halos (use sparingly).
- `scanlines()`, `crt_overlays(clock)` — CRT ambience pieces.
- `blink_on(clock, period, duty)` — blink timing.
- `blink_cursor(clock=...)` — a ready-made blinking block cursor.
- `make_segmented_bar(prog, clock, bar_l, bar_w, bar_y)` — build a cool segmented
  loading bar: `bar = always_redraw(make_segmented_bar(prog, self.clock, -6.6, 11.2, -2.95))`.

## Palette

`BG` `GREEN` `GREEN_BRT` `GREEN_DIM` `RED` (alarm) `BORDER` `PANEL_FILL` `COVER_FILL`.

## Sound effects (`snd("name.wav")`)

`crt_hum.wav` (background), `boot.wav`, `key.wav` (mechanical thock per line),
`click.wav` (clunk), `access.wav` (ACCESS GRANTED), `charge.wav` (ratchet rush),
plus `transition.wav`, `blip.wav`, `loaded.wav`, `confirm.wav`.

Typical: `self.add_sound(snd("key.wav"), gain=-5)` (gain in dB; 0 = loudest).

## Fonts

Default `FONT_BODY = FONT_TITLE = "VT323"`. Swap by passing `font=` to `self.txt`
or changing the constants. Installed families: `VT323`, `Press Start 2P`,
`Oxanium`, `Xolonium`, `TESLA`, `Share Tech Mono`.

> Fonts must be visible to fontconfig. They live in `assets/fonts/`; in a fresh
> environment install them once: `cp assets/fonts/*.ttf assets/fonts/*.otf
> ~/.local/share/fonts/ && fc-cache -f`.

## Environment

Rendering uses the local `./.venv` (Manim CE 0.20.1). System deps: cairo, pango,
ffmpeg. To recreate: `python -m venv .venv && ./.venv/bin/pip install manim`.
