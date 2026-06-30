"""spooky_inquisitor.py - 5s CRT/VHS horror intro: "SPOOKY INQUISITOR PRESENTS".

Hard-cut analog horror title card (NO smooth fades, no modern motion graphics):

    0.00-0.50  black + subtle analog grain
    0.50-0.85  static burst reveals the logo
    0.85-1.15  logo glitches into place (RGB split, tracking jumps, jitter)
    1.15-3.15  logo readable ~2s while the signal stays unstable
    3.15-3.45  "PRESENTS" snaps in with a short flicker
    3.45-4.40  brief hold
    4.40-4.70  harsh VHS glitch tears the logo apart
    4.70-4.90  full static burst
    4.90-5.00  hard cut to black

Everything is driven by per-frame updaters (jitter, RGB split, scanline flicker,
horizontal tracking errors, snow). No self.play()/fades are used at all.

Render:
    manim -pqh --fps 30 scenes/spooky_inquisitor.py SpookyInquisitorTV
"""

import os
import sys

import numpy as np
from manim import *

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find crt_style next to this file
from crt_style import snd  # reuse the assets/audio path helper

# --- palette --------------------------------------------------------------
BLACK   = "#000000"
WHITE   = "#FFFFFF"
RED     = "#FF2B2B"   # readable phosphor red (logo core)
GHOST_R = "#FF0033"   # red channel ghost
GHOST_C = "#1FE6E6"   # cyan channel ghost (green+blue split)

PIXEL = "Press Start 2P"
FW, FH = 14.22, 8.0   # default 16:9 frame size in Manim units

# --- phase boundaries (seconds) ------------------------------------------
T_GRAIN   = 0.50   # black + subtle grain
T_BURST   = 0.85   # static burst reveal
T_GLITCH  = 1.15   # glitch into place
T_HOLD    = 3.15   # readable hold (~2s)
T_PRES    = 3.45   # PRESENTS flicker in
T_HOLD2   = 4.40   # short hold
T_TEAR    = 4.70   # harsh glitch tears logo
T_SNOW    = 4.90   # full static burst
T_END     = 5.00   # hard cut to black


def noise_level(t):
    """Snow intensity per phase (stepped, never a smooth fade)."""
    if t < T_GRAIN:  return 0.16
    if t < T_BURST:  return 1.00
    if t < T_GLITCH: return 0.32
    if t < T_HOLD:   return 0.07
    if t < T_PRES:   return 0.20
    if t < T_HOLD2:  return 0.08
    if t < T_TEAR:   return 0.40
    if t < T_SNOW:   return 1.00
    return 0.0


def glitch_amt(t):
    """Instability amount [0..~1.3]; spikes are added by the caller per frame."""
    if t < T_BURST:  return 0.0
    if t < T_GLITCH: return 1.10
    if t < T_HOLD:   return 0.16
    if t < T_PRES:   return 0.45
    if t < T_HOLD2:  return 0.22
    if t < T_TEAR:   return 1.20
    if t < T_SNOW:   return 1.20
    return 0.0


