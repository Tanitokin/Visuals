"""yellowstone_intro.py - classified intelligence-terminal intro -> YELLOWSTONE.

Scan (live instruments: waveform, radar, scrolling data, ticking readouts) ->
selector spins & decelerates onto YELLOWSTONE -> decrypt to 100% -> the archive
opens into a DOSSIER: a Yellowstone image, coverage stats, and 7 threat levels.

Drop a photo at  assets/yellowstone.jpg  (or .png/.jpeg/.webp) and it loads into
the dossier; otherwise a themed placeholder is shown.

Render:
    manim -pqh --fps 30 scenes/yellowstone_intro.py YellowstoneIntro
"""

import glob
import os
import random

import numpy as np
from manim import *

# --- palette --------------------------------------------------------------
BG     = "#070809"
PANEL  = "#0D1015"
GRID   = "#13171D"
LINE   = "#283039"
WHITE  = "#EAEFF6"
DIM    = "#586273"
AMBER  = "#E2A53E"
RED    = "#E5484D"

UI   = "Oxanium"
DATA = "DejaVu Sans Mono"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(n):
    return os.path.join(AUDIO_DIR, n)


LOCATIONS = [
    "HIMALAYAS", "AMAZON BASIN", "AUSTRALIA", "PACIFIC ISLANDS", "JAPAN",
    "ANTARCTICA", "ALASKA", "APPALACHIA", "SIBERIA", "CONGO BASIN",
    "MARIANA TRENCH", "PATAGONIA", "YELLOWSTONE", "GREENLAND",
    "MOJAVE DESERT", "SCOTTISH HIGHLANDS", "NORWEGIAN FJORDS",
    "LOUISIANA BAYOU", "GOBI DESERT", "NEW GUINEA", "ICELAND", "CARPATHIANS",
]
TARGET = 12

COVERAGE = [
    ("PARK AREA", "8,983 KM²"), ("CALDERA", "72 x 55 KM"),
    ("CLASSIFICATION", "SUPERVOLCANO"), ("MAGMA DEPTH", "5 - 17 KM"),
    ("LAST ERUPTION", "640,000 YBP"), ("ACTIVE VENTS", "10,000+"),
]
LEVELS = [
    ("LEVEL 1", "GEOTHERMAL INSTABILITY", 0.35),
    ("LEVEL 2", "WILDLIFE ANOMALIES", 0.48),
    ("LEVEL 3", "DISAPPEARANCES", 0.6),
    ("LEVEL 4", "RESTRICTED ZONES", 0.72),
    ("LEVEL 5", "SEISMIC EVENTS", 0.83),
    ("LEVEL 6", "[ REDACTED ]", 0.92),
    ("LEVEL 7", "CLASSIFIED", 1.0),
]


def T(s, size, color=WHITE, weight="SEMIBOLD", opacity=1.0):
    return Text(s, font=UI, weight=weight, font_size=size, color=color).set_opacity(opacity)


def hexT(s, size, color=DIM):
    return Text(s, font=DATA, font_size=size, color=color)


def left(m, x, y):
    m.move_to([x, y, 0]).align_to([x, y, 0], LEFT); return m


def right(m, x, y):
    m.move_to([x, y, 0]).align_to([x, y, 0], RIGHT); return m


def rand_hex(n):
    return " ".join("".join(random.choice("0123456789ABCDEF") for _ in range(2)) for _ in range(n))


def neon(m, color, widths=(7, 3), ops=(0.10, 0.22)):
    g = VGroup()
    for w, o in zip(widths, ops):
        h = m.copy().set_stroke(color, width=w, opacity=o); h.set_fill(opacity=0); g.add(h)
    g.add(m); return g


