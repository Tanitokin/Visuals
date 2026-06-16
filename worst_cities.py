"""Worst Fictional Cities to Live In - game menu + loading screen.

An amber CRT "archive terminal" boot screen: a selectable index of 13 fictional
cities. A cursor steps through them one by one; each selection opens the file -
the cover image and dossier update on the right and a per-file loading bar runs
to ACCESS GRANTED before moving on. Ends on PRESS START.

Typography: Press Start 2P (title) + VT323 (terminal body).
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

FONT_TITLE = "Press Start 2P"
FONT_BODY  = "VT323"

COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "assets", "covers")

# name, source, rating, descriptor
CITIES = [
    ("GOTHAM CITY",   "BATMAN",            "EXTREME"),
    ("MIDGAR",        "FINAL FANTASY VII", "SEVERE"),
    ("LOS ANGELES",   "BLADE RUNNER",      "HIGH"),
    ("RAPTURE",       "BIOSHOCK",          "EXTREME"),
    ("CITY 17",       "HALF-LIFE 2",       "SEVERE"),
    ("MEGA-CITY ONE", "JUDGE DREDD",       "APOCALYPTIC"),
    ("ZAUN",          "ARCANE / LOL",      "HIGH"),
    ("YHARNAM",       "BLOODBORNE",        "EXTREME"),
    ("THE CITY",      "BLAME!",            "UNMEASURABLE"),
    ("SILENT HILL",   "SILENT HILL",       "ABSOLUTE"),
    ("NEW CROBUZON",  "BAS-LAG",           "SEVERE"),
    ("COMMORRAGH",    "WARHAMMER 40K",     "APOCALYPTIC"),
    ("DIS",           "DANTE'S INFERNO",   "INFERNAL"),
]

HIGH_TIER = {"EXTREME", "APOCALYPTIC", "UNMEASURABLE", "ABSOLUTE", "INFERNAL"}


def rcolor(rating):
    if rating in HIGH_TIER:
        return RED
    if rating == "SEVERE":
        return AMBER_BRT
    return AMBER_DIM


def slug(name):
    return name.replace(" ", "_").replace("-", "_").replace("'", "")


class WorstCities(Scene):
    def construct(self):
        self.camera.background_color = BG
        N = len(CITIES)

        def T(s, size, color=AMBER, font=FONT_BODY, t2c=None):
            return Text(s, font=font, font_size=size, color=color, t2c=t2c or {})

        def left(mob, x, y):
            mob.move_to([x, y, 0]).align_to([x, y, 0], LEFT)
            return mob

        def right(mob, x, y):
            mob.move_to([x, y, 0]).align_to([x, y, 0], RIGHT)
            return mob

        sel = ValueTracker(0)
        prog = ValueTracker(0.0)

        def cur_i():
            return int(np.clip(round(sel.get_value()), 0, N - 1))

        def cur():
            return CITIES[cur_i()]

        # =================================================================
        # FRAME + HEADER + TITLE
        # =================================================================
        frame = Rectangle(width=13.9, height=7.55, stroke_color=BORDER,
                          stroke_width=1.5, fill_opacity=0)

        hl1 = left(T("WORST CITIES INDEX", 26, AMBER), -6.5, 3.46)
        hl2 = left(T("LOCAL ACCESS TERMINAL // SECTION SELECT", 18, AMBER_DIM), -6.5, 3.18)
        hr1 = right(T("ARCHIVE NODE 07", 26, AMBER), 6.5, 3.46)
        hr2 = right(T("LOCAL NODE // ACTIVE", 18, AMBER_DIM), 6.5, 3.18)
        head_div = Line([-6.55, 2.94, 0], [6.55, 2.94, 0], color=BORDER, stroke_width=1)

        title = Text("WORST CITIES", font=FONT_TITLE, color=AMBER_BRT)
        title.scale_to_fit_width(8.6).move_to([0, 2.30, 0])
        title_glow = title.copy().set_color(AMBER).set_opacity(0.25).set_stroke(AMBER, 6, 0.18)
        subtitle = T("// FICTIONAL CITIES TO LIVE IN //", 20, AMBER_DIM).move_to([0, 1.74, 0])

        # =================================================================
        # LEFT LIST PANEL
        # =================================================================
        list_panel = Rectangle(width=6.55, height=4.05, stroke_color=BORDER,
                               stroke_width=1.5, fill_color=PANEL_FILL,
                               fill_opacity=0.5).move_to([-3.27, -0.55, 0])
        lp_h1 = left(T("CITY FILES", 24, AMBER), -6.36, 1.28)
        lp_h2 = right(T("13 FILES FOUND", 18, AMBER_DIM), 0.16, 1.28)
        lp_div = Line([-6.45, 1.05, 0], [0.2, 1.05, 0], color=BORDER, stroke_width=1)

        row_x, row_y0, row_dy = -6.05, 0.74, 0.255
        row_mobs = []
        for i, (name, source, rating) in enumerate(CITIES):
            s = f"[{i+1:02d}]  {name:<14}{rating:>13}"
            row = left(T(s, 22, AMBER, t2c={rating: rcolor(rating)}),
                       row_x, row_y0 - i * row_dy)
            row_mobs.append(row)

        highlight = always_redraw(lambda: RoundedRectangle(
            width=6.3, height=0.25, corner_radius=0.03, stroke_color=AMBER_BRT,
            stroke_width=1.4, fill_color=AMBER, fill_opacity=0.10
        ).move_to([-3.12, row_y0 - cur_i() * row_dy, 0]))
        marker = always_redraw(lambda: T(">", 22, AMBER_BRT).move_to(
            [-6.33, row_y0 - cur_i() * row_dy, 0]))

        # =================================================================
        # RIGHT COVER PANEL
        # =================================================================
        COVER_C = np.array([3.28, 0.50, 0])
        CBOX_W, CBOX_H = 6.4, 1.62
        cover_panel = Rectangle(width=CBOX_W, height=CBOX_H, stroke_color=BORDER,
                                stroke_width=1.5, fill_color=COVER_FILL,
                                fill_opacity=1).move_to(COVER_C)
        cov_l = left(T("COVER IMAGE", 17, AMBER_DIM), 0.3, 1.05).set_z_index(5)
        cover_tag = always_redraw(lambda: right(
            T(f"{cur_i()+1:02d} // {cur()[0]}", 17, AMBER), 6.26, 1.05).set_z_index(5))
        cover_scan = VGroup(*[
            Line([COVER_C[0] - CBOX_W / 2, y, 0], [COVER_C[0] + CBOX_W / 2, y, 0],
                 color=BG, stroke_width=2, stroke_opacity=0.16)
            for y in np.arange(COVER_C[1] - CBOX_H / 2, COVER_C[1] + CBOX_H / 2, 0.10)
        ]).set_z_index(3)

        def build_cover(i):
            files = sorted(glob.glob(os.path.join(COVER_DIR, f"{i+1:02d}_*")))
            files = [f for f in files if not f.lower().endswith((".md", ".txt"))]
            if files:
                img = ImageMobject(files[0]).set_z_index(1)
                img.scale_to_fit_height(CBOX_H - 0.12)
                if img.width > CBOX_W - 0.12:
                    img.scale_to_fit_width(CBOX_W - 0.12)
                return img.move_to(COVER_C)
            name = CITIES[i][0]
            ph_name = T(name, 30, AMBER)
            if ph_name.width > CBOX_W - 0.8:
                ph_name.scale_to_fit_width(CBOX_W - 0.8)
            ph_tag = T("COVER PENDING", 16, AMBER_DIM)
            ph = VGroup(ph_name, ph_tag).arrange(DOWN, buff=0.18).move_to(COVER_C)
            return ph.set_z_index(1)

        # =================================================================
        # RIGHT FILE-PREVIEW PANEL
        # =================================================================
        prev_panel = Rectangle(width=6.4, height=2.10, stroke_color=BORDER,
                               stroke_width=1.5, fill_color=PANEL_FILL,
                               fill_opacity=0.5).move_to([3.28, -1.52, 0])
        pv_h = left(T("FILE PREVIEW", 22, AMBER), 0.3, -0.66)
        file_tag = always_redraw(lambda: right(
            T(f"FILE_{cur_i()+1:02d}", 18, AMBER_DIM), 6.26, -0.66))

        f_labels = ["TITLE", "SOURCE", "NODE", "THREAT", "STATUS"]
        label_x, val_x = 0.32, 2.05
        fy0, fdy = -1.02, -0.255
        label_mobs = VGroup(*[
            left(T(lbl, 18, AMBER_DIM), label_x, fy0 + k * fdy)
            for k, lbl in enumerate(f_labels)
        ])
        status_val = left(T("ACTIVE / UNSTABLE", 18, RED), val_x, fy0 + 4 * fdy)
        req = left(T("OPEN REQUEST ACCEPTED", 17, AMBER), 0.32, -2.36)

        title_val = always_redraw(lambda: left(T(cur()[0], 18, AMBER_BRT), val_x, fy0))
        source_val = always_redraw(lambda: left(T(cur()[1], 18, AMBER), val_x, fy0 + fdy))
        node_val = always_redraw(lambda: left(
            T(f"SUBSTRUCTURE {cur_i()+1:02d}", 18, AMBER), val_x, fy0 + 2 * fdy))
        threat_val = always_redraw(lambda: left(
            T(cur()[2], 18, rcolor(cur()[2])), val_x, fy0 + 3 * fdy))

        # =================================================================
        # BOTTOM CMD STRIP (per-file loading)
        # =================================================================
        bot_div = Line([-6.55, -2.72, 0], [6.55, -2.72, 0], color=BORDER, stroke_width=1)
        cmd_prefix = left(T("CMD> ", 22, AMBER), -6.5, -2.97)
        cmd_x = -6.5 + cmd_prefix.width + 0.12

        def make_cmd():
            txt = T(f"OPEN {slug(cur()[0])}", 22, AMBER_BRT)
            blk = Rectangle(width=0.17, height=0.30, stroke_width=0,
                            fill_color=AMBER, fill_opacity=1).next_to(txt, RIGHT, buff=0.07)
            return left(VGroup(txt, blk), cmd_x, -2.97)
        cmd_dyn = always_redraw(make_cmd)

        status_dyn = always_redraw(lambda: right(
            T("ACCESS GRANTED" if prog.get_value() > 0.999 else "DECRYPTING ARCHIVE",
              18, AMBER_BRT if prog.get_value() > 0.999 else AMBER_DIM), 6.5, -2.97))

        load_dyn = always_redraw(lambda: left(
            T(f"LOADING  FILE {cur_i()+1:02d}/{N:02d}", 17, AMBER_DIM), -6.5, -3.24))

        bar_l, bar_w, bar_y = -2.55, 6.95, -3.24
        bar_bg = Rectangle(width=bar_w, height=0.15, stroke_color=AMBER_DIM,
                           stroke_width=1, fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])
        bar_fill = always_redraw(lambda: Rectangle(
            width=max(0.001, bar_w * prog.get_value()), height=0.15, stroke_width=0,
            fill_color=AMBER, fill_opacity=1
        ).move_to([bar_l + bar_w * prog.get_value() / 2, bar_y, 0]))
        pct = always_redraw(lambda: right(
            T(f"{int(round(prog.get_value()*100)):3d}%", 18, AMBER_BRT), 6.5, bar_y))

        hint = T("UP/DOWN NAVIGATE      ENTER OPEN FILE      ESC CANCEL",
                 16, AMBER_DIM).move_to([0, -3.52, 0])

        # =================================================================
        # SEQUENCE
        # =================================================================
        # --- Boot ---
        self.play(Create(frame), run_time=0.6)
        self.play(LaggedStart(FadeIn(hl1), FadeIn(hl2), FadeIn(hr1), FadeIn(hr2),
                              lag_ratio=0.15), Create(head_div), run_time=0.8)
        self.add(title_glow)
        self.play(FadeIn(title, scale=1.06), run_time=0.6)
        self.play(FadeIn(subtitle), run_time=0.3)
        self.play(title.animate.set_opacity(0.45), run_time=0.06)
        self.play(title.animate.set_opacity(1.0), run_time=0.06)

        # --- Panels ---
        self.play(Create(list_panel), Create(cover_panel), Create(prev_panel),
                  run_time=0.7)
        self.play(
            FadeIn(lp_h1), FadeIn(lp_h2), Create(lp_div),
            FadeIn(cov_l), FadeIn(pv_h), FadeIn(label_mobs),
            FadeIn(status_val), FadeIn(req), Create(bot_div),
            FadeIn(cmd_prefix), FadeIn(bar_bg), FadeIn(hint),
            run_time=0.6,
        )
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in row_mobs],
                              lag_ratio=0.08), run_time=1.6)

        # add all dynamic / live mobjects
        self.add(highlight, marker, cover_scan, cover_tag, file_tag,
                 title_val, source_val, node_val, threat_val,
                 cmd_dyn, status_dyn, load_dyn, bar_fill, pct)

        # --- Step through every file with a per-file load ---
        prev_cover = build_cover(0)
        self.play(FadeIn(prev_cover), run_time=0.4)
        self.play(prog.animate.set_value(1.0), run_time=0.6)
        self.wait(0.25)

        for i in range(1, N):
            sel.set_value(i)
            prog.set_value(0.0)
            new_cover = build_cover(i)
            self.play(FadeOut(prev_cover), FadeIn(new_cover), run_time=0.3)
            self.play(prog.animate.set_value(1.0), run_time=0.55)
            self.wait(0.22)
            prev_cover = new_cover

        self.wait(0.3)

        # --- PRESS START ---
        dim = Rectangle(width=14.6, height=8.2, stroke_width=0,
                        fill_color=BG, fill_opacity=0.0).set_z_index(10)
        self.add(dim)
        press_bg = Rectangle(width=6.6, height=1.15, stroke_color=AMBER,
                             stroke_width=2.5, fill_color=BG, fill_opacity=0.92
                             ).move_to(ORIGIN).set_z_index(11)
        press = Text("PRESS START", font=FONT_TITLE, color=AMBER_BRT)
        press.scale_to_fit_width(5.4).move_to(ORIGIN).set_z_index(12)
        self.play(dim.animate.set_fill(BG, opacity=0.62), run_time=0.5)
        self.play(FadeIn(press_bg, scale=0.92), FadeIn(press, scale=0.92), run_time=0.45)
        for _ in range(3):
            self.play(press.animate.set_opacity(0.2), run_time=0.45,
                      rate_func=there_and_back)
        self.wait(0.6)
