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
    "MOJAVE DESERT", "SCOTTISH HIGHLANDS", "NORWEGIAN FJORDS",
    "LOUISIANA BAYOU", "GOBI DESERT", "NEW GUINEA", "ICELAND",
    "CARPATHIANS",
]
TARGET = 12


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


def neon(mob, color, widths=(7, 3), ops=(0.10, 0.22)):
    """Soft stroke-halo glow around a mobject."""
    g = VGroup()
    for w, o in zip(widths, ops):
        h = mob.copy().set_stroke(color, width=w, opacity=o)
        h.set_fill(opacity=0)
        g.add(h)
    g.add(mob)
    return g


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
        N = len(LOCATIONS)

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

        def make_hl():
            box = RoundedRectangle(width=4.35, height=0.3, corner_radius=0.04,
                                   stroke_color=RED, stroke_width=1.6, fill_color=RED,
                                   fill_opacity=0.18).move_to([lx + 2.0, ly0 - int(sel.get_value()) * ldy, 0])
            return neon(box, RED, widths=(11, 5), ops=(0.13, 0.24))
        hl = always_redraw(make_hl)
        # the hovered/selected name glows on top of the (dim) row
        hover = always_redraw(lambda: neon(
            left(mono(LOCATIONS[int(sel.get_value())], 16, "#FFE6E6"),
                 lx + 0.55, ly0 - int(sel.get_value()) * ldy),
            RED, widths=(6, 3), ops=(0.16, 0.26)))
        marker = always_redraw(lambda: left(mono("▶", 15, RED), -6.98, ly0 - int(sel.get_value()) * ldy))

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
        self.add(hl, hover, marker, status, scan_status, sweep, rec_dot, rec_tc)

        # --- BEAT 1: scanning spins fast & random, then decelerates onto target ---
        random.seed(7)
        fast = [random.randint(0, N - 1) for _ in range(16)]
        approach = [TARGET - 4, TARGET + 3, TARGET - 2, TARGET + 1, TARGET]
        seq = fast + approach
        rts = [0.05] * len(fast) + [0.13, 0.2, 0.3, 0.45, 0.62]
        jump_anims = [sel.animate(run_time=rt, rate_func=(linear if k < len(fast) else smooth)).set_value(idx)
                      for k, (idx, rt) in enumerate(zip(seq, rts))]
        win_anims = [Succession(FadeIn(w, scale=1.08, run_time=0.16), Wait(0.3), FadeOut(w, run_time=0.16))
                     for w in windows]
        # ticks that follow the decelerating cadence (scheduled by time offset)
        t_fast = sum(rts[:len(fast)])
        for off in [0.0, 0.25, 0.5, t_fast, t_fast + 0.13, t_fast + 0.33, t_fast + 0.63, t_fast + 1.08]:
            self.add_sound(snd("tick.wav"), time_offset=off, gain=-7)
        self.play(LaggedStart(*win_anims, lag_ratio=0.18), Succession(*jump_anims))

        # --- BEAT 2: lock on YELLOWSTONE (reticle snaps in) ---
        self.add_sound(snd("access.wav"), gain=-4)
        phase.set_value(1)
        rows[TARGET][2].become(left(mono("[●]", 16, RED), lx + 3.7, ly0 - TARGET * ldy))
        retic = neon(brackets(rows[TARGET], RED, ear=0.22), RED, widths=(8,), ops=(0.28,)).set_z_index(6)
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

        # auth checklist (fills the right side of the panel as it decrypts)
        auth_txt = ["> KEYFRAME 01 ......... OK", "> KEYFRAME 02 ......... OK",
                    "> CIPHER MATCH ........ OK", "> FIREWALL ........ BYPASSED"]
        auth = VGroup(*[left(mono(a, 13, RED if "BYPASS" in a else AMBER), 3.6, 0.62 - k * 0.34).set_opacity(0)
                        for k, a in enumerate(auth_txt)])
        warn2 = left(mono("// DO NOT TERMINATE SESSION", 13, RED).set_opacity(0.65), -1.7, -1.72)
        self.add(auth, warn2)

        self.add_sound(snd("riser.wav"), gain=-7)
        for k, step in enumerate([0.35, 0.62, 0.85, 1.0]):
            self.add_sound(snd("tick.wav"), gain=-6)
            self.play(prog.animate.set_value(step), auth[k].animate.set_opacity(1),
                      run_time=0.85, rate_func=smooth)

        decrypting[0] = False
        phase.set_value(3)
        for hl_ in hex_lines:
            hl_.clear_updaters()
        self.add_sound(snd("boom.wav"), gain=-1)
        self.add_sound(snd("access.wav"), gain=-2)
        unlocked = mono("ARCHIVE UNLOCKED", 30, WHITE).move_to([2.0, 0.1, 0])
        self.play(FadeOut(hex_lines), FadeOut(pct), FadeOut(bar_fill), FadeOut(bar_bg),
                  FadeOut(auth), FadeOut(warn2),
                  FadeIn(unlocked, scale=1.1), dpanel.animate.set_stroke(WHITE), run_time=0.5)
        self.play(self.flash(WHITE, 0.55), run_time=0.4)

        # =================================================================
        # FINAL: reveal the episode title
        # =================================================================
        self.remove(hl, hover, marker, status, rec_dot, rec_tc, scan_status, sweep)
        self.play(
            FadeOut(header), FadeOut(idx_h), FadeOut(list_div), FadeOut(rows),
            FadeOut(retic), FadeOut(dpanel), FadeOut(dttl), FadeOut(dsub),
            FadeOut(unlocked),
            run_time=0.5,
        )
        et = Text("YELLOWSTONE", font=TITLE, weight=BOLD, color=WHITE).scale_to_fit_width(7.4)
        et.move_to([0, 0.45, 0])
        eglow = et.copy().set_stroke(WHITE, 9, 0.12).set_fill(opacity=0)
        eline = Line(et.get_left(), et.get_right(), color=RED, stroke_width=2.5).next_to(et, DOWN, buff=0.35)
        esub = mono("ANOMALY FILE 023 // DECLASSIFIED", 20, RED).next_to(eline, DOWN, buff=0.3)
        self.add_sound(snd("transition.wav"), gain=-7)
        self.play(FadeIn(eglow), FadeIn(et, scale=1.04), GrowFromCenter(eline), run_time=0.7)
        self.play(FadeIn(esub, shift=UP * 0.1), run_time=0.5)
        self.wait(1.6)

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