class SpookyInquisitorTV(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        np.random.seed(13)

        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # =================================================================
        # Snow / analog noise field (blocky pixel grid).
        # =================================================================
        cols, rows = 52, 30
        cw, ch = FW / cols, FH / rows
        static = VGroup()
        for r in range(rows):
            for c in range(cols):
                sq = Rectangle(width=cw, height=ch, stroke_width=0,
                               fill_color=WHITE, fill_opacity=0.0)
                sq.move_to([-FW / 2 + (c + 0.5) * cw, FH / 2 - (r + 0.5) * ch, 0])
                static.add(sq)
        static.set_z_index(20)
        cells = list(static)

        def static_upd(m):
            lvl = noise_level(clock.get_value())
            if lvl <= 0.0:
                for sq in cells:
                    sq.set_opacity(0.0)
                return
            vals = np.random.uniform(0.04, 0.95, len(cells)) * lvl
            for sq, a in zip(cells, vals):
                sq.set_fill(WHITE, opacity=float(a))
        static.add_updater(static_upd)

        # =================================================================
        # Logo: red core + red/cyan channel ghosts (RGB split).
        # =================================================================
        line1 = Text("SPOOKY", font=PIXEL, color=RED).scale_to_fit_width(8.8).move_to([0, 1.05, 0])
        line2 = Text("INQUISITOR", font=PIXEL, color=RED).scale_to_fit_width(12.4).move_to([0, -0.55, 0])
        core = VGroup(line1, line2).set_z_index(13)
        ghost_r = core.copy().set_color(GHOST_R).set_z_index(11)
        ghost_c = core.copy().set_color(GHOST_C).set_z_index(12)
        TBASE = np.array([0.0, 0.25, 0.0])

        def title_upd(_):
            t = clock.get_value()
            g = glitch_amt(t)
            # random instability spikes while "readable"
            if g and np.random.random() < 0.10 + 0.5 * g:
                g += np.random.uniform(0.2, 0.9)
            vis = 1.0 if (T_GRAIN <= t < T_END and t < T_SNOW + 0.0001) else 0.0
            # heavy snow already hides it during bursts; cut it at the very end
            if t >= T_SNOW:
                vis = 0.0
            # frame jitter + occasional horizontal tracking jump
            jx = np.random.uniform(-1, 1) * 0.045 * g
            jy = np.random.uniform(-1, 1) * 0.035 * g
            if np.random.random() < 0.22 * g:
                jx += np.random.uniform(-1, 1) * 0.55 * g
            base = TBASE + np.array([jx, jy, 0.0])
            split = (0.035 + 0.20 * g)
            if np.random.random() < 0.12:
                split *= 2.6                       # momentary big chroma tear
            core.move_to(base)
            ghost_c.move_to(base + np.array([+split, -0.012, 0.0]))
            ghost_r.move_to(base + np.array([-split, +0.012, 0.0]))
            core.set_opacity(vis)
            ghost_c.set_opacity(0.85 * vis)
            ghost_r.set_opacity(0.85 * vis)
        core.add_updater(title_upd)

        # =================================================================
        # "PRESENTS" - snaps in with a short flicker.
        # =================================================================
        presents = Text("PRESENTS", font=PIXEL, color="#FF6B6B").scale_to_fit_width(5.0)
        presents.move_to([0, -2.55, 0]).set_z_index(13).set_opacity(0.0)
        pr_r = presents.copy().set_color(GHOST_R).set_z_index(11)
        pr_c = presents.copy().set_color(GHOST_C).set_z_index(12)

        def presents_upd(_):
            t = clock.get_value()
            if t < T_PRES:
                on = 0.0
            elif t < T_PRES + 0.30:
                on = 1.0 if (np.random.random() > 0.45) else 0.0   # short flicker
            elif t < T_SNOW:
                on = 1.0
            else:
                on = 0.0
            g = glitch_amt(t)
            split = 0.03 + 0.16 * g
            base = np.array([0, -2.55, 0.0]) + np.array([np.random.uniform(-1, 1) * 0.04 * g, 0, 0])
            presents.move_to(base).set_opacity(on)
            pr_c.move_to(base + np.array([+split, 0, 0])).set_opacity(0.8 * on)
            pr_r.move_to(base + np.array([-split, 0, 0])).set_opacity(0.8 * on)
        presents.add_updater(presents_upd)

        # =================================================================
        # CRT ambience: flickering scanlines, sweeping tracking bar,
        # random dropout lines, brightness flicker / white-flash glitch.
        # =================================================================
        scan = VGroup(*[
            Line([-FW / 2, y, 0], [FW / 2, y, 0], color=BLACK, stroke_width=2.4,
                 stroke_opacity=0.30)
            for y in np.arange(-FH / 2, FH / 2, 0.085)
        ]).set_z_index(30)

        def scan_upd(m):
            g = glitch_amt(clock.get_value())
            m.set_stroke(BLACK, opacity=0.22 + 0.22 * np.random.random() + 0.12 * g)
        scan.add_updater(scan_upd)

        # bright VHS tracking bar that sweeps up the screen
        tbar = Rectangle(width=FW, height=0.5, stroke_width=0,
                         fill_color=WHITE, fill_opacity=0.0).set_z_index(22)

        def tbar_upd(m):
            t = clock.get_value()
            g = glitch_amt(t)
            y = -FH / 2 + ((t * 2.1) % (FH + 1.0))
            op = 0.05 + 0.05 * np.random.random() + 0.18 * g
            m.move_to([np.random.uniform(-1, 1) * 0.2 * g, y, 0]).set_fill(WHITE, opacity=op)
        tbar.add_updater(tbar_upd)

        # random horizontal dropout streaks (signal tears)
        drops = VGroup(*[Line([-FW / 2, 0, 0], [FW / 2, 0, 0], color=WHITE,
                              stroke_width=2, stroke_opacity=0.0) for _ in range(5)]).set_z_index(24)

        def drops_upd(m):
            g = glitch_amt(clock.get_value())
            for ln in m:
                if np.random.random() < 0.10 + 0.45 * g:
                    y = np.random.uniform(-FH / 2 + 0.2, FH / 2 - 0.2)
                    col = WHITE if np.random.random() > 0.4 else BLACK
                    ln.put_start_and_end_on([-FW / 2, y, 0], [FW / 2, y, 0])
                    ln.set_stroke(col, width=float(np.random.uniform(1.5, 5.0)),
                                  opacity=float(np.random.uniform(0.3, 0.9)))
                else:
                    ln.set_stroke(opacity=0.0)
        drops.add_updater(drops_upd)

        # brightness flicker + white-flash on glitches
        flick = Rectangle(width=FW + 1, height=FH + 1, stroke_width=0,
                          fill_color=BLACK, fill_opacity=0.0).set_z_index(36)

        def flick_upd(m):
            g = glitch_amt(clock.get_value())
            if np.random.random() < 0.14 * g:
                m.set_fill(WHITE, opacity=0.12 + 0.22 * np.random.random())
            else:
                m.set_fill(BLACK, opacity=0.03 + 0.06 * np.random.random())
        flick.add_updater(flick_upd)

        # =================================================================
        # Assemble + run. Only self.add / self.wait — no play()/fades.
        # =================================================================
        self.add(ghost_r, ghost_c, core, presents, pr_r, pr_c,
                 static, tbar, drops, scan, flick)

        self.add_sound(snd("ambient.wav"), gain=-15)
        self.wait(T_GRAIN)                                   # black + grain
        self.add_sound(snd("glitch.wav"), gain=-2)
        self.wait(T_BURST - T_GRAIN)                         # static burst reveal
        self.add_sound(snd("glitch.wav"), gain=-7)
        self.wait(T_GLITCH - T_BURST)                        # glitch into place
        self.wait(T_HOLD - T_GLITCH)                         # readable hold (~2s)
        self.add_sound(snd("blip.wav"), gain=-3)
        self.wait(T_PRES - T_HOLD)                           # PRESENTS flicker
        self.wait(T_HOLD2 - T_PRES)                          # short hold
        self.add_sound(snd("glitch.wav"), gain=0)
        self.add_sound(snd("boom.wav"), gain=-5)
        self.wait(T_TEAR - T_HOLD2)                          # harsh tear
        self.wait(T_SNOW - T_TEAR)                           # full static burst
        self.wait(T_END - T_SNOW)                            # hard cut to black
