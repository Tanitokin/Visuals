"""ufo_intro.py - terminal/pixel UFO title reveal (green glow).

A shaded pixel-art neon-green flying saucer descends into a live terminal
(scrolling logs, status bar, scanlines), fires a glowing tractor beam, and the
title is written letter-by-letter streaming out of the beam. Terminal hum +
UI sfx.

Swap TITLE / TAGLINE. Render:
    manim -pqh --fps 30 scenes/ufo_intro.py UFOIntro
"""

import os
import random

import numpy as np
from manim import *

BG     = "#04110B"
GREEN  = "#3DFF7A"
GREENB = "#CFFFDD"
GREEND = "#1F8A45"
GREENM = "#27A653"   # mid shade for disc rim
WINCOL = "#EAFFF0"
GRID   = "#0E2014"

UI   = "Oxanium"
DATA = "DejaVu Sans Mono"
TITLE = "TRANSMISSION"
TAGLINE = "// SIGNAL ORIGIN UNKNOWN"

# shaded pixel-art saucer (17 wide): % dome, W window, # disc bright, = rim, o light
PIX = [
    ".......%%%.......",
    "......%%%%%......",
    ".....%WWWWW%.....",
    "...===========...",
    "#################",
    ".===============.",
    "....o...o...o....",
]
SH = {"%": GREENB, "W": WINCOL, "#": GREEN, "=": GREENM}

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(n):
    return os.path.join(AUDIO_DIR, n)


