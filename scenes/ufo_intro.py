"""ufo_intro.py - terminal/pixel UFO title reveal (green glow).

A pixel-art neon-green UFO descends into a terminal-grid sky, fires a glowing
tractor beam, and the title is written letter-by-letter, each character streaming
down out of the beam and settling glowing into place. Terminal background hum +
UI sound effects.

Swap TITLE / TAGLINE. Render:
    manim -pqh --fps 30 scenes/ufo_intro.py UFOIntro
"""

import os

import numpy as np
from manim import *

BG     = "#04110B"
GREEN  = "#3DFF7A"
GREENB = "#CFFFDD"
GREEND = "#1F8A45"
GRID   = "#0E2014"

UI = "Oxanium"
TITLE = "TRANSMISSION"
TAGLINE = "// SIGNAL ORIGIN UNKNOWN"

# pixel-art saucer (# = body, o = light)
PIX = [
    "    ████    ",
    "   ██████   ",
    "  ████████  ",
    " ██████████ ",
    "████████████",
    " ██████████ ",
    " o  o  o  o ",
]

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
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # --- terminal grid + stars + scanlines + frame ---
        gridm = VGroup()
        for y in np.arange(-4, 4.1, 0.5):
            gridm.add(Line([-7.3, y, 0], [7.3, y, 0], color=GRID, stroke_width=1))
        for x in np.arange(-7, 7.1, 0.5):
            gridm.add(Line([x, -4, 0], [x, 4, 0], color=GRID, stroke_width=1))
        gridm.set_z_index(-10)
        rng = np.random.default_rng(7)
        stars = VGroup(*[Square(side_length=rng.uniform(0.03, 0.06), stroke_width=0, fill_color=GREENB,
                        fill_opacity=rng.uniform(0.2, 0.7)).move_to([rng.uniform(-7, 7), rng.uniform(-3.8, 3.8), 0])
                        for _ in range(55)]).set_z_index(-9)
        scan = VGroup(*[Line([-7.3, y, 0], [7.3, y, 0], color=BG, stroke_width=2, stroke_opacity=0.14)
                        for y in np.arange(-4, 4, 0.12)]).set_z_index(20)
        frame = Rectangle(width=13.9, height=7.6, stroke_color=GREEND, stroke_width=1.5, fill_opacity=0)
        hL = Text("// INCOMING CONTACT", font=UI, weight="SEMIBOLD", font_size=18, color=GREEN).to_corner(UL).shift(RIGHT*0.25+DOWN*0.18)
        status = always_redraw(lambda: Text("TRACKING" + "." * (int(clock.get_value()*4) % 4), font=UI,
                               weight="SEMIBOLD", font_size=18, color=GREEN).to_corner(UR).shift(LEFT*0.25+DOWN*0.18))

        # --- pixel-art UFO ---
        UX, UY = 0.0, 2.25
        cell = 0.185
        rows, cols = len(PIX), max(len(r) for r in PIX)
        body, lights = VGroup(), VGroup()
        for r, row in enumerate(PIX):
            for c, ch in enumerate(row):
                if ch in "█o":
                    x = (c - (cols - 1) / 2) * cell
                    y = ((rows - 1) / 2 - r) * cell
                    sq = Square(side_length=cell * 0.88, stroke_width=0,
                                fill_color=GREENB if ch == "o" else GREEN, fill_opacity=1).move_to([x, y, 0])
                    (lights if ch == "o" else body).add(sq)

        def light_upd(m):
            t = clock.get_value()
            for j, d in enumerate(m):
                d.set_opacity(0.2 + 0.8 * (0.5 + 0.5 * np.sin(t * 6 - j * 1.1)))
        lights.add_updater(light_upd)
        ufo = VGroup(glow(body, GREEN, ((10, 0.05), (5, 0.12))), body, lights).move_to([UX, 5.7, 0])

        def bob(m):
            m.move_to([UX, UY + 0.09 * np.sin(clock.get_value() * 2.2), 0])

        # --- green beam + title ---
        by_top, by_bot = 1.5, -1.95
        beam = Polygon([-0.55, by_top, 0], [0.55, by_top, 0], [2.3, by_bot, 0], [-2.3, by_bot, 0],
                       stroke_width=0, fill_color=GREEN, fill_opacity=0.0).set_z_index(-1)
        beam_edges = VGroup(Line([-0.55, by_top, 0], [-2.3, by_bot, 0], color=GREEN, stroke_width=2),
                            Line([0.55, by_top, 0], [2.3, by_bot, 0], color=GREEN, stroke_width=2)).set_opacity(0)
        beam_floor = Ellipse(width=4.6, height=0.5, stroke_color=GREEN, stroke_width=2, fill_color=GREEN, fill_opacity=0.08).move_to([0, by_bot, 0]).set_opacity(0)

        def beam_pulse(m):
            m.set_fill(GREEN, opacity=0.10 + 0.05 * (0.5 + 0.5 * np.sin(clock.get_value() * 5)))

        dust = VGroup(*[Square(side_length=rng.uniform(0.03, 0.06), stroke_width=0, fill_color=GREENB) for _ in range(16)])
        dstate = [rng.uniform(0, 1) for _ in range(16)]

        def dust_upd(m, dt):
            for j, d in enumerate(m):
                dstate[j] = (dstate[j] + dt * 0.25) % 1.0
                p = dstate[j]
                y = by_bot + (by_top - by_bot) * p
                halfw = 2.3 - (2.3 - 0.55) * p
                d.move_to([np.interp(j % 5, [0, 4], [-halfw * 0.7, halfw * 0.7]), y, 0])
                d.set_opacity((1 - p) * 0.6)

        title = Text(TITLE, font=UI, weight="BOLD", color=GREENB).scale_to_fit_width(7.0).move_to([0, -1.55, 0])
        targets = [L.get_center() for L in title]
        for L in title:
            L.move_to([UX, 1.15, 0]).set_opacity(0)
        tagline = Text(TAGLINE, font=UI, weight="SEMIBOLD", font_size=22, color=GREEN).move_to([0, -2.5, 0]).set_opacity(0)

        # =================================================================
        self.add_sound(snd("crt_hum.wav"), gain=-11)
        self.add(gridm, stars)
        self.play(Create(frame), FadeIn(hL), run_time=0.6)
        self.add(status, scan)

        self.play(ufo.animate.move_to([UX, UY, 0]), run_time=1.1, rate_func=overshoot)
        ufo.add_updater(bob)
        self.wait(0.2)

        self.add_sound(snd("beam_on.wav"), gain=-6)
        self.add(beam, beam_edges, beam_floor)
        self.play(beam.animate.set_fill(GREEN, opacity=0.12), beam_edges.animate.set_opacity(0.7),
                  beam_floor.animate.set_opacity(1), run_time=0.6)
        beam.add_updater(beam_pulse)
        self.add(dust); dust.add_updater(dust_upd)

        # title written letter-by-letter, streaming out of the beam
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
