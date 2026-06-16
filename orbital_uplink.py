"""Orbital uplink animation.

A miniature satellite orbits a wireframe planet, broadcasting glowing pulses to
three ground stations. Each pulse lights up a station card and ticks its stat
counter. Hero moment: all three stations link at once with expanding signal
rings.

Palette: midnight indigo backdrop, electric cyan, white wireframes, one coral
accent for the active signal. Motion: smooth constant orbit, eased pulse travel,
no camera shake.

Render:
    manim -pqh orbital_uplink.py OrbitalUplink
"""

import numpy as np
from manim import *

# --- Palette --------------------------------------------------------------
BG_INDIGO   = "#0B0E24"   # midnight indigo backdrop
INDIGO_LITE = "#1B2150"   # panel / occluder accents
WIRE        = "#E8ECFF"   # white-ish wireframe
CYAN        = "#34E1FF"   # electric cyan
CORAL       = "#FF6F5C"   # coral accent for the active signal
DIM         = "#3A3F6B"   # resting station-card stroke
CARD_FILL   = "#10153A"   # station-card fill


class OrbitalUplink(Scene):
    def construct(self):
        self.camera.background_color = BG_INDIGO

        PLANET = ORIGIN
        r = 1.35                      # planet radius
        ORBIT_RX, ORBIT_RY = 2.55, 0.85   # tilted orbit ellipse
        ORBIT_SPEED = 0.62            # rad / sec  -> smooth constant orbit

        # ----------------------------------------------------------------
        # Sparse pixel stars
        # ----------------------------------------------------------------
        rng = np.random.default_rng(7)
        stars = VGroup()
        for _ in range(70):
            x, y = rng.uniform(-7.0, 7.0), rng.uniform(-4.0, 4.0)
            if np.hypot(x, y) < 1.7:      # keep the planet area clear-ish
                continue
            s = rng.uniform(0.025, 0.06)
            star = Square(
                side_length=s,
                stroke_width=0,
                fill_color=WIRE,
                fill_opacity=rng.uniform(0.25, 0.9),
            ).move_to([x, y, 0])
            stars.add(star)
        stars.set_z_index(-10)

        # ----------------------------------------------------------------
        # Wireframe planet (occluding fill + line work) + equatorial ring
        # ----------------------------------------------------------------
        planet_fill = Circle(
            radius=r, stroke_width=0, fill_color=BG_INDIGO, fill_opacity=1.0
        ).set_z_index(-1)

        outer = Circle(radius=r, color=WIRE, stroke_width=2.5)
        meridians = VGroup(
            Ellipse(width=2 * r * 0.5, height=2 * r, color=WIRE,
                    stroke_width=1.5, stroke_opacity=0.55),
            Ellipse(width=2 * r * 0.85, height=2 * r, color=WIRE,
                    stroke_width=1.2, stroke_opacity=0.40),
        )

        def lat(y_off, flat=0.16):
            half_w = np.sqrt(max(r * r - y_off * y_off, 0.0))
            return Ellipse(width=2 * half_w, height=2 * r * flat, color=WIRE,
                           stroke_width=1.2, stroke_opacity=0.45).shift(UP * y_off)

        latitudes = VGroup(lat(0.0, 0.18), lat(0.62), lat(-0.62))
        wireframe = VGroup(outer, meridians, latitudes).set_z_index(0)

        equator_ring = Ellipse(
            width=2 * r * 1.75, height=2 * r * 0.32,
            color=CYAN, stroke_width=2.0, stroke_opacity=0.85,
        ).set_z_index(1)

        # faint orbit path
        orbit_path = Ellipse(
            width=2 * ORBIT_RX, height=2 * ORBIT_RY,
            color=CYAN, stroke_width=1.2, stroke_opacity=0.22,
        ).set_z_index(-6)

        # ----------------------------------------------------------------
        # Miniature satellite icon
        # ----------------------------------------------------------------
        def make_satellite():
            body = Rectangle(width=0.24, height=0.17, stroke_color=WIRE,
                             stroke_width=2, fill_color=INDIGO_LITE, fill_opacity=1)
            panel_l = Rectangle(width=0.2, height=0.12, stroke_color=CYAN,
                                stroke_width=1.5, fill_color=INDIGO_LITE,
                                fill_opacity=1).next_to(body, LEFT, buff=0.05)
            panel_r = panel_l.copy().next_to(body, RIGHT, buff=0.05)
            antenna = Line(body.get_top(), body.get_top() + UP * 0.13,
                           stroke_width=2, color=WIRE)
            dish = Dot(radius=0.035, color=CORAL).move_to(antenna.get_end())
            return VGroup(panel_l, body, panel_r, antenna, dish)

        satellite = make_satellite()
        sat_state = {"a": -PI / 2}     # start at the front-bottom of the orbit

        def orbit_update(m, dt):
            sat_state["a"] += dt * ORBIT_SPEED
            a = sat_state["a"]
            m.move_to(PLANET + np.array(
                [ORBIT_RX * np.cos(a), ORBIT_RY * np.sin(a), 0]))
            # pass behind the planet on the far (upper) half of the orbit
            m.set_z_index(-2 if np.sin(a) > 0 else 5)

        satellite.move_to(PLANET + np.array([0, -ORBIT_RY, 0]))

        # ----------------------------------------------------------------
        # Ground-station cards
        # ----------------------------------------------------------------
        CARD_W, CARD_H = 1.95, 1.08
        specs = [
            ("STN-01", np.array([-4.7, 1.65, 0]), 1287, 143),
            ("STN-02", np.array([4.7, 1.65, 0]),   864, 219),
            ("STN-03", np.array([0.0, -2.95, 0]), 2042, 178),
        ]

        def edge_anchor(center, direction):
            dx, dy = direction[0], direction[1]
            sx = (CARD_W / 2) / abs(dx) if abs(dx) > 1e-6 else 1e9
            sy = (CARD_H / 2) / abs(dy) if abs(dy) > 1e-6 else 1e9
            return center + direction * min(sx, sy)

        stations = []
        for name, pos, start_v, inc in specs:
            card = RoundedRectangle(
                width=CARD_W, height=CARD_H, corner_radius=0.12,
                stroke_color=DIM, stroke_width=2,
                fill_color=CARD_FILL, fill_opacity=0.85,
            ).move_to(pos).set_z_index(2)

            label = Text(name, font_size=20, color=WIRE)
            label.move_to(card.get_top() + DOWN * 0.27).set_z_index(6)

            tracker = ValueTracker(start_v)
            cpos = card.get_center() + DOWN * 0.13
            # Rebuilt each frame from the tracker (Pango Text -> no LaTeX needed).
            counter = always_redraw(
                lambda t=tracker, p=cpos: Text(
                    f"{int(t.get_value()):,}", font_size=34, color=CYAN
                ).move_to(p).set_z_index(6)
            )

            direction = normalize(PLANET - pos)
            anchor = edge_anchor(pos, direction)

            stations.append(dict(
                name=name, card=card, label=label, counter=counter,
                tracker=tracker, anchor=anchor, inc=inc,
                group=VGroup(card, label),
            ))

        # ----------------------------------------------------------------
        # Helpers
        # ----------------------------------------------------------------
        def pulse_lines(start, end):
            core = DashedLine(start, end, dash_length=0.14, dashed_ratio=0.55,
                              color=CORAL, stroke_width=3).set_z_index(4)
            glow = DashedLine(start, end, dash_length=0.14, dashed_ratio=0.55,
                              color=CORAL, stroke_width=9,
                              stroke_opacity=0.25).set_z_index(4)
            return core, glow

        def light_card(card):
            return card.animate.set_stroke(CYAN, width=3).set_fill(CYAN, opacity=0.22)

        def emit_pulse(st):
            core, glow = pulse_lines(satellite.get_center(), st["anchor"])
            self.play(Create(glow), Create(core), run_time=0.85, rate_func=smooth)
            self.play(
                light_card(st["card"]),
                st["tracker"].animate.set_value(st["tracker"].get_value() + st["inc"]),
                FadeOut(core), FadeOut(glow),
                run_time=0.6, rate_func=smooth,
            )

        # ================================================================
        # SEQUENCE
        # ================================================================
        # Intro: starfield, planet, ring
        self.add(planet_fill)
        self.play(FadeIn(stars, run_time=1.0))
        self.play(Create(wireframe), run_time=1.6)
        self.play(Create(equator_ring), FadeIn(orbit_path), run_time=0.9)

        # Satellite enters and begins its constant orbit
        self.play(FadeIn(satellite, scale=0.4), run_time=0.7)
        satellite.add_updater(orbit_update)

        # Station cards fade in
        self.play(
            LaggedStart(*[FadeIn(st["group"], shift=UP * 0.25) for st in stations],
                        lag_ratio=0.25),
            run_time=1.2,
        )
        self.add(*[st["counter"] for st in stations])
        self.wait(0.4)

        # Sequential pulses — one station at a time
        for st in stations:
            emit_pulse(st)
            self.wait(0.25)

        self.wait(0.4)

        # ----------------------------------------------------------------
        # HERO MOMENT — all three stations link simultaneously
        # ----------------------------------------------------------------
        start = satellite.get_center()
        all_lines = []
        for st in stations:
            core, glow = pulse_lines(start, st["anchor"])
            all_lines += [glow, core]
        self.play(*[Create(l) for l in all_lines], run_time=0.7, rate_func=smooth)

        rings = VGroup()
        ring_anims = []
        for st in stations:
            c = st["card"].get_center()
            for delay_scale in (1.0, 0.7):
                ring = Circle(radius=0.16, color=CYAN, stroke_width=4,
                              stroke_opacity=0.9).move_to(c).set_z_index(3)
                rings.add(ring)
                ring_anims.append(
                    ring.animate(rate_func=rush_from)
                    .scale(9 * delay_scale).set_stroke(opacity=0))
        self.add(rings)

        caption = Text("ALL STATIONS LINKED", font_size=26, color=CYAN)
        caption.to_edge(UP, buff=0.4).set_z_index(7)

        self.play(
            LaggedStart(*ring_anims, lag_ratio=0.12),
            *[st["card"].animate.set_stroke(CORAL, width=4)
              .set_fill(CYAN, opacity=0.3) for st in stations],
            *[st["tracker"].animate.set_value(
                st["tracker"].get_value() + st["inc"] * 2) for st in stations],
            *[FadeOut(l) for l in all_lines],
            FadeIn(caption, shift=UP * 0.2),
            run_time=1.8,
        )

        # Settle the cards to the resting lit (cyan) state
        self.play(
            *[st["card"].animate.set_stroke(CYAN, width=3) for st in stations],
            run_time=0.6,
        )

        # Let the satellite keep orbiting smoothly to close
        self.wait(2.2)
