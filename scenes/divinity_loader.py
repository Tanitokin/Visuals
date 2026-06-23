"""divinity_loader.py - ARTIFICIAL DIVINITY INDEX // ARCHIVE EDITION boot.

A clean, high-contrast OS-style boot screen with premium motion that plays
before the selector. Pure-black, saturated blue accent, Ethnocentric title with
a crisp neon glow + a light-sweep reveal, drawn flourishes, a glossy segmented
bar with a pulsing leading edge and a travelling shine, status lines that pop
in with a flare, a drifting scan line for life, and an ACCESS GRANTED burst.

Title font: Ethnocentric.  Body font: TheSansMonoSCd.  SFX from assets/.

Render at 4K/60 for supersampled sharpness, then bloom + lanczos downscale to
1080p + light unsharp + trim to length with an audio fade:
    ./.venv/bin/manim -qk --fps 60 scenes/divinity_loader.py DivinityLoader
    ffmpeg -i <raw4k>.mp4 -t 8.23 -filter_complex \
      "[0:v]format=gbrp,split=2[a][b];[b]gblur=sigma=18[bl];\
       [a][bl]blend=all_mode=screen:all_opacity=0.42[o];\
       [o]scale=1920:1080:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,\
       eq=contrast=1.06:saturation=1.18,format=yuv420p[v]" \
      -map "[v]" -map 0:a -af "afade=t=out:st=7.93:d=0.3" \
      -r 60 -c:v libx264 -crf 12 -pix_fmt yuv420p -c:a aac -b:a 192k <final>.mp4
"""

import os
import sys

import numpy as np
from manim import *
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crt_style import snd

