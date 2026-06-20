"""divinity_loader.py - ARTIFICIAL DIVINITY INDEX // ARCHIVE EDITION boot.

A clean, premium OS-style boot screen (in the spirit of a polished XP-era
loader) that plays before the ARTIFICIAL DIVINITY INDEX selector:

  - an app-icon tile with a red targeting reticle, beside the system title
  - title (white) with "INDEX" picked out in blue, soft glow
  - "ARCHIVE EDITION" subtitle flanked by flourish lines
  - a glossy segmented loading bar
  - three status lines with circle markers, activating one by one
  - a three-column corporate footer with a live STATUS field
  - ACCESS GRANTED, then a clean flash to black (cuts into the selector)

Textures are static and even (no random noise / flicker). Font: TheSansMonoSCd.

Render, then add the premium glow (bloom) + trim in post (screen-blend must be
done in RGB - format=gbrp - or YUV chroma washes the frame):

    ./.venv/bin/manim -qh --fps 30 scenes/divinity_loader.py DivinityLoader
    ffmpeg -i media/videos/divinity_loader/1080p30/DivinityLoader.mp4 -t 5.5 \
      -filter_complex "[0:v]format=gbrp,split=3[b][g1][g2];\
        [g1]gblur=sigma=4[x];[g2]gblur=sigma=15[y];\
        [b][x]blend=all_mode=screen:all_opacity=0.55[t];\
        [t][y]blend=all_mode=screen:all_opacity=0.5[v]" -map "[v]" \
      -af "afade=t=out:st=5.2:d=0.3" -c:v libx264 -crf 16 -pix_fmt yuv420p \
      -c:a aac -b:a 192k DivinityLoader_final.mp4
"""

import os
import sys

import numpy as np
from manim import *
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crt_style import snd

