"""Worst Fictional Cities to Live In - cinematic loading screen.

A clean amber CRT archive terminal streams through 13 fictional cities, one at a
time. Each city gets a near-fullscreen card: a large cover image (loaded from
assets/covers/) on the left, and its dossier on the right - index, name, source,
threat level, a hazard meter and a one-line descriptor. Smooth crossfades, a
loading bar and segmented progress ticks tie it together, ending on PRESS START.

Cover images: drop one file per city in assets/covers/ named with the number
prefix (e.g. 01_gotham_city.png). Missing files fall back to a clean placeholder.

Render:
    manim -pqh worst_cities.py WorstCities
"""

import glob
import os
import textwrap

import numpy as np
from manim import *

# --- Palette --------------------------------------------------------------
BG          = "#0E0A08"
AMBER       = "#EAA13B"
AMBER_BRT   = "#FFC872"
AMBER_DIM   = "#6E5326"
RED         = "#FF5141"
BORDER      = "#7A4B1E"
PANEL_FILL  = "#140D08"
COVER_FILL  = "#0A0605"

MONO = "DejaVu Sans Mono"

COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "assets", "covers")

# name, source, rating, hazard(/6), descriptor
CITIES = [
    ("GOTHAM CITY",   "BATMAN",            "EXTREME",      5,
     "Crime never sleeps. Neither should you."),
    ("MIDGAR",        "FINAL FANTASY VII", "SEVERE",       4,
     "Mako-poisoned skies over a corporate dystopia."),
    ("LOS ANGELES",   "BLADE RUNNER",      "HIGH",         3,
     "Acid rain, replicants, and permanent night."),
    ("RAPTURE",       "BIOSHOCK",          "EXTREME",      5,
     "A drowned utopia run by spliced madmen."),
    ("CITY 17",       "HALF-LIFE 2",       "SEVERE",       4,
     "Combine occupation. Citizenship is mandatory."),
    ("MEGA-CITY ONE", "JUDGE DREDD",       "APOCALYPTIC",  6,
     "800 million souls. One judge per block."),
    ("ZAUN",          "ARCANE / LOL",      "HIGH",         3,
     "The toxic underbelly of a shining city."),
    ("YHARNAM",       "BLOODBORNE",        "EXTREME",      5,
     "A plague of beasts and very bad blood."),
    ("THE CITY",      "BLAME!",            "UNMEASURABLE", 6,
     "Infinite architecture. There is no exit."),
    ("SILENT HILL",   "SILENT HILL",       "ABSOLUTE",     6,
     "The town remembers what you did."),
    ("NEW CROBUZON",  "BAS-LAG",           "SEVERE",       4,
     "An industrial nightmare of flesh and steam."),
    ("COMMORRAGH",    "WARHAMMER 40K",     "APOCALYPTIC",  6,
     "The dark city feeds on living suffering."),
    ("DIS",           "DANTE'S INFERNO",   "INFERNAL",     6,
     "The iron city at the heart of Hell."),
]

HIGH_TIER = {"EXTREME", "APOCALYPTIC", "UNMEASURABLE", "ABSOLUTE", "INFERNAL"}


def rcolor(rating):
    if rating in HIGH_TIER:
        return RED
    if rating == "SEVERE":
        return AMBER_BRT
    return AMBER_DIM


