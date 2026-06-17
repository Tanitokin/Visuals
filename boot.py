"""WORST CITIES - boot / initial loading screen.

A simple green-CRT terminal boot sequence: title flickers on, a log of startup
tasks ticks off one by one with check marks while a loading bar fills, ending on
ACCESS GRANTED -> OPENING WORST CITIES DATABASE -> PRESS ENTER TO CONTINUE.

Original layout in the CRT-terminal style (not a copy of any reference).

Render:
    manim -pqh --fps 30 boot.py WorstCitiesBoot
"""

import os

import numpy as np
from manim import *

# --- Neon-green palette ---------------------------------------------------
BG        = "#04110B"
GREEN     = "#3DFF7A"
GREEN_BRT = "#CFFFDD"
GREEN_DIM = "#1F8A45"
BORDER    = "#1F8A45"

FONT_TITLE = "Press Start 2P"
FONT_BODY  = "VT323"

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(name):
    return os.path.join(AUDIO_DIR, name)


BOOT_LINES = [
    "INITIALIZING HAZARD INDEX...",
    "LOADING ARCHIVE: FICTIONAL CITIES",
    "CHECKING THREAT LEVELS...",
    "CONNECTING TO FIELD SURVEY NODE",
    "CALIBRATING DANGER METRICS",
    "PARSING CITY DOSSIERS",
    "RANKING 13 LOCATIONS // 13 TO 01",
    "SYNCING TERMINAL FEED",
    "ACCESS GRANTED",
]


def neon(mob, color, widths=(6, 3), ops=(0.10, 0.20)):
    g = VGroup()
    for w, o in zip(widths, ops):
        h = mob.copy().set_stroke(color, width=w, opacity=o)
        h.set_fill(opacity=0)
        g.add(h)
    g.add(mob)
    return g


class WorstCitiesBoot(Scene):
    def construct(self):
        self.camera.background_color = BG

        def T(s, size, color=GREEN, font=FONT_BODY):
            return Text(s, font=font, font_size=size, color=color)

        def left(mob, x, y):
            mob.move_to([x, y, 0]).align_to([x, y, 0], LEFT)
            return mob

        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))

        def blink(period=0.7, duty=0.6):
            return (clock.get_value() % period) < period * duty

        # --- header + title ---
        header = left(T("WORST CITIES DATABASE  /  BOOT SEQUENCE", 16, GREEN_DIM), -6.6, 3.55)

        title_t = Text("WORST CITIES", font=FONT_TITLE, color=GREEN_BRT).scale_to_fit_width(8.7)
        left(title_t, -6.62, 2.65)
        title = neon(title_t, GREEN, widths=(8, 4), ops=(0.08, 0.16))
        subtitle = left(T("FICTIONAL CITY HAZARD  //  RANKING SYSTEM", 19, GREEN_DIM), -6.58, 1.78)

        # --- boot log lines ---
        log_x, log_y0, log_dy = -6.55, 1.25, 0.315
        lines = []
        for i, txt in enumerate(BOOT_LINES):
            y = log_y0 - i * log_dy
            granted = (txt == "ACCESS GRANTED")
            chk = T("✓", 20, GREEN_BRT)
            left(chk, log_x, y)
            body = T(txt, 20, GREEN_BRT if granted else GREEN)
            left(body, log_x + 0.45, y)
            lines.append(VGroup(chk, body))

        open_y = log_y0 - len(BOOT_LINES) * log_dy - 0.05
        open_t = left(T("> OPENING WORST CITIES DATABASE", 20, GREEN_BRT), log_x, open_y)
        open_cur = Rectangle(width=0.16, height=0.30, stroke_width=0, fill_color=GREEN,
                             fill_opacity=1).next_to(open_t, RIGHT, buff=0.1)
        open_cur.add_updater(lambda m: m.set_opacity(1.0 if blink(0.5) else 0.0))

        # --- loading bar ---
        prog = ValueTracker(0.0)
        bar_l, bar_w, bar_y = -6.6, 11.2, -2.95
        bar_bg = Rectangle(width=bar_w, height=0.2, stroke_color=GREEN_DIM, stroke_width=1,
                           fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])

        def make_bar():
            w = max(0.001, bar_w * prog.get_value())
            r = Rectangle(width=w, height=0.2, stroke_width=0, fill_color=GREEN,
                          fill_opacity=1).move_to([bar_l + w / 2, bar_y, 0])
            return neon(r, GREEN, widths=(7,), ops=(0.18,))
        bar = always_redraw(make_bar)
        pct = always_redraw(lambda: T(f"{int(round(prog.get_value()*100)):3d}%", 18, GREEN_BRT).move_to([6.15, bar_y, 0]))

        # --- bottom lines ---
        ref = left(T("THREAT REF:  HIGH / SEVERE / EXTREME / APOCALYPTIC / UNMEASURABLE",
                     15, GREEN_DIM), -6.6, -3.4)
        press = left(T("PRESS ENTER TO CONTINUE", 18, GREEN), -6.6, -3.68)
        press_cur = Rectangle(width=0.15, height=0.26, stroke_width=0, fill_color=GREEN,
                              fill_opacity=1).next_to(press, RIGHT, buff=0.08)
        press_cur.add_updater(lambda m: m.set_opacity(1.0 if blink(0.55) else 0.0))

        # global CRT scanlines
        scan = VGroup(*[
            Line([-7.2, y, 0], [7.2, y, 0], color=BG, stroke_width=2, stroke_opacity=0.11)
            for y in np.arange(-4.0, 4.0, 0.15)
        ]).set_z_index(15)

        # =================================================================
        # SEQUENCE
        # =================================================================
        self.add(clock)
        self.add_sound(snd("ambient.wav"), gain=-16)
        self.add_sound(snd("boot.wav"), gain=-3)

        # CRT power-on flicker into the title
        self.add(scan)
        self.play(FadeIn(header), run_time=0.3)
        self.add(title)
        for op, rt in [(0.15, 0.05), (1.0, 0.05), (0.3, 0.05), (1.0, 0.07)]:
            self.play(title.animate.set_opacity(op), run_time=rt)
        self.play(FadeIn(subtitle), run_time=0.3)
        self.add(bar_bg, bar, pct)

        # boot log: tick off each task + fill the bar
        n = len(lines)
        for i, line in enumerate(lines):
            self.add_sound(snd("blip.wav"), gain=-11)
            self.play(
                FadeIn(line, shift=RIGHT * 0.08),
                prog.animate.set_value((i + 1) / n),
                run_time=0.16,
            )
            if i < n - 1:
                self.wait(0.16)
        self.add_sound(snd("loaded.wav"), gain=-5)
        self.wait(0.3)

        # opening line + press enter
        self.play(AddTextLetterByLetter(open_t), run_time=0.6)
        self.add(open_cur)
        self.wait(0.5)
        self.add_sound(snd("transition.wav"), gain=-9)
        self.play(FadeIn(ref), FadeIn(press), run_time=0.4)
        self.add(press_cur)
        self.wait(2.6)
