"""Worst Fictional Cities to Live In - ranked countdown menu + loading screen.

Neon-green CRT "archive terminal" boot screen: a ranked index of the 13 worst
fictional cities (#13 at the top down to #01 at the bottom). A cursor steps
through them one by one from #13 to #01; each selection opens the file with a
short CRT flicker that masks the cover swap, the dossier updates, and a per-file
loading bar runs to ACCESS GRANTED. The countdown ends on #01 THE MEGASTRUCTURE,
then PRESS START.

Typography: Press Start 2P (title) + VT323 (terminal body). Neon glow on the
hero elements. Cover images: drop one file per city in assets/covers/ named with
the RANK prefix (e.g. 01_the_megastructure.png is #1). Missing files fall back to
a clean placeholder.

Render:
    manim -pqh --fps 30 worst_cities.py WorstCities
"""

import glob
import os

import numpy as np
from manim import *

# --- Neon-green palette ---------------------------------------------------
BG          = "#04110B"   # green-black
GREEN       = "#3DFF7A"   # neon phosphor green
GREEN_BRT   = "#CFFFDD"   # bright
GREEN_DIM   = "#1F8A45"   # dim
RED         = "#FF4D4D"   # alarm red (high threats)
BORDER      = "#1F8A45"
PANEL_FILL  = "#08180F"
COVER_FILL  = "#040D08"

FONT_TITLE = "Press Start 2P"
FONT_BODY  = "VT323"

COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "assets", "covers")

# Display order = ranked countdown: top of list is #13, bottom is #01.
CITIES = [
    ("LOS SUEÑOS",        "READY OR NOT",       "HIGH"),          # 13
    ("NIGHT CITY",        "CYBERPUNK 2077",     "SEVERE"),        # 12
    ("RAPTURE",           "BIOSHOCK",           "EXTREME"),       # 11
    ("CITY 17",           "HALF-LIFE 2",        "EXTREME"),       # 10
    ("HANUDA VILLAGE",    "FORBIDDEN SIREN",    "LETHAL"),        # 09
    ("THE CITY",          "PROJECT MOON",       "APOCALYPTIC"),   # 08
    ("YHARNAM",           "BLOODBORNE",         "APOCALYPTIC"),   # 07
    ("NEW CROBUZON",      "BAS-LAG",            "NIGHTMARE"),     # 06
    ("SILENT HILL",       "SILENT HILL",        "PSYCHIC"),       # 05
    ("CARCOSA",           "THE KING IN YELLOW", "COGNITOHAZARD"), # 04
    ("MA'HABRE",          "FEAR & HUNGER",      "ABYSSAL"),       # 03
    ("COMMORRAGH",        "WARHAMMER 40K",      "ABSOLUTE"),      # 02
    ("THE MEGASTRUCTURE", "BLAME!",             "UNMEASURABLE"),  # 01
]

HIGH_TIER = {"EXTREME", "LETHAL", "APOCALYPTIC", "NIGHTMARE", "PSYCHIC",
             "COGNITOHAZARD", "ABYSSAL", "ABSOLUTE", "UNMEASURABLE"}


def rcolor(rating):
    if rating in HIGH_TIER:
        return RED
    if rating == "SEVERE":
        return GREEN_BRT
    return GREEN_DIM


def slug(name):
    out = name.upper()
    for a, b in [(" ", "_"), ("-", "_"), ("'", ""), ("Ñ", "N"), ("!", ""),
                 ("&", "AND")]:
        out = out.replace(a, b)
    return out


def neon(mob, color, widths=(9, 5, 2.5), ops=(0.05, 0.09, 0.16)):
    """Wrap a mobject in soft stroke halos for a neon glow."""
    g = VGroup()
    for w, o in zip(widths, ops):
        h = mob.copy().set_stroke(color, width=w, opacity=o)
        h.set_fill(opacity=0)
        g.add(h)
    g.add(mob)
    return g


