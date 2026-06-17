"""crt_style.py - reusable "green CRT terminal" toolkit for Manim CE.

Import this to build new scenes in the WORST CITIES / archive-terminal style:

    from crt_style import *

    class MyScene(CRTScene):
        def construct(self):
            self.start_crt()                       # bg + clock + scanlines + hum
            title = self.txt("HELLO", 48, GREEN_BRT)
            self.play(FadeIn(title))
            self.wait(1)

Provides: palette, fonts, alignment + glow helpers, CRT ambience (scanlines,
drifting glow band, subtle flicker), a blinking-cursor helper, a cool segmented
loading bar, and easy access to the synthesized SFX in assets/audio/.

Reference implementations: boot.py (WorstCitiesBoot) and worst_cities.py.
"""

import os

import numpy as np
from manim import *

# --- Neon-green palette ---------------------------------------------------
BG         = "#04110B"   # green-black background
GREEN      = "#3DFF7A"   # primary neon green
GREEN_BRT  = "#CFFFDD"   # bright / highlight
GREEN_DIM  = "#1F8A45"   # dim / secondary
RED        = "#FF4D4D"   # alarm / high threat
BORDER     = "#1F8A45"   # panel borders
PANEL_FILL = "#08180F"   # panel fill
COVER_FILL = "#040D08"   # image/cover backing

# --- Fonts (installed under assets/fonts, registered via fontconfig) -------
# Body/title default: VT323 (clean CRT terminal). Also available if installed:
# "Press Start 2P", "Oxanium", "Xolonium", "TESLA", "Share Tech Mono".
FONT_BODY  = "VT323"
FONT_TITLE = "VT323"

# --- Asset paths ----------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (file lives in scenes/)
AUDIO_DIR = os.path.join(BASE, "assets", "audio")
COVER_DIR = os.path.join(BASE, "assets", "covers")


def snd(name):
    """Absolute path to a sound in assets/audio (e.g. snd('key.wav'))."""
    return os.path.join(AUDIO_DIR, name)


# Synthesized SFX shipped in assets/audio (see scripts that generated them):
#   crt_hum.wav  - CRT/computer background hum (loopable ambience)
#   boot.wav     - power-on clunk + hum rise
#   key.wav      - mechanical key "thock" (per log line / per keystroke)
#   click.wav    - bigger mechanical clunk (a confirm/hit)
#   access.wav   - ACCESS GRANTED: click + bright ascending confirm
#   charge.wav   - accelerating ratchet (final bar rush)
#   transition.wav, blip.wav, loaded.wav, confirm.wav ... (extra UI sfx)


# =========================================================================
# Small helpers
# =========================================================================
def left(mob, x, y):
    """Place a mobject with its LEFT edge at (x, y)."""
    mob.move_to([x, y, 0]).align_to([x, y, 0], LEFT)
    return mob


def right(mob, x, y):
    """Place a mobject with its RIGHT edge at (x, y)."""
    mob.move_to([x, y, 0]).align_to([x, y, 0], RIGHT)
    return mob


def neon(mob, color=GREEN, widths=(6, 3), ops=(0.10, 0.20)):
    """Wrap a mobject in soft stroke halos for a neon glow (use sparingly)."""
    g = VGroup()
    for w, o in zip(widths, ops):
        h = mob.copy().set_stroke(color, width=w, opacity=o)
        h.set_fill(opacity=0)
        g.add(h)
    g.add(mob)
    return g


def scanlines(opacity=0.11, spacing=0.15, z_index=15):
    """Static full-frame CRT scanlines."""
    return VGroup(*[
        Line([-7.2, y, 0], [7.2, y, 0], color=BG, stroke_width=2, stroke_opacity=opacity)
        for y in np.arange(-4.0, 4.0, spacing)
    ]).set_z_index(z_index)


