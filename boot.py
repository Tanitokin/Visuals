"""WORST CITIES - boot / initial loading screen (v2).

Green-CRT terminal boot sequence: a crisp glitch-revealed title, a startup log
that ticks off tasks with sharp key clicks, a cool segmented loading bar that
fills block-by-block and hits a CLICK + ACCESS chime at 100% (with a screen
flash), then OPENING WORST CITIES DATABASE -> PRESS ENTER TO CONTINUE.

Render:
    manim -pqh --fps 30 boot.py WorstCitiesBoot
"""

import os

import numpy as np
from manim import *

BG        = "#04110B"
GREEN     = "#3DFF7A"
GREEN_BRT = "#CFFFDD"
GREEN_DIM = "#1F8A45"
GREEN_SHA = "#0E5A28"   # extrude shadow
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

        def blink(period=0.6, duty=0.6):
            return (clock.get_value() % period) < period * duty

        # --- header ---
        header = left(T("WORST CITIES DATABASE   /   BOOT SEQUENCE", 16, GREEN_DIM), -6.6, 3.55)

        # --- title: crisp pixel wordmark with a 3D extrude shadow ---
        main = Text("WORST CITIES", font=FONT_TITLE, color=GREEN_BRT).scale_to_fit_width(9.0)
        main.move_to([0, 2.45, 0]).set_z_index(22)
        extrude = VGroup()
        for k in range(5, 0, -1):
            e = main.copy().set_color(GREEN_SHA if k > 2 else GREEN)
            e.shift(np.array([0.05, -0.05, 0]) * k).set_z_index(20)
            extrude.add(e)
        ghostL = main.copy().set_color(GREEN).set_opacity(0.6).shift(LEFT * 0.22).set_z_index(21)
        ghostR = main.copy().set_color(GREEN_BRT).set_opacity(0.6).shift(RIGHT * 0.22).set_z_index(21)

        subtitle = left(T("FICTIONAL CITY HAZARD   //   RANKING SYSTEM", 19, GREEN_DIM), -6.58, 1.62)
        underline = Line([-6.6, 1.36, 0], [6.6, 1.36, 0], color=BORDER, stroke_width=1.5)

        # --- boot log ---
        log_x, log_y0, log_dy = -6.55, 1.02, 0.305
        lines = []
        for i, txt in enumerate(BOOT_LINES):
            y = log_y0 - i * log_dy
            granted = (txt == "ACCESS GRANTED")
            chk = T("[", 20, GREEN_DIM)
            ok = T("OK", 20, GREEN_BRT)
            chk2 = T("]", 20, GREEN_DIM)
            grp = VGroup(chk, ok, chk2).arrange(RIGHT, buff=0.06)
            left(grp, log_x, y)
            body = left(T(txt, 20, GREEN_BRT if granted else GREEN), log_x + 0.95, y)
            lines.append(VGroup(grp, body))

        open_y = log_y0 - len(BOOT_LINES) * log_dy - 0.04
        open_t = left(T("> OPENING WORST CITIES DATABASE", 20, GREEN_BRT), log_x, open_y)
        open_cur = Rectangle(width=0.16, height=0.30, stroke_width=0, fill_color=GREEN,
                             fill_opacity=1).next_to(open_t, RIGHT, buff=0.1)
        open_cur.add_updater(lambda m: m.set_opacity(1.0 if blink(0.5) else 0.0))

        # --- cool segmented loading bar ---
        prog = ValueTracker(0.0)
        bar_l, bar_w, bar_y = -6.6, 11.2, -2.95
        NSEG = 44
        seg_w = bar_w / NSEG
        bar_bg = Rectangle(width=bar_w + 0.08, height=0.28, stroke_color=GREEN_DIM,
                           stroke_width=1.2, fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])

        def make_bar():
            val = prog.get_value()
            edge = int(val * NSEG)
            g = VGroup()
            for k in range(NSEG):
                cx = bar_l + (k + 0.5) * seg_w
                if k < edge:
                    g.add(Rectangle(width=seg_w * 0.74, height=0.2, stroke_width=0,
                                    fill_color=GREEN, fill_opacity=1).move_to([cx, bar_y, 0]))
                elif k == edge and val < 0.999:
                    p = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(clock.get_value() * 26))
                    g.add(Rectangle(width=seg_w * 0.74, height=0.2, stroke_width=0,
                                    fill_color=GREEN_BRT, fill_opacity=p).move_to([cx, bar_y, 0]))
                else:
                    g.add(Rectangle(width=seg_w * 0.74, height=0.2, stroke_width=1,
                                    stroke_color=GREEN_DIM, fill_opacity=0).move_to([cx, bar_y, 0]))
            fw = max(0.001, bar_w * val)
            glow = Rectangle(width=fw, height=0.2, stroke_width=0, fill_opacity=0).move_to([bar_l + fw / 2, bar_y, 0])
            glow = glow.set_stroke(GREEN, 7, 0.18)
            return VGroup(glow, g)
        bar = always_redraw(make_bar)
        pct = always_redraw(lambda: T(f"{int(round(prog.get_value()*100)):3d}%", 20, GREEN_BRT).move_to([6.15, bar_y, 0]))

        # --- bottom ---
        ref = left(T("THREAT REF:  HIGH / SEVERE / EXTREME / APOCALYPTIC / UNMEASURABLE", 15, GREEN_DIM), -6.6, -3.4)
        press = left(T("PRESS ENTER TO CONTINUE", 18, GREEN), -6.6, -3.68)
        press_cur = Rectangle(width=0.15, height=0.26, stroke_width=0, fill_color=GREEN,
                              fill_opacity=1).next_to(press, RIGHT, buff=0.08)
        press_cur.add_updater(lambda m: m.set_opacity(1.0 if blink(0.55) else 0.0))

        scan = VGroup(*[
            Line([-7.2, y, 0], [7.2, y, 0], color=BG, stroke_width=2, stroke_opacity=0.11)
            for y in np.arange(-4.0, 4.0, 0.15)
        ]).set_z_index(15)

        def flash(op=0.22, color=GREEN):
            fl = Rectangle(width=15, height=8.5, stroke_width=0, fill_color=color, fill_opacity=0.0).set_z_index(40)
            self.add(fl)
            self.play(fl.animate.set_fill(color, opacity=op), run_time=0.05)
            self.play(fl.animate.set_fill(color, opacity=0.0), run_time=0.13)
            self.remove(fl)

        # =================================================================
        # SEQUENCE
        # =================================================================
        self.add(clock)
        self.add_sound(snd("ambient.wav"), gain=-14)
        self.add_sound(snd("boot.wav"), gain=-3)

        self.add(scan)
        self.play(FadeIn(header), run_time=0.3)

        # glitch reveal of the title
        self.add(extrude, ghostL, ghostR)
        self.play(
            FadeIn(main),
            ghostL.animate.shift(RIGHT * 0.22).set_opacity(0),
            ghostR.animate.shift(LEFT * 0.22).set_opacity(0),
            run_time=0.32,
        )
        self.remove(ghostL, ghostR)
        for op, rt in [(0.35, 0.04), (1.0, 0.05), (0.5, 0.04), (1.0, 0.06)]:
            self.play(main.animate.set_opacity(op), run_time=rt)
        # scanline sweep across the title
        sweep = Rectangle(width=9.6, height=0.07, stroke_width=0, fill_color=GREEN_BRT,
                          fill_opacity=0.8).move_to([0, 2.95, 0]).set_z_index(23)
        self.add(sweep)
        self.play(sweep.animate.move_to([0, 1.95, 0]), run_time=0.4, rate_func=linear)
        self.remove(sweep)

        self.play(FadeIn(subtitle), Create(underline), run_time=0.35)
        self.add(bar_bg, bar, pct)

        # boot log (fills to ~90%, each line a sharp key click)
        n = len(lines)
        for i, line in enumerate(lines):
            self.add_sound(snd("key.wav"), gain=-5)
            self.play(FadeIn(line, shift=RIGHT * 0.06),
                      prog.animate.set_value((i + 1) / (n + 1)), run_time=0.16)
            if i < n - 1:
                self.wait(0.14)

        # final rush to 100% -> CLICK + ACCESS + flash
        self.add_sound(snd("charge.wav"), gain=-5)
        self.play(prog.animate.set_value(1.0), run_time=0.5, rate_func=rush_into)
        self.add_sound(snd("click.wav"), gain=-2)
        self.add_sound(snd("access.wav"), gain=-2)
        flash(0.22)
        self.wait(0.35)

        # opening line + press enter
        self.play(AddTextLetterByLetter(open_t), run_time=0.55)
        self.add(open_cur)
        self.wait(0.5)
        self.add_sound(snd("transition.wav"), gain=-8)
        self.play(FadeIn(ref), FadeIn(press), run_time=0.4)
        self.add(press_cur)
        self.wait(2.4)
