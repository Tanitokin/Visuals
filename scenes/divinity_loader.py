"""divinity_loader.py - ARTIFICIAL DIVINITY INDEX // ARCHIVE EDITION boot.

A clean, high-contrast OS-style boot screen that plays before the selector:
pure-black background, a saturated blue accent, a centred title (Oxanium) with
a crisp neon glow (stroke halos - keeps the black pure, no bloom wash), an
"ARCHIVE EDITION" subtitle, a glossy segmented loading bar, three status lines
with circle markers, a three-column corporate footer, and ACCESS GRANTED.

Title font: Oxanium (Bold).  Body font: TheSansMonoSCd.  SFX from assets/.

Render (then just trim to length + audio fade - NO post bloom):
    ./.venv/bin/manim -qh --fps 30 scenes/divinity_loader.py DivinityLoader
    ffmpeg -i <raw>.mp4 -t 5.5 -af "afade=t=out:st=5.2:d=0.3" \
        -c:v libx264 -crf 14 -pix_fmt yuv420p -c:a aac -b:a 192k <final>.mp4
"""

import os
import sys

import numpy as np
from manim import *
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crt_style import snd

# --- High-contrast palette (pure black, saturated blue) -------------------
BG       = "#000000"
WHITE    = "#FFFFFF"
BLUE     = "#246BFF"     # vivid, saturated
BLUE_BRT = "#7FB2FF"
DIM      = "#5A6E92"
DIMMER   = "#33425E"

TITLE_FONT = "Ethnocentric"
FONT = "TheSansMonoSCd"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF = os.path.join(BASE, "assets", "godforge", "Godforge_Intro_Assets")
SCALE_DIR = os.path.join(BASE, "media", "_scaled")
os.makedirs(SCALE_DIR, exist_ok=True)


def gf(rel, target_w=1280):
    src = os.path.join(GF, rel)
    out = os.path.join(SCALE_DIR, rel.replace("/", "_") + f".{target_w}.png")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        im = PILImage.open(src)
        if im.width > target_w:
            im = im.resize((target_w, round(im.height * target_w / im.width)), PILImage.LANCZOS)
        im.save(out)
    return ImageMobject(out)


