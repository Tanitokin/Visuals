"""yellowstone_intro.py - classified intelligence-terminal intro -> YELLOWSTONE.

A dark "anomaly archive" interface scans global locations, locks onto an
encrypted archive, runs a decryption sequence to 100%, then descends through an
"iceberg of information" into the dark. Polished: live REC/scan elements, smooth
eased animations, a clean grid layout, and a synthesized cinematic sound design.

Style: black / charcoal / white, subtle amber, red warnings. ~19s.

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

MONO   = "Share Tech Mono"
TITLE  = "Oxanium"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(name):
    return os.path.join(AUDIO_DIR, name)


LOCATIONS = [
    "HIMALAYAS", "AMAZON BASIN", "AUSTRALIA", "PACIFIC ISLANDS", "JAPAN",
    "ANTARCTICA", "ALASKA", "APPALACHIA", "SIBERIA", "CONGO BASIN",
    "MARIANA TRENCH", "PATAGONIA", "YELLOWSTONE", "GREENLAND",
    "MOJAVE DESERT", "SCOTTISH HIGHLANDS",
]
TARGET = 12

BERG = [
    ("SURFACE LAYER", ["GEOTHERMAL ANOMALIES", "MISSING PERSONS: 1,100+"]),
    ("LEVEL 01", ["UNIDENTIFIED WILDLIFE", "BACKCOUNTRY DISAPPEARANCES"]),
    ("LEVEL 02", ["CAVE SYSTEM REPORTS", "UNLOGGED EXPEDITIONS"]),
    ("LEVEL 03", ["RESTRICTED SECTOR 4", "WITNESS STATEMENTS SEALED"]),
    ("LEVEL 04", ["[ REDACTED ]", "ANOMALOUS SIGNALS"]),
    ("LEVEL 05", ["CLASSIFIED // EYES ONLY", "DO NOT RELEASE"]),
    ("LEVEL 06", ["██████  ████", "CASE STATUS: BURIED"]),
    ("LEVEL 07", ["[ DATA CORRUPTED ]", "██████████"]),
    ("▼  DEPTH UNKNOWN", ["...", "███  ████  ██"]),
]


def mono(s, size, color=WHITE, opacity=1.0):
    return Text(s, font=MONO, font_size=size, color=color).set_opacity(opacity)


def left(mob, x, y):
    mob.move_to([x, y, 0]).align_to([x, y, 0], LEFT)
    return mob


def right(mob, x, y):
    mob.move_to([x, y, 0]).align_to([x, y, 0], RIGHT)
    return mob


def rand_hex(n):
    return " ".join("".join(random.choice("0123456789ABCDEF") for _ in range(2)) for _ in range(n))


def brackets(target, color=RED, sw=2.5, ear=0.18, buff=0.12):
    """4 corner brackets around a mobject (targeting reticle)."""
    target = target.copy().scale(1).set_opacity(0)
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
        cam = self.camera.frame

        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        phase = ValueTracker(0)

        grid = VGroup(*[Line([-7.3, y, 0], [7.3, y, 0], color=GRID, stroke_width=1)
                        for y in np.arange(-3.8, 3.9, 0.34)]).set_z_index(-5)
        self.add(grid)

        # ---------------- header ----------------
        h_l = left(mono("GLOBAL ANOMALY ARCHIVE", 22, WHITE), -6.9, 3.62)
        h_v = mono("v2.7.1", 16, AMBER).next_to(h_l, RIGHT, buff=0.25).align_to(h_l, DOWN)
        h_c = mono("CASE FILE: 023 / 050", 17, DIM).move_to([0, 3.62, 0])

        def status_fn():
            p = int(phase.get_value())
            if p == 0:
                return left(mono("// SCANNING" + "." * (int(clock.get_value() * 4) % 4), 17, AMBER), 4.3, 3.62)
            if p == 1:
                return left(mono("// TARGET LOCKED", 17, RED), 4.7, 3.62)
            if p == 2:
                return left(mono("// DECRYPTING", 17, RED), 5.0, 3.62)
            return left(mono("// ACCESS GRANTED", 17, WHITE), 4.6, 3.62)
        status = always_redraw(status_fn)
        top_div = Line([-6.95, 3.34, 0], [6.95, 3.34, 0], color=LINE, stroke_width=1.2)
        header = VGroup(h_l, h_v, h_c, top_div)

        # ---------------- left location index ----------------
        lx, ly0, ldy = -6.85, 2.85, 0.295
        idx_h = left(mono("// LOCATION INDEX", 16, RED), lx, 3.05)
        rows = VGroup()
        for i, name in enumerate(LOCATIONS):
            y = ly0 - i * ldy
            num = left(mono(f"{i+1:02d}", 16, DIM), lx, y)
            nm = left(mono(name, 16, WHITE), lx + 0.55, y)
            box = left(mono("[ ]", 16, DIM), lx + 3.7, y)
            rows.add(VGroup(num, nm, box))
        list_div = Line([-3.0, 3.2, 0], [-3.0, -3.7, 0], color=LINE, stroke_width=1.2)

        sel = ValueTracker(0)
        hl = always_redraw(lambda: Rectangle(
            width=4.3, height=0.27, stroke_width=0, fill_color=RED, fill_opacity=0.16
        ).move_to([lx + 2.0, ly0 - int(sel.get_value()) * ldy, 0]))
        marker = always_redraw(lambda: left(mono("▶", 14, RED), -6.98, ly0 - int(sel.get_value()) * ldy))

        # ---------------- live elements (más vida) ----------------
        # blinking REC + ticking timecode
        rec_dot = always_redraw(lambda: Dot(radius=0.06, color=RED).move_to([3.05, -3.55, 0])
                                .set_opacity(1.0 if (clock.get_value() % 0.9) < 0.5 else 0.15))
        rec_tc = always_redraw(lambda: left(
            mono(f"REC  00:17:{(36 + int(clock.get_value()*9)) % 60:02d}", 15, DIM), 3.2, -3.55))
        # ticking scan counter
        scan_status = always_redraw(lambda: left(mono(
            f"SCANNING {min(497, 40 + int(clock.get_value()*150)):04d} LOCATIONS // CROSS-REFERENCING", 15, DIM),
            -2.7, -3.55) if int(phase.get_value()) == 0 else VMobject())
        # vertical scanner sweep across the main area (during scan only)
        sweep = always_redraw(lambda: Line(
            [(-2.5 + (clock.get_value() * 4.2) % 9.3), 3.15, 0],
            [(-2.5 + (clock.get_value() * 4.2) % 9.3), -2.95, 0],
            color=AMBER, stroke_width=1.5, stroke_opacity=0.22) if int(phase.get_value()) == 0 else VMobject())

        # ---------------- flashing case windows ----------------
        def case_window(pos, w, h, code):
            panel = Rectangle(width=w, height=h, stroke_color=LINE, stroke_width=1.2,
                              fill_color=PANEL, fill_opacity=0.92)
            bar = Rectangle(width=w, height=0.26, stroke_width=0, fill_color="#141922",
                            fill_opacity=1).align_to(panel, UP).match_x(panel)
            ttl = mono(code, 13, AMBER).move_to(bar.get_center())
            sil = Polygon([-0.18, -0.35, 0], [0.18, -0.35, 0], [0.26, 0.1, 0], [0, 0.4, 0], [-0.26, 0.1, 0],
                          stroke_width=0, fill_color="#1a2029", fill_opacity=1).scale(0.9)
            sil.move_to(panel.get_center() + LEFT * (w / 2 - 0.5) + DOWN * 0.1)
            b1 = Rectangle(width=w * 0.42, height=0.1, stroke_width=0, fill_color=DIM, fill_opacity=0.5)
            b2 = Rectangle(width=w * 0.55, height=0.1, stroke_width=0, fill_color=DIM, fill_opacity=0.32)
            b3 = Rectangle(width=w * 0.3, height=0.1, stroke_width=0, fill_color=RED, fill_opacity=0.5)
            bars = VGroup(b1, b2, b3).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
            bars.move_to(panel.get_center() + RIGHT * 0.45 + DOWN * 0.05)
            return VGroup(panel, bar, ttl, sil, bars).move_to(pos)

        spots = [(-0.1, 2.2, 2.6, 1.5), (2.9, 1.9, 2.7, 1.7), (5.0, 0.3, 2.4, 1.6),
                 (0.6, -0.4, 2.8, 1.7), (3.6, -1.6, 2.9, 1.6), (-0.3, -2.2, 2.5, 1.5),
                 (5.3, -2.4, 2.3, 1.5), (1.9, 0.9, 2.2, 1.3)]
        codes = ["CASE_2231", "FILE_0094", "REPORT_771", "SIGHTING_18",
                 "ARCHIVE_45", "DOC_9920", "FEED_07", "LOG_3380"]
        windows = [case_window([x, y, 0], w, h, c) for (x, y, w, h), c in zip(spots, codes)]

        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-11)
        self.add_sound(snd("boot.wav"), gain=-6)

        self.play(FadeIn(header), FadeIn(idx_h), Create(list_div), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.06) for r in rows], lag_ratio=0.03), run_time=0.9)
        self.add(hl, marker, status, scan_status, sweep, rec_dot, rec_tc)

        # --- BEAT 1: scanning ---
        random.seed(7)
        jumps = [3, 9, 1, 14, 6, 11, 4, 15, 8, 2]
        win_anims = [Succession(FadeIn(w, scale=1.08, run_time=0.16), Wait(0.28), FadeOut(w, run_time=0.16))
                     for w in windows]
        for j in jumps[:4]:
            self.add_sound(snd("blip.wav"), gain=-14)
        self.play(
            LaggedStart(*win_anims, lag_ratio=0.16),
            Succession(*[sel.animate(run_time=0.3).set_value(j) for j in jumps]),
            run_time=3.0,
        )

        # --- BEAT 2: lock on YELLOWSTONE (reticle snaps in) ---
        self.add_sound(snd("access.wav"), gain=-4)
        phase.set_value(1)
        self.play(sel.animate.set_value(TARGET), run_time=0.25)
        rows[TARGET][2].become(left(mono("[●]", 16, RED), lx + 3.7, ly0 - TARGET * ldy))
        retic = brackets(rows[TARGET], RED, ear=0.22).set_z_index(6)
        warn = mono("ANOMALY DETECTED", 30, RED).move_to([1.6, 0.4, 0])
        self.play(FadeIn(warn, scale=1.1), GrowFromCenter(retic), self.flash(RED, 0.26), run_time=0.45)
        self.play(FadeOut(warn), run_time=0.45)
        self.play(rows.animate.set_opacity(0.22), run_time=0.5)
        rows[TARGET].set_opacity(1.0)

        # --- BEAT 3: decryption ---
        phase.set_value(2)
        dpanel = Rectangle(width=8.6, height=4.0, stroke_color=RED, stroke_width=1.5,
                           fill_color=PANEL, fill_opacity=0.96).move_to([2.0, 0.1, 0])
        dttl = left(mono("ENCRYPTED ARCHIVE // YELLOWSTONE", 20, WHITE), -2.0, 1.65)
        dsub = left(mono("AES-512 // SECURITY LAYER 5 // EYES ONLY", 14, RED), -2.0, 1.3)
        self.play(FadeIn(dpanel, shift=UP * 0.1), FadeIn(dttl), FadeIn(dsub), run_time=0.45)

        decrypting = [True]
        hex_lines = VGroup(*[mono(rand_hex(14), 14, DIM) for _ in range(5)])
        for k, hl_ in enumerate(hex_lines):
            left(hl_, -1.7, 0.7 - k * 0.34)

        def hex_upd(m):
            if decrypting[0]:
                i = hex_lines.submobjects.index(m)
                random.seed(int(clock.get_value() * 20) * 7 + i)
                m.become(left(mono(rand_hex(14), 14, DIM), -1.7, 0.7 - i * 0.34))
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
            mono(f"DECRYPTING {int(round(prog.get_value()*100)):3d}%", 16, WHITE), -1.7, -1.0))
        self.add(bar_bg, bar_fill, pct)

        self.add_sound(snd("riser.wav"), gain=-7)
        for step in [0.35, 0.62, 0.85, 1.0]:
            self.add_sound(snd("tick.wav"), gain=-6)
            self.play(prog.animate.set_value(step), run_time=0.85, rate_func=smooth)

        decrypting[0] = False
        phase.set_value(3)
        for hl_ in hex_lines:
            hl_.clear_updaters()
        self.add_sound(snd("boom.wav"), gain=-1)
        self.add_sound(snd("access.wav"), gain=-2)
        unlocked = mono("ARCHIVE UNLOCKED", 30, WHITE).move_to([2.0, 0.1, 0])
        self.play(FadeOut(hex_lines), FadeOut(pct), FadeOut(bar_fill), FadeOut(bar_bg),
                  FadeIn(unlocked, scale=1.1), dpanel.animate.set_stroke(WHITE), run_time=0.5)
        self.play(self.flash(WHITE, 0.55), run_time=0.4)

        # =================================================================
        # BEAT 4: iceberg descent
        # =================================================================
        self.remove(hl, marker, status, rec_dot, rec_tc, scan_status, sweep)
        self.play(
            FadeOut(header), FadeOut(idx_h), FadeOut(list_div), FadeOut(rows),
            FadeOut(grid), FadeOut(retic),
            FadeOut(dpanel), FadeOut(dttl), FadeOut(dsub), FadeOut(unlocked),
            run_time=0.5,
        )

        berg = VGroup()
        top, gap = 2.4, 3.4
        apex_y = top - len(BERG) * gap - 1.0
        body_wedge = Polygon([-5.5, top + 0.3, 0], [5.5, top + 0.3, 0], [0.7, apex_y, 0], [-0.7, apex_y, 0],
                             stroke_width=0, fill_color="#0B1118", fill_opacity=0.6).set_z_index(-3)
        edgeL = Line([-5.5, top + 0.3, 0], [-0.7, apex_y, 0], color=LINE, stroke_width=1.5, stroke_opacity=0.5)
        edgeR = Line([5.5, top + 0.3, 0], [0.7, apex_y, 0], color=LINE, stroke_width=1.5, stroke_opacity=0.5)
        waterline = DashedLine([-7, top + 0.3, 0], [7, top + 0.3, 0], color=AMBER, stroke_width=1.5, dash_length=0.18)
        berg.add(body_wedge, edgeL, edgeR, waterline)

        title = Text("YELLOWSTONE", font=TITLE, weight=BOLD, color=WHITE).scale_to_fit_width(5.6)
        title.move_to([0, top + 0.95, 0])

        strata = []   # (group, y) for proximity reveal
        for k, (lvl, items) in enumerate(BERG):
            y = top - k * gap
            base = max(0.12, 1.0 - k * 0.10)
            col = WHITE if k < 4 else RED if k < 7 else "#7a2a2c"
            div = Line([-6.6, y + 0.55, 0], [6.6, y + 0.55, 0], color=LINE, stroke_width=1, stroke_opacity=0.4 * base)
            lab = left(mono(lvl, 18, AMBER), -6.4, y + 0.2)
            body = VGroup(*[mono(it, 22 if k < 5 else 20, col) for it in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            left(body, -6.4, y - 0.4)
            depth = left(mono(f"-{k*440:04d} M", 14, DIM), 4.6, y + 0.2)
            g = VGroup(div, lab, body, depth)
            berg.add(g)
            strata.append((g, y, base))

        # drifting particles (depth / life)
        rng = np.random.default_rng(4)
        parts = VGroup(*[Dot(radius=rng.uniform(0.012, 0.03), color=WHITE,
                            fill_opacity=rng.uniform(0.05, 0.22)).move_to(
                            [rng.uniform(-6.5, 6.5), rng.uniform(apex_y, top), 0]) for _ in range(70)])
        parts.set_z_index(-2)

        # camera-following progressive darkening (into the dark)
        start_y = 0.0
        dark = Rectangle(width=15, height=9, stroke_width=0, fill_color="#000000", fill_opacity=0).set_z_index(40)

        def dark_upd(m):
            cy = cam.get_center()[1]
            m.move_to(cam.get_center())
            m.set_opacity(float(np.clip((start_y - cy) / (start_y - (apex_y + 2.0)) * 0.75, 0, 0.75)))
        dark.add_updater(dark_upd)

        # proximity reveal: each stratum brightens as the camera nears it
        def make_reveal(g, gy, base):
            def upd(m):
                d = abs(cam.get_center()[1] - gy)
                m.set_opacity(float(np.clip(base * (1.2 - d / 6.0), 0.0, base)))
            return upd
        for g, gy, base in strata:
            g.add_updater(make_reveal(g, gy, base))

        self.add(berg, parts, dark, title)
        self.add_sound(snd("transition.wav"), gain=-9)
        self.play(FadeIn(title, shift=DOWN * 0.2), waterline.animate.set_opacity(1), run_time=0.7)
        self.add_sound(snd("riser.wav"), gain=-12)
        self.play(
            cam.animate.move_to([0, apex_y + 2.5, 0]).set_height(9.2),
            title.animate.shift(UP * 1.2).set_opacity(0.0),
            run_time=5.2, rate_func=smooth,
        )
        self.play(cam.animate.move_to([0, apex_y + 1.0, 0]), run_time=1.1, rate_func=smooth)
        self.wait(0.7)

    # --- helper: full-frame flash that follows the camera ---
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
