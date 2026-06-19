"""divinity_index.py - ARTIFICIAL DIVINITY INDEX // character-select screen.

A premium, dark VHS/CRT "forbidden archive" interface for The Great Abyss video
"The Most Horrifying Man-Made Gods in Fiction". A 2x5 grid of 10 entity cards;
the selector steps 01 -> 10 (top row L->R, then bottom). The selected subject
shows in colour with its name and a blinking videogame-style frame, while the
others stay locked in black-and-white. Rhythm per subject: revealed ~4s ->
a "click" -> fade to black -> next. A lower panel shows each subject's name.

Title font: Halo. Body font: VCR OSD Mono. CRT overlays + SFX from assets/.

Entity images: assets/divinity/entity_01.png ... entity_10.png  (drop your own;
any aspect - they are centre-cropped to the card. Placeholders ship by default).

Render:
    ./.venv/bin/manim -pqh --fps 30 scenes/divinity_index.py DivinityIndex
"""

import os
import sys

import numpy as np
from manim import *
from PIL import Image as PILImage, ImageOps, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crt_style import (BG, GREEN, GREEN_BRT, GREEN_DIM, RED, BORDER,
                       PANEL_FILL, COVER_FILL, left, right, neon, snd)

# --- Fonts ----------------------------------------------------------------
FONT_TITLE = "Halo"
FONT_BODY = "VCR OSD Mono"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIV_DIR = os.path.join(BASE, "assets", "divinity")
GF = os.path.join(BASE, "assets", "godforge", "Godforge_Intro_Assets")
CROP_DIR = os.path.join(BASE, "media", "_crops")
SCALE_DIR = os.path.join(BASE, "media", "_scaled")
os.makedirs(CROP_DIR, exist_ok=True)
os.makedirs(SCALE_DIR, exist_ok=True)


def gf(rel, target_w=1920):
    """ImageMobject for a godforge asset, pre-downscaled + cached so Manim
    isn't resampling a 4K source every frame (huge render-time win)."""
    src = os.path.join(GF, rel)
    out = os.path.join(SCALE_DIR, rel.replace("/", "_") + f".{target_w}.png")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        im = PILImage.open(src)
        if im.width > target_w:
            im = im.resize((target_w, round(im.height * target_w / im.width)), PILImage.LANCZOS)
        im.save(out)
    return ImageMobject(out)

# =========================================================================
# Entity data.  Fill in `name` and `info` per subject when you have them;
# leave them "" to show the default  ENTITY NN // DOSSIER READY  line.
# =========================================================================
ENTITIES = [
    {"label": "ENTITY 01", "name": "MOTHER BRAIN",        "info": "METROID"},
    {"label": "ENTITY 02", "name": "SAMARITAN",           "info": "PERSON OF INTEREST"},
    {"label": "ENTITY 03", "name": "AM",                  "info": "I HAVE NO MOUTH, AND I MUST SCREAM"},
    {"label": "ENTITY 04", "name": "THE WAU",             "info": "SOMA"},
    {"label": "ENTITY 05", "name": "FATHER",              "info": "FULLMETAL ALCHEMIST"},
    {"label": "ENTITY 06", "name": "DEUS",                "info": "XENOGEARS"},
    {"label": "ENTITY 07", "name": "THE NUMIDIUM",        "info": "THE ELDER SCROLLS"},
    {"label": "ENTITY 08", "name": "THE HEALING CHURCH",  "info": "ATTEMPT TO BIRTH GREAT ONES // BLOODBORNE"},
    {"label": "ENTITY 09", "name": "HUMAN INSTRUMENTALITY", "info": "PROJECT LILITH-REI // EVANGELION"},
    {"label": "ENTITY 10", "name": "THE EMPEROR OF MANKIND", "info": "WARHAMMER 40,000"},
]

# --- Grid / layout geometry (Manim frame is 14.222 x 8) -------------------
COLS, ROWS = 5, 2
CARD_W, CARD_H = 2.36, 2.06
GAP_X, GAP_Y = 0.30, 0.30
PAD = 0.085                       # inner padding of a card
IMG_W = CARD_W - 2 * PAD          # image slot width
IMG_H = IMG_W * 3 / 4             # 4:3 image slot
LABEL_H = CARD_H - 2 * PAD - IMG_H - 0.05
GRID_CY = 0.05                    # vertical centre of the grid

