"""cryptid_registry.py - CRYPTID FIELD REGISTRY // REGION SELECT.

A retro CRT "global anomaly database" boot in the same archive style as the
divinity loader: a dotted-LED world map powers on, a scanner reticle sweeps the
globe and LOCKS onto EUROPE (region lights green, target box snaps in, ping),
the view push-ins toward Europe and anomaly markers ping in at the sites of
famous European cryptids with callout labels, then a REGISTRY LOCKED stamp.

Title font: Ethnocentric.  Body font: TheSansMonoSCd.  SFX from assets/.

Render at 4K/60 for supersampled sharpness, then bloom + lanczos downscale to
1080p + light unsharp + trim with an audio fade (see divinity_loader docstring).
    ./.venv/bin/manim -qk --fps 60 scenes/cryptid_registry.py CryptidRegistry
"""

import os
import sys

import numpy as np
from manim import *
from PIL import Image as PILImage, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crt_style import snd

BG        = "#000000"
WHITE     = "#FFFFFF"
BLUE      = "#246BFF"
BLUE_BRT  = "#7FB2FF"
TITLE_BLUE = "#3F8BFF"
GREEN     = "#2BE04F"
GREEN_BRT = "#8BFFAD"
AMBER     = "#FFC24B"
DIM       = "#5A6E92"
DIMMER    = "#33425E"
LAND      = (54, 92, 158)     # dim steel-blue LED land
LAND_HI   = (120, 178, 255)
EUR       = (60, 224, 90)     # green europe highlight

TITLE_FONT = "Ethnocentric"
FONT = "TheSansMonoSCd"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(BASE, "assets", "cryptid")
os.makedirs(ASSET, exist_ok=True)

# --- world map placement (manim units) -------------------------------------
WMW, WMH = 10.4, 5.2          # 2:1 equirectangular
MAP_CX, MAP_CY = 0.0, -0.35

# Europe selection bounding box (lon/lat degrees)
EU_LON = (-11.0, 42.0)
EU_LAT = (34.0, 72.0)

# famous European cryptids: (name, tag, lon, lat)
CRYPTIDS = [
    ("LOCH NESS MONSTER", "EU-01", -4.4, 57.3),
    ("THE KRAKEN",        "EU-02",  4.5, 66.0),
    ("BEAST OF GEVAUDAN", "EU-03",  3.4, 44.8),
    ("TATZELWURM",        "EU-04", 10.6, 46.9),
    ("BLACK SHUCK",       "EU-05",  1.3, 52.6),
]

# rough continent ellipses (lon0, lat0, semi_lon, semi_lat) for the land mask
CONTINENTS = [
    (-100, 50, 27, 17), (-118, 60, 12, 13), (-86, 32, 12, 11), (-92, 20, 7, 8),
    (-80, 11, 6, 4),                                   # N. America + Central
    (-42, 72, 11, 8),                                  # Greenland
    (-62, -8, 11, 15), (-66, -30, 8, 13), (-71, -46, 4, 8),   # S. America
    (12, 52, 13, 8), (26, 61, 11, 9),                  # Europe
    (-3, 54, 3.6, 4.2),                                # UK / Ireland
    (18, 6, 17, 17), (26, -18, 13, 13), (12, 26, 11, 7),     # Africa
    (45, 33, 11, 9),                                   # Middle East
    (92, 56, 46, 21), (78, 24, 12, 12), (108, 32, 13, 12),
    (116, 12, 8, 8), (140, 40, 3.5, 6),                # Asia + Japan
    (134, -25, 12, 9), (146, -41, 2.5, 2.5),           # Australia
]


def _hash(c, r):
    x = ((c * 73856093) ^ (r * 19349663)) & 0xFFFF
    return x / 0xFFFF


def is_land(lon, lat):
    if lat < -74:
        return True
    for lo, la, a, b in CONTINENTS:
        if ((lon - lo) / a) ** 2 + ((lat - la) / b) ** 2 <= 1.0:
            return True
    return False


