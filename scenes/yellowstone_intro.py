"""yellowstone_intro.py - classified intelligence-terminal intro -> YELLOWSTONE.

A dark "anomaly archive" interface scans global locations; the selector spins
fast and decelerates onto YELLOWSTONE; the encrypted archive is decrypted to
100%; the episode title is revealed. Clean Oxanium typography, crisp snapping
selector, real CC0 UI sound effects (Kenney) + synth ambience.

Style: black / charcoal / white, subtle amber, red warnings. ~14s.

Render:
    manim -pqh --fps 30 scenes/yellowstone_intro.py YellowstoneIntro
"""

import os
import random

import numpy as np
from manim import *

# --- Intelligence-agency palette -----------------------------------------
BG     = "#070809"
PANEL  = "#0D1015"
GRID   = "#13171D"
LINE   = "#283039"
WHITE  = "#EAEFF6"
DIM    = "#586273"
AMBER  = "#E2A53E"
RED    = "#E5484D"

UI     = "Oxanium"          # all interface type
DATA   = "DejaVu Sans Mono" # the hex data block (kept monospace)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(name):
    return os.path.join(AUDIO_DIR, name)


LOCATIONS = [
    "HIMALAYAS", "AMAZON BASIN", "AUSTRALIA", "PACIFIC ISLANDS", "JAPAN",
    "ANTARCTICA", "ALASKA", "APPALACHIA", "SIBERIA", "CONGO BASIN",
    "MARIANA TRENCH", "PATAGONIA", "YELLOWSTONE", "GREENLAND",
    "MOJAVE DESERT", "SCOTTISH HIGHLANDS", "NORWEGIAN FJORDS",
    "LOUISIANA BAYOU", "GOBI DESERT", "NEW GUINEA", "ICELAND", "CARPATHIANS",
]
TARGET = 12


def T(s, size, color=WHITE, weight="SEMIBOLD", opacity=1.0):
    return Text(s, font=UI, weight=weight, font_size=size, color=color).set_opacity(opacity)


def hexT(s, size, color=DIM):
    return Text(s, font=DATA, font_size=size, color=color)


def left(mob, x, y):
    mob.move_to([x, y, 0]).align_to([x, y, 0], LEFT)
    return mob


def right(mob, x, y):
    mob.move_to([x, y, 0]).align_to([x, y, 0], RIGHT)
    return mob


def rand_hex(n):
    return " ".join("".join(random.choice("0123456789ABCDEF") for _ in range(2)) for _ in range(n))


def neon(mob, color, widths=(7, 3), ops=(0.10, 0.22)):
    g = VGroup()
    for w, o in zip(widths, ops):
        h = mob.copy().set_stroke(color, width=w, opacity=o)
        h.set_fill(opacity=0)
        g.add(h)
    g.add(mob)
    return g


def brackets(target, color=RED, sw=2.5, ear=0.2, buff=0.12):
    box = SurroundingRectangle(target, buff=buff, stroke_width=0)
    g = VGroup()
    for cd in [UL, UR, DL, DR]:
        c = box.get_corner(cd)
        hx = ear if cd[0] < 0 else -ear
        vy = -ear if cd[1] > 0 else ear
        g.add(Line(c, c + RIGHT * hx, color=color, stroke_width=sw),
              Line(c, c + UP * vy, color=color, stroke_width=sw))
    return g