def crt_overlays(clock):
    """A slow drifting glow band + a subtle global brightness flicker.

    Both are driven by `clock` (a ValueTracker advanced by dt). Returns
    (drift_band, flicker_overlay); add them to the scene."""
    drift = Rectangle(width=15, height=0.7, stroke_width=0,
                      fill_color=GREEN, fill_opacity=0.05).set_z_index(13)
    drift.add_updater(lambda m: m.move_to([0, 4.2 - ((clock.get_value() * 1.7) % 8.4), 0]))

    flick = Rectangle(width=15, height=8.6, stroke_width=0,
                      fill_color=BG, fill_opacity=0.0).set_z_index(38)

    def flick_up(m):
        t = clock.get_value()
        base = 0.02 + 0.025 * (0.5 + 0.5 * np.sin(t * 6.3))
        spike = 0.06 if (np.sin(t * 47.0) > 0.93) else 0.0
        m.set_opacity(base + spike)
    flick.add_updater(flick_up)
    return drift, flick


def blink_on(clock, period=0.7, duty=0.6):
    """True for the 'on' part of a blink cycle (drive cursors/highlights)."""
    return (clock.get_value() % period) < period * duty


def make_segmented_bar(prog, clock, bar_l, bar_w, bar_y, nseg=44, height=0.2, glow=True):
    """Return a builder for an always_redraw segmented loading bar.

        bar = always_redraw(make_segmented_bar(prog, self.clock, -6.6, 11.2, -2.95))
    `prog` is a ValueTracker in [0, 1]."""
    seg_w = bar_w / nseg

    def builder():
        val = prog.get_value()
        edge = int(val * nseg)
        g = VGroup()
        for k in range(nseg):
            cx = bar_l + (k + 0.5) * seg_w
            if k < edge:
                g.add(Rectangle(width=seg_w * 0.74, height=height, stroke_width=0,
                                fill_color=GREEN, fill_opacity=1).move_to([cx, bar_y, 0]))
            elif k == edge and val < 0.999:
                p = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(clock.get_value() * 26))
                g.add(Rectangle(width=seg_w * 0.74, height=height, stroke_width=0,
                                fill_color=GREEN_BRT, fill_opacity=p).move_to([cx, bar_y, 0]))
            else:
                g.add(Rectangle(width=seg_w * 0.74, height=height, stroke_width=1,
                                stroke_color=GREEN_DIM, fill_opacity=0).move_to([cx, bar_y, 0]))
        if glow:
            fw = max(0.001, bar_w * val)
            gl = Rectangle(width=fw, height=height, stroke_width=0, fill_opacity=0)
            gl.move_to([bar_l + fw / 2, bar_y, 0]).set_stroke(GREEN, 7, 0.18)
            return VGroup(gl, g)
        return g
    return builder


def blink_cursor(width=0.16, height=0.30, clock=None, period=0.5, color=GREEN):
    """A block cursor that blinks. Pass a clock to animate it, then .next_to(...)."""
    cur = Rectangle(width=width, height=height, stroke_width=0,
                    fill_color=color, fill_opacity=1)
    if clock is not None:
        cur.add_updater(lambda m: m.set_opacity(1.0 if blink_on(clock, period) else 0.0))
    return cur


# =========================================================================
# Base scene
# =========================================================================
class CRTScene(Scene):
    """Scene with the green-CRT look wired up.

    Call self.start_crt() at the top of construct() to get the dark-green
    background, a running self.clock, scanlines, drifting glow + flicker, and
    the CRT hum background track. Use self.txt(...) for terminal text and
    self.blink() for cursor/highlight blinking."""

    def start_crt(self, ambience=True, hum=True, hum_gain=-10):
        self.camera.background_color = BG
        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        if ambience:
            self.scan = scanlines()
            self.drift, self.flick = crt_overlays(self.clock)
            self.add(self.scan, self.drift, self.flick)
        if hum and os.path.exists(snd("crt_hum.wav")):
            self.add_sound(snd("crt_hum.wav"), gain=hum_gain)

    def txt(self, s, size, color=GREEN, font=FONT_BODY):
        return Text(s, font=font, font_size=size, color=color)

    def blink(self, period=0.7, duty=0.6):
        return blink_on(self.clock, period, duty)

    def flash(self, op=0.25, color=GREEN, z_index=40):
        """Quick full-screen flash (e.g. on ACCESS GRANTED)."""
        fl = Rectangle(width=15, height=8.6, stroke_width=0,
                       fill_color=color, fill_opacity=0.0).set_z_index(z_index)
        self.add(fl)
        self.play(fl.animate.set_fill(color, opacity=op), run_time=0.06)
        self.play(fl.animate.set_fill(color, opacity=0.0), run_time=0.16, rate_func=smooth)
        self.remove(fl)