# --- Palette (deep navy, white + blue, one red accent) --------------------
BG       = "#000000"
WHITE    = "#EAF1FF"
BLUE     = "#3E82F7"
BLUE_BRT = "#8FBAFF"
RED      = "#FF3A3A"
DIM      = "#56678A"
DIMMER   = "#36425C"
TILE     = "#0C1322"

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

        # =================================================================
        # BACKGROUND  (static, even textures only)
        # =================================================================
        vign = gf("07_Effects/vignette_overlay.png", 768).scale_to_fit_height(8.0).set_z_index(40).set_opacity(0.45)
        scan = gf("07_Effects/crt_scanlines.png", 1920).scale_to_fit_height(8.0).set_z_index(41).set_opacity(0.06)

        # =================================================================
        # EMBLEM TILE  (app icon: rounded tile + red targeting reticle)
        # =================================================================
        tile = RoundedRectangle(width=1.0, height=1.0, corner_radius=0.2,
                                stroke_color=BLUE_BRT, stroke_width=1.6,
                                fill_color=TILE, fill_opacity=1)
        tile_glow = RoundedRectangle(width=1.0, height=1.0, corner_radius=0.2,
                                     stroke_color=WHITE, stroke_width=4, fill_opacity=0).set_stroke(opacity=0.10)
        rg = Circle(radius=0.30, stroke_color=RED, stroke_width=9).set_stroke(opacity=0.22)
        ro = Circle(radius=0.30, stroke_color=RED, stroke_width=2.4)
        cross = VGroup()
        for a in [0, 90, 180, 270]:
            v = np.array([np.cos(a * DEGREES), np.sin(a * DEGREES), 0])
            cross.add(Line(v * 0.13, v * 0.30, color=RED, stroke_width=2.2))
        cdot = Dot(radius=0.045, color="#FFE0E0")
        reticle = VGroup(rg, ro, cross, cdot)

        def reticle_pulse(m):
            p = 0.5 + 0.5 * np.sin(clock.get_value() * 2.4)
            rg.set_stroke(RED, 9, 0.14 + 0.16 * p)
        rg.add_updater(reticle_pulse)
        emblem = VGroup(tile_glow, tile, reticle)

        # =================================================================
        # TITLE + SUBTITLE
        # =================================================================
        title = T("ARTIFICIAL DIVINITY INDEX", 38, WHITE, t2c={"INDEX": BLUE})
        title.scale_to_fit_width(6.7)
        tglow = title.copy().set_color(BLUE_BRT).scale(1.03).set_opacity(0.0)
        tglow.add_updater(lambda m: m.set_opacity(0.22 + 0.08 * (0.5 + 0.5 * np.sin(clock.get_value() * 1.8))))

        head = VGroup(emblem.scale_to_fit_height(1.06), title).arrange(RIGHT, buff=0.42).move_to([0, 1.55, 0])
        tglow.move_to(title.get_center())

        subtitle = T("A R C H I V E   E D I T I O N", 17, WHITE).set_opacity(0.9)
        subtitle.move_to([0, 0.78, 0])
        sl, sr = subtitle.get_left()[0], subtitle.get_right()[0]
        fl_l = VGroup(Line([sl - 1.05, 0.78, 0], [sl - 0.28, 0.78, 0], color=BLUE, stroke_width=1.4),
                      Dot([sl - 0.18, 0.78, 0], radius=0.022, color=BLUE))
        fl_r = VGroup(Line([sr + 1.05, 0.78, 0], [sr + 0.28, 0.78, 0], color=BLUE, stroke_width=1.4),
                      Dot([sr + 0.18, 0.78, 0], radius=0.022, color=BLUE))

        # =================================================================
        # SEGMENTED LOADING BAR  (glossy XP-style blocks)
        # =================================================================
        bar_w, bar_y = 6.8, 0.0
        bar_l = -bar_w / 2
        container = RoundedRectangle(width=bar_w + 0.16, height=0.42, corner_radius=0.08,
                                     stroke_color=DIM, stroke_width=1.4, fill_color="#070C16",
                                     fill_opacity=1).move_to([0, bar_y, 0])
        cont_glow = RoundedRectangle(width=bar_w + 0.16, height=0.42, corner_radius=0.08,
                                     stroke_color=BLUE, stroke_width=4, fill_opacity=0).set_stroke(opacity=0.10)
        prog = ValueTracker(0.0)
        NSEG = 22
        seg_w = bar_w / NSEG

        def make_blocks():
            edge = prog.get_value() * NSEG
            g = VGroup()
            for k in range(NSEG):
                if k < edge - 0.001:
                    cx = bar_l + (k + 0.5) * seg_w
                    blk = Rectangle(width=seg_w * 0.72, height=0.24, stroke_width=0,
                                    fill_color=BLUE, fill_opacity=1).move_to([cx, bar_y, 0])
                    gloss = Rectangle(width=seg_w * 0.72, height=0.10, stroke_width=0,
                                      fill_color=BLUE_BRT, fill_opacity=0.55).move_to([cx, bar_y + 0.06, 0])
                    g.add(blk, gloss)
            if len(g):
                fw = bar_w * prog.get_value()
                halo = Rectangle(width=fw, height=0.24, stroke_width=0, fill_opacity=0
                                 ).move_to([bar_l + fw / 2, bar_y, 0]).set_stroke(BLUE, 9, 0.22)
                g.add(halo)
            return g
        blocks = always_redraw(make_blocks)

        # =================================================================
        # STATUS LINES  (circle marker + text; activate one by one)
        # =================================================================
        STATUS = ["Initializing subject registry",
                  "Mounting restricted dossiers",
                  "Verifying divinity index"]
        ly = [-0.78, -1.16, -1.54]
        rows = []
        for i, s in enumerate(STATUS):
            mk = Circle(radius=0.075, stroke_color=DIM, stroke_width=1.8, fill_color=BLUE, fill_opacity=0.0)
            mglow = Circle(radius=0.075, stroke_color=BLUE, stroke_width=5, fill_opacity=0).set_stroke(opacity=0.0)
            txt = T(s, 19, DIM)
            VGroup(mk, txt).arrange(RIGHT, buff=0.28).move_to([0, ly[i], 0]).align_to([-2.95, 0, 0], LEFT)
            mglow.move_to(mk.get_center())
            rows.append({"mk": mk, "mglow": mglow, "txt": txt})

        # =================================================================
        # FOOTER  (three columns) + live STATUS field
        # =================================================================
        fy = -3.18
        f_l1 = T("A.D.I. ARCHIVE EDITION v1.0.4", 15, DIM)
        f_l2 = T("BUILD 667.01.13", 15, BLUE)
        fl_col = VGroup(f_l1, f_l2).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        fl_col.move_to([-6.65 + fl_col.width / 2, fy - 0.07, 0])

        f_c1 = T("(C) 2001-2026  BLACKSITE RESEARCH DIVISION", 14, DIM)
        f_c2 = T("ALL RIGHTS RESERVED", 13, DIMMER)
        fc_col = VGroup(f_c1, f_c2).arrange(DOWN, buff=0.1).move_to([0, fy - 0.07, 0])

        f_r1 = T("ARTIFICIAL DIVINITY SUBSYSTEM", 15, DIM)
        status_field = VGroup(T("STATUS: ", 15, DIM), T("BOOTING", 15, BLUE)).arrange(RIGHT, buff=0.12)
        fr_col = VGroup(f_r1, status_field).arrange(DOWN, aligned_edge=RIGHT, buff=0.1)
        fr_col.move_to([6.65 - fr_col.width / 2, fy - 0.07, 0])

        # =================================================================
        # SEQUENCE  (~5s, clean and deterministic)
        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-18)
        self.add(vign, scan)
        self.add(tglow)

        static = VGroup(emblem, title, subtitle, fl_l, fl_r, container, cont_glow,
                        fl_col, fc_col, fr_col)
        self.play(FadeIn(static), run_time=0.7, rate_func=smooth)
        for r in rows:
            self.add(r["mk"], r["mglow"], r["txt"])
        self.add(blocks)
        self.add_sound(snd("es_loading_slow.wav"), gain=-10)
        self.wait(0.3)

        def activate(i, target, prev=None):
            self.add_sound(snd("es_system_beep.wav"), gain=-11)
            anims = [rows[i]["txt"].animate.set_color(WHITE),
                     rows[i]["mk"].animate.set_fill(BLUE, 1.0).set_stroke(BLUE, 1.8),
                     rows[i]["mglow"].animate.set_stroke(BLUE, 5, 0.45),
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

        # STATUS: BOOTING -> ACCESS GRANTED
        self.add_sound(snd("es_select_ok.wav"), gain=-6)
        new_status = VGroup(T("STATUS: ", 15, DIM), T("READY", 15, BLUE_BRT)).arrange(RIGHT, buff=0.12)
        new_status.move_to(status_field.get_right(), aligned_edge=RIGHT)
        ag = T("ACCESS GRANTED", 26, WHITE, t2c={"GRANTED": BLUE_BRT}).move_to([0, -2.18, 0])
        self.play(FadeIn(ag, scale=1.1),
                  Transform(status_field, new_status), run_time=0.4, rate_func=rush_from)
        self.wait(0.45)

        # clean flash -> fade to black
        self.add_sound(snd("transition.wav"), gain=-9)
        flash = Rectangle(width=15, height=8.6, stroke_width=0, fill_color=WHITE, fill_opacity=0.0).set_z_index(50)
        self.add(flash)
        self.play(flash.animate.set_fill(WHITE, 0.45), run_time=0.08, rate_func=linear)
        black = Rectangle(width=15, height=8.6, stroke_width=0, fill_color="#000000", fill_opacity=0.0).set_z_index(51)
        self.add(black)
        self.play(flash.animate.set_fill(WHITE, 0.0), black.animate.set_fill("#000000", 1.0),
                  run_time=0.34, rate_func=smooth)
        self.wait(0.22)