def brackets(target, color=RED, sw=2.5, ear=0.22, buff=0.12):
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
        T0 = clock.get_value

        grid = VGroup(*[Line([-7.3, y, 0], [7.3, y, 0], color=GRID, stroke_width=1)
                        for y in np.arange(-3.8, 3.9, 0.34)]).set_z_index(-5)
        self.add(grid)

        # ===== persistent live layer ====================================
        def waveform(x0, x1, yc, amp, color, n=64, sw=1.6):
            def build():
                t = T0()
                pts = [[x0 + (x1 - x0) * k / (n - 1),
                        yc + amp * (0.55 * np.sin((x0 + (x1 - x0) * k / (n - 1)) * 3 + t * 6)
                                    + 0.35 * np.sin((x0 + (x1 - x0) * k / (n - 1)) * 8 - t * 9)
                                    + 0.18 * np.sin(t * 23 + k)), 0]
                       for k in range(n)]
                return VMobject().set_points_as_corners(pts).set_stroke(color, sw)
            return always_redraw(build)

        # scrolling data column (far right, behind panels)
        data_lines = VGroup(*[hexT(rand_hex(6), 12, DIM).set_opacity(0.5) for _ in range(26)])
        for k, dl in enumerate(data_lines):
            right(dl, 7.05, 3.4 - k * 0.32)
        ddir = {"o": 0.0}

        def data_upd(m, dt):
            ddir["o"] = (ddir["o"] + dt * 0.9) % 0.32
            for k, dl in enumerate(m):
                y = 3.4 - k * 0.32 + ddir["o"]
                dl.move_to([dl.get_center()[0], y, 0])
                dl.set_opacity(0.0 if y > 3.45 or y < -3.7 else 0.45)
        data_lines.add_updater(data_upd)
        data_lines.set_z_index(-4)

        bottom_wave = waveform(-6.6, -3.2, -3.55, 0.12, AMBER, sw=1.3)

        # ===== header ====================================================
        h_l = left(T("GLOBAL ANOMALY ARCHIVE", 24), -6.9, 3.6)
        h_v = T("v2.7.1", 16, AMBER).next_to(h_l, RIGHT, buff=0.28).align_to(h_l, DOWN)
        h_c = T("CASE FILE 023 / 050", 16, DIM).move_to([-0.4, 3.6, 0])
        sigpc = always_redraw(lambda: left(T(
            f"SIGNAL {78 + int(8*np.sin(T0()*3)+4*np.sin(T0()*11)):02d}%", 15, AMBER if int(T0()*2) % 2 else DIM), 2.0, 3.6))

        def status_fn():
            p = int(phase.get_value())
            if p == 0:
                return right(T("SCANNING" + "." * (int(T0() * 4) % 4), 16, AMBER), 6.9, 3.6)
            if p == 1:
                return right(T("TARGET LOCKED", 16, RED), 6.9, 3.6)
            if p == 2:
                return right(T("DECRYPTING", 16, RED), 6.9, 3.6)
            return right(T("FILE OPEN", 16, WHITE), 6.9, 3.6)
        status = always_redraw(status_fn)
        top_div = Line([-6.95, 3.32, 0], [6.95, 3.32, 0], color=LINE, stroke_width=1.2)
        header = VGroup(h_l, h_v, h_c, top_div)

        # ===== left index ===============================================
        lx, ly0, ldy = -6.85, 2.82, 0.292
        idx_h = left(T("LOCATION INDEX", 15, RED), lx, 3.04)
        rows = VGroup()
        for i, name in enumerate(LOCATIONS):
            y = ly0 - i * ldy
            rows.add(VGroup(left(T(f"{i+1:02d}", 15, DIM), lx, y),
                            left(T(name, 16, WHITE), lx + 0.6, y),
                            right(T("[  ]", 15, DIM), -3.2, y)))
        list_div = Line([-3.0, 3.18, 0], [-3.0, -3.7, 0], color=LINE, stroke_width=1.2)

        sel = ValueTracker(0)
        def cy():
            return ly0 - int(np.clip(round(sel.get_value()), 0, N - 1)) * ldy
        hl = always_redraw(lambda: neon(RoundedRectangle(
            width=4.35, height=0.3, corner_radius=0.05, stroke_color=RED, stroke_width=1.6,
            fill_color=RED, fill_opacity=0.16).move_to([lx + 2.0, cy(), 0]), RED, (11, 5), (0.13, 0.22)))
        hover = always_redraw(lambda: neon(left(T(
            LOCATIONS[int(np.clip(round(sel.get_value()), 0, N - 1))], 16, "#FFE6E6"), lx + 0.6, cy()),
            RED, (6, 3), (0.16, 0.26)))
        marker = always_redraw(lambda: left(T("▶", 14, RED), -6.98, cy()))

        # live readouts (bottom)
        rec_dot = always_redraw(lambda: Dot(radius=0.06, color=RED).move_to([2.0, -3.55, 0])
                                .set_opacity(1.0 if (T0() % 0.9) < 0.5 else 0.15))
        rec_tc = always_redraw(lambda: left(T(f"REC 00:17:{(36+int(T0()*9))%60:02d}", 14, DIM), 2.18, -3.55))
        coords = always_redraw(lambda: left(T(
            f"LAT {44.4+0.02*np.sin(T0()*5):06.3f}  LON {-110.6+0.02*np.cos(T0()*4):07.3f}", 14, DIM), -2.7, -3.55))

        # ===== scan instruments (right; fade at lock) ===================
        sig_box = Rectangle(width=4.7, height=1.5, stroke_color=LINE, stroke_width=1.2,
                            fill_color=PANEL, fill_opacity=0.6).move_to([4.45, 2.1, 0])
        sig_lab = left(T("SIGNAL MONITOR", 13, AMBER), 2.3, 2.66)
        sig_wave = waveform(2.35, 6.55, 1.95, 0.32, AMBER, n=80, sw=1.6)

        rcx, rcy, rr = 5.7, -2.05, 0.78
        radar_rings = VGroup(Circle(rr, color=LINE, stroke_width=1.2),
                             Circle(rr * 0.62, color=LINE, stroke_width=1),
                             Circle(rr * 0.3, color=LINE, stroke_width=1),
                             Line([rcx - rr, rcy, 0], [rcx + rr, rcy, 0], color=LINE, stroke_width=1),
                             Line([rcx, rcy - rr, 0], [rcx, rcy + rr, 0], color=LINE, stroke_width=1)
                             ).move_to([rcx, rcy, 0])
        radar_lab = left(T("PROXIMITY SCAN", 13, AMBER), 4.05, -1.0)
        radar_sweep = always_redraw(lambda: Line(
            [rcx, rcy, 0], [rcx + rr * np.cos(-T0() * 2.2), rcy + rr * np.sin(-T0() * 2.2), 0],
            color=AMBER, stroke_width=1.6, stroke_opacity=0.8))
        rng0 = np.random.default_rng(3)
        blips = VGroup(*[Dot(radius=0.04, color=RED).move_to(
            [rcx + rng0.uniform(-rr*0.7, rr*0.7), rcy + rng0.uniform(-rr*0.7, rr*0.7), 0]) for _ in range(4)])
        blips_a = always_redraw(lambda: VGroup(*[b.copy().set_opacity(0.3 + 0.7 * (0.5 + 0.5 * np.sin(T0()*3 + j*1.7)))
                                                 for j, b in enumerate(blips)]))
        instruments = VGroup(sig_box, sig_lab, radar_rings, radar_lab)

        # ===== cycling case windows =====================================
        def case_window(pos, w, h, code):
            p = Rectangle(width=w, height=h, stroke_color=LINE, stroke_width=1.2, fill_color=PANEL, fill_opacity=0.92)
            bar = Rectangle(width=w, height=0.26, stroke_width=0, fill_color="#141922", fill_opacity=1).align_to(p, UP).match_x(p)
            ttl = T(code, 12, AMBER).move_to(bar.get_center())
            sil = Polygon([-0.16, -0.28, 0], [0.16, -0.28, 0], [0.23, 0.1, 0], [0, 0.36, 0], [-0.23, 0.1, 0],
                          stroke_width=0, fill_color="#1a2029", fill_opacity=1).move_to(p.get_center() + LEFT*(w/2-0.45) + DOWN*0.06)
            b = VGroup(Rectangle(width=w*0.4, height=0.09, stroke_width=0, fill_color=DIM, fill_opacity=0.5),
                       Rectangle(width=w*0.52, height=0.09, stroke_width=0, fill_color=DIM, fill_opacity=0.3),
                       Rectangle(width=w*0.28, height=0.09, stroke_width=0, fill_color=RED, fill_opacity=0.5)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(p.get_center() + RIGHT*0.4 + DOWN*0.03)
            return VGroup(p, bar, ttl, sil, b).move_to(pos)
        wspots = [(0.7, 0.9, 2.5, 1.45), (3.4, 0.3, 2.5, 1.5), (1.2, -1.5, 2.5, 1.45),
                  (4.0, -1.4, 2.4, 1.4), (2.2, 1.4, 2.3, 1.3), (0.4, -0.6, 2.3, 1.3)]
        wcodes = ["CASE_2231", "FILE_0094", "REPORT_771", "DOC_9920", "FEED_07", "LOG_3380"]
        windows = [case_window([x, y, 0], w, h, c) for (x, y, w, h), c in zip(wspots, wcodes)]

        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-12)
        self.play(FadeIn(header), FadeIn(idx_h), Create(list_div), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.06) for r in rows], lag_ratio=0.03), run_time=0.8)
        self.add(data_lines, bottom_wave, sigpc, status, rec_dot, rec_tc, coords,
                 hl, hover, marker)
        self.play(FadeIn(instruments), run_time=0.4)
        self.add(sig_wave, radar_sweep, blips_a)

        # --- BEAT 1: selector spins & decelerates ---
        random.seed(7)
        ivals = [0.07, 0.07, 0.07, 0.08, 0.08, 0.09, 0.10, 0.12, 0.16, 0.21, 0.27, 0.35, 0.46, 0.60]
        idxs = [random.randint(0, N - 1) for _ in range(9)] + [TARGET-3, TARGET+2, TARGET-1, TARGET, TARGET]
        sched, t = [], 0.0
        for itv, i in zip(ivals, idxs):
            sched.append((t, i)); t += itv
        total = t + 0.12
        scan = {"t0": None, "on": True}

        def sel_upd(m, dt):
            if not scan["on"]:
                return
            if scan["t0"] is None:
                scan["t0"] = T0()
            e = T0() - scan["t0"]; idx = sched[0][1]
            for tt, ii in sched:
                if e >= tt:
                    idx = ii
                else:
                    break
            m.set_value(idx)
        sel.add_updater(sel_upd); self.add(sel)
        for k, (tt, ii) in enumerate(sched):
            soft = k < 9
            self.add_sound(snd("ui_scan.wav") if soft else snd("ui_step.wav"), time_offset=tt, gain=-14 if soft else -6)
        win_anims = [Succession(FadeIn(w, scale=1.08, run_time=0.16), Wait(0.28), FadeOut(w, run_time=0.16)) for w in windows]
        self.play(LaggedStart(*win_anims, lag_ratio=0.12), run_time=total)
        scan["on"] = False; sel.remove_updater(sel_upd); sel.set_value(TARGET)

        # --- BEAT 2: lock ---
        self.add_sound(snd("ui_lock.wav"), gain=-3)
        phase.set_value(1)
        rows[TARGET][2].become(right(T("[●]", 15, RED), -3.2, ly0 - TARGET * ldy))
        retic = neon(brackets(rows[TARGET], RED), RED, (8,), (0.28,)).set_z_index(6)
        warn = T("ANOMALY DETECTED", 30, RED).move_to([2.6, 0.4, 0])
        self.play(FadeIn(warn, scale=1.1), GrowFromCenter(retic),
                  FadeOut(instruments), self.flash(RED, 0.24), run_time=0.45)
        self.remove(sig_wave, radar_sweep, blips_a)
        self.play(FadeOut(warn), rows.animate.set_opacity(0.22), run_time=0.45)
        rows[TARGET].set_opacity(1.0)

        # --- BEAT 3: decryption ---
        phase.set_value(2)
        dpanel = Rectangle(width=8.6, height=4.0, stroke_color=RED, stroke_width=1.5,
                           fill_color=PANEL, fill_opacity=0.96).move_to([2.0, 0.1, 0])
        dttl = left(T("ENCRYPTED ARCHIVE // YELLOWSTONE", 21, WHITE), -2.0, 1.65)
        dsub = left(T("AES-512  //  SECURITY LAYER 5  //  EYES ONLY", 14, RED), -2.0, 1.28)
        self.play(FadeIn(dpanel, shift=UP * 0.1), FadeIn(dttl), FadeIn(dsub), run_time=0.45)

        decrypting = [True]
        hex_lines = VGroup(*[hexT(rand_hex(10), 15, DIM) for _ in range(5)])
        for k, x in enumerate(hex_lines):
            left(x, -1.7, 0.66 - k * 0.32)

        def hex_upd(m):
            if decrypting[0]:
                i = hex_lines.submobjects.index(m)
                random.seed(int(T0() * 20) * 7 + i)
                m.become(left(hexT(rand_hex(10), 15, DIM), -1.7, 0.66 - i * 0.32))
        for x in hex_lines:
            x.add_updater(hex_upd)
        self.add(hex_lines)

        prog = ValueTracker(0.0)
        bar_l, bar_w, bar_y = -1.7, 7.0, -1.35
        bar_bg = Rectangle(width=bar_w, height=0.22, stroke_color=LINE, stroke_width=1, fill_opacity=0).move_to([bar_l + bar_w/2, bar_y, 0])
        bar_fill = always_redraw(lambda: Rectangle(width=max(0.001, bar_w*prog.get_value()), height=0.22, stroke_width=0,
                                 fill_color=RED, fill_opacity=0.9).move_to([bar_l + bar_w*prog.get_value()/2, bar_y, 0]))
        pct = always_redraw(lambda: left(T(f"DECRYPTING  {int(round(prog.get_value()*100)):3d}%", 16, WHITE), -1.7, -1.0))
        self.add(bar_bg, bar_fill, pct)
        auth_items = [("KEYFRAME 01", "OK", AMBER), ("KEYFRAME 02", "OK", AMBER),
                      ("CIPHER MATCH", "OK", AMBER), ("FIREWALL", "BYPASSED", RED)]
        auth = VGroup()
        for k, (lab, st, col) in enumerate(auth_items):
            yk = 0.62 - k * 0.34
            auth.add(VGroup(left(T(f"> {lab}", 13, DIM), 3.5, yk), right(T(st, 13, col), 6.3, yk)).set_opacity(0))
        warn2 = left(T("// DO NOT TERMINATE SESSION", 13, RED, opacity=0.65), -1.7, -1.72)
        self.add(auth, warn2)
        self.add_sound(snd("riser.wav"), gain=-8)
        for k, step in enumerate([0.35, 0.62, 0.85, 1.0]):
            self.add_sound(snd("ui_tick.wav"), gain=-6)
            self.play(prog.animate.set_value(step), auth[k].animate.set_opacity(1), run_time=0.8, rate_func=smooth)

        decrypting[0] = False
        phase.set_value(3)
        for x in hex_lines:
            x.clear_updaters()
        self.add_sound(snd("ui_unlock.wav"), gain=-2)
        self.add_sound(snd("boom.wav"), gain=-3)
        # full clean takeover: drop every interface element behind the dossier
        self.remove(hl, hover, marker, status, rec_dot, rec_tc, coords, sigpc,
                    data_lines, bottom_wave)
        self.play(FadeOut(dpanel), FadeOut(dttl), FadeOut(dsub), FadeOut(hex_lines),
                  FadeOut(pct), FadeOut(bar_fill), FadeOut(bar_bg), FadeOut(auth), FadeOut(warn2),
                  FadeOut(retic), FadeOut(header), FadeOut(idx_h), FadeOut(list_div),
                  FadeOut(rows), FadeOut(grid), self.flash(WHITE, 0.5), run_time=0.5)

        # =================================================================
        # BEAT 4: YELLOWSTONE DOSSIER
        # =================================================================
        dpan = Rectangle(width=13.3, height=7.1, stroke_color=LINE, stroke_width=1.5,
                         fill_color=PANEL, fill_opacity=1).move_to(ORIGIN)
        dpan_glow = dpan.copy().set_stroke(WHITE, 5, 0.12)
        d_title = left(T("YELLOWSTONE", 36, WHITE, weight="BOLD"), -6.2, 2.78)
        d_sub = left(T("ANOMALY DOSSIER  //  FILE 023  //  DECLASSIFIED", 15, RED), -6.2, 2.3)
        d_tdiv = Line([-6.3, 2.05, 0], [6.3, 2.05, 0], color=LINE, stroke_width=1)
        self.play(FadeIn(dpan_glow), FadeIn(dpan), run_time=0.4)
        self.play(AddTextLetterByLetter(d_title), run_time=0.45)
        self.play(FadeIn(d_sub), Create(d_tdiv), run_time=0.3)

        # --- image (upper-left) ---
        IW, IH = 4.9, 2.9
        ibx, iby = -3.75, 0.4
        iframe = Rectangle(width=IW, height=IH, stroke_color=AMBER, stroke_width=1.5,
                           fill_color="#070A0D", fill_opacity=1).move_to([ibx, iby, 0])
        files = [f for f in glob.glob(os.path.join(BASE, "assets", "yellowstone.*"))
                 if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
        if files:
            img = ImageMobject(files[0])
            img.scale_to_fit_height(IH - 0.14)
            if img.width > IW - 0.14:
                img.scale_to_fit_width(IW - 0.14)
            picture = img.move_to([ibx, iby, 0])
        else:
            bg_im = Rectangle(width=IW, height=IH, stroke_width=0, fill_color="#0A0E12", fill_opacity=1).move_to([ibx, iby, 0])
            rings = VGroup(*[Ellipse(width=(IW - 0.5) * (1 - j * 0.17), height=(IH - 0.5) * (1 - j * 0.19),
                            stroke_color=c, stroke_width=3, stroke_opacity=0.7)
                            for j, c in enumerate(["#d8ad3e", "#83b24c", "#2fa07c", "#2c6cb0"])]).move_to([ibx, iby + 0.1, 0])
            picture = VGroup(bg_im, rings,
                             T("VISUAL FEED // DROP assets/yellowstone.jpg", 12, DIM).move_to([ibx, iby - IH/2 + 0.26, 0]))
        topbar = Rectangle(width=IW, height=0.3, stroke_width=0, fill_color="#10151C", fill_opacity=1).move_to([ibx, iby + IH/2 - 0.15, 0])
        ilab = left(T("VISUAL FEED", 12, DIM), ibx - IW/2 + 0.15, iby + IH/2 - 0.15)
        istat = right(T("THERMAL", 12, RED), ibx + IW/2 - 0.15, iby + IH/2 - 0.15)
        scanbar = Rectangle(width=IW, height=0.05, stroke_width=0, fill_color=AMBER, fill_opacity=0.85).move_to([ibx, iby + IH/2, 0]).set_z_index(8)
        self.add(picture, iframe, topbar, ilab, istat)
        self.add_sound(snd("ui_scan.wav"), gain=-8)
        self.play(scanbar.animate.move_to([ibx, iby - IH/2, 0]), FadeIn(picture, run_time=0.1), run_time=0.55, rate_func=linear)
        self.remove(scanbar)

        # --- coverage (upper-right) ---
        cov_h = left(T("// COVERAGE", 14, RED), 0.6, 1.55)
        cstats = VGroup()
        for k, (lab, val) in enumerate(COVERAGE):
            yk = 1.18 - k * 0.32
            cstats.add(VGroup(left(T(lab, 14, DIM), 0.6, yk), right(T(val, 14, WHITE), 6.0, yk)))
        self.play(FadeIn(cov_h), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.05) for c in cstats], lag_ratio=0.07), run_time=0.7)

        # --- threat levels 1-7 (full-width bottom band, animated bars) ---
        lv_head = left(T("// THREAT LEVELS  [ 1 - 7 ]", 14, RED), -6.2, -1.2)
        self.play(FadeIn(lv_head), run_time=0.25)
        lv_y0, lv_dy, lv_lx, lv_bx, lv_bw = -1.55, 0.265, -6.2, -1.3, 7.1
        levels = VGroup()
        bar_anims = []
        for k, (lv, lab, sev) in enumerate(LEVELS):
            yk = lv_y0 - k * lv_dy
            col = AMBER if sev < 0.7 else RED
            levels.add(left(T(lv, 13, AMBER), lv_lx, yk),
                       left(T(lab, 13, WHITE if sev < 0.92 else RED), lv_lx + 1.05, yk))
            track = Rectangle(width=lv_bw, height=0.12, stroke_color=LINE, stroke_width=1, fill_opacity=0).move_to([lv_bx + lv_bw / 2, yk, 0])
            fillr = Rectangle(width=0.001, height=0.12, stroke_width=0, fill_color=col, fill_opacity=0.9).move_to([lv_bx, yk, 0])
            levels.add(track)
            self.add(track, fillr)
            bar_anims.append((fillr, sev, yk))
        self.add(levels)
        for fillr, sev, yk in bar_anims:
            self.add_sound(snd("ui_tick.wav"), gain=-9)
            self.play(fillr.animate.stretch_to_fit_width(lv_bw * sev).move_to([lv_bx + lv_bw * sev / 2, yk, 0]),
                      run_time=0.16, rate_func=smooth)
        self.wait(1.6)

    def flash(self, color=RED, op=0.28):
        fr = self.camera.frame
        fl = Rectangle(width=fr.get_width()*1.3, height=fr.get_height()*1.3, stroke_width=0,
                       fill_color=color, fill_opacity=0.0).move_to(fr.get_center()).set_z_index(50)
        self.add(fl)
        return Succession(fl.animate(run_time=0.07).set_fill(color, opacity=op),
                          fl.animate(run_time=0.2, rate_func=smooth).set_fill(color, opacity=0.0))