def build_maps(cols=176, rows=88, W=7200):
    """Render the LED world map (blue land) and a green Europe-only overlay."""
    base_p = os.path.join(ASSET, f"world_led_{cols}x{rows}_{W}.png")
    eur_p = os.path.join(ASSET, f"europe_led_{cols}x{rows}_{W}.png")
    if os.path.exists(base_p) and os.path.exists(eur_p):
        return base_p, eur_p
    H = W // 2
    cw = W / cols
    sq = cw * 0.60
    base = PILImage.new("RGBA", (W, H), (0, 0, 0, 255))
    eur = PILImage.new("RGBA", (W, H), (0, 0, 0, 0))
    db, de = ImageDraw.Draw(base), ImageDraw.Draw(eur)
    # faint graticule every 30 deg
    for lon in range(-180, 181, 30):
        x = int((lon + 180) / 360 * W)
        db.line([(x, 0), (x, H)], fill=(20, 32, 58, 255), width=2)
    for lat in range(-90, 91, 30):
        y = int((90 - lat) / 180 * H)
        db.line([(0, y), (W, y)], fill=(20, 32, 58, 255), width=2)
    for c in range(cols):
        lon = -180 + (c + 0.5) / cols * 360
        for r in range(rows):
            lat = 90 - (r + 0.5) / rows * 180
            h = _hash(c, r)
            # ragged edges + a little dropout for texture
            thr = 1.0 + (h - 0.5) * 0.16
            inside = False
            if lat < -74:
                inside = True
            else:
                for lo, la, a, b in CONTINENTS:
                    if ((lon - lo) / a) ** 2 + ((lat - la) / b) ** 2 <= thr:
                        inside = True
                        break
            if not inside or h < 0.06:
                continue
            cx = (lon + 180) / 360 * W
            cy = (90 - lat) / 180 * H
            box = [cx - sq / 2, cy - sq / 2, cx + sq / 2, cy + sq / 2]
            b_ = 0.82 + 0.18 * _hash(r, c)
            db.rectangle(box, fill=(int(LAND[0] * b_), int(LAND[1] * b_), int(LAND[2] * b_), 255))
            if EU_LON[0] <= lon <= EU_LON[1] and EU_LAT[0] <= lat <= EU_LAT[1]:
                de.rectangle(box, fill=(int(EUR[0] * b_), int(EUR[1] * b_), int(EUR[2] * b_), 255))
    base.save(base_p)
    eur.save(eur_p)
    return base_p, eur_p