class DivinityLoader(Scene):
    def construct(self):
        self.camera.background_color = BG
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def T(s, size, color=WHITE, **kw):
            return Text(s, font=FONT, font_size=size, color=color, **kw)

        # --- very subtle CRT scanlines (keep it clean; pure black bg) ----
        scan = gf("07_Effects/crt_scanlines.png", 1920).scale_to_fit_height(8.0).set_z_index(40).set_opacity(0.06)

        # =================================================================
        # TITLE  (Oxanium, centred, crisp white + blue "INDEX", neon glow)
        # =================================================================
        title = Text("ARTIFICIAL DIVINITY INDEX", font=TITLE_FONT,
                     color=WHITE).scale_to_fit_width(8.8).move_to([0, 1.45, 0])
        # neon glow = stroke halos behind (no fill) -> clean glow, pure-black safe
        glow = VGroup()
        for w, o in [(16, 0.06), (9, 0.12), (4, 0.22)]:
            glow.add(title.copy().set_fill(opacity=0).set_stroke(BLUE, width=w, opacity=o))
        glow.set_z_index(-1)
        glow.add_updater(lambda m: m.set_opacity(0.8 + 0.2 * (0.5 + 0.5 * np.sin(clock.get_value() * 1.9))))

        subtitle = T("A R C H I V E   E D I T I O N", 17, WHITE).set_opacity(0.9).move_to([0, 0.66, 0])
        sl, sr = subtitle.get_left()[0], subtitle.get_right()[0]
        fl_l = VGroup(Line([sl - 1.05, 0.66, 0], [sl - 0.28, 0.66, 0], color=BLUE, stroke_width=1.6),
                      Dot([sl - 0.18, 0.66, 0], radius=0.024, color=BLUE))
        fl_r = VGroup(Line([sr + 1.05, 0.66, 0], [sr + 0.28, 0.66, 0], color=BLUE, stroke_width=1.6),
                      Dot([sr + 0.18, 0.66, 0], radius=0.024, color=BLUE))

        # =================================================================
        # SEGMENTED LOADING BAR
        # =================================================================
        bar_w, bar_y = 6.8, -0.18
        bar_l = -bar_w / 2
        container = RoundedRectangle(width=bar_w + 0.16, height=0.42, corner_radius=0.08,
                                     stroke_color=DIM, stroke_width=1.4, fill_color="#04060C",
                                     fill_opacity=1).move_to([0, bar_y, 0])
        cont_glow = RoundedRectangle(width=bar_w + 0.16, height=0.42, corner_radius=0.08,
                                     stroke_color=BLUE, stroke_width=5, fill_opacity=0).set_stroke(opacity=0.12)
        prog = ValueTracker(0.0)
        NSEG = 22
        seg_w = bar_w / NSEG

        def make_blocks():
            edge = prog.get_value() * NSEG
            g = VGroup()
            fw = bar_w * prog.get_value()
            if fw > 0.01:
                g.add(Rectangle(width=fw, height=0.26, stroke_width=0, fill_opacity=0
                                ).move_to([bar_l + fw / 2, bar_y, 0]).set_stroke(BLUE, 12, 0.28))
            for k in range(NSEG):
                if k < edge - 0.001:
                    cx = bar_l + (k + 0.5) * seg_w
                    g.add(Rectangle(width=seg_w * 0.72, height=0.24, stroke_width=0,
                                    fill_color=BLUE, fill_opacity=1).move_to([cx, bar_y, 0]))
                    g.add(Rectangle(width=seg_w * 0.72, height=0.09, stroke_width=0,
                                    fill_color=BLUE_BRT, fill_opacity=0.7).move_to([cx, bar_y + 0.07, 0]))
            return g
        blocks = always_redraw(make_blocks)

        # =================================================================
        # STATUS LINES
        # =================================================================
        STATUS = ["Initializing subject registry",
                  "Mounting restricted dossiers",
                  "Verifying divinity index"]
        ly = [-0.92, -1.28, -1.64]
        rows = []
        for i, s in enumerate(STATUS):
            mk = Circle(radius=0.075, stroke_color=DIM, stroke_width=1.8, fill_color=BLUE, fill_opacity=0.0)
            mglow = Circle(radius=0.075, stroke_color=BLUE, stroke_width=5, fill_opacity=0).set_stroke(opacity=0.0)
            txt = T(s, 19, DIM)
            VGroup(mk, txt).arrange(RIGHT, buff=0.28).move_to([0, ly[i], 0]).align_to([-2.95, 0, 0], LEFT)
            mglow.move_to(mk.get_center())
            rows.append({"mk": mk, "mglow": mglow, "txt": txt})

        # =================================================================
        # FOOTER (three columns) + live STATUS
        # =================================================================
        fy = -3.2
        f_l1 = T("A.D.I. ARCHIVE EDITION v1.0.4", 15, DIM)
        f_l2 = T("BUILD 667.01.13", 15, BLUE_BRT)
        fl_col = VGroup(f_l1, f_l2).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        fl_col.move_to([-6.65 + fl_col.width / 2, fy - 0.07, 0])

        f_c1 = T("(C) 2001-2026  BLACKSITE RESEARCH DIVISION", 14, DIM)
        f_c2 = T("ALL RIGHTS RESERVED", 13, DIMMER)
        fc_col = VGroup(f_c1, f_c2).arrange(DOWN, buff=0.1).move_to([0, fy - 0.07, 0])

        f_r1 = T("ARTIFICIAL DIVINITY SUBSYSTEM", 15, DIM)
        status_field = VGroup(T("STATUS: ", 15, DIM), T("BOOTING", 15, BLUE_BRT)).arrange(RIGHT, buff=0.12)
        fr_col = VGroup(f_r1, status_field).arrange(DOWN, aligned_edge=RIGHT, buff=0.1)
        fr_col.move_to([6.65 - fr_col.width / 2, fy - 0.07, 0])

        # =================================================================
        # SEQUENCE  (~5s)
        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-22)
        self.add(scan, glow)

        static = VGroup(title, subtitle, fl_l, fl_r, container, cont_glow, fl_col, fc_col, fr_col)
        self.play(FadeIn(static), run_time=0.7, rate_func=smooth)
        for r in rows:
            self.add(r["mk"], r["mglow"], r["txt"])
        self.add(blocks)
        self.add_sound(snd("es_loading_slow.wav"), gain=-6)   # the loading sound
        self.wait(0.35)

        def activate(i, target, prev=None):
            self.add_sound(snd("es_system_beep.wav"), gain=-11)
            anims = [rows[i]["txt"].animate.set_color(WHITE),
                     rows[i]["mk"].animate.set_fill(BLUE, 1.0).set_stroke(BLUE, 1.8),
                     rows[i]["mglow"].animate.set_stroke(BLUE, 5, 0.5),
                     prog.animate.set_value(target)]
            if prev is not None:
                anims += [rows[prev]["txt"].animate.set_color(DIM),
                          rows[prev]["mglow"].animate.set_stroke(BLUE, 5, 0.0),
                          rows[prev]["mk"].animate.set_fill(BLUE, 0.5)]
            self.play(*anims, run_time=0.82, rate_func=smooth)

        activate(0, 0.34)
        self.wait(0.12)
        activate(1, 0.69, prev=0)
        self.wait(0.12)
        activate(2, 1.0, prev=1)
        self.play(rows[2]["mglow"].animate.set_stroke(BLUE, 5, 0.0),
                  rows[2]["mk"].animate.set_fill(BLUE, 0.5),
                  rows[2]["txt"].animate.set_color(DIM), run_time=0.3)

        # ACCESS GRANTED + STATUS -> READY
        self.add_sound(snd("es_select_ok.wav"), gain=-6)
        new_status = VGroup(T("STATUS: ", 15, DIM), T("READY", 15, BLUE_BRT)).arrange(RIGHT, buff=0.12)
        new_status.move_to(status_field.get_right(), aligned_edge=RIGHT)
        ag = Text("ACCESS GRANTED", font=TITLE_FONT, font_size=24,
                  color=WHITE, t2c={"GRANTED": BLUE_BRT}).move_to([0, -2.28, 0])
        ag_glow = VGroup(*[ag.copy().set_fill(opacity=0).set_stroke(BLUE, width=w, opacity=o)
                           for w, o in [(16, 0.07), (8, 0.14)]]).set_z_index(-1)
        self.play(FadeIn(ag, scale=1.1), FadeIn(ag_glow),
                  Transform(status_field, new_status), run_time=0.4, rate_func=rush_from)
        self.wait(0.5)

        # clean cut to black (into the selector)
        self.add_sound(snd("es_system_beep.wav"), gain=-9)
        black = Rectangle(width=15, height=8.6, stroke_width=0, fill_color="#000000",
                          fill_opacity=0.0).set_z_index(60)
        self.add(black)
        self.play(black.animate.set_fill("#000000", 1.0), run_time=0.3, rate_func=smooth)
        self.wait(0.2)
