"""godforge_intro.py - GODFORGE OS / MAN-MADE DEITY INDEX intro.

Restricted-archive boot for "The Great Abyss". Composites the Godforge asset
pack: dark green CRT terminal, grid, frame, scrolling code columns, boot text
typing line-by-line, the artificial-halo + deity-bust central icon, GODFORGE
title flicker, loading bar + status labels, and a CONTAINMENT FAILED glitch.

Render:
    manim -pqh --fps 30 scenes/godforge_intro.py GodforgeIntro
"""

import os
import random

import numpy as np
from manim import *

BG    = "#03100A"
GREEN = "#48F08A"
RED   = "#FF4D4D"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AD = os.path.join(BASE, "assets", "godforge", "Godforge_Intro_Assets")
AUDIO_DIR = os.path.join(BASE, "assets", "audio")


def snd(n):
    return os.path.join(AUDIO_DIR, n)


def img(rel):
    return ImageMobject(os.path.join(AD, rel))


def ff(rel):
    return img(rel).scale_to_fit_height(8.0)


def el(rel, w=None, h=None):
    m = img(rel)
    if h:
        m.scale_to_fit_height(h)
    if w:
        m.scale_to_fit_width(w)
    return m


class GodforgeIntro(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG
        random.seed(3)
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # ---- layers (built, added on cue) ----
        grid = ff("01_Backgrounds/bg_grid_soft.png").set_z_index(-10)
        frame = ff("02_UI_Frame/frame_full.png").set_z_index(6)
        bloom = ff("07_Effects/light_bloom.png").set_z_index(-4).set_opacity(0)
        header = el("06_Text_Overlays/header_labels.png", w=6.2).set_z_index(7)
        header.to_corner(UL).shift(RIGHT * 0.35 + DOWN * 0.3)
        footer = el("06_Text_Overlays/footer_labels.png", w=12.0).set_z_index(7).move_to([0, -3.5, 0])

        # scrolling code columns (two copies each for seamless wrap)
        def col(rel, x):
            H = 4.6
            a = el(rel, h=H).move_to([x, 0, 0])
            b = el(rel, h=H).move_to([x, H, 0])
            g = Group(a, b)
            st = {"o": 0.0}

            def upd(m, dt):
                st["o"] = (st["o"] + dt * 0.45) % H
                a.move_to([x, -H / 2 + st["o"], 0])
                b.move_to([x, -H / 2 + st["o"] - H, 0])
            g.add_updater(upd)
            return g.set_z_index(-3)
        colL = col("06_Text_Overlays/code_column_left.png", -6.45)
        colR = col("06_Text_Overlays/code_column_right.png", 6.45)

        # central icon (halo + bust)
        IY = 1.35
        halo = el("04_Icons/icon_artificial_halo.png", h=2.5).move_to([0, IY, 0]).set_z_index(2)
        bust = el("04_Icons/icon_deity_bust.png", h=1.7).move_to([0, IY - 0.05, 0]).set_z_index(3)

        # boot lines (cropped strips)
        boot = Group(*[el(f"06_Text_Overlays/boot_lines/line_{i}.png", w=5.6) for i in range(6)])
        for i, ln in enumerate(boot):
            ln.move_to([0, 0.95 - i * 0.42, 0]).set_z_index(4)

        # title + subtitle
        gtitle = el("03_Titles/godforge_title.png", w=7.4).move_to([0, -0.2, 0]).set_z_index(4)
        subtitle = el("03_Titles/man_made_deity_index.png", w=5.2).move_to([0, -1.25, 0]).set_z_index(4)

        # loading bar (their track + clean growing fill)
        bar_w = 6.6
        track = el("05_System_Elements/loading_bar_long_empty.png", w=bar_w).move_to([0, -1.95, 0]).set_z_index(4)
        bar_h = track.height
        fill = Rectangle(width=0.001, height=bar_h * 0.5, stroke_width=0, fill_color=GREEN, fill_opacity=0.9
                         ).move_to([track.get_left()[0], -1.95, 0]).set_z_index(5)

        # overlays (top)
        scan = ff("07_Effects/crt_scanlines.png").set_z_index(30).set_opacity(0.28)
        vign = ff("07_Effects/vignette_overlay.png").set_z_index(29).set_opacity(0.7)
        noise1 = ff("07_Effects/noise_overlay_01.png").set_z_index(31)
        noise2 = ff("07_Effects/noise_overlay_02.png").set_z_index(31)
        noise_amt = ValueTracker(0.30)

        def noise_upd(m):
            on = int(clock.get_value() * 12) % 2
            a = noise_amt.get_value()
            noise1.set_opacity(a if on == 0 else 0.0)
            noise2.set_opacity(a if on == 1 else 0.0)
        noise1.add_updater(noise_upd)

        # warning stamp + glitch strips (for the end)
        stamp = el("06_Text_Overlays/warning_stamp_containment_failed.png", w=6.0).move_to([0, 0, 0]).set_z_index(36).set_opacity(0)

        # =================================================================
        # 0:00-0:01  black + CRT noise
        # =================================================================
        self.add_sound(snd("crt_hum.wav"), gain=-12)
        self.add(noise1, noise2)
        self.add_sound(snd("boot.wav"), gain=-6)
        self.wait(1.0)

        # 0:01-0:02  UI frame + grid appear
        noise_amt.set_value(0.12)
        self.add(colL, colR)
        self.play(FadeIn(grid), FadeIn(frame), FadeIn(header), run_time=0.5)
        self.add(scan, vign)
        self.wait(0.4)

        # 0:02-0:04  boot text types line by line
        for i, ln in enumerate(boot):
            self.add_sound(snd("ui_step.wav"), gain=-10)
            self.play(FadeIn(ln, shift=RIGHT * 0.08), run_time=0.16)
            self.wait(0.14)

        # 0:04-0:06  halo + bust render in center
        self.play(boot.animate.shift(UP * 0.6).set_opacity(0), run_time=0.4)
        self.remove(boot)
        self.add_sound(snd("beam_on.wav"), gain=-9)
        self.add(bloom)
        self.play(bloom.animate.set_opacity(0.55), FadeIn(halo, scale=1.08), run_time=0.7)
        self.play(FadeIn(bust, scale=1.05), run_time=0.5)
        self.play(halo.animate.set_opacity(1.0), run_time=0.4)  # settle
        self.wait(0.2)

        # 0:06-0:08  GODFORGE title appears with flicker
        self.add_sound(snd("ui_lock.wav"), gain=-5)
        self.play(FadeIn(gtitle), run_time=0.35)
        for op, rt in [(0.35, 0.05), (1.0, 0.06), (0.55, 0.05), (1.0, 0.07)]:
            self.play(gtitle.animate.set_opacity(op), run_time=rt)
        self.play(FadeIn(subtitle, shift=UP * 0.06), run_time=0.4)
        self.wait(0.3)

        # 0:08-0:10  loading bar fills + status labels appear
        self.add(track, fill)
        self.add_sound(snd("riser.wav"), gain=-9)
        self.play(fill.animate.stretch_to_fit_width(bar_w * 0.78).move_to([track.get_left()[0] + bar_w * 0.78 / 2, -1.95, 0]),
                  run_time=1.3, rate_func=smooth)
        self.add_sound(snd("ui_tick.wav"), gain=-7)
        self.play(FadeIn(footer, shift=UP * 0.05), run_time=0.5)
        self.wait(0.3)

        # 0:10-0:12  CONTAINMENT FAILED glitch transition
        content = Group(halo, bust, gtitle, subtitle, track, fill, footer, header)
        self.add_sound(snd("boom.wav"), gain=-2)
        self.add_sound(snd("ui_unlock.wav"), gain=-3)
        gstrip = el("07_Effects/glitch_strip_01.png", w=14.3).set_z_index(33)
        gstrip2 = el("07_Effects/glitch_strip_02.png", w=14.3).set_z_index(33)
        # red flash + stamp slam
        red = Rectangle(width=15, height=8.5, stroke_width=0, fill_color=RED, fill_opacity=0).set_z_index(34)
        self.add(red, stamp)
        self.play(stamp.animate.set_opacity(1).scale(1.06), red.animate.set_fill(RED, opacity=0.18),
                  noise_amt.animate.set_value(0.35), run_time=0.18, rate_func=rush_from)
        # glitch jitter: flash strips at random y + jitter content
        for _ in range(5):
            yy = random.uniform(-2.5, 2.5)
            s = random.choice([gstrip, gstrip2]).copy().move_to([random.uniform(-0.5, 0.5), yy, 0])
            self.add(s)
            self.play(content.animate.shift(RIGHT * random.uniform(-0.18, 0.18)),
                      red.animate.set_fill(RED, opacity=random.uniform(0.05, 0.25)), run_time=0.06)
            self.remove(s)
        # cut to black
        black = Rectangle(width=15, height=8.5, stroke_width=0, fill_color="#000000", fill_opacity=0).set_z_index(45)
        self.add(black)
        self.play(black.animate.set_fill("#000000", opacity=1.0), run_time=0.25)
        self.wait(0.3)