STEP_X = CARD_W + GAP_X
STEP_Y = CARD_H + GAP_Y
COL_X = [(-(COLS - 1) / 2 + c) * STEP_X for c in range(COLS)]
ROW_Y = [GRID_CY + (ROWS - 1) / 2 * STEP_Y - r * STEP_Y for r in range(ROWS)]

VIEW = 3.0        # seconds the subject is held (after fading back in) before the next
FADE = 0.5        # smooth fade-to-black duration


def card_center(i):
    return COL_X[i % COLS], ROW_Y[i // COLS]


def cover_crop(path, aspect, key):
    """Centre-crop to `aspect` (w/h); cache a colour and a desaturated
    ('locked') greyscale version. Returns (color_path, gray_path)."""
    color_out = os.path.join(CROP_DIR, f"{key}.png")
    gray_out = os.path.join(CROP_DIR, f"{key}_bw.png")
    try:
        im = PILImage.open(path).convert("RGB")
    except Exception:
        return path, path
    w, h = im.size
    if w / h > aspect:                       # too wide -> crop sides
        nw = int(h * aspect)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:                                    # too tall -> crop top/bottom
        nh = int(w / aspect)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    if im.width > 384:                        # downscale so Manim isn't
        im = im.resize((384, round(im.height * 384 / im.width)), PILImage.LANCZOS)
    im.save(color_out)
    g = ImageOps.grayscale(im).convert("RGB")        # locked = greyscale ...
    g = ImageEnhance.Brightness(g).enhance(0.82)      # ... slightly dimmed
    g.save(gray_out)
    return color_out, gray_out


class DivinityIndex(Scene):
    def construct(self):
        self.camera.background_color = BG
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        self.clock = clock

        def T(s, size, color=GREEN, font=FONT_BODY):
            return Text(s, font=font, font_size=size, color=color)

        def blink(period=0.7, duty=0.6):
            return (clock.get_value() % period) < period * duty

        # =================================================================
        # BACKGROUND + FRAME + CHROME
        # =================================================================
        frame = gf("02_UI_Frame/frame_full.png", 1280).scale_to_fit_height(7.74)
        frame.set_z_index(6)

        # Title (Halo), centred, with a soft pulsing glow
        title = Text("ARTIFICIAL DIVINITY INDEX", font=FONT_TITLE, color=GREEN_BRT)
        title.scale_to_fit_width(9.9).move_to([0, 3.16, 0]).set_z_index(7)
        title_glow = title.copy().set_color(GREEN).set_z_index(6).scale(1.05)
        title_glow.add_updater(lambda m: m.set_opacity(
            0.16 + 0.12 * (0.5 + 0.5 * np.sin(clock.get_value() * 2.3))))

        # =================================================================
        # CARDS
        # =================================================================
        cards = []          # dict per card with all handles
        for i, e in enumerate(ENTITIES):
            cx, cy = card_center(i)
            img_cy = cy + CARD_H / 2 - PAD - IMG_H / 2
            lbl_cy = cy - CARD_H / 2 + PAD + LABEL_H / 2

            bg = Rectangle(width=CARD_W, height=CARD_H, stroke_color=BORDER,
                           stroke_width=1.4, fill_color=PANEL_FILL, fill_opacity=0.55
                           ).move_to([cx, cy, 0]).set_z_index(0)
            slotbg = Rectangle(width=IMG_W, height=IMG_H, stroke_width=0,
                               fill_color=COVER_FILL, fill_opacity=1
                               ).move_to([cx, img_cy, 0]).set_z_index(0)

            src = os.path.join(DIV_DIR, f"entity_{i+1:02d}.png")
            color_path = None
            if os.path.exists(src):
                color_path, gray_path = cover_crop(src, IMG_W / IMG_H, f"entity_{i+1:02d}")
                img = ImageMobject(gray_path).scale_to_fit_width(IMG_W)   # locked = b/w
                if img.height > IMG_H + 1e-3:
                    img.scale_to_fit_height(IMG_H)
                img.move_to([cx, img_cy, 0]).set_z_index(1)
            else:
                img = T("NO SIGNAL", 16, GREEN_DIM).move_to([cx, img_cy, 0]).set_z_index(1)

            veil = Rectangle(width=IMG_W, height=IMG_H, stroke_width=0,
                             fill_color=BG, fill_opacity=0.40       # locked dim
                             ).move_to([cx, img_cy, 0]).set_z_index(2)

            num = left(T(f"{i+1:02d}", 22, GREEN_BRT),
                       cx - CARD_W / 2 + 0.14, img_cy + IMG_H / 2 - 0.2).set_z_index(4)
            lbl = T(f"ENTITY {i+1:02d}", 19, GREEN).move_to([cx, lbl_cy, 0]).set_z_index(4)

            cards.append(dict(i=i, cx=cx, cy=cy, img_cy=img_cy,
                              bg=bg, slotbg=slotbg, img=img, veil=veil,
                              num=num, lbl=lbl, color_path=color_path,
                              color_img=None, name_lbl=None))

        # =================================================================
        # SELECTION CURSOR  (moves card-to-card; pulses via updater)
        # =================================================================
        sel = {"i": 0, "t0": 0.0, "cx": cards[0]["cx"], "cy": cards[0]["cy"]}

        border = Rectangle(width=CARD_W + 0.05, height=CARD_H + 0.05,
                           stroke_color=GREEN_BRT, stroke_width=2.5, fill_opacity=0
                           ).set_z_index(8)
        glow = Rectangle(width=CARD_W + 0.05, height=CARD_H + 0.05,
                         stroke_color=GREEN, stroke_width=10, fill_opacity=0
                         ).set_z_index(7)
        # corner brackets that hug the card corners pointing inward ("locked")
        ticks = VGroup()
        for _ in range(8):
            ticks.add(Line(ORIGIN, ORIGIN, color=GREEN_BRT, stroke_width=4))
        ticks.set_z_index(8)

        def place_cursor(cx, cy):
            border.move_to([cx, cy, 0])
            glow.move_to([cx, cy, 0])
            hw, hh, L = (CARD_W + 0.05) / 2, (CARD_H + 0.05) / 2, 0.30
            corners = [(-hw, hh), (hw, hh), (-hw, -hh), (hw, -hh)]
            k = 0
            for (dx, dy) in corners:
                ox, oy = cx + dx, cy + dy
                sx = 1 if dx < 0 else -1          # point inward along the edge
                sy = -1 if dy > 0 else 1
                ticks[k].put_start_and_end_on([ox, oy, 0], [ox + sx * L, oy, 0]); k += 1
                ticks[k].put_start_and_end_on([ox, oy, 0], [ox, oy + sy * L, 0]); k += 1

        place_cursor(cards[0]["cx"], cards[0]["cy"])

        def cursor_blink(m):
            # hard on/off blink, like a videogame character-select frame
            on = (clock.get_value() % 0.46) < 0.46 * 0.58
            border.set_stroke(GREEN_BRT, 2.8, 1.0 if on else 0.12)
            glow.set_stroke(GREEN, 11, 0.34 if on else 0.05)
            ticks.set_stroke(GREEN_BRT, 4.2, 1.0 if on else 0.14)
        border.add_updater(cursor_blink)

        def make_color(card):
            """Full-colour version of a card's image (shown only when active)."""
            ci = ImageMobject(card["color_path"]).scale_to_fit_width(IMG_W)
            if ci.height > IMG_H + 1e-3:
                ci.scale_to_fit_height(IMG_H)
            return ci.move_to([card["cx"], card["img_cy"], 0]).scale(1.02).set_z_index(3)

        def select(card):
            """Reveal colour, lift veil, and swap label ENTITY NN -> god name."""
            card["veil"].set_opacity(0.0)
            if card["color_path"]:
                ci = make_color(card)
                card["color_img"] = ci
                self.add(ci)
            nm = ENTITIES[card["i"]]["name"]
            if nm:
                card["lbl"].set_opacity(0.0)
                nl = T(nm, 18, GREEN_BRT)
                if nl.width > CARD_W - 0.16:
                    nl.scale_to_fit_width(CARD_W - 0.16)
                nl.move_to(card["lbl"].get_center()).set_z_index(4)
                card["name_lbl"] = nl
                self.add(nl)

        def deselect(card):
            """Return a card to its locked black-and-white state (ENTITY NN)."""
            card["veil"].set_opacity(0.40)
            if card["color_img"] is not None:
                self.remove(card["color_img"])
                card["color_img"] = None
            if card["name_lbl"] is not None:
                self.remove(card["name_lbl"])
                card["name_lbl"] = None
            card["lbl"].set_opacity(1.0)

        # faint thin scanline easing down the active card's image
        sweep = Rectangle(width=IMG_W, height=0.02, stroke_width=0,
                          fill_color=GREEN_BRT, fill_opacity=0.0).set_z_index(3)

        def sweep_upd(m):
            top = sel["cy"] + CARD_H / 2 - PAD
            phase = ((clock.get_value() - sel["t0"]) * 0.7) % 1.0
            m.move_to([sel["cx"], top - phase * IMG_H, 0])
            m.set_fill(GREEN_BRT, 0.10 * np.sin(phase * np.pi))
        sweep.add_updater(sweep_upd)

        # =================================================================
        # LOWER PANEL  (rebuilt per selection)
        # =================================================================
        panel = RoundedRectangle(width=9.4, height=0.86, corner_radius=0.05,
                                 stroke_color=BORDER, stroke_width=1.5,
                                 fill_color=PANEL_FILL, fill_opacity=0.62
                                 ).move_to([0, -2.94, 0]).set_z_index(4)
        panel_glow = panel.copy().set_stroke(GREEN, 5, 0.08).set_fill(opacity=0).set_z_index(3)
        play = Triangle(color=GREEN_BRT, fill_color=GREEN_BRT, fill_opacity=1
                        ).scale(0.15).rotate(-90 * DEGREES)
        play.move_to([-4.32, -2.96, 0]).set_z_index(5)
        sel_label = left(T("// SELECT SUBJECT", 15, GREEN_DIM), -4.0, -2.70).set_z_index(5)

        def build_panel_text(i):
            e = ENTITIES[i]
            g = VGroup()
            if e["name"]:
                main = left(T(f"{e['label']}  //  {e['name']}", 22, GREEN_BRT), -4.0, -2.96)
                if main.width > 7.8:
                    main.scale_to_fit_width(7.8)
                    left(main, -4.0, -2.96)
            else:
                main = VGroup(
                    T(f"{e['label']} ", 22, GREEN_BRT),
                    T("// DOSSIER READY", 22, GREEN),
                ).arrange(RIGHT, buff=0.1)
                left(main, -4.0, -2.96)
            g.add(main.set_z_index(5))
            info = e["info"] or "Dossier decrypted // awaiting classification."
            inf = left(T(info, 15, GREEN_DIM), -4.0, -3.20)
            if inf.width > 8.4:
                inf.scale_to_fit_width(8.4)
                left(inf, -4.0, -3.20)
            g.add(inf.set_z_index(5))
            # blinking cursor after the main line
            cur = Rectangle(width=0.12, height=0.24, stroke_width=0,
                            fill_color=GREEN, fill_opacity=1).set_z_index(5)
            cur.next_to(main, RIGHT, buff=0.1)
            cur.add_updater(lambda m: m.set_opacity(1.0 if blink(0.55) else 0.0))
            g.add(cur)
            return g

        # =================================================================
        # BOTTOM NAV HINT + clock + REC
        # =================================================================
        nav = left(T("<>  NAVIGATE      [ENTER] SELECT      [ESC] BACK", 15, GREEN_DIM),
                   -6.6, -3.60).set_z_index(7)
        clk = right(T("22:17:09", 15, GREEN_DIM), 5.95, -3.60).set_z_index(7)
        rec_t = right(T("REC", 15, RED), 6.62, -3.60).set_z_index(7)
        rec_dot = Dot([6.78, -3.595, 0], radius=0.055, color=RED).set_z_index(7)
        rec_dot.add_updater(lambda m: m.set_opacity(1.0 if blink(0.9, 0.55) else 0.15))

        # =================================================================
        # CRT OVERLAYS  (top)
        # =================================================================
        scan = gf("07_Effects/crt_scanlines.png").scale_to_fit_height(8.0).set_z_index(30).set_opacity(0.22)
        vign = gf("07_Effects/vignette_overlay.png", 768).scale_to_fit_height(8.0).set_z_index(29).set_opacity(0.75)
        noise1 = gf("07_Effects/noise_overlay_01.png", 512).scale_to_fit_height(8.0).set_z_index(31)
        noise2 = gf("07_Effects/noise_overlay_02.png", 512).scale_to_fit_height(8.0).set_z_index(31)
        NOISE = 0.06

        def noise_upd(m):
            on = int(clock.get_value() * 11) % 2
            noise1.set_opacity(NOISE if on == 0 else 0.0)
            noise2.set_opacity(NOISE if on == 1 else 0.0)
        noise1.add_updater(noise_upd)

        # drifting glow band + global flicker (subtle)
        drift = Rectangle(width=15, height=0.8, stroke_width=0, fill_color=GREEN,
                          fill_opacity=0.04).set_z_index(13)
        drift.add_updater(lambda m: m.move_to([0, 4.2 - ((clock.get_value() * 1.5) % 8.4), 0]))
        flick = Rectangle(width=15, height=8.6, stroke_width=0, fill_color=BG,
                          fill_opacity=0.0).set_z_index(33)

        def flick_upd(m):
            t = clock.get_value()
            base = 0.015 + 0.02 * (0.5 + 0.5 * np.sin(t * 6.0))
            spike = 0.05 if (np.sin(t * 41.0) > 0.94) else 0.0
            m.set_opacity(base + spike)
        flick.add_updater(flick_upd)

        # =================================================================
        # SEQUENCE
        # =================================================================
        self.add_sound(snd("crt_hum.wav"), gain=-14)
        self.add_sound(snd("dark_drone.wav"), gain=-19)

        # chrome appears immediately, then cards load in fast (~1s)
        self.add(frame, vign, scan, drift, flick, noise1, noise2)
        self.add(title_glow, title, nav, clk, rec_t, rec_dot)
        self.add(panel_glow, panel, play, sel_label)

        self.add_sound(snd("es_loading_slow.wav"), gain=-11)
        card_groups = [Group(c["bg"], c["slotbg"], c["img"], c["veil"], c["num"], c["lbl"])
                       for c in cards]
        # quick scanline pass during the card load
        load_band = Rectangle(width=14.6, height=0.5, stroke_width=0, fill_color=GREEN,
                              fill_opacity=0.0).move_to([0, 4.3, 0]).set_z_index(20)
        self.add(load_band)
        self.play(
            LaggedStart(*[FadeIn(g, shift=UP * 0.05) for g in card_groups], lag_ratio=0.05),
            load_band.animate(rate_func=linear).set_opacity(0.10).move_to([0, -4.3, 0]),
            run_time=0.95,
        )
        self.remove(load_band)
        # short title flicker on settle
        for op, rt in [(0.45, 0.05), (1.0, 0.06), (0.7, 0.05), (1.0, 0.06)]:
            self.play(title.animate.set_opacity(op), run_time=rt)

        # cursor + sweep + the smooth fade-to-black overlay
        self.add(glow, border, ticks, sweep)
        blk = Rectangle(width=15, height=8.6, stroke_width=0, fill_color="#000000",
                        fill_opacity=0.0).set_z_index(44)
        self.add(blk)

        def fade_to_black():
            self.play(blk.animate.set_fill("#000000", 1.0), run_time=FADE, rate_func=smooth)

        def fade_back():
            self.play(blk.animate.set_fill("#000000", 0.0), run_time=FADE, rate_func=smooth)

        def cycle(card):
            # subject shown -> select click -> fade to black -> back with the SAME
            # one selected -> hold 3s.  (Then the caller passes to the next.)
            self.add_sound(snd("es_select_ok.wav"), gain=-9)
            self.flash_card(card)
            fade_to_black()
            fade_back()
            self.wait(VIEW)

        # ENTITY 01 (revealed by the card load above)
        panel_txt = build_panel_text(0)
        self.add(panel_txt)
        sel["i"], sel["cx"], sel["cy"], sel["t0"] = 0, cards[0]["cx"], cards[0]["cy"], clock.get_value()
        select(cards[0])
        cycle(cards[0])

        for i in range(1, len(cards)):
            prev, cur = cards[i - 1], cards[i]
            # pass to the next subject (cursor jumps, it lights up in colour)
            deselect(prev)
            old_txt = panel_txt
            panel_txt = build_panel_text(i)
            self.remove(old_txt)
            place_cursor(cur["cx"], cur["cy"])
            sel["i"], sel["cx"], sel["cy"], sel["t0"] = i, cur["cx"], cur["cy"], clock.get_value()
            select(cur)
            self.add(panel_txt)
            cycle(cur)

        # ending: fade out and hold on black
        self.add_sound(snd("es_disconnect.wav"), gain=-6)
        fade_to_black()
        self.wait(0.6)

    # ---------------------------------------------------------------------
    def flash_card(self, card):
        """2-3 frame green/white flash on a card."""
        fl = Rectangle(width=CARD_W + 0.06, height=CARD_H + 0.06, stroke_width=0,
                       fill_color=GREEN_BRT, fill_opacity=0.0
                       ).move_to([card["cx"], card["cy"], 0]).set_z_index(9)
        self.add(fl)
        self.play(fl.animate.set_fill(GREEN_BRT, 0.55), run_time=1 / 30, rate_func=linear)
        self.play(fl.animate.set_fill(GREEN, 0.0), run_time=2 / 30, rate_func=linear)
        self.remove(fl)
