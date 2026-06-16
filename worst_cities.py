"""Worst Fictional Cities to Live In - video-game style loading screen.

An amber CRT "archive terminal" boots up, indexes 13 fictional cities, sweeps a
selection cursor down the list while a file-preview panel updates, fills a
loading bar, and finishes on PRESS START.

Render:
    manim -pqh worst_cities.py WorstCities
"""

import numpy as np
from manim import *

# --- Palette --------------------------------------------------------------
BG          = "#0E0A08"   # warm near-black
AMBER       = "#EAA13B"   # primary amber
AMBER_BRT   = "#FFC872"   # bright highlight amber
AMBER_DIM   = "#6E5326"   # dim amber
RED         = "#FF5141"   # high-threat red
BORDER      = "#7A4B1E"
PANEL_FILL  = "#140D08"
COVER_FILL  = "#0A0605"

MONO = "DejaVu Sans Mono"

# city, source, threat rating
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

        # =================================================================
        # STATIC FRAME + HEADER + TITLE
        # =================================================================
        frame = RoundedRectangle(width=13.7, height=7.45, corner_radius=0.1,
                                 stroke_color=BORDER, stroke_width=2,
                                 fill_opacity=0)

        hl1 = left(T("WORST CITIES INDEX", 17, AMBER), -6.45, 3.36)
        hl2 = left(T("LOCAL ACCESS TERMINAL // SECTION SELECT", 13, AMBER_DIM),
                   -6.45, 3.10)
        hr1 = right(T("ARCHIVE NODE 07", 17, AMBER), 6.45, 3.36)
        hr2 = right(T("LOCAL NODE // ACTIVE ■", 13, AMBER_DIM), 6.45, 3.10)
        head_div = Line([-6.5, 2.84, 0], [6.5, 2.84, 0],
                        color=BORDER, stroke_width=1.2)

        title = T("WORST CITIES", 46, AMBER_BRT, weight=BOLD).move_to([0, 2.30, 0])
        title_glow = T("WORST CITIES", 46, AMBER, weight=BOLD).move_to([0, 2.30, 0])
        title_glow.set_opacity(0.35).set_stroke(AMBER, width=4, opacity=0.2)
        subtitle = T("// FICTIONAL CITIES TO LIVE IN //", 14, AMBER_DIM).move_to([0, 1.80, 0])

        # =================================================================
        # LEFT LIST PANEL
        # =================================================================
        list_panel = Rectangle(width=6.55, height=4.10, stroke_color=BORDER,
                               stroke_width=1.5, fill_color=PANEL_FILL,
                               fill_opacity=0.5).move_to([-3.27, -0.50, 0])
        lp_h1 = left(T("CITY FILES", 16, AMBER), -6.38, 1.30)
        lp_h2 = right(T("13 FILES FOUND", 14, AMBER_DIM), 0.18, 1.30)
        lp_div = Line([-6.45, 1.10, 0], [0.2, 1.10, 0], color=BORDER, stroke_width=1)

        row_x = -6.00
        row_y0 = 0.80
        row_dy = 0.255
        row_mobs = []
        for i, (name, source, rating) in enumerate(CITIES):
            s = f"[{i+1:02d}]  {name:<14}{rating:>13}"
            row = left(T(s, 15, AMBER, t2c={rating: rcolor(rating)}),
                       row_x, row_y0 - i * row_dy)
            row_mobs.append(row)

        # =================================================================
        # RIGHT COVER PANEL
        # =================================================================
        cover_panel = Rectangle(width=6.4, height=1.70, stroke_color=BORDER,
                                stroke_width=1.5, fill_color=COVER_FILL,
                                fill_opacity=1).move_to([3.28, 0.70, 0])
        cov_l = left(T("COVER IMAGE", 12, AMBER_DIM), 0.25, 1.30)

        rng = np.random.default_rng(11)
        skyline = VGroup()
        bx, baseline = 0.0, -0.02
        while bx < 6.05:
            bw = rng.uniform(0.18, 0.42)
            bh = rng.uniform(0.18, 0.85)
            b = Rectangle(width=bw, height=bh, stroke_width=0,
                          fill_color="#2A1A0C", fill_opacity=1)
            b.move_to([0.22 + bx + bw / 2, baseline + bh / 2, 0])
            skyline.add(b)
            bx += bw + rng.uniform(0.02, 0.12)
        for b in list(skyline):
            if rng.random() < 0.55:
                for _ in range(int(rng.integers(1, 4))):
                    wx = b.get_center()[0] + rng.uniform(-0.08, 0.08)
                    wy = rng.uniform(b.get_bottom()[1] + 0.04, b.get_top()[1] - 0.04)
                    skyline.add(Square(0.03, stroke_width=0, fill_color=AMBER,
                                       fill_opacity=rng.uniform(0.3, 0.8)).move_to([wx, wy, 0]))
        scan = VGroup(*[Line([0.2, y, 0], [6.35, y, 0], color=BG,
                             stroke_width=2, stroke_opacity=0.18)
                        for y in np.arange(-0.02, 1.05, 0.12)])
        cov_scale = left(T("SCALE: METROPOLITAN // SECTOR", 11, AMBER_DIM), 0.25, 0.02)
        cov_status = right(T("ACTIVE / UNSTABLE", 11, RED), 6.3, 0.02)

        # =================================================================
        # RIGHT FILE-PREVIEW PANEL
        # =================================================================
        prev_panel = Rectangle(width=6.4, height=2.20, stroke_color=BORDER,
                               stroke_width=1.5, fill_color=PANEL_FILL,
                               fill_opacity=0.5).move_to([3.28, -1.45, 0])
        pv_h = left(T("FILE PREVIEW", 15, AMBER), 0.25, -0.58)

        f_labels = ["TITLE", "SOURCE", "NODE", "TYPE", "THREAT", "STATUS"]
        label_x, val_x = 0.30, 1.85
        fy0, fdy = -0.92, -0.235
        label_mobs = VGroup(*[
            left(T(lbl, 12, AMBER_DIM), label_x, fy0 + k * fdy)
            for k, lbl in enumerate(f_labels)
        ])
        node_val = left(T("SUBSTRUCTURE 01", 12, AMBER), val_x, fy0 + 2 * fdy)
        type_val = left(T("URBAN HAZARD ZONE", 12, AMBER), val_x, fy0 + 3 * fdy)
        status_val = left(T("ACTIVE / UNSTABLE", 12, RED), val_x, fy0 + 5 * fdy)
        req = left(T("OPEN REQUEST IN PROGRESS", 12, AMBER), 0.30, -2.40)

        # =================================================================
        # BOTTOM CMD STRIP
        # =================================================================
        bot_div = Line([-6.5, -2.72, 0], [6.5, -2.72, 0], color=BORDER, stroke_width=1)
        cmd_prefix = left(T("CMD> ", 14, AMBER), -6.45, -2.98)
        loading_lbl = left(T("LOADING", 12, AMBER_DIM), -6.45, -3.24)
        hint = left(T("↑/↓ NAVIGATE     ENTER OPEN FILE     ESC CANCEL",
                      11, AMBER_DIM), -6.45, -3.50)

        prog = ValueTracker(0.0)
        bar_l, bar_w, bar_y = -1.95, 6.1, -3.24
        bar_bg = Rectangle(width=bar_w, height=0.16, stroke_color=AMBER_DIM,
                           stroke_width=1, fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])
        bar_fill = always_redraw(lambda: Rectangle(
            width=max(0.001, bar_w * prog.get_value()), height=0.16,
            stroke_width=0, fill_color=AMBER, fill_opacity=1
        ).move_to([bar_l + bar_w * prog.get_value() / 2, bar_y, 0]))
        pct = always_redraw(lambda: right(
            T(f"{int(round(prog.get_value()*100)):3d}%", 13, AMBER_BRT), 6.45, bar_y))

        # =================================================================
        # DYNAMIC (selection-driven) preview
        # =================================================================
        sel = ValueTracker(0)

        def cur_idx():
            return int(np.clip(round(sel.get_value()), 0, len(CITIES) - 1))

        def cur():
            return CITIES[cur_idx()]

        cover_tag = always_redraw(lambda: right(
            T(f"{cur_idx()+1:02d} // {cur()[0]}", 12, AMBER), 6.3, 1.30))
        file_tag = always_redraw(lambda: right(
            T(f"FILE_{cur_idx()+1:02d}", 14, AMBER_DIM), 6.3, -0.58))
        title_val = always_redraw(lambda: left(
            T(cur()[0], 12, AMBER_BRT), val_x, fy0 + 0 * fdy))
        source_val = always_redraw(lambda: left(
            T(cur()[1], 12, AMBER), val_x, fy0 + 1 * fdy))
        threat_val = always_redraw(lambda: left(
            T(cur()[2], 12, rcolor(cur()[2])), val_x, fy0 + 4 * fdy))

        highlight = always_redraw(lambda: RoundedRectangle(
            width=6.30, height=0.245, corner_radius=0.03,
            stroke_color=AMBER_BRT, stroke_width=1.4,
            fill_color=AMBER, fill_opacity=0.10
        ).move_to([-3.12, row_y0 - cur_idx() * row_dy, 0]))
        marker = always_redraw(lambda: T(">", 15, AMBER_BRT).move_to(
            [-6.30, row_y0 - cur_idx() * row_dy, 0]))

        # blinking cursor block (after CMD text)
        blink = {"t": 0.0}
        cursor = Rectangle(width=0.13, height=0.24, stroke_width=0,
                           fill_color=AMBER, fill_opacity=1)

        def blink_u(m, dt):
            blink["t"] += dt
            m.set_opacity(1.0 if (blink["t"] % 0.7) < 0.42 else 0.0)

        def status_text(s):
            return right(T(s, 12, AMBER_DIM), 6.45, -2.98)

        status = status_text("INDEXING ARCHIVE NODES")

        # =================================================================
        # ANIMATION SEQUENCE
        # =================================================================
        # --- Boot ---
        self.play(Create(frame), run_time=0.7)
        self.play(
            LaggedStart(FadeIn(hl1), FadeIn(hl2), FadeIn(hr1), FadeIn(hr2),
                        lag_ratio=0.15),
            Create(head_div), run_time=0.9,
        )
        self.add(title_glow)
        self.play(Write(title), run_time=0.7)
        self.play(FadeIn(subtitle), run_time=0.3)
        self.play(title.animate.set_opacity(0.4), run_time=0.06)
        self.play(title.animate.set_opacity(1.0), run_time=0.06)

        # --- Panels in ---
        self.play(Create(list_panel), Create(cover_panel), Create(prev_panel),
                  run_time=0.7)
        self.play(
            FadeIn(lp_h1), FadeIn(lp_h2), Create(lp_div),
            FadeIn(cov_l), FadeIn(cov_scale), FadeIn(cov_status), FadeIn(pv_h),
            run_time=0.6,
        )

        # --- Cover art draws in ---
        self.add(scan)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in skyline],
                              lag_ratio=0.015), run_time=1.0)
        self.add(cover_tag)

        # --- Index the list (rows populate, bar climbs) ---
        self.add(status)
        self.play(
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.12) for r in row_mobs],
                        lag_ratio=0.10),
            prog.animate.set_value(0.55),
            run_time=2.4,
        )

        # --- Preview fields appear ---
        self.add(file_tag)
        self.play(
            FadeIn(label_mobs), FadeIn(node_val), FadeIn(type_val),
            FadeIn(status_val), FadeIn(req),
            run_time=0.5,
        )
        self.add(title_val, source_val, threat_val)

        # --- Selection sweep down the whole list ---
        self.add(highlight, marker)
        self.play(
            sel.animate.set_value(len(CITIES) - 1),
            prog.animate.set_value(0.9),
            Transform(status, status_text("SCANNING THREAT PROFILES")),
            run_time=3.2, rate_func=linear,
        )
        self.play(sel.animate.set_value(0), run_time=0.5)

        # --- CMD types the open request + bar completes ---
        self.add(cmd_prefix, loading_lbl, hint, bot_div, bar_bg, bar_fill, pct)
        cmd_txt = left(T("OPEN GOTHAM_CITY", 14, AMBER_BRT), -5.62, -2.98)
        self.play(AddTextLetterByLetter(cmd_txt), run_time=0.9)
        cursor.next_to(cmd_txt, RIGHT, buff=0.06)
        cursor.add_updater(blink_u)
        self.add(cursor)
        self.play(
            prog.animate.set_value(1.0),
            Transform(status, status_text("ARCHIVE INDEX COMPLETE")),
            run_time=1.2,
        )

        # --- PRESS START (dim the UI, classic game finish) ---
        dim = Rectangle(width=14.5, height=8.2, stroke_width=0,
                        fill_color=BG, fill_opacity=0.0).set_z_index(10)
        self.add(dim)
        press_bg = Rectangle(width=4.9, height=1.0,
                             stroke_color=AMBER, stroke_width=2.5,
                             fill_color=BG, fill_opacity=0.9
                             ).move_to(ORIGIN).set_z_index(11)
        press = T("PRESS START", 32, AMBER_BRT, weight=BOLD).move_to(ORIGIN).set_z_index(12)
        self.play(dim.animate.set_fill(BG, opacity=0.62), run_time=0.5)
        self.play(FadeIn(press_bg, scale=0.92), FadeIn(press, scale=0.92), run_time=0.45)
        for _ in range(3):
            self.play(press.animate.set_opacity(0.2), run_time=0.45,
                      rate_func=there_and_back)
        self.wait(0.8)