class YellowstoneIntro(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        phase = ValueTracker(0)
        N = len(LOCATIONS)

        grid = VGroup(*[Line([-7.3, y, 0], [7.3, y, 0], color=GRID, stroke_width=1)
                        for y in np.arange(-3.8, 3.9, 0.34)]).set_z_index(-5)
        self.add(grid)

        # ---------------- header ----------------
        h_l = left(T("GLOBAL ANOMALY ARCHIVE", 24), -6.9, 3.6)
        h_v = T("v2.7.1", 16, AMBER).next_to(h_l, RIGHT, buff=0.28).align_to(h_l, DOWN)
        h_c = T("CASE FILE  023 / 050", 16, DIM).move_to([0, 3.6, 0])

        def status_fn():
            p = int(phase.get_value())
            if p == 0:
                return right(T("SCANNING" + "." * (int(clock.get_value() * 4) % 4), 16, AMBER), 6.9, 3.6)
            if p == 1:
                return right(T("TARGET LOCKED", 16, RED), 6.9, 3.6)
            if p == 2:
                return right(T("DECRYPTING", 16, RED), 6.9, 3.6)
            return right(T("ACCESS GRANTED", 16, WHITE), 6.9, 3.6)
        status = always_redraw(status_fn)
        top_div = Line([-6.95, 3.32, 0], [6.95, 3.32, 0], color=LINE, stroke_width=1.2)
        header = VGroup(h_l, h_v, h_c, top_div)

        # ---------------- left location index ----------------
        lx, ly0, ldy = -6.85, 2.82, 0.292
        idx_h = left(T("LOCATION INDEX", 15, RED), lx, 3.04)
        rows = VGroup()
        for i, name in enumerate(LOCATIONS):
            y = ly0 - i * ldy
            num = left(T(f"{i+1:02d}", 15, DIM), lx, y)
            nm = left(T(name, 16, WHITE), lx + 0.6, y)
            box = right(T("[  ]", 15, DIM), -3.2, y)
            rows.add(VGroup(num, nm, box))
        list_div = Line([-3.0, 3.18, 0], [-3.0, -3.7, 0], color=LINE, stroke_width=1.2)

        sel = ValueTracker(0)

        def cur_y():
            return ly0 - int(np.clip(round(sel.get_value()), 0, N - 1)) * ldy

        def make_hl():
            box = RoundedRectangle(width=4.35, height=0.3, corner_radius=0.05,
                                   stroke_color=RED, stroke_width=1.6, fill_color=RED,
                                   fill_opacity=0.16).move_to([lx + 2.0, cur_y(), 0])
            return neon(box, RED, widths=(11, 5), ops=(0.13, 0.22))
        hl = always_redraw(make_hl)
        hover = always_redraw(lambda: neon(
            left(T(LOCATIONS[int(np.clip(round(sel.get_value()), 0, N - 1))], 16, "#FFE6E6"), lx + 0.6, cur_y()),
            RED, widths=(6, 3), ops=(0.16, 0.26)))
        marker = always_redraw(lambda: left(T("▶", 14, RED), -6.98, cur_y()))

        # ---------------- live elements ----------------
        rec_dot = always_redraw(lambda: Dot(radius=0.06, color=RED).move_to([3.05, -3.55, 0])
                                .set_opacity(1.0 if (clock.get_value() % 0.9) < 0.5 else 0.15))
        rec_tc = always_redraw(lambda: left(
            T(f"REC  00:17:{(36 + int(clock.get_value()*9)) % 60:02d}", 15, DIM), 3.22, -3.55))
        scan_status = always_redraw(lambda: left(T(
            f"SCANNING {min(497, 40 + int(clock.get_value()*150)):04d} LOCATIONS // CROSS-REFERENCING", 15, DIM),
            -2.7, -3.55) if int(phase.get_value()) == 0 else VMobject())
        sweep = always_redraw(lambda: Line(
            [(-2.5 + (clock.get_value() * 4.2) % 9.3), 3.12, 0],
            [(-2.5 + (clock.get_value() * 4.2) % 9.3), -3.0, 0],
            color=AMBER, stroke_width=1.4, stroke_opacity=0.18) if int(phase.get_value()) == 0 else VMobject())

        # ---------------- flashing case windows ----------------
        def case_window(pos, w, h, code):
            panel = Rectangle(width=w, height=h, stroke_color=LINE, stroke_width=1.2,
                              fill_color=PANEL, fill_opacity=0.92)
            bar = Rectangle(width=w, height=0.28, stroke_width=0, fill_color="#141922",
                            fill_opacity=1).align_to(panel, UP).match_x(panel)
            ttl = T(code, 13, AMBER).move_to(bar.get_center())
            sil = Polygon([-0.18, -0.32, 0], [0.18, -0.32, 0], [0.26, 0.12, 0], [0, 0.42, 0], [-0.26, 0.12, 0],
                          stroke_width=0, fill_color="#1a2029", fill_opacity=1).scale(0.9)
            sil.move_to(panel.get_center() + LEFT * (w / 2 - 0.5) + DOWN * 0.08)
            b1 = Rectangle(width=w * 0.42, height=0.1, stroke_width=0, fill_color=DIM, fill_opacity=0.5)
            b2 = Rectangle(width=w * 0.55, height=0.1, stroke_width=0, fill_color=DIM, fill_opacity=0.32)
            b3 = Rectangle(width=w * 0.3, height=0.1, stroke_width=0, fill_color=RED, fill_opacity=0.5)
            bars = VGroup(b1, b2, b3).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
            bars.move_to(panel.get_center() + RIGHT * 0.45 + DOWN * 0.04)
            return VGroup(panel, bar, ttl, sil, bars).move_to(pos)

        spots = [(-0.1, 2.2, 2.6, 1.5), (2.9, 1.9, 2.7, 1.7), (5.0, 0.3, 2.4, 1.6),
                 (0.6, -0.4, 2.8, 1.7), (3.6, -1.6, 2.9, 1.6), (-0.3, -2.2, 2.5, 1.5),
                 (5.3, -2.4, 2.3, 1.5), (1.9, 0.9, 2.2, 1.3)]
        codes = ["CASE_2231", "FILE_0094", "REPORT_771", "SIGHTING_18",
                 "ARCHIVE_45", "DOC_9920", "FEED_07", "LOG_3380"]
        windows = [case_window([x, y, 0], w, h, c) for (x, y, w, h), c in zip(spots, codes)]

        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-12)

        self.play(FadeIn(header), FadeIn(idx_h), Create(list_div), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.06) for r in rows], lag_ratio=0.03), run_time=0.9)
        self.add(hl, hover, marker, status, scan_status, sweep, rec_dot, rec_tc)

        # --- BEAT 1: selector spins fast, decelerates onto YELLOWSTONE (crisp snaps) ---
        random.seed(7)
        ivals = [0.07, 0.07, 0.07, 0.08, 0.08, 0.09, 0.10, 0.12, 0.16, 0.21, 0.27, 0.35, 0.46, 0.60]
        idxs = [random.randint(0, N - 1) for _ in range(9)] + [TARGET - 3, TARGET + 2, TARGET - 1, TARGET, TARGET]
        sched, t = [], 0.0
        for itv, i in zip(ivals, idxs):
            sched.append((t, i)); t += itv
        total = t + 0.12

        scan = {"t0": None, "on": True}

        def sel_upd(m, dt):
            if not scan["on"]:
                return
            if scan["t0"] is None:
                scan["t0"] = clock.get_value()
            e = clock.get_value() - scan["t0"]
            idx = sched[0][1]
            for tt, ii in sched:
                if e >= tt:
                    idx = ii
                else:
                    break
            m.set_value(idx)
        sel.add_updater(sel_upd)
        self.add(sel)

        for k, (tt, ii) in enumerate(sched):
            soft = k < 9
            self.add_sound(snd("ui_scan.wav") if soft else snd("ui_step.wav"),
                           time_offset=tt, gain=-14 if soft else -6)
        win_anims = [Succession(FadeIn(w, scale=1.08, run_time=0.16), Wait(0.3), FadeOut(w, run_time=0.16))
                     for w in windows]
        self.play(LaggedStart(*win_anims, lag_ratio=0.16), run_time=total)
        scan["on"] = False
        sel.remove_updater(sel_upd)
        sel.set_value(TARGET)

        # --- BEAT 2: lock ---
        self.add_sound(snd("ui_lock.wav"), gain=-3)
        phase.set_value(1)
        rows[TARGET][2].become(right(T("[●]", 15, RED), -3.2, ly0 - TARGET * ldy))
        retic = neon(brackets(rows[TARGET], RED, ear=0.22), RED, widths=(8,), ops=(0.28,)).set_z_index(6)
        warn = T("ANOMALY DETECTED", 30, RED).move_to([1.6, 0.4, 0])
        self.play(FadeIn(warn, scale=1.1), GrowFromCenter(retic), self.flash(RED, 0.24), run_time=0.45)
        self.play(FadeOut(warn), run_time=0.4)
        self.play(rows.animate.set_opacity(0.22), run_time=0.5)
        rows[TARGET].set_opacity(1.0)

        # --- BEAT 3: decryption ---
        phase.set_value(2)
        dpanel = Rectangle(width=8.6, height=4.0, stroke_color=RED, stroke_width=1.5,
                           fill_color=PANEL, fill_opacity=0.96).move_to([2.0, 0.1, 0])
        dttl = left(T("ENCRYPTED ARCHIVE // YELLOWSTONE", 21, WHITE), -2.0, 1.65)
        dsub = left(T("AES-512  //  SECURITY LAYER 5  //  EYES ONLY", 14, RED), -2.0, 1.28)
        self.play(FadeIn(dpanel, shift=UP * 0.1), FadeIn(dttl), FadeIn(dsub), run_time=0.45)

        decrypting = [True]
        hex_lines = VGroup(*[hexT(rand_hex(14), 15, DIM) for _ in range(5)])
        for k, hl_ in enumerate(hex_lines):
            left(hl_, -1.7, 0.66 - k * 0.32)

        def hex_upd(m):
            if decrypting[0]:
                i = hex_lines.submobjects.index(m)
                random.seed(int(clock.get_value() * 20) * 7 + i)
                m.become(left(hexT(rand_hex(14), 15, DIM), -1.7, 0.66 - i * 0.32))
        for hl_ in hex_lines:
            hl_.add_updater(hex_upd)
        self.add(hex_lines)

        prog = ValueTracker(0.0)
        bar_l, bar_w, bar_y = -1.7, 7.0, -1.35
        bar_bg = Rectangle(width=bar_w, height=0.22, stroke_color=LINE, stroke_width=1,
                           fill_opacity=0).move_to([bar_l + bar_w / 2, bar_y, 0])
        bar_fill = always_redraw(lambda: Rectangle(
            width=max(0.001, bar_w * prog.get_value()), height=0.22, stroke_width=0,
            fill_color=RED, fill_opacity=0.9).move_to([bar_l + bar_w * prog.get_value() / 2, bar_y, 0]))
        pct = always_redraw(lambda: left(
            T(f"DECRYPTING  {int(round(prog.get_value()*100)):3d}%", 16, WHITE), -1.7, -1.0))
        self.add(bar_bg, bar_fill, pct)

        # auth checklist with right-aligned status column (clean in any font)
        auth_items = [("KEYFRAME 01", "OK", AMBER), ("KEYFRAME 02", "OK", AMBER),
                      ("CIPHER MATCH", "OK", AMBER), ("FIREWALL", "BYPASSED", RED)]
        auth = VGroup()
        for k, (lab, st, col) in enumerate(auth_items):
            yk = 0.62 - k * 0.34
            a = left(T(f"> {lab}", 13, DIM), 3.5, yk)
            b = right(T(st, 13, col), 6.3, yk)
            auth.add(VGroup(a, b).set_opacity(0))
        warn2 = left(T("// DO NOT TERMINATE SESSION", 13, RED, opacity=0.65), -1.7, -1.72)
        self.add(auth, warn2)

        self.add_sound(snd("riser.wav"), gain=-8)
        for k, step in enumerate([0.35, 0.62, 0.85, 1.0]):
            self.add_sound(snd("ui_tick.wav"), gain=-6)
            self.play(prog.animate.set_value(step), auth[k].animate.set_opacity(1),
                      run_time=0.85, rate_func=smooth)

        decrypting[0] = False
        phase.set_value(3)
        for hl_ in hex_lines:
            hl_.clear_updaters()
        self.add_sound(snd("ui_unlock.wav"), gain=-2)
        self.add_sound(snd("boom.wav"), gain=-3)
        unlocked = T("ARCHIVE UNLOCKED", 30, WHITE).move_to([2.0, 0.1, 0])
        self.play(FadeOut(hex_lines), FadeOut(pct), FadeOut(bar_fill), FadeOut(bar_bg),
                  FadeOut(auth), FadeOut(warn2),
                  FadeIn(unlocked, scale=1.1), dpanel.animate.set_stroke(WHITE), run_time=0.5)
        self.play(self.flash(WHITE, 0.5), run_time=0.4)

        # --- FINAL: episode title ---
        self.remove(hl, hover, marker, status, rec_dot, rec_tc, scan_status, sweep)
        self.play(
            FadeOut(header), FadeOut(idx_h), FadeOut(list_div), FadeOut(rows),
            FadeOut(retic), FadeOut(dpanel), FadeOut(dttl), FadeOut(dsub),
            FadeOut(unlocked), FadeOut(grid),
            run_time=0.5,
        )
        et = Text("YELLOWSTONE", font=UI, weight="BOLD", color=WHITE).scale_to_fit_width(7.4)
        et.move_to([0, 0.45, 0])
        eglow = et.copy().set_stroke(WHITE, 9, 0.12).set_fill(opacity=0)
        eline = Line(et.get_left(), et.get_right(), color=RED, stroke_width=2.5).next_to(et, DOWN, buff=0.35)
        esub = T("ANOMALY FILE 023  //  DECLASSIFIED", 20, RED).next_to(eline, DOWN, buff=0.3)
        self.add_sound(snd("transition.wav"), gain=-9)
        self.play(FadeIn(eglow), FadeIn(et, scale=1.04), GrowFromCenter(eline), run_time=0.7)
        self.play(FadeIn(esub, shift=UP * 0.1), run_time=0.5)
        self.wait(1.6)

    def flash(self, color=RED, op=0.28):
        fr = self.camera.frame
        fl = Rectangle(width=fr.get_width() * 1.3, height=fr.get_height() * 1.3,
                       stroke_width=0, fill_color=color, fill_opacity=0.0
                       ).move_to(fr.get_center()).set_z_index(50)
        self.add(fl)
        return Succession(
            fl.animate(run_time=0.07).set_fill(color, opacity=op),
            fl.animate(run_time=0.2, rate_func=smooth).set_fill(color, opacity=0.0),
        )
