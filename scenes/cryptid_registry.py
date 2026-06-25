"""cryptid_registry.py - CRYPTID FIELD REGISTRY // EUROPE.

A retro CRT "global anomaly database" boot focused on EUROPE, drawn from REAL
geography (Natural-Earth country polygons -> shapely -> Mercator -> LED map, see
geo_europe.py).  The accurate dotted map of Europe powers on with a scan-line
wipe, country labels resolve, a reticle LOCKS the region (green brackets + ping),
then anomaly markers ping in at the real locations of famous European cryptids
with callout labels, and a REGISTRY LOCKED stamp closes it out.

Title font: Ethnocentric.  Body font: TheSansMonoSCd.  SFX from assets/.

Render at 4K/60 then bloom + lanczos downscale to 1080p + unsharp + trim:
    ./.venv/bin/manim -qk --fps 60 scenes/cryptid_registry.py CryptidRegistry
"""

import os
import sys

import numpy as np
from manim import *
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crt_style import snd
import geo_europe as geo

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

TITLE_FONT = "Ethnocentric"
FONT = "TheSansMonoSCd"

# map placement (manim units) - width derived from the PNG aspect (no distortion)
MAPH = 5.8
MAP_CX, MAP_CY = 0.0, -0.45


class CryptidRegistry(Scene):
    def construct(self):
        self.camera.background_color = BG
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def T(s, size, color=WHITE, **kw):
            return Text(s, font=FONT, font_size=size, color=color, **kw)

        # ---- build / load the accurate Europe LED map -------------------
        png = geo.build_europe_map()
        iw, ih = PILImage.open(png).size
        MAPW = MAPH * iw / ih
        mtop, mbot = MAP_CY + MAPH / 2, MAP_CY - MAPH / 2

        def to_screen(lon, lat):
            u, v = geo.to_uv(lon, lat)
            return np.array([MAP_CX + (u - 0.5) * MAPW, MAP_CY + (v - 0.5) * MAPH, 0.0])

        mapimg = ImageMobject(png).set_z_index(2)
        mapimg.stretch_to_fit_width(MAPW).stretch_to_fit_height(MAPH).move_to([MAP_CX, MAP_CY, 0])

        frame = Rectangle(width=MAPW + 0.35, height=MAPH + 0.35, stroke_color=DIMMER,
                          stroke_width=1.4).move_to([MAP_CX, MAP_CY, 0]).set_z_index(4)

        # ---- title / chrome ---------------------------------------------
        title = Text("CRYPTID FIELD REGISTRY", font=TITLE_FONT,
                     color=TITLE_BLUE).scale_to_fit_width(7.4).move_to([0, 3.2, 0])
        subtitle = T("S E C T O R   E U - W E S T   //   A N O M A L Y   M A P", 14, DIM).move_to([0, 2.66, 0])

        fy = -3.62
        f_l = VGroup(T("CRYPTOZOOLOGICAL DIVISION", 13, DIM),
                     T("FIELD REGISTRY v3.7", 12, BLUE_BRT)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        f_l.move_to([-6.85 + f_l.width / 2, fy, 0])
        f_c = T("(C) 1947-2026  BLACKSITE RESEARCH DIVISION  -  CONTAINMENT CLEARANCE REQUIRED", 12, DIMMER).move_to([0, fy, 0])
        status_field = VGroup(T("STATUS: ", 13, DIM), T("MAPPING", 13, BLUE_BRT)).arrange(RIGHT, buff=0.1)
        f_r = VGroup(T("ANOMALY TRACKING SYSTEM", 13, DIM), status_field).arrange(DOWN, aligned_edge=RIGHT, buff=0.08)
        f_r.move_to([6.85 - f_r.width / 2, fy, 0])

        scanline = Rectangle(width=20, height=0.03, stroke_width=0, fill_color=BLUE_BRT,
                             fill_opacity=0.05).set_z_index(36)
        scanline.add_updater(lambda m: m.move_to([0, 4.0 - ((clock.get_value() * 1.5) % 8.0), 0]))

        def light_sweep(target, run_time=0.55, color=WHITE, op=0.5, z=20):
            cy = target.get_center()[1]
            x0, x1 = target.get_left()[0] - 0.3, target.get_right()[0] + 0.3
            h = target.height + 0.25
            bar = Rectangle(width=0.16, height=h, stroke_width=0, fill_color=color,
                            fill_opacity=0.0).move_to([x0, cy, 0]).set_z_index(z)
            self.add(bar)
            self.play(UpdateFromAlphaFunc(bar, lambda m, a: m.move_to(
                [x0 + (x1 - x0) * a, cy, 0]).set_fill(color, op * np.sin(a * np.pi))),
                run_time=run_time, rate_func=linear)
            self.remove(bar)

        def crosshair(color=BLUE_BRT, r=0.3):
            g = VGroup(Circle(radius=r, stroke_color=color, stroke_width=2.2),
                       Circle(radius=r * 0.16, stroke_color=color, stroke_width=2.2))
            for ang in (0, 90, 180, 270):
                v = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang)), 0])
                g.add(Line(v * (r * 0.5), v * (r * 1.5), color=color, stroke_width=2.2))
            return g.set_z_index(22)

        # =================================================================
        # SEQUENCE
        # =================================================================
        self.add_sound(snd("dark_drone.wav"), gain=-22)
        self.add_sound(snd("ambient.wav"), gain=-21)
        self.add(scanline)

        # 1) title in
        self.play(FadeIn(title, scale=1.05, shift=DOWN * 0.05), run_time=0.6, rate_func=smooth)
        light_sweep(title)
        self.add_sound(snd("es_system_beep.wav"), gain=-15)
        self.play(FadeIn(subtitle, scale=1.02), run_time=0.4, rate_func=smooth)

        # 2) map powers on with a top->bottom scan-line wipe
        self.add_sound(snd("es_loading_slow.wav"), gain=-7)
        cover = Rectangle(width=MAPW + 0.5, height=MAPH + 0.5, stroke_width=0,
                          fill_color=BG, fill_opacity=1).move_to([MAP_CX, MAP_CY, 0]).set_z_index(14)
        edge = Rectangle(width=MAPW + 0.5, height=0.06, stroke_width=0,
                         fill_color=BLUE_BRT, fill_opacity=0.0).set_z_index(15)
        self.add(mapimg, frame, cover, edge)
        self.play(FadeIn(f_l), FadeIn(f_c), FadeIn(f_r), run_time=0.4)

        def rev(m, a):
            yline = mtop + 0.25 - (MAPH + 0.5) * a
            base = mbot - 0.25
            h = max(0.0002, yline - base)
            cover.stretch_to_fit_height(h).move_to([MAP_CX, (yline + base) / 2, 0])
            edge.move_to([MAP_CX, yline, 0]).set_fill(BLUE_BRT, 0.0 if a <= 0.02 or a >= 0.98 else 0.85)
        self.play(UpdateFromAlphaFunc(cover, rev), run_time=1.15, rate_func=linear)
        self.remove(cover, edge)

        # 3) country labels resolve in (faint)
        clabels = VGroup()
        for name, lon, lat in geo.COUNTRY_LABELS:
            p = to_screen(lon, lat)
            if abs(p[0] - MAP_CX) > MAPW / 2 or abs(p[1] - MAP_CY) > MAPH / 2:
                continue
            clabels.add(T(name, 10, DIM).set_opacity(0.0).move_to(p).set_z_index(8))
        self.play(LaggedStart(*[l.animate.set_opacity(0.5) for l in clabels], lag_ratio=0.06),
                  run_time=0.8)

        # 4) reticle roams, then LOCK region: green brackets + sweep + ping
        ch = crosshair().move_to(to_screen(-15, 45))
        self.play(FadeIn(ch), run_time=0.25)
        for lon, lat in [(28, 60), (10, 41)]:
            self.add_sound(snd("es_system_beep.wav"), gain=-16)
            self.play(ch.animate.move_to(to_screen(lon, lat)), run_time=0.4, rate_func=smooth)
        self.add_sound(snd("es_system_beep.wav"), gain=-12)
        self.play(ch.animate.move_to([MAP_CX, MAP_CY, 0]).scale(0.7), run_time=0.4, rate_func=rush_from)

        def bracket(sx, sy):
            cx = MAP_CX + sx * (MAPW + 0.35) / 2
            cy = MAP_CY + sy * (MAPH + 0.35) / 2
            L = 0.55
            return VGroup(Line([cx, cy, 0], [cx - sx * L, cy, 0], color=GREEN, stroke_width=3.2),
                          Line([cx, cy, 0], [cx, cy - sy * L, 0], color=GREEN, stroke_width=3.2)).set_z_index(12)
        brackets = VGroup(*[bracket(sx, sy) for sx, sy in [(-1, 1), (1, 1), (-1, -1), (1, -1)]])
        eu_tag = T("E U R O P E    //    R E G I O N   L O C K E D", 14, GREEN_BRT).move_to([0, 2.66, 0]).set_z_index(13)
        self.add_sound(snd("es_select_ok.wav"), gain=-6)
        self.play(FadeIn(brackets, scale=1.12), FadeOut(subtitle),
                  FadeIn(eu_tag, shift=DOWN * 0.05), FadeOut(ch), run_time=0.5, rate_func=rush_from)
        light_sweep(mapimg, run_time=0.55, color=GREEN_BRT, op=0.28, z=10)
        status_new = VGroup(T("STATUS: ", 13, DIM), T("LOCKED", 13, GREEN_BRT)).arrange(RIGHT, buff=0.1)
        status_new.move_to(status_field.get_right(), aligned_edge=RIGHT)
        self.play(Transform(status_field, status_new), run_time=0.3)
        self.wait(0.25)

        # 5) cryptid anomaly markers ping in with callouts
        left = [(-6.25, 2.05), (-6.25, 0.35), (-6.25, -1.35)]
        right = [(6.05, 2.05), (6.05, 0.35), (6.05, -1.35)]
        # explicit 3/3 split (by index), each side ordered top->bottom by latitude
        west = sorted([geo.CRYPTIDS[i] for i in (0, 1, 3)], key=lambda c: -c[3])
        east = sorted([geo.CRYPTIDS[i] for i in (2, 4, 5)], key=lambda c: -c[3])
        order = []
        for i in range(3):
            order.append((west[i], left[i]))
            order.append((east[i], right[i]))

        for (name, tag, lon, lat), (lx, ly) in order:
            p = to_screen(lon, lat)
            isleft = lx < 0
            ed = LEFT if isleft else RIGHT
            ring = Circle(radius=0.13, stroke_color=AMBER, stroke_width=3.2).move_to(p).set_z_index(24)
            dot = VGroup(Dot(p, radius=0.075, color=AMBER), Dot(p, radius=0.03, color=WHITE)).set_z_index(25)
            card = VGroup(T(tag, 11, AMBER), T(name, 14, WHITE)).arrange(DOWN, aligned_edge=ed, buff=0.05)
            card.move_to([lx, ly, 0], aligned_edge=ed).set_z_index(26)
            join = card.get_edge_center(-ed) + (-ed) * 0.12
            conn = VGroup(Line(join, [p[0], join[1], 0], color=DIM, stroke_width=1.6),
                          Line([p[0], join[1], 0], p, color=DIM, stroke_width=1.6),
                          Dot(join, radius=0.022, color=AMBER)).set_z_index(23)
            self.add_sound(snd("es_system_beep.wav"), gain=-14)
            self.play(FadeIn(dot, scale=0.4), ring.animate.scale(2.4).set_stroke(opacity=0.0),
                      run_time=0.42, rate_func=rush_from)
            self.remove(ring)
            self.play(Create(conn), FadeIn(card, shift=ed * 0.08), run_time=0.34, rate_func=smooth)

        self.wait(0.3)

        # 6) REGISTRY LOCKED stamp
        self.add_sound(snd("es_select_ok.wav"), gain=-7)
        stamp = Text("REGISTRY LOCKED   //   06 ENTITIES", font=TITLE_FONT, font_size=16,
                     color=GREEN_BRT).move_to([0, -3.52, 0]).set_z_index(30)
        stampg = VGroup(*[stamp.copy().set_fill(opacity=0).set_stroke(GREEN, width=w, opacity=0)
                          for w in (14, 7)]).set_z_index(29)
        self.add(stampg)
        self.play(FadeIn(stamp, scale=1.14), stampg.animate.set_stroke(GREEN, 12, 0.18),
                  FadeOut(f_c), run_time=0.45, rate_func=rush_from)
        light_sweep(stamp, run_time=0.4, color=GREEN_BRT, op=0.5)
        self.wait(0.6)

        # 7) cut to black
        self.add_sound(snd("es_system_beep.wav"), gain=-9)
        black = Rectangle(width=16, height=9, stroke_width=0, fill_color="#000000",
                          fill_opacity=0.0).set_z_index(60)
        self.add(black)
        self.play(black.animate.set_fill("#000000", 1.0), run_time=0.32, rate_func=smooth)
        self.wait(0.2)
