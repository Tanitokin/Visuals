"""ufo_intro.py - terminal/sci-fi UFO title reveal.

A neon UFO descends into a dark terminal-grid sky, fires a glowing tractor beam,
and the title is written letter-by-letter, each character streaming down out of
the beam and settling glowing into place. Then a neon pulse + tagline.

Swap TITLE / TAGLINE. Render:
    manim -pqh --fps 30 scenes/ufo_intro.py UFOIntro
"""

import os

import numpy as np
from manim import *

BG    = "#03070C"
NEON  = "#34E6FF"
NEONB = "#CFFBFF"
NEOND = "#1C6F82"
GRID  = "#0B1A22"

UI = "Oxanium"
TITLE = "TRANSMISSION"
TAGLINE = "// SIGNAL ORIGIN UNKNOWN"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(n):
    return os.path.join(AUDIO_DIR, n)


def overshoot(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def glow(mob, color=NEON, specs=((12, 0.05), (6, 0.11), (3, 0.2))):
    """Halo-only glow (copies); does NOT include the original mobject."""
    return VGroup(*[mob.copy().set_stroke(color, width=w, opacity=o).set_fill(opacity=0)
                    for w, o in specs])


class UFOIntro(MovingCameraScene):
    def flash(self, op=0.5):
        fr = self.camera.frame
        fl = Rectangle(width=fr.get_width() * 1.3, height=fr.get_height() * 1.3, stroke_width=0,
                       fill_color=NEONB, fill_opacity=0.0).move_to(fr.get_center()).set_z_index(40)
        self.add(fl)
        return Succession(fl.animate(run_time=0.06).set_fill(NEONB, opacity=op),
                          fl.animate(run_time=0.25, rate_func=smooth).set_fill(NEONB, opacity=0.0))

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
        stars = VGroup(*[Dot(radius=rng.uniform(0.01, 0.03), color=NEONB, fill_opacity=rng.uniform(0.2, 0.7))
                        .move_to([rng.uniform(-7, 7), rng.uniform(-3.8, 3.8), 0]) for _ in range(60)]).set_z_index(-9)
        scan = VGroup(*[Line([-7.3, y, 0], [7.3, y, 0], color=BG, stroke_width=2, stroke_opacity=0.16)
                        for y in np.arange(-4, 4, 0.12)]).set_z_index(20)
        frame = Rectangle(width=13.9, height=7.6, stroke_color=NEOND, stroke_width=1.5, fill_opacity=0)
        hL = Text("// INCOMING CONTACT", font=UI, weight="SEMIBOLD", font_size=18, color=NEON).to_corner(UL).shift(RIGHT*0.25+DOWN*0.18)
        status = always_redraw(lambda: Text("TRACKING" + "." * (int(clock.get_value()*4) % 4), font=UI,
                               weight="SEMIBOLD", font_size=18, color=NEON).to_corner(UR).shift(LEFT*0.25+DOWN*0.18))

        # --- UFO ---
        UX, UY = 0.0, 2.2
        body = Ellipse(width=2.7, height=0.6, stroke_color=NEON, stroke_width=3, fill_color="#06141B", fill_opacity=1)
        dome = Arc(radius=0.72, start_angle=0, angle=PI, stroke_color=NEON, stroke_width=3).stretch(1.25, 1)
        dome.next_to(body.get_top(), UP, buff=-0.06)
        win = Arc(radius=0.42, start_angle=0, angle=PI, stroke_color=NEONB, stroke_width=2).stretch(1.15, 1)
        win.next_to(body.get_top(), UP, buff=-0.02)
        ufo_core = VGroup(body, dome, win)
        lights = VGroup(*[Dot(radius=0.06, color=NEONB).move_to(body.get_center() + RIGHT*x + DOWN*0.26)
                          for x in np.linspace(-1.05, 1.05, 7)])

        def light_upd(m):
            t = clock.get_value()
            for j, d in enumerate(m):
                d.set_opacity(0.25 + 0.75 * (0.5 + 0.5 * np.sin(t * 6 - j * 0.9)))
        lights.add_updater(light_upd)
        ufo = VGroup(glow(ufo_core, NEON, ((13, 0.05), (7, 0.12))), ufo_core, lights).move_to([UX, 5.7, 0])

        def bob(m):
            m.move_to([UX, UY + 0.09 * np.sin(clock.get_value() * 2.2), 0])

        # --- beam + title ---
        by_top, by_bot = 1.5, -1.95
        beam = Polygon([-0.55, by_top, 0], [0.55, by_top, 0], [2.3, by_bot, 0], [-2.3, by_bot, 0],
                       stroke_width=0, fill_color=NEON, fill_opacity=0.0).set_z_index(-1)
        beam_edges = VGroup(Line([-0.55, by_top, 0], [-2.3, by_bot, 0], color=NEON, stroke_width=2),
                            Line([0.55, by_top, 0], [2.3, by_bot, 0], color=NEON, stroke_width=2)).set_opacity(0)
        beam_floor = Ellipse(width=4.6, height=0.5, stroke_color=NEON, stroke_width=2, fill_color=NEON, fill_opacity=0.08).move_to([0, by_bot, 0]).set_opacity(0)

        def beam_pulse(m):
            m.set_fill(NEON, opacity=0.10 + 0.05 * (0.5 + 0.5 * np.sin(clock.get_value() * 5)))

        dust = VGroup(*[Dot(radius=rng.uniform(0.015, 0.04), color=NEONB) for _ in range(16)])
        dstate = [rng.uniform(0, 1) for _ in range(16)]

        def dust_upd(m, dt):
            for j, d in enumerate(m):
                dstate[j] = (dstate[j] + dt * 0.25) % 1.0
                p = dstate[j]
                y = by_bot + (by_top - by_bot) * p
                halfw = 2.3 - (2.3 - 0.55) * p
                d.move_to([np.interp(j % 5, [0, 4], [-halfw * 0.7, halfw * 0.7]), y, 0])
                d.set_opacity((1 - p) * 0.6)

        title = Text(TITLE, font=UI, weight="BOLD", color=NEONB).scale_to_fit_width(7.0).move_to([0, -1.55, 0])
        targets = [L.get_center() for L in title]
        for L in title:
            L.move_to([UX, 1.15, 0]).set_opacity(0)
        tagline = Text(TAGLINE, font=UI, weight="SEMIBOLD", font_size=22, color=NEON).move_to([0, -2.5, 0]).set_opacity(0)

        # =================================================================
        self.add_sound(snd("ufo_hum.wav"), gain=-12)
        self.add(gridm, stars)
        self.play(Create(frame), FadeIn(hL), run_time=0.6)
        self.add(status, scan)

        self.play(ufo.animate.move_to([UX, UY, 0]), run_time=1.1, rate_func=overshoot)
        ufo.add_updater(bob)
        self.wait(0.2)

        self.add_sound(snd("beam_on.wav"), gain=-6)
        self.add(beam, beam_edges, beam_floor)
        self.play(beam.animate.set_fill(NEON, opacity=0.12), beam_edges.animate.set_opacity(0.7),
                  beam_floor.animate.set_opacity(1), run_time=0.6)
        beam.add_updater(beam_pulse)
        self.add(dust); dust.add_updater(dust_upd)

        # title written letter-by-letter, streaming out of the beam
        self.add(title)
        n = len(title)
        for j in range(n):
            self.add_sound(snd("letter.wav"), time_offset=0.1 + j * (1.45 / n), gain=-8)
        self.play(LaggedStart(*[L.animate(rate_func=rush_from).move_to(tp).set_opacity(1)
                                for L, tp in zip(title, targets)], lag_ratio=0.12), run_time=1.7)

        # neon pulse + tagline
        tglow = glow(title, NEON, ((15, 0.05), (8, 0.10), (4, 0.2)))
        self.add_sound(snd("beam_on.wav"), gain=-11)
        self.play(FadeIn(tglow), self.flash(0.45), run_time=0.4)
        self.play(FadeIn(tagline, shift=UP * 0.1), run_time=0.5)

        self.wait(0.6)
        beam.clear_updaters(); dust.clear_updaters()
        self.play(beam.animate.set_fill(NEON, opacity=0.0), beam_edges.animate.set_opacity(0),
                  beam_floor.animate.set_opacity(0), FadeOut(dust), run_time=0.5)
        self.wait(1.0)