BG       = "#000000"
WHITE    = "#FFFFFF"
BLUE     = "#246BFF"
BLUE_BRT = "#7FB2FF"
TITLE_BLUE = "#3F8BFF"
GREEN     = "#2BE04F"
GREEN_BRT = "#8BFFAD"
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

        scan = gf("07_Effects/crt_scanlines.png", 1920).scale_to_fit_height(8.0).set_z_index(40).set_opacity(0.06)

        # drifting scan line (subtle life)
        scanline = Rectangle(width=15, height=0.04, stroke_width=0, fill_color=BLUE_BRT,
                             fill_opacity=0.05).set_z_index(38)
        scanline.add_updater(lambda m: m.move_to([0, 4.2 - ((clock.get_value() * 1.6) % 8.4), 0]))

        # =================================================================
        # TITLE + GLOW
        # =================================================================
        # title in BLUE; the soft glow behind comes from the post bloom
        title = Text("ARTIFICIAL DIVINITY INDEX", font=TITLE_FONT,
                     color=TITLE_BLUE).scale_to_fit_width(8.8).move_to([0, 1.45, 0])

        subtitle = T("A R C H I V E   E D I T I O N", 17, WHITE).set_opacity(0.9).move_to([0, 0.66, 0])
        sl, sr = subtitle.get_left()[0], subtitle.get_right()[0]
        fl_l = VGroup(Line([-0.2, 0.66, 0], [sl - 0.28, 0.66, 0], color=BLUE, stroke_width=1.6),
                      Dot([sl - 0.18, 0.66, 0], radius=0.024, color=BLUE))
        fl_r = VGroup(Line([0.2, 0.66, 0], [sr + 0.28, 0.66, 0], color=BLUE, stroke_width=1.6),
                      Dot([sr + 0.18, 0.66, 0], radius=0.024, color=BLUE))

        # =================================================================
        # SEGMENTED BAR + animated shine / leading edge
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

        lead = Rectangle(width=0.07, height=0.32, stroke_width=0, fill_color=WHITE, fill_opacity=0.0).set_z_index(6)

        def lead_upd(m):
            fw = bar_w * prog.get_value()
            if fw < 0.05 or prog.get_value() > 0.999:
                m.set_opacity(0.0)
                return
            p = 0.55 + 0.45 * (0.5 + 0.5 * np.sin(clock.get_value() * 18))
            m.move_to([bar_l + fw, bar_y, 0]).set_fill(WHITE, p)
        lead.add_updater(lead_upd)

        shine = Rectangle(width=0.55, height=0.24, stroke_width=0, fill_color=BLUE_BRT, fill_opacity=0.0).set_z_index(5)

        def shine_upd(m):
            fw = bar_w * prog.get_value()
            if fw < 0.4:
                m.set_opacity(0.0)
                return
            t = (clock.get_value() * 1.15) % 1.0
            m.move_to([bar_l + t * fw, bar_y, 0]).set_fill(BLUE_BRT, 0.45 * np.sin(t * np.pi))
        shine.add_updater(shine_upd)

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
            grp = VGroup(mk, txt).arrange(RIGHT, buff=0.28).move_to([0, ly[i], 0]).align_to([-2.95, 0, 0], LEFT)
            mglow.move_to(mk.get_center())
            rows.append({"mk": mk, "mglow": mglow, "txt": txt, "grp": grp, "x": grp.get_center()[0]})

        # =================================================================
        # FOOTER
        # =================================================================
        fy = -3.2
        fl_col = VGroup(T("A.D.I. ARCHIVE EDITION v1.0.4", 15, DIM),
                        T("BUILD 667.01.13", 15, BLUE_BRT)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        fl_col.move_to([-6.65 + fl_col.width / 2, fy - 0.07, 0])
        fc_col = VGroup(T("(C) 2001-2026  BLACKSITE RESEARCH DIVISION", 14, DIM),
                        T("ALL RIGHTS RESERVED", 13, DIMMER)).arrange(DOWN, buff=0.1).move_to([0, fy - 0.07, 0])
        status_field = VGroup(T("STATUS: ", 15, DIM), T("BOOTING", 15, BLUE_BRT)).arrange(RIGHT, buff=0.12)
        fr_col = VGroup(T("ARTIFICIAL DIVINITY SUBSYSTEM", 15, DIM), status_field).arrange(DOWN, aligned_edge=RIGHT, buff=0.1)
        fr_col.move_to([6.65 - fr_col.width / 2, fy - 0.07, 0])

        def light_sweep(target, run_time=0.55, color=WHITE, op=0.55):
            cy = target.get_center()[1]
            x0, x1 = target.get_left()[0] - 0.3, target.get_right()[0] + 0.3
            h = target.height + 0.25
            bar = Rectangle(width=0.16, height=h, stroke_width=0, fill_color=color,
                            fill_opacity=0.0).move_to([x0, cy, 0]).set_z_index(8)
            self.add(bar)

            def u(m, a):
                m.move_to([x0 + (x1 - x0) * a, cy, 0]).set_fill(color, op * np.sin(a * np.pi))
            self.play(UpdateFromAlphaFunc(bar, u), run_time=run_time, rate_func=linear)
            self.remove(bar)

        # =================================================================
        # SEQUENCE  (~6s, choreographed)
        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-22)
        self.add_sound(snd("ambient.wav"), gain=-21)  # soft terminal-room ambience
        self.add(scan, scanline)

        # 1) title resolves in, light sweep across it (glow added in post)
        self.play(FadeIn(title, scale=1.06, shift=DOWN * 0.06),
                  run_time=0.6, rate_func=smooth)
        light_sweep(title)

        # 2) flourishes draw out, subtitle in
        self.add_sound(snd("es_system_beep.wav"), gain=-15)
        self.play(Create(fl_l), Create(fl_r), FadeIn(subtitle, scale=1.04), run_time=0.45, rate_func=smooth)

        # 3) bar + footer assemble
        self.play(FadeIn(container, scale=1.02), FadeIn(cont_glow),
                  LaggedStart(FadeIn(fl_col, shift=UP * 0.08), FadeIn(fc_col, shift=UP * 0.08),
                              FadeIn(fr_col, shift=UP * 0.08), lag_ratio=0.25),
                  run_time=0.55, rate_func=smooth)
        for r in rows:
            self.add(r["mk"], r["mglow"], r["txt"])
        self.add(blocks, shine, lead)
        self.add_sound(snd("es_loading_slow.wav"), gain=-6)
        self.wait(0.3)

        # 4) status lines activate one by one with a pop + flare
        def activate(i, target, prev=None):
            self.add_sound(snd("es_system_beep.wav"), gain=-11)
            r = rows[i]
            anims = [r["txt"].animate.set_color(BLUE_BRT),
                     r["mk"].animate.set_fill(BLUE, 1.0).set_stroke(BLUE, 1.8),
                     prog.animate.set_value(target)]
            if prev is not None:
                pr = rows[prev]
                anims += [pr["txt"].animate.set_color(DIM),
                          pr["mglow"].animate.set_stroke(BLUE, 5, 0.0),
                          pr["mk"].animate.set_fill(BLUE, 0.5)]
            self.play(*anims, run_time=0.8, rate_func=smooth)
            # circle pop / flare
            r["mglow"].set_stroke(BLUE, 7, 0.0)
            self.play(r["mglow"].animate.set_stroke(BLUE, 7, 0.65).scale(1.7),
                      run_time=0.28, rate_func=there_and_back)
            r["mglow"].set_stroke(BLUE, 5, 0.45)

        activate(0, 0.34)
        activate(1, 0.69, prev=0)
        activate(2, 1.0, prev=1)
        self.play(rows[2]["mglow"].animate.set_stroke(BLUE, 5, 0.0),
                  rows[2]["mk"].animate.set_fill(BLUE, 0.5),
                  rows[2]["txt"].animate.set_color(DIM), run_time=0.25)

        # 5) bar complete: a bright sweep across it
        light_sweep(container, run_time=0.4, color=BLUE_BRT, op=0.6)

        # 6) ACCESS GRANTED burst + STATUS -> READY
        self.add_sound(snd("es_select_ok.wav"), gain=-6)
        new_status = VGroup(T("STATUS: ", 15, DIM), T("READY", 15, GREEN_BRT)).arrange(RIGHT, buff=0.12)
        new_status.move_to(status_field.get_right(), aligned_edge=RIGHT)
        ag = Text("ACCESS GRANTED", font=TITLE_FONT, font_size=24, color=GREEN_BRT
                  ).move_to([0, -2.3, 0])
        agglow = VGroup(*[ag.copy().set_fill(opacity=0).set_stroke(GREEN, width=w, opacity=o)
                          for w, o in [(18, 0.0), (9, 0.0)]]).set_z_index(-1)
        self.add(agglow)
        self.play(FadeIn(ag, scale=1.18),
                  agglow.animate.set_stroke(GREEN, 14, 0.20),
                  Transform(status_field, new_status), run_time=0.45, rate_func=rush_from)
        light_sweep(ag, run_time=0.4, color=GREEN_BRT, op=0.5)
        self.wait(0.5)

        # 7) clean cut to black
        self.add_sound(snd("es_system_beep.wav"), gain=-9)
        black = Rectangle(width=15, height=8.6, stroke_width=0, fill_color="#000000",
                          fill_opacity=0.0).set_z_index(60)
        self.add(black)
        self.play(black.animate.set_fill("#000000", 1.0), run_time=0.32, rate_func=smooth)
        self.wait(0.2)
