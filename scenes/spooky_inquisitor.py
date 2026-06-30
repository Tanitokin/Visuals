"""spooky_inquisitor.py - "SPOOKY INQUISITOR PRESENTS" old-TV title card.

A vintage CRT television turns on (a bright horizontal line blooms open into a
full screen), bursts into snowy static, then settles into heavy scanlines while
the title is written in red pixel letters ("Press Start 2P") with bad-convergence
colour fringing, a drifting vertical-hold roll bar, and a flickering red glow.
Finally the set powers off, collapsing back to a dot. Black background.

Render:
    manim -pqh --fps 30 scenes/spooky_inquisitor.py SpookyInquisitorTV
"""

import os
import sys

import numpy as np
from manim import *

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find crt_style next to this file
from crt_style import snd  # reuse the assets/audio path helper

# --- old-TV palette -------------------------------------------------------
TVBLACK = "#000000"   # screen black
RED     = "#FF2B2B"   # phosphor red
RED_BRT = "#FF7A6B"   # hot highlight
RED_DIM = "#7E1212"   # dim red
WHITE   = "#FFFFFF"   # power-on bloom / hot scanline
GHOST_B = "#2BB6FF"   # bad-convergence blue fringe
GHOST_G = "#2BFF8F"   # bad-convergence green fringe

PIXEL = "Press Start 2P"

FW, FH = 14.22, 8.0   # default 16:9 frame size in Manim units


def glow(mob, color=RED, specs=((16, 0.05), (9, 0.11), (4.5, 0.22))):
    """Soft red phosphor halo behind text (stacked translucent strokes)."""
    return VGroup(*[mob.copy().set_stroke(color, width=w, opacity=o).set_fill(opacity=0)
                    for w, o in specs])


def fringe(mob, dx=0.06):
    """Bad-convergence colour fringing: faint blue/green ghosts offset L/R."""
    b = mob.copy().set_color(GHOST_B).set_opacity(0.45).shift(LEFT * dx + UP * 0.012)
    g = mob.copy().set_color(GHOST_G).set_opacity(0.32).shift(RIGHT * dx + DOWN * 0.012)
    return VGroup(b, g)