class WorstCities(Scene):
    def construct(self):
        self.camera.background_color = BG

        def T(s, size, color=AMBER, weight=NORMAL, t2c=None):
            return Text(s, font=MONO, font_size=size, color=color,
                        weight=weight, t2c=t2c or {})

        def left(mob, x, y):
            mob.move_to([x, y, 0]).align_to([x, y, 0], LEFT)
            return mob

        def right(mob, x, y):
            mob.move_to([x, y, 0]).align_to([x, y, 0], RIGHT)
            return mob

        N = len(CITIES)

        # ---- geometry --------------------------------------------------
        COVER_C = np.array([-3.55, -0.10, 0])
        BOX_W, BOX_H = 5.25, 4.25
        TX = -0.55                      # left edge of the text column

        # =================================================================
        # PERSISTENT CHROME
        # =================================================================
        frame = Rectangle(width=13.9, height=7.55, stroke_color=BORDER,
                          stroke_width=1.5, fill_opacity=0)

        hl = left(T("WORST CITIES // UNINHABITABLE ARCHIVE", 15, AMBER), -6.55, 3.5)
        hr = right(T("NODE 07 // STREAMING", 15, AMBER_DIM), 6.55, 3.5)
        head_div = Line([-6.6, 3.28, 0], [6.6, 3.28, 0], color=BORDER, stroke_width=1)

        # cover frame chrome (image swaps inside; this stays put)
        cover_bg = Rectangle(width=BOX_W, height=BOX_H, stroke_width=0,
                             fill_color=COVER_FILL, fill_opacity=1).move_to(COVER_C)
        cover_scan = VGroup(*[
            Line([COVER_C[0] - BOX_W / 2, y, 0], [COVER_C[0] + BOX_W / 2, y, 0],
                 color=BG, stroke_width=2, stroke_opacity=0.16)
            for y in np.arange(COVER_C[1] - BOX_H / 2, COVER_C[1] + BOX_H / 2, 0.11)
        ]).set_z_index(3)
        cover_frame = Rectangle(width=BOX_W, height=BOX_H, stroke_color=AMBER,
                                stroke_width=2, fill_opacity=0).move_to(COVER_C).set_z_index(4)
        cov_l = left(T("COVER IMAGE", 12, AMBER_DIM), COVER_C[0] - BOX_W / 2 + 0.12,
                     COVER_C[1] + BOX_H / 2 - 0.22).set_z_index(5)

        # footer
        foot_div = Line([-6.6, -2.55, 0], [6.6, -2.55, 0], color=BORDER, stroke_width=1)
        load_lbl = left(T("STREAMING ARCHIVE", 13, AMBER_DIM), -6.55, -2.92)

        prog = ValueTracker(0.0)
        bar_l, bar_w, bar_y = -3.55, 8.55, -2.92
        bar_bg = Rectangle(width=bar_w, height=0.15, stroke_color=AMBER_DIM,
                           stroke_width=1, fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])
        bar_fill = always_redraw(lambda: Rectangle(
            width=max(0.001, bar_w * prog.get_value()), height=0.15, stroke_width=0,
            fill_color=AMBER, fill_opacity=1
        ).move_to([bar_l + bar_w * prog.get_value() / 2, bar_y, 0]))
        pct = always_redraw(lambda: right(
            T(f"{int(round(prog.get_value()*100)):3d}%", 13, AMBER_BRT), 6.55, bar_y))

        # segmented progress ticks
        cur = ValueTracker(-1)
        tick_x0, tick_dx, tick_y = -6.55, 13.1 / (N - 1), -3.32

        def cur_i():
            return int(round(cur.get_value()))

        ticks = always_redraw(lambda: VGroup(*[
            Rectangle(width=0.74, height=0.07, stroke_width=0, fill_opacity=1,
                      fill_color=(AMBER_BRT if k == cur_i()
                                  else AMBER if k < cur_i() else AMBER_DIM)
                      ).move_to([tick_x0 + k * tick_dx, tick_y, 0])
            for k in range(N)]))

        hint = T("ESC ABORT      ENTER OPEN FILE      ◄ ► CYCLE",
                 11, AMBER_DIM).move_to([0, -3.62, 0])

        chrome = Group(frame, hl, hr, head_div, cover_bg, cover_scan, cover_frame,
                       cov_l, foot_div, load_lbl, bar_bg, bar_fill, pct, ticks, hint)

        # =================================================================
        # PER-CITY BUILDERS
        # =================================================================
        def build_cover(i):
            files = sorted(glob.glob(os.path.join(COVER_DIR, f"{i+1:02d}_*")))
            files = [f for f in files if not f.lower().endswith((".md", ".txt"))]
            if files:
                img = ImageMobject(files[0]).set_z_index(1)
                img.scale_to_fit_height(BOX_H - 0.16)
                if img.width > BOX_W - 0.16:
                    img.scale_to_fit_width(BOX_W - 0.16)
                img.move_to(COVER_C)
                return img
            # clean placeholder
            name = CITIES[i][0]
            ph_name = VGroup(*[T(ln, 22, AMBER, weight=BOLD)
                               for ln in textwrap.wrap(name, 12)]).arrange(DOWN, buff=0.12)
            ph_tag = T("COVER PENDING", 13, AMBER_DIM)
            ph = VGroup(ph_name, ph_tag).arrange(DOWN, buff=0.45).move_to(COVER_C)
            ph.set_z_index(1)
            return ph

        def build_text(i):
            name, source, rating, hazard, desc = CITIES[i]

            idx = T(f"{i+1:02d}", 58, AMBER_BRT, weight=BOLD)
            left(idx, TX, 1.55)
            idx_tot = left(T(f"/ {N:02d}", 18, AMBER_DIM), TX + idx.width + 0.2, 1.42)

            name_m = T(name, 36, AMBER_BRT, weight=BOLD)
            if name_m.width > 6.9:
                name_m.scale_to_fit_width(6.9)
            left(name_m, TX, 0.62)

            source_m = left(T("SOURCE", 16, AMBER_DIM), TX, 0.06)
            source_v = left(T(source, 16, AMBER), TX + 1.55, 0.06)

            div = Line([TX, -0.28, 0], [6.4, -0.28, 0], color=BORDER, stroke_width=1)

            thr_l = left(T("THREAT LEVEL", 14, AMBER_DIM), TX, -0.66)
            pill_t = T(rating, 15, rcolor(rating), weight=BOLD)
            pill = SurroundingRectangle(pill_t, color=rcolor(rating), buff=0.13,
                                        corner_radius=0.06, stroke_width=1.6)
            pill_g = VGroup(pill, pill_t)
            left(pill_g, TX + 2.55, -0.66)

            # hazard meter (6 blocks)
            blocks = VGroup()
            for k in range(6):
                filled = k < hazard
                blocks.add(Rectangle(
                    width=0.46, height=0.20, stroke_width=1.2,
                    stroke_color=rcolor(rating) if filled else AMBER_DIM,
                    fill_color=rcolor(rating) if filled else BG,
                    fill_opacity=1 if filled else 0))
            blocks.arrange(RIGHT, buff=0.12)
            haz_l = left(T("HAZARD", 14, AMBER_DIM), TX, -1.2)
            left(blocks, TX + 1.7, -1.2)

            desc_lines = textwrap.wrap(desc, 38)
            desc_m = VGroup(*[T(ln, 15, AMBER) for ln in desc_lines])
            desc_m.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            left(desc_m, TX, -1.78)

            return VGroup(idx, idx_tot, name_m, source_m, source_v, div,
                          thr_l, pill_g, haz_l, blocks, desc_m)

        # =================================================================
        # SEQUENCE
        # =================================================================
        # --- Intro ---
        self.play(Create(frame), run_time=0.6)
        self.play(LaggedStart(FadeIn(hl), FadeIn(hr), lag_ratio=0.2),
                  Create(head_div), run_time=0.7)

        big = T("WORST CITIES", 56, AMBER_BRT, weight=BOLD).move_to([0, 0.45, 0])
        big_sub = T("13 LOCATIONS FLAGGED UNINHABITABLE", 18, AMBER_DIM).move_to([0, -0.45, 0])
        self.play(Write(big), run_time=0.8)
        self.play(FadeIn(big_sub, shift=UP * 0.15), run_time=0.4)
        self.wait(0.7)
        self.play(FadeOut(big, shift=UP * 0.2), FadeOut(big_sub), run_time=0.5)

        # --- Reveal chrome ---
        self.play(
            FadeIn(cover_bg), FadeIn(cover_frame), FadeIn(cov_l),
            Create(foot_div), FadeIn(load_lbl),
            FadeIn(bar_bg), run_time=0.6,
        )
        self.add(cover_scan, bar_fill, pct, ticks, hint)

        # --- City stream ---
        prev = None
        for i in range(N):
            cover = build_cover(i)
            text = build_text(i)
            card = Group(cover, text)
            if prev is None:
                self.play(
                    FadeIn(cover), FadeIn(text, shift=LEFT * 0.25),
                    prog.animate.set_value((i + 1) / N),
                    cur.animate.set_value(i),
                    run_time=0.55,
                )
            else:
                self.play(
                    FadeOut(prev, shift=LEFT * 0.2),
                    FadeIn(cover), FadeIn(text, shift=LEFT * 0.25),
                    prog.animate.set_value((i + 1) / N),
                    cur.animate.set_value(i),
                    run_time=0.45,
                )
            self.wait(0.7)
            prev = card

        self.wait(0.3)

        # --- Outro: PRESS START ---
        self.play(
            FadeOut(prev, shift=LEFT * 0.2),
            Transform(load_lbl, left(T("ARCHIVE STREAM COMPLETE", 13, AMBER), -6.55, -2.92)),
            run_time=0.5,
        )
        dim = Rectangle(width=14.6, height=8.2, stroke_width=0,
                        fill_color=BG, fill_opacity=0.0).set_z_index(10)
        self.add(dim)
        press_bg = Rectangle(width=4.9, height=1.0, stroke_color=AMBER,
                             stroke_width=2.5, fill_color=BG, fill_opacity=0.9
                             ).move_to(ORIGIN).set_z_index(11)
        press = T("PRESS START", 32, AMBER_BRT, weight=BOLD).move_to(ORIGIN).set_z_index(12)
        self.play(dim.animate.set_fill(BG, opacity=0.6), run_time=0.5)
        self.play(FadeIn(press_bg, scale=0.92), FadeIn(press, scale=0.92), run_time=0.45)
        for _ in range(3):
            self.play(press.animate.set_opacity(0.2), run_time=0.45,
                      rate_func=there_and_back)
        self.wait(0.6)
