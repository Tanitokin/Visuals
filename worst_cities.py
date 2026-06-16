"""Worst Fictional Cities to Live In - ranked countdown menu + loading screen.

Neon-green pixel-CRT terminal with sound. A ranked index of the 13 worst
fictional cities (#13 top -> #01 bottom). A cursor steps through them, the
selected row blinks, each file opens with a CRT "vwip" that masks the cover swap,
a big 16:9 cover loads with a compact dossier, a worked segmented loading bar
runs to 100%, and a LOADED stamp lands before moving on. Ends on #01 THE
MEGASTRUCTURE.

Typography: TITLE_FONT (swappable) + VT323 (terminal body).
Audio: synthesized bed + UI SFX in assets/audio/.
Cover images: assets/covers/NN_*  (NN = rank, 01 = the #1 worst).

Render:
    manim -pqh --fps 30 worst_cities.py WorstCities
"""

import glob
import os

import numpy as np
from manim import *

# --- Neon-green palette ---------------------------------------------------
BG          = "#04110B"
GREEN       = "#3DFF7A"
GREEN_BRT   = "#CFFFDD"
GREEN_DIM   = "#1F8A45"
RED         = "#FF4D4D"
BORDER      = "#1F8A45"
PANEL_FILL  = "#08180F"
COVER_FILL  = "#040D08"

# Title typography (swap here): VT323 / "Press Start 2P" / BITSUMIS / TESLA / Xolonium
TITLE_FONT   = "Press Start 2P"
TITLE_WEIGHT = NORMAL
TITLE_W      = 7.8
FONT_BODY    = "VT323"

BASE = os.path.dirname(os.path.abspath(__file__))
COVER_DIR = os.path.join(BASE, "assets", "covers")
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(name):
    return os.path.join(AUDIO_DIR, name)


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
    g = VGroup()
    for w, o in zip(widths, ops):
        h = mob.copy().set_stroke(color, width=w, opacity=o)
        h.set_fill(opacity=0)
        g.add(h)
    g.add(mob)
    return g


# loading "stutter": jumps and stalls instead of a smooth fill
_LP = [(0, 0), (0.15, 0.30), (0.32, 0.33), (0.55, 0.70),
       (0.68, 0.72), (0.88, 0.95), (1, 1)]


def loadrf(t):
    for i in range(len(_LP) - 1):
        x0, y0 = _LP[i]
        x1, y1 = _LP[i + 1]
        if t <= x1:
            f = (t - x0) / (x1 - x0) if x1 > x0 else 0
            return y0 + (y1 - y0) * f
    return 1.0