class WorstCities(Scene):
    def construct(self):
        self.camera.background_color = BG
        N = len(CITIES)

        def T(s, size, color=GREEN, font=FONT_BODY, t2c=None):
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

        def rank(i):
            return N - i

        def cur_rank():
            return rank(cur_i())

        # =================================================================
        # FRAME + HEADER + TITLE
        # =================================================================
        frame = Rectangle(width=13.9, height=7.55, stroke_color=BORDER,
                          stroke_width=1.5, fill_opacity=0)
        frame_glow = frame.copy().set_stroke(GREEN, 5, 0.10)

        hl1 = left(T("WORST CITIES INDEX", 26, GREEN), -6.5, 3.46)
        hl2 = left(T("LOCAL ACCESS TERMINAL // RANKED COUNTDOWN", 18, GREEN_DIM), -6.5, 3.18)
        hr1 = right(T("ARCHIVE NODE 07", 26, GREEN), 6.5, 3.46)
        hr2 = right(T("LOCAL NODE // ACTIVE", 18, GREEN_DIM), 6.5, 3.18)
        head_div = Line([-6.55, 2.94, 0], [6.55, 2.94, 0], color=BORDER, stroke_width=1)

        title = Text("WORST CITIES", font=FONT_TITLE, color=GREEN_BRT)
        title.scale_to_fit_width(7.8).move_to([0, 2.32, 0])
        title_neon = neon(title, GREEN, widths=(16, 9, 4), ops=(0.05, 0.10, 0.22))
        subtitle = T("// THE 13 WORST PLACES TO LIVE // 13 TO 01 //", 20, GREEN_DIM).move_to([0, 1.74, 0])

        # =================================================================
        # LEFT LIST PANEL
        # =================================================================
        list_panel = Rectangle(width=6.55, height=4.05, stroke_color=BORDER,
                               stroke_width=1.5, fill_color=PANEL_FILL,
                               fill_opacity=0.5).move_to([-3.27, -0.55, 0])
        lp_h1 = left(T("CITY FILES", 24, GREEN), -6.36, 1.28)
        lp_h2 = right(T("13 FILES FOUND", 18, GREEN_DIM), 0.16, 1.28)
        lp_div = Line([-6.45, 1.05, 0], [0.2, 1.05, 0], color=BORDER, stroke_width=1)

        row_x, rate_x, row_y0, row_dy = -6.05, -0.35, 0.74, 0.255
        row_mobs = []
        for i, (name, source, rating) in enumerate(CITIES):
            lbl = left(T(f"[{rank(i):02d}]  {name}", 20, GREEN), row_x, row_y0 - i * row_dy)
            rt = right(T(rating, 20, rcolor(rating)), rate_x, row_y0 - i * row_dy)
            row_mobs.append(VGroup(lbl, rt))

        def make_highlight():
            box = RoundedRectangle(width=6.3, height=0.25, corner_radius=0.03,
                                   stroke_color=GREEN_BRT, stroke_width=1.6,
                                   fill_color=GREEN, fill_opacity=0.12)
            box.move_to([-3.12, row_y0 - cur_i() * row_dy, 0])
            return neon(box, GREEN, widths=(7, 3), ops=(0.10, 0.22))
        highlight = always_redraw(make_highlight)
        marker = always_redraw(lambda: T(">", 22, GREEN_BRT).move_to(
            [-6.33, row_y0 - cur_i() * row_dy, 0]))

        # =================================================================
        # RIGHT COVER PANEL
        # =================================================================
        COVER_C = np.array([3.28, 0.50, 0])
        CBOX_W, CBOX_H = 6.4, 1.62
        cover_panel = Rectangle(width=CBOX_W, height=CBOX_H, stroke_color=BORDER,
                                stroke_width=1.5, fill_color=COVER_FILL,
                                fill_opacity=1).move_to(COVER_C)
        cov_l = left(T("COVER IMAGE", 17, GREEN_DIM), 0.3, 1.05).set_z_index(5)
        cover_tag = always_redraw(lambda: right(
            T(f"{cur_rank():02d} // {cur()[0]}", 17, GREEN), 6.26, 1.05).set_z_index(5))

        def build_cover(i):
            files = sorted(glob.glob(os.path.join(COVER_DIR, f"{rank(i):02d}_*")))
            files = [f for f in files if not f.lower().endswith((".md", ".txt"))]
            if files:
                img = ImageMobject(files[0]).set_z_index(1)
                img.scale_to_fit_height(CBOX_H - 0.12)
                if img.width > CBOX_W - 0.12:
                    img.scale_to_fit_width(CBOX_W - 0.12)
                return img.move_to(COVER_C)
            name = CITIES[i][0]
            ph_name = T(name, 30, GREEN)
            if ph_name.width > CBOX_W - 0.8:
                ph_name.scale_to_fit_width(CBOX_W - 0.8)
            ph_tag = T("COVER PENDING", 16, GREEN_DIM)
            ph = VGroup(ph_name, ph_tag).arrange(DOWN, buff=0.18).move_to(COVER_C)
            return ph.set_z_index(1)

        # =================================================================
        # RIGHT FILE-PREVIEW PANEL
        # =================================================================
        prev_panel = Rectangle(width=6.4, height=2.10, stroke_color=BORDER,
                               stroke_width=1.5, fill_color=PANEL_FILL,
                               fill_opacity=0.5).move_to([3.28, -1.52, 0])
        pv_h = left(T("FILE PREVIEW", 22, GREEN), 0.3, -0.66)
        file_tag = always_redraw(lambda: right(
            T(f"RANK_{cur_rank():02d}", 18, GREEN_DIM), 6.26, -0.66))

        f_labels = ["TITLE", "SOURCE", "RANK", "THREAT", "STATUS"]
        label_x, val_x = 0.32, 2.05
        fy0, fdy = -1.02, -0.255
        label_mobs = VGroup(*[
            left(T(lbl, 18, GREEN_DIM), label_x, fy0 + k * fdy)
            for k, lbl in enumerate(f_labels)
        ])
        status_val = left(T("ACTIVE / UNSTABLE", 18, RED), val_x, fy0 + 4 * fdy)
        req = left(T("OPEN REQUEST ACCEPTED", 17, GREEN), 0.32, -2.36)

        title_val = always_redraw(lambda: left(T(cur()[0], 18, GREEN_BRT), val_x, fy0))
        source_val = always_redraw(lambda: left(T(cur()[1], 18, GREEN), val_x, fy0 + fdy))
        rank_val = always_redraw(lambda: left(
            T(f"#{cur_rank():02d} OF {N:02d}", 18, GREEN), val_x, fy0 + 2 * fdy))
        threat_val = always_redraw(lambda: left(
            neon(T(cur()[2], 18, rcolor(cur()[2])), rcolor(cur()[2]),
                 widths=(6, 2.5), ops=(0.10, 0.22)), val_x, fy0 + 3 * fdy))

        # =================================================================
        # BOTTOM CMD STRIP (per-file loading)
        # =================================================================
        bot_div = Line([-6.55, -2.72, 0], [6.55, -2.72, 0], color=BORDER, stroke_width=1)
        cmd_prefix = left(T("CMD> ", 22, GREEN), -6.5, -2.97)
        cmd_x = -6.5 + cmd_prefix.width + 0.12

        def make_cmd():
            txt = T(f"OPEN {slug(cur()[0])}", 22, GREEN_BRT)
            blk = Rectangle(width=0.17, height=0.30, stroke_width=0,
                            fill_color=GREEN, fill_opacity=1).next_to(txt, RIGHT, buff=0.07)
            grp = neon(VGroup(txt, blk), GREEN, widths=(5, 2.5), ops=(0.08, 0.18))
            return left(grp, cmd_x, -2.97)
        cmd_dyn = always_redraw(make_cmd)

        status_dyn = always_redraw(lambda: right(
            T("ACCESS GRANTED" if prog.get_value() > 0.999 else "DECRYPTING ARCHIVE",
              18, GREEN_BRT if prog.get_value() > 0.999 else GREEN_DIM), 6.5, -2.97))

        load_dyn = always_redraw(lambda: left(
            T(f"LOADING  RANK {cur_rank():02d}/{N:02d}", 17, GREEN_DIM), -6.5, -3.24))

        bar_l, bar_w, bar_y = -2.55, 6.95, -3.24
        bar_bg = Rectangle(width=bar_w, height=0.15, stroke_color=GREEN_DIM,
                           stroke_width=1, fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])

        def make_bar():
            w = max(0.001, bar_w * prog.get_value())
            r = Rectangle(width=w, height=0.15, stroke_width=0,
                          fill_color=GREEN, fill_opacity=1)
            r.move_to([bar_l + w / 2, bar_y, 0])
            return neon(r, GREEN, widths=(6, 2.5), ops=(0.12, 0.25))
        bar_fill = always_redraw(make_bar)
        pct = always_redraw(lambda: right(
            T(f"{int(round(prog.get_value()*100)):3d}%", 18, GREEN_BRT), 6.5, bar_y))

        hint = T("UP/DOWN NAVIGATE      ENTER OPEN FILE      ESC CANCEL",
                 16, GREEN_DIM).move_to([0, -3.52, 0])

        # global CRT scanlines (subtle)
        scan = VGroup(*[
            Line([-6.9, y, 0], [6.9, y, 0], color=BG, stroke_width=2, stroke_opacity=0.10)
            for y in np.arange(-3.7, 3.7, 0.16)
        ]).set_z_index(15)

        # =================================================================
        # SEQUENCE
        # =================================================================
        # --- Boot ---
        self.add(frame_glow)
        self.play(Create(frame), run_time=0.6)
        self.play(LaggedStart(FadeIn(hl1), FadeIn(hl2), FadeIn(hr1), FadeIn(hr2),
                              lag_ratio=0.15), Create(head_div), run_time=0.8)
        self.play(FadeIn(title_neon, scale=1.06), run_time=0.7)
        self.play(FadeIn(subtitle), run_time=0.3)
        self.play(title_neon.animate.set_opacity(0.4), run_time=0.06)
        self.play(title_neon.animate.set_opacity(1.0), run_time=0.06)

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

        self.add(scan, highlight, marker, cover_tag, file_tag,
                 title_val, source_val, rank_val, threat_val,
                 cmd_dyn, status_dyn, load_dyn, bar_fill, pct)

        # --- Countdown with CRT flicker between files ---
        def flicker_swap(swap_fn):
            ov = Rectangle(width=14.6, height=8.3, stroke_width=0,
                           fill_color=BG, fill_opacity=0.0).set_z_index(30)
            band = Rectangle(width=14.6, height=0.22, stroke_width=0,
                             fill_color=GREEN_BRT, fill_opacity=0.0).move_to([0, 3.9, 0]).set_z_index(31)
            self.add(ov, band)
            self.play(ov.animate.set_fill(BG, opacity=0.95),
                      band.animate.set_opacity(0.85).move_to([0, -3.9, 0]),
                      run_time=0.13, rate_func=linear)
            swap_fn()                       # hidden behind the blackout
            self.play(ov.animate.set_fill(BG, opacity=0.12), run_time=0.06)
            self.play(ov.animate.set_fill(BG, opacity=0.8), run_time=0.05)
            self.play(ov.animate.set_fill(BG, opacity=0.0),
                      band.animate.set_opacity(0.0), run_time=0.13)
            self.remove(ov, band)

        prev_cover = build_cover(0)
        self.play(FadeIn(prev_cover), run_time=0.4)
        self.play(prog.animate.set_value(1.0), run_time=0.7)
        self.wait(2.1)

        for i in range(1, N):
            new_cover = build_cover(i)
            last = (i == N - 1)

            def swap(old=prev_cover, new=new_cover, idx=i):
                self.remove(old)
                self.add(new)
                sel.set_value(idx)
                prog.set_value(0.0)
            flicker_swap(swap)

            self.play(prog.animate.set_value(1.0), run_time=0.8 if last else 0.6)
            self.wait(2.6 if last else 2.05)
            prev_cover = new_cover

        self.wait(0.3)

        # --- PRESS START ---
        dim = Rectangle(width=14.6, height=8.3, stroke_width=0,
                        fill_color=BG, fill_opacity=0.0).set_z_index(34)
        self.add(dim)
        press_bg = Rectangle(width=6.6, height=1.15, stroke_color=GREEN,
                             stroke_width=2.5, fill_color=BG, fill_opacity=0.92
                             ).move_to(ORIGIN).set_z_index(35)
        press_t = Text("PRESS START", font=FONT_TITLE, color=GREEN_BRT)
        press_t.scale_to_fit_width(5.4).move_to(ORIGIN)
        press = neon(press_t, GREEN, widths=(12, 6, 3), ops=(0.06, 0.12, 0.25)).set_z_index(36)
        self.play(dim.animate.set_fill(BG, opacity=0.66), run_time=0.5)
        self.play(FadeIn(press_bg, scale=0.92), FadeIn(press, scale=0.92), run_time=0.45)
        for _ in range(3):
            self.play(press_t.animate.set_opacity(0.2), run_time=0.45,
                      rate_func=there_and_back)
        self.wait(0.6)
