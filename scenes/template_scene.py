"""template_scene.py - minimal starter using the crt_style toolkit.

A tiny demo: header + title + a panel + a segmented loading bar that fills with
mechanical clicks and an ACCESS GRANTED at 100%, plus a blinking prompt. Copy
this file and edit to start a new CRT-terminal scene.

Render:
    manim -pqh --fps 30 scenes/template_scene.py CRTTemplate
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find crt_style next to this file
from crt_style import *


class CRTTemplate(CRTScene):
    def construct(self):
        self.start_crt()                       # bg + clock + scanlines + hum
        self.add_sound(snd("boot.wav"), gain=-4)

        # frame + header
        frame = Rectangle(width=13.9, height=7.55, stroke_color=BORDER,
                          stroke_width=1.5, fill_opacity=0)
        header = left(self.txt("TEMPLATE TERMINAL   /   READY", 16, GREEN_DIM), -6.55, 3.5)
        self.play(Create(frame), run_time=0.5)
        self.play(AddTextLetterByLetter(header), run_time=0.6)

        # title (same font as body, left aligned)
        title = left(self.txt("NEW PROJECT", 64, GREEN_BRT), -6.55, 2.3)
        self.play(FadeIn(title, scale=1.04), run_time=0.5)

        # a panel with some content
        panel = Rectangle(width=8.0, height=2.4, stroke_color=BORDER, stroke_width=1.5,
                          fill_color=PANEL_FILL, fill_opacity=0.5).move_to([-2.6, -0.3, 0])
        body = left(self.txt("> system online\n> awaiting input", 24, GREEN), -6.3, -0.3)
        self.play(Create(panel), FadeIn(body), run_time=0.6)

        # segmented loading bar
        prog = ValueTracker(0.0)
        bar_l, bar_w, bar_y = -6.6, 11.2, -2.4
        bar = always_redraw(make_segmented_bar(prog, self.clock, bar_l, bar_w, bar_y))
        pct = always_redraw(lambda: self.txt(
            f"{int(round(prog.get_value()*100)):3d}%", 20, GREEN_BRT).move_to([6.15, bar_y, 0]))
        self.add(bar, pct)
        for i in range(5):
            self.add_sound(snd("key.wav"), gain=-5)
            self.play(prog.animate.set_value((i + 1) / 6), run_time=0.18, rate_func=smooth)
            self.wait(0.1)
        self.add_sound(snd("charge.wav"), gain=-6)
        self.play(prog.animate.set_value(1.0), run_time=0.5, rate_func=smooth)
        self.add_sound(snd("click.wav"), gain=0)
        self.add_sound(snd("access.wav"), gain=1)
        self.flash(0.25)

        # blinking prompt
        prompt = left(self.txt("PRESS ENTER TO CONTINUE", 20, GREEN), -6.6, -3.5)
        cur = blink_cursor(clock=self.clock).next_to(prompt, RIGHT, buff=0.1)
        self.play(FadeIn(prompt), run_time=0.4)
        self.add(cur)
        self.wait(1.6)