class WorstCities(Scene):
    def construct(self):
        self.camera.background_color = BG
        N = len(CITIES)

        def T(s, size, color=GREEN, font=FONT_BODY, weight=NORMAL, t2c=None):
            return Text(s, font=font, font_size=size, color=color,
                        weight=weight, t2c=t2c or {})

        def left(mob, x, y):
            mob.move_to([x, y, 0]).align_to([x, y, 0], LEFT)
            return mob

        def right(mob, x, y):
            mob.move_to([x, y, 0]).align_to([x, y, 0], RIGHT)
            return mob

        sel = ValueTracker(0)
        prog = ValueTracker(0.0)
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))

        def cur_i():
            return int(np.clip(round(sel.get_value()), 0, N - 1))

        def cur():
            return CITIES[cur_i()]

        def rank(i):
            return N - i

        def cur_rank():
            return rank(cur_i())

        def blink_on(period=0.9, duty=0.62):
            return (clock.get_value() % period) < period * duty

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

        title_t = Text("WORST CITIES", font=TITLE_FONT, weight=TITLE_WEIGHT,
                       color=GREEN_BRT).scale_to_fit_width(TITLE_W).move_to([0, 2.30, 0])
        # single subtle glow layer (no heavy halos), kept above the scanlines
        title = neon(title_t, GREEN, widths=(4,), ops=(0.12,)).set_z_index(20)
        subtitle = T("// THE 13 WORST PLACES TO LIVE // 13 TO 01 //", 20, GREEN_DIM).move_to([0, 1.72, 0])

        # =================================================================
        # LEFT LIST PANEL
        # =================================================================
        list_panel = Rectangle(width=6.5, height=4.02, stroke_color=BORDER,
                               stroke_width=1.5, fill_color=PANEL_FILL,
                               fill_opacity=0.5).move_to([-3.30, -0.52, 0])
        lp_h1 = left(T("CITY FILES", 24, GREEN), -6.38, 1.28)
        lp_h2 = right(T("13 FILES FOUND", 17, GREEN_DIM), -0.22, 1.28)
        lp_div = Line([-6.45, 1.05, 0], [-0.1, 1.05, 0], color=BORDER, stroke_width=1)

        row_x, rate_x, row_y0, row_dy = -6.05, -0.30, 0.75, 0.255
        row_mobs = []
        for i, (name, source, rating) in enumerate(CITIES):
            lbl = left(T(f"[{rank(i):02d}]  {name}", 20, GREEN), row_x, row_y0 - i * row_dy)
            rt = right(T(rating, 20, rcolor(rating)), rate_x, row_y0 - i * row_dy)
            row_mobs.append(VGroup(lbl, rt))

        def make_highlight():
            on = blink_on()
            box = RoundedRectangle(width=6.28, height=0.25, corner_radius=0.03,
                                   stroke_color=GREEN_BRT, stroke_width=1.8,
                                   fill_color=GREEN, fill_opacity=0.22 if on else 0.05)
            box.set_stroke(opacity=1.0 if on else 0.4)
            box.move_to([-3.15, row_y0 - cur_i() * row_dy, 0])
            k = 1.0 if on else 0.4
            return neon(box, GREEN, widths=(7, 3), ops=(0.12 * k, 0.24 * k))
        highlight = always_redraw(make_highlight)
        marker = always_redraw(lambda: T(">", 22, GREEN_BRT).set_opacity(
            1.0 if blink_on() else 0.2).move_to([-6.32, row_y0 - cur_i() * row_dy, 0]))

        # =================================================================
        # RIGHT - BIG 16:9 COVER
        # =================================================================
        COVER_C = np.array([3.30, -0.08, 0])
        CBOX_W, CBOX_H = 6.5, 3.18
        cover_panel = Rectangle(width=CBOX_W, height=CBOX_H, stroke_color=BORDER,
                                stroke_width=1.5, fill_color=COVER_FILL,
                                fill_opacity=1).move_to(COVER_C)
        top_strip = Rectangle(width=CBOX_W, height=0.36, stroke_width=0,
                              fill_color=BG, fill_opacity=0.62
                              ).move_to([COVER_C[0], COVER_C[1] + CBOX_H / 2 - 0.18, 0]).set_z_index(2)
        bot_strip = top_strip.copy().move_to([COVER_C[0], COVER_C[1] - CBOX_H / 2 + 0.18, 0])
        cover_tag = always_redraw(lambda: right(
            T(f"{cur_rank():02d} // {cur()[0]}", 17, GREEN),
            6.42, COVER_C[1] + CBOX_H / 2 - 0.18).set_z_index(5))
        feed_tag = left(T("VISUAL FEED", 15, GREEN_DIM), 0.2,
                        COVER_C[1] + CBOX_H / 2 - 0.18).set_z_index(5)
        cov_status = right(T("ACTIVE / UNSTABLE", 15, RED), 6.42,
                           COVER_C[1] - CBOX_H / 2 + 0.18).set_z_index(5)
        cov_scale = left(T("SIGNAL // UNSTABLE", 14, GREEN_DIM), 0.2,
                         COVER_C[1] - CBOX_H / 2 + 0.18).set_z_index(5)
        cover_frame = Rectangle(width=CBOX_W, height=CBOX_H, stroke_color=GREEN,
                                stroke_width=1.5, fill_opacity=0).move_to(COVER_C).set_z_index(6)

        def build_cover(i):
            files = sorted(glob.glob(os.path.join(COVER_DIR, f"{rank(i):02d}_*")))
            files = [f for f in files if not f.lower().endswith((".md", ".txt"))]
            if files:
                img = ImageMobject(files[0]).set_z_index(1)
                img.scale_to_fit_height(CBOX_H - 0.10)
                if img.width > CBOX_W - 0.10:
                    img.scale_to_fit_width(CBOX_W - 0.10)
                return img.move_to(COVER_C)
            name = CITIES[i][0]
            ph_name = T(name, 30, GREEN)
            if ph_name.width > CBOX_W - 0.8:
                ph_name.scale_to_fit_width(CBOX_W - 0.8)
            ph = VGroup(ph_name, T("COVER PENDING", 16, GREEN_DIM)).arrange(DOWN, buff=0.2).move_to(COVER_C)
            return ph.set_z_index(1)

        def make_loaded():
            txt = T("LOADED", 46, GREEN_BRT)
            box = SurroundingRectangle(txt, color=GREEN, buff=0.28, stroke_width=3.5)
            grp = VGroup(box, txt).rotate(-7 * DEGREES).move_to(COVER_C + np.array([0, 0.1, 0]))
            return neon(grp, GREEN, widths=(11, 5), ops=(0.08, 0.18)).set_z_index(9)

        # =================================================================
        # RIGHT - COMPACT DOSSIER STRIP
        # =================================================================
        doss = Rectangle(width=6.5, height=0.80, stroke_color=BORDER,
                         stroke_width=1.5, fill_color=PANEL_FILL,
                         fill_opacity=0.5).move_to([3.30, -2.12, 0])
        d_lab = VGroup(
            left(T("TITLE", 14, GREEN_DIM), 0.18, -1.93),
            left(T("SOURCE", 14, GREEN_DIM), 0.18, -2.31),
            left(T("THREAT", 14, GREEN_DIM), 3.75, -1.93),
            left(T("RANK", 14, GREEN_DIM), 3.75, -2.31),
        )
        d_title = always_redraw(lambda: left(T(cur()[0], 19, GREEN_BRT), 1.25, -1.93))
        d_source = always_redraw(lambda: left(T(cur()[1], 18, GREEN), 1.25, -2.31))
        d_threat = always_redraw(lambda: left(
            neon(T(cur()[2], 18, rcolor(cur()[2])), rcolor(cur()[2]),
                 widths=(5, 2.5), ops=(0.10, 0.22)), 4.65, -1.93))
        d_rank = always_redraw(lambda: left(T(f"#{cur_rank():02d} / {N:02d}", 18, GREEN), 4.65, -2.31))

        # =================================================================
        # BOTTOM CMD STRIP + worked segmented loading bar
        # =================================================================
        bot_div = Line([-6.55, -2.72, 0], [6.55, -2.72, 0], color=BORDER, stroke_width=1)
        cmd_prefix = left(T("CMD> ", 22, GREEN), -6.5, -2.99)
        cmd_x = -6.5 + cmd_prefix.width + 0.12

        def make_cmd():
            txt = T(f"OPEN {slug(cur()[0])}", 22, GREEN_BRT)
            blk = Rectangle(width=0.17, height=0.30, stroke_width=0, fill_color=GREEN,
                            fill_opacity=1.0 if blink_on(0.6) else 0.0).next_to(txt, RIGHT, buff=0.07)
            return left(neon(VGroup(txt, blk), GREEN, widths=(5, 2.5), ops=(0.08, 0.18)), cmd_x, -2.99)
        cmd_dyn = always_redraw(make_cmd)
        status_dyn = always_redraw(lambda: right(
            T("ACCESS GRANTED" if prog.get_value() > 0.999 else "DECRYPTING ARCHIVE",
              18, GREEN_BRT if prog.get_value() > 0.999 else GREEN_DIM), 6.5, -2.99))
        load_dyn = always_redraw(lambda: left(
            T(f"LOADING  RANK {cur_rank():02d}/{N:02d}", 18, GREEN_DIM), -6.5, -3.26))

        bar_l, bar_w, bar_y = -2.55, 6.95, -3.26
        NSEG = 30
        seg_w = bar_w / NSEG
        bar_bg = Rectangle(width=bar_w + 0.06, height=0.21, stroke_color=GREEN_DIM,
                           stroke_width=1, fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])

        def make_bar():
            val = prog.get_value()
            filled = val * NSEG
            edge = int(filled)
            blocks = VGroup()
            for k in range(NSEG):
                cx = bar_l + (k + 0.5) * seg_w
                if k < edge:
                    blocks.add(Rectangle(width=seg_w * 0.72, height=0.15, stroke_width=0,
                                         fill_color=GREEN, fill_opacity=1).move_to([cx, bar_y, 0]))
                elif k == edge and val < 0.999:
                    p = 0.45 + 0.55 * (0.5 + 0.5 * np.sin(clock.get_value() * 22))
                    blocks.add(Rectangle(width=seg_w * 0.72, height=0.15, stroke_width=0,
                                         fill_color=GREEN_BRT, fill_opacity=p).move_to([cx, bar_y, 0]))
                else:
                    blocks.add(Rectangle(width=seg_w * 0.72, height=0.15, stroke_width=1,
                                         stroke_color=GREEN_DIM, fill_opacity=0).move_to([cx, bar_y, 0]))
            fw = max(0.001, bar_w * val)
            glow = Rectangle(width=fw, height=0.15, stroke_width=0, fill_opacity=0).move_to([bar_l + fw / 2, bar_y, 0])
            return VGroup(neon(glow, GREEN, widths=(7,), ops=(0.18,)), blocks)
        bar_fill = always_redraw(make_bar)
        pct = always_redraw(lambda: right(
            T(f"{int(round(prog.get_value()*100)):3d}%", 18, GREEN_BRT), 6.5, bar_y))

        hint = T("UP/DOWN NAVIGATE      ENTER OPEN FILE      ESC CANCEL",
                 16, GREEN_DIM).move_to([0, -3.54, 0])

        scan = VGroup(*[
            Line([-6.9, y, 0], [6.9, y, 0], color=BG, stroke_width=2, stroke_opacity=0.10)
            for y in np.arange(-3.7, 3.7, 0.16)
        ]).set_z_index(15)

        # =================================================================
        # SEQUENCE  (+ audio)
        # =================================================================
        self.add(clock)
        self.add_sound(snd("ambient.wav"), gain=-15)
        self.add_sound(snd("boot.wav"), gain=-5)

        self.add(frame_glow)
        self.play(Create(frame), run_time=0.6)
        self.play(LaggedStart(FadeIn(hl1), FadeIn(hl2), FadeIn(hr1), FadeIn(hr2),
                              lag_ratio=0.15), Create(head_div), run_time=0.8)
        self.play(FadeIn(title, scale=1.06), run_time=0.7)
        self.play(FadeIn(subtitle), run_time=0.3)

        self.play(Create(list_panel), Create(cover_panel), Create(cover_frame),
                  Create(doss), run_time=0.7)
        self.play(
            FadeIn(lp_h1), FadeIn(lp_h2), Create(lp_div),
            FadeIn(top_strip), FadeIn(bot_strip), FadeIn(feed_tag), FadeIn(cov_scale),
            FadeIn(cov_status), FadeIn(d_lab), Create(bot_div),
            FadeIn(cmd_prefix), FadeIn(bar_bg), FadeIn(hint),
            run_time=0.6,
        )
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in row_mobs],
                              lag_ratio=0.08), run_time=1.6)

        self.add(scan, highlight, marker, cover_tag, d_title, d_source, d_threat, d_rank,
                 cmd_dyn, status_dyn, load_dyn, bar_fill, pct)

        def flicker_swap(swap_fn):
            self.add_sound(snd("transition.wav"), gain=-7)
            ov = Rectangle(width=14.6, height=8.3, stroke_width=0,
                           fill_color=BG, fill_opacity=0.0).set_z_index(30)
            band = Rectangle(width=14.6, height=0.22, stroke_width=0,
                             fill_color=GREEN_BRT, fill_opacity=0.0).move_to([0, 3.9, 0]).set_z_index(31)
            self.add(ov, band)
            self.play(ov.animate.set_fill(BG, opacity=0.96),
                      band.animate.set_opacity(0.85).move_to([0, -3.9, 0]),
                      run_time=0.13, rate_func=linear)
            swap_fn()
            self.play(ov.animate.set_fill(BG, opacity=0.1), run_time=0.06)
            self.play(ov.animate.set_fill(BG, opacity=0.0),
                      band.animate.set_opacity(0.0), run_time=0.12)
            self.remove(ov, band)

        def load_and_stamp(last=False):
            self.add_sound(snd("blip.wav"), gain=-9)
            self.play(prog.animate.set_value(1.0), run_time=1.2, rate_func=loadrf)
            stamp = make_loaded()
            self.add_sound(snd("loaded.wav"), gain=-4)
            self.play(FadeIn(stamp, scale=1.6), run_time=0.22, rate_func=rush_from)
            self.wait(1.4 if last else 1.0)
            return stamp

        prev_cover = build_cover(0)
        self.play(FadeIn(prev_cover), run_time=0.4)
        prev_stamp = load_and_stamp()

        for i in range(1, N):
            new_cover = build_cover(i)
            last = (i == N - 1)

            def swap(old=prev_cover, stamp=prev_stamp, new=new_cover, idx=i):
                self.remove(old, stamp)
                self.add(new)
                sel.set_value(idx)
                prog.set_value(0.0)
            flicker_swap(swap)

            prev_cover = new_cover
            prev_stamp = load_and_stamp(last=last)

        self.wait(1.6)
