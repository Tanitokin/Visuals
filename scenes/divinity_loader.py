"""divinity_loader.py - ARCHIVE ACCESS PROTOCOL loading screen.

A short (~5s) corporate / black-budget archive boot that plays BEFORE the
ARTIFICIAL DIVINITY INDEX selector. Dark navy, pale green-white text, a cool
green-cyan glow; a centred system title with a small classified-division
emblem to its left, a subtitle, one loading bar, three status lines that
appear one by one, and a small corporate footer. Ends on ACCESS GRANTED and a
clean flash to black (cuts straight into the selector).

Font: TheSansMonoSCd.  CRT overlays + SFX reused from assets/.

Render:
    ./.venv/bin/manim -qh --fps 30 scenes/divinity_loader.py DivinityLoader
"""

import os
import sys

import numpy as np
from manim import *
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crt_style import snd

# --- Corporate palette (cool, controlled) ---------------------------------
NAVY   = "#060A12"   # very dark navy-black
TXT    = "#E8F4EE"   # pale green-white
ACCENT = "#54DCB4"   # cool green-cyan
DIM    = "#5C8579"   # muted gray-green
DIMMER = "#33514A"

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


def emblem():
    """A simple, elegant classified-division mark: hexagon + inscribed
    triangle + centre dot.  Geometric and corporate, not occult."""
    hexa = RegularPolygon(6, start_angle=PI / 2, radius=0.36).set_stroke(ACCENT, 2.6)
    inner = RegularPolygon(6, start_angle=PI / 2, radius=0.215).set_stroke(ACCENT, 1.3, opacity=0.55)
    tri = Triangle().scale(0.135).set_stroke(TXT, 1.8).set_fill(opacity=0).shift(UP * 0.02)
    dot = Dot(radius=0.028, color=TXT)
    halo = hexa.copy().set_stroke(ACCENT, 7, 0.14)
    return VGroup(halo, hexa, inner, tri, dot)