def overshoot(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def glow(mob, color=GREEN, specs=((9, 0.05), (5, 0.10), (2.5, 0.2))):
    return VGroup(*[mob.copy().set_stroke(color, width=w, opacity=o).set_fill(opacity=0)
                    for w, o in specs])


def code_line():
    toks = ["0x" + "".join(random.choice("0123456789ABCDEF") for _ in range(4)),
            "SCAN", "PKT" + str(random.randint(0, 999)), "::", "OK", "RX",
            "SIG", "..", ">" + str(random.randint(10, 99))]
    return " ".join(random.choice(toks) for _ in range(3))


class UFOIntro(MovingCameraScene):
    def flash(self, op=0.4):
        fr = self.camera.frame
        fl = Rectangle(width=fr.get_width() * 1.3, height=fr.get_height() * 1.3, stroke_width=0,
                       fill_color=GREENB, fill_opacity=0.0).move_to(fr.get_center()).set_z_index(40)
        self.add(fl)
        return Succession(fl.animate(run_time=0.06).set_fill(GREENB, opacity=op),
                          fl.animate(run_time=0.25, rate_func=smooth).set_fill(GREENB, opacity=0.0))

    def construct(self):
        self.camera.background_color = BG
        random.seed(11)
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # --- terminal grid / scanlines / frame ---
        gridm = VGroup()
        for y in np.arange(-4, 4.1, 0.5):
            gridm.add(Line([-7.3, y, 0], [7.3, y, 0], color=GRID, stroke_width=1))
        for x in np.arange(-7, 7.1, 0.5):
            gridm.add(Line([x, -4, 0], [x, 4, 0], color=GRID, stroke_width=1))
        gridm.set_z_index(-10)
        scan = VGroup(*[Line([-7.3, y, 0], [7.3, y, 0], color=BG, stroke_width=2, stroke_opacity=0.18)
                        for y in np.arange(-4, 4, 0.1)]).set_z_index(20)
        frame = Rectangle(width=13.9, height=7.6, stroke_color=GREEND, stroke_width=1.5, fill_opacity=0)
        cbr = VGroup(*[Line(ORIGIN, RIGHT * 0.3, color=GREEN).move_to(frame.get_corner(d)).shift(v)
                       for d, v in [(UL, RIGHT*0.15), (UR, LEFT*0.15), (DL, RIGHT*0.15), (DR, LEFT*0.15)]])

        hL = Text("// INCOMING CONTACT", font=UI, weight="SEMIBOLD", font_size=18, color=GREEN).to_corner(UL).shift(RIGHT*0.3+DOWN*0.2)
        status = always_redraw(lambda: Text("TRACKING" + "." * (int(clock.get_value()*4) % 4), font=UI,
                               weight="SEMIBOLD", font_size=18, color=GREEN).to_corner(UR).shift(LEFT*0.3+DOWN*0.2))

        # --- scrolling terminal log columns (left + right) ---
        def make_log(x):
            lines = VGroup(*[Text(code_line(), font=DATA, font_size=12, color=GREEND).set_opacity(0.4) for _ in range(20)])
            for k, ln in enumerate(lines):
                ln.move_to([x, 3.5 - k * 0.32, 0]).align_to([x, 0, 0], LEFT)
            return lines
        logL, logR = make_log(-6.85), make_log(5.0)
        off = {"v": 0.0}

        def log_upd(m, dt):
            off["v"] = (off["v"] + dt * 1.1) % 0.32
            for k, ln in enumerate(m):
                y = 3.5 - k * 0.32 + off["v"]
                ln.move_to([ln.get_x(), y, 0])
                ln.set_opacity(0.0 if (y > 3.5 or y < -3.4) else 0.38)
        logL.add_updater(log_upd)
        logR.add_updater(log_upd)
        logL.set_z_index(-6); logR.set_z_index(-6)

        # --- bottom status bar + cursor ---
        sbar = Text("SYS://TRACK   OBJ-CLASS: UNIDENTIFIED   //   ALT 12.4 KM   //   STATE: INBOUND",
                    font=DATA, font_size=14, color=GREEND).move_to([0, -3.62, 0])
        cursor = Square(side_length=0.16, stroke_width=0, fill_color=GREEN, fill_opacity=1).next_to(sbar, RIGHT, buff=0.12)
        cursor.add_updater(lambda m: m.set_opacity(1.0 if (clock.get_value() % 0.7) < 0.45 else 0.0))

        # --- pixel-art UFO ---
        UX, UY = 0.0, 2.05
        cell = 0.16
        rows, cols = len(PIX), max(len(r) for r in PIX)
        body, lights = VGroup(), VGroup()
        for r, row in enumerate(PIX):
            for c, ch in enumerate(row):
                if ch in SH or ch == "o":
                    x = (c - (cols - 1) / 2) * cell
                    y = ((rows - 1) / 2 - r) * cell
                    sq = Square(side_length=cell * 0.9, stroke_width=0,
                                fill_color=GREENB if ch == "o" else SH[ch], fill_opacity=1).move_to([x, y, 0])
                    (lights if ch == "o" else body).add(sq)

        def light_upd(m):
            t = clock.get_value()
            for j, d in enumerate(m):
                d.set_opacity(0.18 + 0.82 * (0.5 + 0.5 * np.sin(t * 6 - j * 1.4)))
        lights.add_updater(light_upd)
        ufo = VGroup(glow(body, GREEN, ((11, 0.05), (6, 0.12))), body, lights).move_to([UX, 5.8, 0])

        def bob(m):
            m.move_to([UX, UY + 0.08 * np.sin(clock.get_value() * 2.2), 0])

        # --- beam + title ---
        by_top, by_bot = 1.35, -1.95
        beam = Polygon([-0.6, by_top, 0], [0.6, by_top, 0], [2.4, by_bot, 0], [-2.4, by_bot, 0],
                       stroke_width=0, fill_color=GREEN, fill_opacity=0.0).set_z_index(-1)
        beam_edges = VGroup(Line([-0.6, by_top, 0], [-2.4, by_bot, 0], color=GREEN, stroke_width=2),
                            Line([0.6, by_top, 0], [2.4, by_bot, 0], color=GREEN, stroke_width=2)).set_opacity(0)
        beam_floor = Ellipse(width=4.8, height=0.5, stroke_color=GREEN, stroke_width=2, fill_color=GREEN, fill_opacity=0.08).move_to([0, by_bot, 0]).set_opacity(0)

        def beam_pulse(m):
            m.set_fill(GREEN, opacity=0.10 + 0.05 * (0.5 + 0.5 * np.sin(clock.get_value() * 5)))

        dust = VGroup(*[Square(side_length=np.random.uniform(0.03, 0.06), stroke_width=0, fill_color=GREENB) for _ in range(16)])
        dstate = [np.random.uniform(0, 1) for _ in range(16)]

        def dust_upd(m, dt):
            for j, d in enumerate(m):
                dstate[j] = (dstate[j] + dt * 0.25) % 1.0
                p = dstate[j]
                y = by_bot + (by_top - by_bot) * p
                halfw = 2.4 - (2.4 - 0.6) * p
                d.move_to([np.interp(j % 5, [0, 4], [-halfw * 0.7, halfw * 0.7]), y, 0])
                d.set_opacity((1 - p) * 0.6)

        title = Text(TITLE, font=UI, weight="BOLD", color=GREENB).scale_to_fit_width(7.0).move_to([0, -1.5, 0])
        targets = [L.get_center() for L in title]
        for L in title:
            L.move_to([UX, 1.0, 0]).set_opacity(0)
        tagline = Text(TAGLINE, font=UI, weight="SEMIBOLD", font_size=22, color=GREEN).move_to([0, -2.45, 0]).set_opacity(0)

        # =================================================================
        self.add_sound(snd("crt_hum.wav"), gain=-11)
        self.add(gridm, logL, logR)
        self.play(Create(frame), FadeIn(cbr), FadeIn(hL), FadeIn(sbar), run_time=0.6)
        self.add(status, scan, cursor)

        self.play(ufo.animate.move_to([UX, UY, 0]), run_time=1.1, rate_func=overshoot)
        ufo.add_updater(bob)
        self.wait(0.2)

        self.add_sound(snd("beam_on.wav"), gain=-6)
        self.add(beam, beam_edges, beam_floor)
        self.play(beam.animate.set_fill(GREEN, opacity=0.12), beam_edges.animate.set_opacity(0.7),
                  beam_floor.animate.set_opacity(1), run_time=0.6)
        beam.add_updater(beam_pulse)
        self.add(dust); dust.add_updater(dust_upd)

        self.add(title)
        n = len(title)
        for j in range(n):
            self.add_sound(snd("ui_step.wav"), time_offset=0.1 + j * (1.45 / n), gain=-9)
        self.play(LaggedStart(*[L.animate(rate_func=rush_from).move_to(tp).set_opacity(1)
                                for L, tp in zip(title, targets)], lag_ratio=0.12), run_time=1.7)

        tglow = glow(title, GREEN, ((15, 0.05), (8, 0.10), (4, 0.2)))
        self.add_sound(snd("beam_on.wav"), gain=-11)
        self.play(FadeIn(tglow), self.flash(0.4), run_time=0.4)
        self.play(FadeIn(tagline, shift=UP * 0.1), run_time=0.5)

        self.wait(0.6)
        beam.clear_updaters(); dust.clear_updaters()
        self.play(beam.animate.set_fill(GREEN, opacity=0.0), beam_edges.animate.set_opacity(0),
                  beam_floor.animate.set_opacity(0), FadeOut(dust), run_time=0.5)
        self.wait(1.0)
