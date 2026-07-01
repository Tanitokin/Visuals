"""spooky_inquisitor.py - "SPOOKY INQUISITOR PRESENTS" old-TV title card.

A vintage CRT television turns on (a bright horizontal line blooms open into a
full screen), bursts into snowy static, then settles into heavy scanlines while
the title lights up letter by letter in red pixels ("Press Start 2P") with
phosphor flicker, bad-convergence colour fringing, a drifting vertical-hold
roll bar, occasional horizontal tracking slips, and a curved-tube vignette.
"PRESENTS" strobes in like a failing sign. Finally the set powers off,
collapsing to a bright line, then a dot with a red afterglow. Black background.

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
        # CRT ambience: tube mask, scanlines, roll bar, brightness flicker.
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

        # curved-tube mask: black frame with a rounded-rect hole, so the
        # picture (including flashes and snow) has classic CRT corners
        tube_hole = RoundedRectangle(corner_radius=1.0, width=FW * 0.985, height=FH * 0.97)
        tube = Cutout(Rectangle(width=FW + 2, height=FH + 2), tube_hole,
                      fill_color=TVBLACK, fill_opacity=1.0, stroke_width=0).set_z_index(50)
        # soft inner edge shading ring just inside the tube edge
        tube_edge = RoundedRectangle(corner_radius=1.0, width=FW * 0.985, height=FH * 0.97,
                                     stroke_color=TVBLACK, stroke_width=26,
                                     stroke_opacity=0.55, fill_opacity=0).set_z_index(49)

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
        self.add(tube, tube_edge)
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
        self.wait(0.5)                      # snow
        self.add(scan, roll, flick)         # bring CRT ambience up under the snow
        self.play(static.animate.set_opacity(0.0), run_time=0.4)
        static.clear_updaters()
        self.remove(static)

        # =================================================================
        # 3) TITLE: letters ignite one by one with phosphor flicker.
        # =================================================================
        line1 = Text("SPOOKY", font=PIXEL, color=RED).scale_to_fit_width(9.6).move_to([0, 1.75, 0])
        line2 = Text("INQUISITOR", font=PIXEL, color=RED).scale_to_fit_width(12.2).move_to([0, 0.15, 0])
        presents = Text("PRESENTS", font=PIXEL, color=RED_BRT).scale_to_fit_width(5.4).move_to([0, -2.05, 0])

        def ignite(word, step=0.09, flick_dur=0.14):
            """Reveal a word letter by letter: each letter strobes a few frames
            before holding, like phosphor segments warming up."""
            fr = fringe(word).set_z_index(8)
            word.set_z_index(10)
            for L in word:
                L.set_opacity(0.0)
            fr.set_opacity(0.0)
            self.add(fr, word)
            t0 = clock.get_value() + 0.05
            finals = [1.0, 0.45, 0.32]   # core, blue ghost, green ghost

            def upd(_):
                t = clock.get_value()
                for gi, grp in enumerate([word, fr[0], fr[1]]):
                    for i, L in enumerate(grp):
                        ti = t0 + i * step
                        if t < ti:
                            L.set_opacity(0.0)
                        elif t < ti + flick_dur:
                            on = np.random.random() > 0.38
                            L.set_opacity(finals[gi] if on else finals[gi] * 0.15)
                        else:
                            L.set_opacity(finals[gi])
            word.add_updater(upd)
            n = len(word)
            for i in range(n):
                self.add_sound(snd("tv_snap.wav"), time_offset=0.05 + i * step, gain=-14)
            self.wait(0.05 + n * step + flick_dur + 0.05)
            word.clear_updaters()
            for gi, grp in enumerate([word, fr[0], fr[1]]):
                grp.set_opacity(finals[gi])
            gl = glow(word).set_z_index(7)
            self.add(gl)
            return VGroup(word, fr, gl)

        g1 = ignite(line1)
        g2 = ignite(line2, step=0.07)
        self.wait(0.15)

        # "PRESENTS" strobes in like a failing sign (no smooth fade)
        pfr = fringe(presents, dx=0.04).set_z_index(8)
        pgl = glow(presents, color=RED, specs=((10, 0.05), (5, 0.12))).set_z_index(7)
        presents.set_z_index(10)
        pgroup = VGroup(presents, pfr, pgl)
        pgroup.set_opacity(0.0)
        self.add(pgl, pfr, presents)
        self.add_sound(snd("tv_snap.wav"), gain=-6)

        def p_op(k):
            presents.set_opacity(k)
            pfr[0].set_opacity(0.40 * k)
            pfr[1].set_opacity(0.30 * k)
            for h in pgl:
                h.set_stroke(opacity=h.get_stroke_opacity() if False else 0.10 * k)
        for k, d in [(1.0, 0.05), (0.1, 0.04), (1.0, 0.07), (0.15, 0.03), (1.0, 0.0)]:
            p_op(k)
            if d:
                self.wait(d)

        # white settle flash (the picture "locking")
        fl = Rectangle(width=FW + 1, height=FH + 1, stroke_width=0,
                       fill_color=WHITE, fill_opacity=0.0).set_z_index(42)
        self.add(fl)
        self.play(fl.animate.set_fill(WHITE, opacity=0.22), run_time=0.06)
        self.play(fl.animate.set_fill(WHITE, opacity=0.0), run_time=0.22, rate_func=smooth)
        self.remove(fl)

        # =================================================================
        # 4) HOLD: glow pulse + occasional horizontal tracking slips.
        # =================================================================
        title = VGroup(g1, g2, pgroup)
        base = title.get_center().copy()
        slip = {"dx": 0.0, "frames": 0}

        def hold_upd(m):
            t = clock.get_value()
            for w in (line1, line2):
                w.set_color(interpolate_color(
                    ManimColor(RED), ManimColor(RED_BRT), 0.5 + 0.5 * np.sin(t * 3.2)))
            if slip["frames"] > 0:
                slip["frames"] -= 1
                if slip["frames"] == 0:
                    slip["dx"] = 0.0
            elif np.random.random() < 0.025:
                slip["frames"] = int(np.random.randint(2, 5))
                slip["dx"] = float(np.random.uniform(-0.16, 0.16))
            m.move_to(base + np.array([slip["dx"], 0.0, 0.0]))
        title.add_updater(hold_upd)
        self.wait(2.5)
        title.clear_updaters()
        title.move_to(base)

        # =================================================================
        # 5) POWER OFF: collapse to a line, a dot, then a red afterglow.
        # =================================================================
        self.add_sound(snd("tv_off.wav"), gain=-3)
        sheet = Rectangle(width=FW, height=FH, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.0).set_z_index(44)
        self.add(sheet)
        self.play(FadeOut(title), FadeOut(scan), FadeOut(roll),
                  sheet.animate.set_fill(WHITE, opacity=0.85), run_time=0.16)
        self.play(sheet.animate.stretch_to_fit_height(0.06).set_fill(WHITE, opacity=1.0),
                  run_time=0.18, rate_func=rush_into)
        dot = Dot([0, 0, 0], radius=0.05, color=WHITE).set_z_index(45)
        halo = Dot([0, 0, 0], radius=0.16, color=RED).set_opacity(0.0).set_z_index(44)
        self.add(halo, dot)
        self.play(sheet.animate.stretch_to_fit_width(0.06), FadeIn(dot), run_time=0.12)
        self.remove(sheet)
        flick.clear_updaters()
        # the dot shrinks but a dim red phosphor afterglow lingers a moment
        self.play(dot.animate.scale(0.35).set_color(RED_BRT),
                  halo.animate.set_opacity(0.30),
                  flick.animate.set_opacity(0.0), run_time=0.30, rate_func=rush_into)
        self.play(dot.animate.scale(0.05).set_opacity(0.0),
                  halo.animate.scale(0.3).set_opacity(0.0), run_time=0.55)
        self.wait(0.4)