class SpookyInquisitorTV(Scene):
    def construct(self):
        self.camera.background_color = TVBLACK
        np.random.seed(7)

        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # =================================================================
        # CRT ambience: scanlines, drifting roll bar, brightness flicker.
        # Kept above the picture so it cuts into the lit red text.
        # =================================================================
        scan = VGroup(*[
            Line([-FW / 2, y, 0], [FW / 2, y, 0], color=TVBLACK, stroke_width=2.6,
                 stroke_opacity=0.30)
            for y in np.arange(-FH / 2, FH / 2, 0.085)
        ]).set_z_index(30)

        # vertical-hold "roll" band that slowly creeps up the screen
        roll = Rectangle(width=FW, height=0.55, stroke_width=0,
                         fill_color=WHITE, fill_opacity=0.05).set_z_index(28)
        roll.add_updater(lambda m: m.move_to(
            [0, -FH / 2 + ((clock.get_value() * 1.3) % (FH + 0.55)), 0]))

        # global brightness flicker + rare interference spikes
        flick = Rectangle(width=FW + 1, height=FH + 1, stroke_width=0,
                          fill_color=TVBLACK, fill_opacity=0.0).set_z_index(36)

        def flick_upd(m):
            t = clock.get_value()
            base = 0.05 + 0.05 * (0.5 + 0.5 * np.sin(t * 7.0))
            spike = 0.10 if (np.sin(t * 53.0) > 0.9) else 0.0
            m.set_opacity(base + spike)
        flick.add_updater(flick_upd)

        # corner vignette (four dim wedges so the tube edges fall off to black)
        vig = VGroup()
        for cx, cy in [(-FW / 2, FH / 2), (FW / 2, FH / 2), (-FW / 2, -FH / 2), (FW / 2, -FH / 2)]:
            d = Dot([cx, cy, 0], radius=3.4, color=TVBLACK).set_opacity(0.0)
            vig.add(d)
        vig.set_z_index(26)

        # --- snowy static field (blocky grayscale grid; only shown briefly) ---
        cols, rows = 48, 27
        cw, ch = FW / cols, FH / rows
        static = VGroup()
        for r in range(rows):
            for c in range(cols):
                sq = Rectangle(width=cw, height=ch, stroke_width=0,
                               fill_color=WHITE, fill_opacity=0.0)
                sq.move_to([-FW / 2 + (c + 0.5) * cw, FH / 2 - (r + 0.5) * ch, 0])
                static.add(sq)
        static.set_z_index(20)

        def static_upd(m):
            v = np.random.uniform(0.05, 0.85, len(m))
            for sq, a in zip(m, v):
                sq.set_fill(WHITE, opacity=float(a))

        # =================================================================
        # 1) POWER ON: a hot white line blooms open into a full screen.
        # =================================================================
        self.add_sound(snd("tv_on.wav"), gain=-4)
        self.add_sound(snd("tv_hum.wav"), gain=-20)

        bloom = Rectangle(width=FW, height=0.0, stroke_width=0,
                          fill_color=WHITE, fill_opacity=1.0).set_z_index(40)
        hot_line = Line([-FW / 2, 0, 0], [FW / 2, 0, 0], color=WHITE,
                        stroke_width=4).set_z_index(41)
        self.add(hot_line)
        self.play(hot_line.animate.set_stroke(width=8, opacity=1.0), run_time=0.18)
        self.add(bloom)
        self.play(bloom.animate.stretch_to_fit_height(FH).set_fill(WHITE, opacity=0.9),
                  hot_line.animate.set_opacity(0.0), run_time=0.28, rate_func=rush_from)
        self.remove(hot_line)

        # =================================================================
        # 2) STATIC burst, then settle into the dark CRT.
        # =================================================================
        self.add_sound(snd("tv_static.wav"), gain=-7)
        self.add(static)
        static.add_updater(lambda m: static_upd(m))
        self.play(bloom.animate.set_fill(WHITE, opacity=0.0), run_time=0.18)
        self.remove(bloom)
        self.wait(0.55)                     # snow
        self.add(scan, roll, vig, flick)    # bring CRT ambience up under the snow
        self.play(static.animate.set_opacity(0.0), run_time=0.45)
        static.clear_updaters()
        self.remove(static)

        # =================================================================
        # 3) TITLE: red pixel letters with colour fringing + glow.
        # =================================================================
        line1 = Text("SPOOKY", font=PIXEL, color=RED).scale_to_fit_width(9.6).move_to([0, 1.75, 0])
        line2 = Text("INQUISITOR", font=PIXEL, color=RED).scale_to_fit_width(12.2).move_to([0, 0.15, 0])
        presents = Text("PRESENTS", font=PIXEL, color=RED_BRT).scale_to_fit_width(5.4).move_to([0, -2.05, 0])

        def reveal(word, sound="letter.wav", glitch=True):
            """Pop a word in with a quick horizontal jitter + colour fringe."""
            fr = fringe(word).set_z_index(8)
            gl = glow(word).set_z_index(7)
            word.set_z_index(10)
            self.add_sound(snd(sound), gain=-5)
            self.add(fr, gl)
            # brief horizontal "tracking" jitter as it locks in
            jit = VGroup(word, fr, gl)
            self.play(FadeIn(word, scale=1.06), FadeIn(gl), FadeIn(fr), run_time=0.28)
            if glitch:
                for dx in (0.18, -0.12, 0.06, 0.0):
                    self.play(jit.animate.shift([dx, 0, 0]), run_time=0.05)
            return VGroup(word, fr, gl)

        g1 = reveal(line1, sound="tv_snap.wav")
        self.wait(0.08)
        g2 = reveal(line2, sound="tv_snap.wav")
        self.wait(0.12)

        # "PRESENTS" fades up dimmer, with a settle flash
        pfr = fringe(presents, dx=0.04).set_z_index(8)
        pgl = glow(presents, color=RED, specs=((10, 0.05), (5, 0.12))).set_z_index(7)
        presents.set_z_index(10)
        self.add_sound(snd("tv_snap.wav"), gain=-3)
        self.add(pfr, pgl)
        self.play(FadeIn(presents, shift=UP * 0.12), FadeIn(pgl), FadeIn(pfr), run_time=0.5)

        # white settle flash (the picture "locking")
        fl = Rectangle(width=FW + 1, height=FH + 1, stroke_width=0,
                       fill_color=WHITE, fill_opacity=0.0).set_z_index(42)
        self.add(fl)
        self.play(fl.animate.set_fill(WHITE, opacity=0.22), run_time=0.06)
        self.play(fl.animate.set_fill(WHITE, opacity=0.0), run_time=0.22, rate_func=smooth)
        self.remove(fl)

        # =================================================================
        # 4) HOLD: red glow pulse + occasional tracking wobble on the title.
        # =================================================================
        title = VGroup(g1, g2, VGroup(presents, pfr, pgl))

        def pulse_upd(m):
            t = clock.get_value()
            for w in (line1, line2):
                w.set_color(interpolate_color(
                    ManimColor(RED), ManimColor(RED_BRT), 0.5 + 0.5 * np.sin(t * 3.2)))
        title.add_updater(pulse_upd)
        self.wait(2.4)
        title.clear_updaters()

        # =================================================================
        # 5) POWER OFF: collapse to a bright line, then a dot, then black.
        # =================================================================
        self.add_sound(snd("tv_off.wav"), gain=-3)
        collapse = VGroup(scan, roll, vig, title)
        sheet = Rectangle(width=FW, height=FH, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.0).set_z_index(44)
        self.add(sheet)
        self.play(FadeOut(title), FadeOut(scan), FadeOut(roll), FadeOut(vig),
                  sheet.animate.set_fill(WHITE, opacity=0.85), run_time=0.16)
        self.play(sheet.animate.stretch_to_fit_height(0.06).set_fill(WHITE, opacity=1.0),
                  run_time=0.18, rate_func=rush_into)
        dot = Dot([0, 0, 0], radius=0.05, color=WHITE).set_z_index(45)
        self.add(dot)
        self.play(sheet.animate.stretch_to_fit_width(0.06), FadeIn(dot), run_time=0.12)
        self.remove(sheet)
        flick.clear_updaters()
        self.play(dot.animate.scale(0.01).set_opacity(0.0),
                  flick.animate.set_opacity(0.0), run_time=0.45, rate_func=rush_into)
        self.wait(0.4)