class CryptidRegistry(Scene):
    def construct(self):
        self.camera.background_color = BG
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def T(s, size, color=WHITE, **kw):
            return Text(s, font=FONT, font_size=size, color=color, **kw)

        # ---- map coordinate helpers -------------------------------------
        def m0(lon, lat):
            return np.array([MAP_CX + lon / 180 * (WMW / 2),
                             MAP_CY + lat / 90 * (WMH / 2), 0.0])

        eu_c = m0((EU_LON[0] + EU_LON[1]) / 2, (EU_LAT[0] + EU_LAT[1]) / 2)
        ZS = 4.6                          # zoom scale
        ct = np.array([0.0, -0.35, 0.0])  # where europe lands after zoom

        def mz(lon, lat):                 # screen pos after the push-in
            return ct + ZS * (m0(lon, lat) - eu_c)

        # ---- build the LED map images -----------------------------------
        base_p, eur_p = build_maps()
        world = ImageMobject(base_p).set_z_index(2)
        world.stretch_to_fit_width(WMW).stretch_to_fit_height(WMH).move_to([MAP_CX, MAP_CY, 0])
        eur = ImageMobject(eur_p).set_z_index(3)
        eur.stretch_to_fit_width(WMW).stretch_to_fit_height(WMH).move_to([MAP_CX, MAP_CY, 0])
        eur.set_opacity(0.0)
        maps = Group(world, eur)

        # subtle map frame
        frame = Rectangle(width=WMW + 0.3, height=WMH + 0.3, stroke_color=DIMMER,
                          stroke_width=1.4).move_to([MAP_CX, MAP_CY, 0]).set_z_index(4)
        corners = VGroup()
        for sx, sy in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
            cxx = MAP_CX + sx * (WMW + 0.3) / 2
            cyy = MAP_CY + sy * (WMH + 0.3) / 2
            corners.add(Line([cxx, cyy, 0], [cxx - sx * 0.28, cyy, 0], color=BLUE, stroke_width=2.4),
                        Line([cxx, cyy, 0], [cxx, cyy - sy * 0.28, 0], color=BLUE, stroke_width=2.4))
        corners.set_z_index(5)

        # ---- title / chrome ---------------------------------------------
        title = Text("CRYPTID FIELD REGISTRY", font=TITLE_FONT,
                     color=TITLE_BLUE).scale_to_fit_width(7.6).move_to([0, 3.05, 0])
        subtitle = T("G L O B A L   A N O M A L Y   D A T A B A S E", 15, DIM).move_to([0, 2.5, 0])

        fy = -3.45
        f_l = VGroup(T("CRYPTOZOOLOGICAL DIVISION", 14, DIM),
                     T("FIELD REGISTRY v3.7", 13, BLUE_BRT)).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        f_l.move_to([-6.7 + f_l.width / 2, fy, 0])
        f_c = VGroup(T("(C) 1947-2026  BLACKSITE RESEARCH DIVISION", 13, DIM),
                     T("CONTAINMENT CLEARANCE REQUIRED", 12, DIMMER)).arrange(DOWN, buff=0.09).move_to([0, fy, 0])
        scan_field = VGroup(T("SCAN: ", 14, DIM), T("GLOBAL", 14, BLUE_BRT)).arrange(RIGHT, buff=0.1)
        f_r = VGroup(T("ANOMALY TRACKING SYSTEM", 14, DIM), scan_field).arrange(DOWN, aligned_edge=RIGHT, buff=0.09)
        f_r.move_to([6.7 - f_r.width / 2, fy, 0])

        # drifting scan line for life
        scanline = Rectangle(width=20, height=0.035, stroke_width=0, fill_color=BLUE_BRT,
                             fill_opacity=0.06).set_z_index(36)
        scanline.add_updater(lambda m: m.move_to([0, 4.0 - ((clock.get_value() * 1.5) % 8.0), 0]))

        def light_sweep(target, run_time=0.55, color=WHITE, op=0.5):
            cy = target.get_center()[1]
            x0, x1 = target.get_left()[0] - 0.3, target.get_right()[0] + 0.3
            h = target.height + 0.25
            bar = Rectangle(width=0.16, height=h, stroke_width=0, fill_color=color,
                            fill_opacity=0.0).move_to([x0, cy, 0]).set_z_index(20)
            self.add(bar)
            self.play(UpdateFromAlphaFunc(bar, lambda m, a: m.move_to(
                [x0 + (x1 - x0) * a, cy, 0]).set_fill(color, op * np.sin(a * np.pi))),
                run_time=run_time, rate_func=linear)
            self.remove(bar)

        def crosshair(color=BLUE_BRT, r=0.34):
            g = VGroup(
                Circle(radius=r, stroke_color=color, stroke_width=2.2),
                Circle(radius=r * 0.18, stroke_color=color, stroke_width=2.2),
                *[Line(ORIGIN, d, color=color, stroke_width=2.2).shift(d * (r * 0.0)) for d in []],
            )
            for ang in [0, 90, 180, 270]:
                v = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang)), 0])
                g.add(Line(v * (r * 0.55), v * (r * 1.45), color=color, stroke_width=2.2))
            return g.set_z_index(22)

        # =================================================================
        # SEQUENCE
        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-22)
        self.add_sound(snd("ambient.wav"), gain=-21)
        self.add(scanline)

        # 1) title in
        self.play(FadeIn(title, scale=1.06, shift=DOWN * 0.05), run_time=0.6, rate_func=smooth)
        light_sweep(title)
        self.add_sound(snd("es_system_beep.wav"), gain=-15)
        self.play(FadeIn(subtitle, scale=1.03), run_time=0.4, rate_func=smooth)

        # 2) map powers on
        self.add_sound(snd("es_loading_slow.wav"), gain=-7)
        self.play(FadeIn(maps), Create(frame), Create(corners),
                  LaggedStart(FadeIn(f_l, shift=UP * 0.08), FadeIn(f_c, shift=UP * 0.08),
                              FadeIn(f_r, shift=UP * 0.08), lag_ratio=0.2),
                  run_time=0.8, rate_func=smooth)
        light_sweep(world, run_time=0.7, color=BLUE_BRT, op=0.32)

        # 3) scanner reticle sweeps, then snaps to Europe
        ch = crosshair().move_to(m0(-150, 20))
        scan_txt = T("SCANNING GLOBAL SECTORS", 16, BLUE_BRT).move_to([0, 1.9, 0]).set_z_index(22)
        self.play(FadeIn(ch), FadeIn(scan_txt), run_time=0.3)
        for lon, lat in [(-60, -20), (120, 40)]:
            self.add_sound(snd("es_system_beep.wav"), gain=-16)
            self.play(ch.animate.move_to(m0(lon, lat)), run_time=0.45, rate_func=smooth)
        # snap to Europe
        self.add_sound(snd("es_system_beep.wav"), gain=-12)
        self.play(ch.animate.move_to(eu_c).scale(0.7),
                  scan_txt.animate.set_opacity(0.0),
                  run_time=0.5, rate_func=rush_from)
        self.remove(scan_txt)

        # 4) LOCK on Europe: green region + target box + ping + label
        bx0, by0 = m0(EU_LON[0], EU_LAT[0])[:2]
        bx1, by1 = m0(EU_LON[1], EU_LAT[1])[:2]
        box = Rectangle(width=abs(bx1 - bx0) + 0.18, height=abs(by1 - by0) + 0.18,
                        stroke_color=GREEN, stroke_width=2.6).move_to(
            [(bx0 + bx1) / 2, (by0 + by1) / 2, 0]).set_z_index(10)
        boxg = box.copy().set_stroke(GREEN, 7, 0.0)
        eu_label = T("> EUROPE <", 20, GREEN_BRT).next_to(box, UP, buff=0.12).set_z_index(11)
        self.add_sound(snd("es_select_ok.wav"), gain=-6)
        self.add(boxg)
        self.play(eur.animate.set_opacity(1.0),
                  Create(box), FadeIn(eu_label, shift=DOWN * 0.06),
                  boxg.animate.set_stroke(GREEN, 12, 0.4),
                  FadeOut(ch), run_time=0.55, rate_func=rush_from)
        self.play(boxg.animate.set_stroke(GREEN, 12, 0.0).scale(1.05), run_time=0.3)
        self.remove(boxg)

        # region info panel (left)
        info = VGroup(
            VGroup(T("REGION", 13, DIM), T("EUROPE", 15, GREEN_BRT)).arrange(RIGHT, buff=0.2, aligned_edge=DOWN),
            VGroup(T("SECTOR", 13, DIM), T("EU-WEST / 04", 15, BLUE_BRT)).arrange(RIGHT, buff=0.2, aligned_edge=DOWN),
            VGroup(T("ENTITIES", 13, DIM), T("05 LOGGED", 15, BLUE_BRT)).arrange(RIGHT, buff=0.2, aligned_edge=DOWN),
            VGroup(T("CLEARANCE", 13, DIM), T("OMEGA", 15, AMBER)).arrange(RIGHT, buff=0.2, aligned_edge=DOWN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).set_z_index(22)
        info.to_corner(DL).shift(UP * 0.5 + RIGHT * 0.2)
        self.play(FadeIn(info, shift=RIGHT * 0.1), run_time=0.4)
        self.wait(0.3)

        # 5) PUSH-IN zoom toward Europe (only the map images move)
        self.add_sound(snd("es_retro_jump.wav"), gain=-12)
        self.play(maps.animate.scale(ZS, about_point=eu_c).shift(ct - eu_c),
                  FadeOut(box), FadeOut(eu_label), FadeOut(frame), FadeOut(corners),
                  FadeOut(info), FadeOut(f_l), FadeOut(f_c), FadeOut(f_r),
                  run_time=1.2, rate_func=smooth)
        zoom_hdr = T("EUROPE  //  ANOMALY SITES", 16, BLUE_BRT).move_to([0, 3.05, 0]).set_z_index(22)
        self.play(FadeOut(subtitle), title.animate.set_opacity(0.0), FadeIn(zoom_hdr), run_time=0.3)

        # 6) cryptid markers ping in with callout labels
        slots = [(-5.2, 2.05), (4.7, 2.0), (-5.2, -0.2), (4.7, -1.3), (-5.2, 1.0)]
        for (name, tag, lon, lat), (lx, ly) in zip(CRYPTIDS, slots):
            p = mz(lon, lat)
            ring = Circle(radius=0.13, stroke_color=AMBER, stroke_width=3.2).move_to(p).set_z_index(24)
            dot = VGroup(Dot(p, radius=0.075, color=AMBER),
                         Dot(p, radius=0.032, color=WHITE)).set_z_index(25)
            anchor = np.array([lx, ly, 0])
            side = LEFT if lx < 0 else RIGHT
            card = VGroup(T(tag, 12, AMBER), T(name, 15, WHITE)).arrange(DOWN, aligned_edge=(LEFT if lx < 0 else RIGHT), buff=0.05)
            card.move_to(anchor, aligned_edge=(LEFT if lx < 0 else RIGHT)).set_z_index(26)
            join = card.get_edge_center(RIGHT if lx < 0 else LEFT) + (RIGHT if lx < 0 else LEFT) * 0.12
            conn = VGroup(Line(join, [p[0], join[1], 0], color=DIM, stroke_width=1.6),
                          Line([p[0], join[1], 0], p, color=DIM, stroke_width=1.6),
                          Dot(join, radius=0.022, color=AMBER))
            conn.set_z_index(23)
            self.add_sound(snd("es_system_beep.wav"), gain=-14)
            self.play(FadeIn(dot, scale=0.4),
                      ring.animate.scale(2.4).set_stroke(opacity=0.0), run_time=0.42, rate_func=rush_from)
            self.remove(ring)
            self.play(Create(conn), FadeIn(card, shift=side * 0.08), run_time=0.34, rate_func=smooth)

        self.wait(0.3)

        # 7) REGISTRY LOCKED stamp + status -> ACTIVE
        self.add_sound(snd("es_select_ok.wav"), gain=-7)
        stamp = Text("REGISTRY LOCKED", font=TITLE_FONT, font_size=22, color=GREEN_BRT).move_to([0, -2.95, 0]).set_z_index(30)
        stampg = VGroup(*[stamp.copy().set_fill(opacity=0).set_stroke(GREEN, width=w, opacity=0)
                          for w in (16, 8)]).set_z_index(29)
        self.add(stampg)
        self.play(FadeIn(stamp, scale=1.16), stampg.animate.set_stroke(GREEN, 13, 0.18),
                  run_time=0.45, rate_func=rush_from)
        light_sweep(stamp, run_time=0.4, color=GREEN_BRT, op=0.5)
        self.wait(0.6)

        # 8) cut to black
        self.add_sound(snd("es_system_beep.wav"), gain=-9)
        black = Rectangle(width=16, height=9, stroke_width=0, fill_color="#000000",
                          fill_opacity=0.0).set_z_index(60)
        self.add(black)
        self.play(black.animate.set_fill("#000000", 1.0), run_time=0.32, rate_func=smooth)
        self.wait(0.2)