class DivinityLoader(Scene):
    def construct(self):
        self.camera.background_color = NAVY
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def T(s, size, color=TXT, weight=NORMAL):
            return Text(s, font=FONT, font_size=size, color=color, weight=weight)

        # --- soft centre glow (clean glow, very subtle) ------------------
        bloom = Ellipse(width=9, height=5, stroke_width=0, fill_color=ACCENT,
                        fill_opacity=0.05).move_to([0, 0.4, 0]).set_z_index(-5)

        # --- title + emblem (emblem to the LEFT of a centred title) ------
        title = T("ARTIFICIAL DIVINITY INDEX", 40, TXT).scale_to_fit_width(7.4).move_to([0, 1.5, 0])
        tg = title.copy().set_color(ACCENT).set_opacity(0.0)
        tg.add_updater(lambda m: m.set_opacity(0.10 + 0.06 * (0.5 + 0.5 * np.sin(clock.get_value() * 2.2))))
        em = emblem().scale_to_fit_height(0.72).move_to([title.get_left()[0] - 0.62, 1.5, 0])
        subtitle = T("ARCHIVE ACCESS PROTOCOL", 21, DIM).move_to([0, 0.92, 0])
        # letter-spacing-ish divider under subtitle
        sdiv = Line([-2.4, 0.66, 0], [2.4, 0.66, 0], color=DIMMER, stroke_width=1)

        # --- loading bar -------------------------------------------------
        bar_w, bar_y = 6.2, 0.12
        track = RoundedRectangle(width=bar_w + 0.08, height=0.17, corner_radius=0.05,
                                 stroke_color=DIM, stroke_width=1.3, fill_opacity=0).move_to([0, bar_y, 0])
        prog = ValueTracker(0.0)

        def make_fill():
            w = max(0.0008, bar_w * prog.get_value())
            cx = -bar_w / 2 + w / 2
            fill = Rectangle(width=w, height=0.12, stroke_width=0, fill_color=ACCENT,
                             fill_opacity=1).move_to([cx, bar_y, 0])
            glow = Rectangle(width=w, height=0.12, stroke_width=0, fill_opacity=0
                             ).move_to([cx, bar_y, 0]).set_stroke(ACCENT, 7, 0.22)
            return VGroup(glow, fill)
        fill = always_redraw(make_fill)
        pct = always_redraw(lambda: T(f"{int(round(prog.get_value()*100)):02d}%", 16, DIM)
                            .move_to([bar_w / 2 + 0.5, bar_y, 0]))

        # --- three status lines (built hidden, revealed one by one) ------
        STATUS = ["Initializing subject registry",
                  "Mounting restricted dossiers",
                  "Verifying divinity index"]
        line_y = [-0.62, -0.99, -1.36]
        lines = []
        for i, s in enumerate(STATUS):
            mark = T(">", 18, ACCENT)
            txt = T(s, 19, TXT)
            ok = T("OK", 16, ACCENT)
            row = VGroup(mark, txt).arrange(RIGHT, buff=0.22)
            row.move_to([0, line_y[i], 0]).align_to([-2.85, 0, 0], LEFT)
            ok.move_to([2.95, line_y[i], 0]).set_opacity(0.0)
            grp = VGroup(row, ok).set_opacity(1.0)
            grp.set_opacity(0.0)
            lines.append({"grp": grp, "row": row, "mark": mark, "txt": txt, "ok": ok})

        # --- ACCESS GRANTED (hidden until the end) -----------------------
        ag = T("ACCESS GRANTED", 30, ACCENT).move_to([0, -0.99, 0]).set_opacity(0.0)
        ag_glow = ag.copy().set_stroke(ACCENT, 6, 0.0).set_opacity(0.0)

        # --- corporate footer --------------------------------------------
        f1 = T("A.D.I. ARCHIVE BUILD v1.0.4", 15, DIM)
        f2 = T("BLACKSITE RESEARCH DIVISION", 14, DIMMER)
        f3 = T("INTERNAL USE ONLY", 13, DIMMER)
        footer = VGroup(f1, f2, f3).arrange(DOWN, buff=0.12).move_to([0, -3.18, 0])

        # --- CRT overlays (subtle) ---------------------------------------
        scan = gf("07_Effects/crt_scanlines.png").scale_to_fit_height(8.0).set_z_index(30).set_opacity(0.12)
        vign = gf("07_Effects/vignette_overlay.png", 768).scale_to_fit_height(8.0).set_z_index(29).set_opacity(0.62)
        noise1 = gf("07_Effects/noise_overlay_01.png", 512).scale_to_fit_height(8.0).set_z_index(31)
        noise2 = gf("07_Effects/noise_overlay_02.png", 512).scale_to_fit_height(8.0).set_z_index(31)

        def noise_upd(m):
            on = int(clock.get_value() * 10) % 2
            noise1.set_opacity(0.022 if on == 0 else 0.0)
            noise2.set_opacity(0.022 if on == 1 else 0.0)
        noise1.add_updater(noise_upd)

        flick = Rectangle(width=15, height=8.6, stroke_width=0, fill_color=NAVY, fill_opacity=0.0).set_z_index(33)
        flick.add_updater(lambda m: m.set_opacity(0.012 + 0.018 * (0.5 + 0.5 * np.sin(clock.get_value() * 5.5))))

        # =================================================================
        # SEQUENCE  (~5s)
        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-17)
        self.add_sound(snd("boot.wav"), gain=-9)
        self.add(bloom, scan, vign, noise1, noise2, flick)

        # the screen fades in already assembled
        static = VGroup(em, title, subtitle, sdiv, track, pct, footer)
        self.add(tg)
        self.play(FadeIn(static), run_time=0.6, rate_func=smooth)
        for ln in lines:
            self.add(ln["grp"])
        self.add(fill)

        # short settle, then bar fills while the 3 lines appear one by one
        self.add_sound(snd("riser.wav"), gain=-15)
        self.wait(0.35)

        def reveal(i, target, prev=None):
            self.add_sound(snd("ui_tick.wav"), gain=-12)
            anims = [lines[i]["row"].animate.set_opacity(1.0),
                     prog.animate.set_value(target)]
            if prev is not None:
                anims.append(lines[prev]["row"].animate.set_opacity(0.42))
                anims.append(lines[prev]["ok"].animate.set_opacity(0.9))
            self.play(*anims, run_time=0.85, rate_func=smooth)

        reveal(0, 0.36)
        self.wait(0.15)
        reveal(1, 0.70, prev=0)
        self.wait(0.15)
        reveal(2, 1.0, prev=1)
        # last line completes
        self.play(lines[2]["row"].animate.set_opacity(0.42),
                  lines[2]["ok"].animate.set_opacity(0.9), run_time=0.3)

        # ACCESS GRANTED
        self.add_sound(snd("access.wav"), gain=-5)
        self.add(ag_glow)
        ag.move_to([0, -2.05, 0]); ag_glow.move_to([0, -2.05, 0])
        self.play(FadeIn(ag, scale=1.12),
                  ag_glow.animate.set_stroke(ACCENT, 6, 0.22).set_opacity(1.0),
                  run_time=0.4, rate_func=rush_from)
        self.wait(0.45)

        # clean flash -> fade to black (cuts into the selector)
        self.add_sound(snd("transition.wav"), gain=-8)
        flash = Rectangle(width=15, height=8.6, stroke_width=0, fill_color=TXT, fill_opacity=0.0).set_z_index(40)
        self.add(flash)
        self.play(flash.animate.set_fill(TXT, 0.5), run_time=0.08, rate_func=linear)
        black = Rectangle(width=15, height=8.6, stroke_width=0, fill_color="#000000", fill_opacity=0.0).set_z_index(41)
        self.add(black)
        self.play(flash.animate.set_fill(TXT, 0.0), black.animate.set_fill("#000000", 1.0),
                  run_time=0.32, rate_func=smooth)
        self.wait(0.25)
