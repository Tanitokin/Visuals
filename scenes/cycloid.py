"""Cycloid animation.

A circle rolls without slipping along a straight number line. A bright dot
marked on its rim traces out a cycloid curve as the circle rotates.

Render:
    manim -pqh scenes/cycloid.py CycloidScene
"""

import numpy as np
from manim import *


class CycloidScene(Scene):
    def construct(self):
        # Dark background and rolling parameters.
        self.camera.background_color = "#0e1117"

        r = 1.0           # radius of the rolling circle
        line_y = -2.5     # vertical position of the number line
        x_start = -6.6    # x-position where the contact point begins
        turns = 2         # number of full revolutions (= number of arches)

        # The rolling angle theta drives the whole animation.
        theta = ValueTracker(0.0)

        # --- Number line at the bottom of the screen ---------------------
        number_line = NumberLine(
            x_range=[-7, 7, 1],
            length=14,
            color=GREY_B,
            stroke_width=2,
            include_ticks=True,
            include_numbers=False,
        ).move_to([0, line_y, 0])

        # --- Geometry of the rolling circle ------------------------------
        def center_point():
            # Center moves right at the same rate the rim arc unrolls.
            return np.array([x_start + r * theta.get_value(), line_y + r, 0])

        def dot_point():
            # Parametric cycloid: marked point starts at the contact point.
            th = theta.get_value()
            return np.array([
                x_start + r * (th - np.sin(th)),
                line_y + r * (1 - np.cos(th)),
                0,
            ])

        # Wheel = circle + spokes, rebuilt each frame to show rotation.
        def make_wheel():
            c = center_point()
            th = theta.get_value()
            circle = Circle(radius=r, color=BLUE_B, stroke_width=4).move_to(c)
            spokes = VGroup(*[
                Line(
                    c,
                    c + r * np.array([np.cos(-th + k * PI / 2),
                                      np.sin(-th + k * PI / 2), 0]),
                    color=BLUE_E,
                    stroke_width=2,
                )
                for k in range(4)
            ])
            return VGroup(circle, spokes)

        wheel = always_redraw(make_wheel)

        # Bright dot on the rim.
        dot = Dot(point=dot_point(), radius=0.10, color=YELLOW)
        dot.set_sheen(0.4, UP)
        dot.add_updater(lambda m: m.move_to(dot_point()))

        # --- Glowing traced path -----------------------------------------
        # Two layered traces: a wide faint halo plus a thin bright core.
        glow = TracedPath(
            dot.get_center,
            stroke_color=YELLOW,
            stroke_width=14,
            stroke_opacity=0.25,
        )
        trace = TracedPath(
            dot.get_center,
            stroke_color=YELLOW,
            stroke_width=4,
            stroke_opacity=1.0,
        )

        # --- Animate ------------------------------------------------------
        self.play(Create(number_line), run_time=1.2)
        self.play(FadeIn(wheel, shift=DOWN * 0.3), FadeIn(dot), run_time=0.8)

        # Add traces just before rolling so the path starts clean.
        self.add(glow, trace)
        self.bring_to_front(dot)

        self.play(
            theta.animate.set_value(turns * TAU),
            run_time=7,
            rate_func=linear,
        )

        # Freeze the dot/wheel updaters so the final frame is static.
        dot.clear_updaters()
        self.wait(0.3)

        # --- Label --------------------------------------------------------
        label = Text("Cycloid", color="#FFE45E", weight=BOLD, font_size=48)
        label.move_to([0, line_y + 2 * r + 0.7, 0])
        self.play(FadeIn(label, shift=UP * 0.3), run_time=1.0)
        self.wait(1.5)
