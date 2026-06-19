# Visuals

Green-CRT terminal motion graphics, made with [Manim](https://www.manim.community/).
A reusable "archive terminal" style (neon-green phosphor UI, scanlines, glow,
segmented loading bars, mechanical SFX) plus a few standalone animations.

## Structure

```
.
├── README.md
├── setup.sh                 # one-shot env bootstrap (fonts + venv + deps)
├── scenes/                  # all Manim scenes
│   ├── crt_style.py         # the reusable CRT toolkit (CRTScene + helpers)
│   ├── template_scene.py    # minimal starter — copy to begin a new scene
│   ├── boot.py              # WORST CITIES boot / loading screen
│   ├── worst_cities.py      # WORST CITIES ranked countdown menu
│   ├── divinity_index.py    # ARTIFICIAL DIVINITY INDEX 2x5 select screen
│   ├── divinity_loader.py   # ARCHIVE ACCESS PROTOCOL corporate loading screen
│   ├── cycloid.py           # a rolling-circle cycloid animation
│   └── orbital_uplink.py    # a satellite / ground-station animation
├── docs/
│   └── TEMPLATE.md          # how to use the CRT toolkit
├── assets/
│   ├── fonts/               # VT323, Press Start 2P, Oxanium, Xolonium, TESLA…
│   ├── audio/               # synthesized SFX + CRT hum
│   └── covers/              # per-city cover images (worst_cities)
└── .claude/                 # SessionStart hook that runs setup.sh on web sessions
```

## Quick start

```bash
bash setup.sh                                            # fonts + .venv + Manim
./.venv/bin/manim -pqh --fps 30 scenes/boot.py WorstCitiesBoot
```

Quality flags: `-ql` (480p draft) · `-qh` (1080p) · add `--fps 30`.
Output lands in `media/` (git-ignored).

## Scenes

| Scene file | Class | What it is |
|------------|-------|------------|
| `scenes/boot.py` | `WorstCitiesBoot` | CRT boot sequence: log ticks off, bar fills, ACCESS GRANTED. |
| `scenes/worst_cities.py` | `WorstCities` | Ranked countdown #13→#01 with covers + dossier. |
| `scenes/divinity_index.py` | `DivinityIndex` | "ARTIFICIAL DIVINITY INDEX" 2×5 god-select screen: cursor steps 01→10, selected in colour + name, others b/w, per-god select-click + fade-to-black. Images in `assets/divinity/`. |
| `scenes/divinity_loader.py` | `DivinityLoader` | "ARCHIVE ACCESS PROTOCOL" ~5s corporate loading screen (emblem, bar, status lines, ACCESS GRANTED) that plays before the selector. Font: TheSansMonoSCd. |
| `scenes/template_scene.py` | `CRTTemplate` | Minimal starter using the toolkit. |
| `scenes/cycloid.py` | `CycloidScene` | Rolling circle traces a cycloid. |
| `scenes/orbital_uplink.py` | `OrbitalUplink` | Satellite orbiting a wireframe planet. |

## Making something new

```python
from crt_style import *          # scenes/template_scene.py handles the import path

class MyScene(CRTScene):
    def construct(self):
        self.start_crt()          # bg + clock + scanlines + CRT hum
        self.play(FadeIn(left(self.txt("HELLO", 64, GREEN_BRT), -6.55, 2.3)))
        self.wait(1)
```

See [docs/TEMPLATE.md](docs/TEMPLATE.md) for the full toolkit (palette, fonts,
glow, segmented bar, blinking cursor, SFX).

## Environment

Rendering uses a local `./.venv` (Manim CE 0.20.1) with system libs (cairo,
pango, ffmpeg). `setup.sh` is idempotent; on Claude Code web sessions the
`.claude/` SessionStart hook runs it automatically.
