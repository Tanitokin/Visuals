"""WORST CITIES - boot / initial loading screen (v3).

Green-CRT terminal boot. Single-layer title (no extrude/ghost layers) with a
gentle "alive" CRT flicker; smooth fade reveals; a soft glow band that drifts
down the screen and a subtle global brightness flicker keep everything alive. A
segmented loading bar fills and hits a CLICK + ACCESS chime + flash at 100%,
then OPENING WORST CITIES DATABASE -> PRESS ENTER TO CONTINUE.

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

        # --- header + single-layer title ---
        header = left(T("WORST CITIES DATABASE   /   BOOT SEQUENCE", 16, GREEN_DIM), -6.6, 3.55)

        # title in the same font as the body (VT323), left-aligned, single layer
        title = Text("WORST CITIES", font=FONT_BODY, color=GREEN_BRT).scale_to_fit_width(6.6)
        left(title, -6.6, 2.55)
        title.set_z_index(22)

        subtitle = left(T("FICTIONAL CITY HAZARD   //   RANKING SYSTEM", 19, GREEN_DIM), -6.58, 1.62)
        underline = Line([-6.6, 1.36, 0], [6.6, 1.36, 0], color=BORDER, stroke_width=1.5)

        # --- boot log ---
        log_x, log_y0, log_dy = -6.55, 1.02, 0.305
        lines = []
        for i, txt in enumerate(BOOT_LINES):
            y = log_y0 - i * log_dy
            granted = (txt == "ACCESS GRANTED")
            tag = VGroup(T("[", 20, GREEN_DIM), T("OK", 20, GREEN_BRT), T("]", 20, GREEN_DIM)).arrange(RIGHT, buff=0.06)
            left(tag, log_x, y)
            body = left(T(txt, 20, GREEN_BRT if granted else GREEN), log_x + 0.95, y)
            lines.append(VGroup(tag, body))

        open_y = log_y0 - len(BOOT_LINES) * log_dy - 0.04
        open_t = left(T("> OPENING WORST CITIES DATABASE", 20, GREEN_BRT), log_x, open_y)
        open_cur = Rectangle(width=0.16, height=0.30, stroke_width=0, fill_color=GREEN,
                             fill_opacity=1).next_to(open_t, RIGHT, buff=0.1)
        open_cur.add_updater(lambda m: m.set_opacity(1.0 if blink(0.5) else 0.0))

        # --- segmented loading bar ---
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
            glow.set_stroke(GREEN, 7, 0.18)
            return VGroup(glow, g)
        bar = always_redraw(make_bar)
        pct = always_redraw(lambda: T(f"{int(round(prog.get_value()*100)):3d}%", 20, GREEN_BRT).move_to([6.15, bar_y, 0]))

        # --- bottom ---
        ref = left(T("THREAT REF:  HIGH / SEVERE / EXTREME / APOCALYPTIC / UNMEASURABLE", 15, GREEN_DIM), -6.6, -3.4)
        press = left(T("PRESS ENTER TO CONTINUE", 18, GREEN), -6.6, -3.68)
        press_cur = Rectangle(width=0.15, height=0.26, stroke_width=0, fill_color=GREEN,
                              fill_opacity=1).next_to(press, RIGHT, buff=0.08)
        press_cur.add_updater(lambda m: m.set_opacity(1.0 if blink(0.55) else 0.0))

        # --- "alive" CRT ambience: static scanlines + drifting glow band + flicker ---
        scan = VGroup(*[
            Line([-7.2, y, 0], [7.2, y, 0], color=BG, stroke_width=2, stroke_opacity=0.11)
            for y in np.arange(-4.0, 4.0, 0.15)
        ]).set_z_index(15)

        drift = Rectangle(width=15, height=0.7, stroke_width=0, fill_color=GREEN, fill_opacity=0.05).set_z_index(13)
        drift.add_updater(lambda m: m.move_to([0, 4.2 - ((clock.get_value() * 1.7) % 8.4), 0]))

        flick = Rectangle(width=15, height=8.6, stroke_width=0, fill_color=BG, fill_opacity=0.0).set_z_index(38)

        def flick_up(m):
            t = clock.get_value()
            base = 0.02 + 0.025 * (0.5 + 0.5 * np.sin(t * 6.3))
            spike = 0.06 if (np.sin(t * 47.0) > 0.93) else 0.0
            m.set_opacity(base + spike)
        flick.add_updater(flick_up)

        # title breathing (single mobject, no extra layers)
        def title_alive(m):
            t = clock.get_value()
            m.set_opacity(0.9 + 0.1 * (0.5 + 0.5 * np.sin(t * 2.3)) - (0.25 if np.sin(t * 39) > 0.96 else 0))
        # (added after reveal)

        def flash(op=0.22, color=GREEN):
            fl = Rectangle(width=15, height=8.6, stroke_width=0, fill_color=color, fill_opacity=0.0).set_z_index(40)
            self.add(fl)
            self.play(fl.animate.set_fill(color, opacity=op), run_time=0.06)
            self.play(fl.animate.set_fill(color, opacity=0.0), run_time=0.16, rate_func=smooth)
            self.remove(fl)

        # =================================================================
        # SEQUENCE
        # =================================================================
        self.add(clock)
        self.add_sound(snd("crt_hum.wav"), gain=-10)
        self.add_sound(snd("boot.wav"), gain=-3)

        self.add(scan, drift, flick)
        self.play(FadeIn(header), run_time=0.4, rate_func=smooth)

        # smooth title reveal + a couple of gentle flickers, then it "breathes"
        self.play(FadeIn(title, scale=1.04), run_time=0.55, rate_func=smooth)
        for op, rt in [(0.45, 0.05), (1.0, 0.06), (0.6, 0.05), (1.0, 0.07)]:
            self.play(title.animate.set_opacity(op), run_time=rt)
        title.add_updater(title_alive)

        self.play(FadeIn(subtitle, shift=UP * 0.06), Create(underline), run_time=0.45, rate_func=smooth)
        self.add(bar_bg, bar, pct)

        # boot log: smooth fade-up reveals, sharp click each, bar steps up
        n = len(lines)
        for i, line in enumerate(lines):
            self.add_sound(snd("key.wav"), gain=-5)
            self.play(FadeIn(line, shift=UP * 0.12), prog.animate.set_value((i + 1) / (n + 1)),
                      run_time=0.3, rate_func=smooth)
            if i < n - 1:
                self.wait(0.12)

        # smooth rush to 100% -> CLICK + ACCESS + flash
        self.add_sound(snd("charge.wav"), gain=-6)
        self.play(prog.animate.set_value(1.0), run_time=0.55, rate_func=smooth)
        self.add_sound(snd("click.wav"), gain=0)
        self.add_sound(snd("access.wav"), gain=1)
        flash(0.26)
        self.wait(0.45)

        # opening line + press enter
        self.play(AddTextLetterByLetter(open_t), run_time=0.6)
        self.add(open_cur)
        self.wait(0.5)
        self.add_sound(snd("transition.wav"), gain=-8)
        self.play(FadeIn(ref, shift=UP * 0.05), FadeIn(press, shift=UP * 0.05), run_time=0.45, rate_func=smooth)
        self.add(press_cur)
        self.wait(1.3)
