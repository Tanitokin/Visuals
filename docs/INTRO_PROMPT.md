# Reusable intro prompt — "Classified Anomaly Archive → {LOCATION}"

Swap `{LOCATION}` (and optionally the scanned list + iceberg layers) to generate
the same intro for any episode. Two forms below: a **cinematic prompt** (for AI
video tools or as a creative brief) and a **build prompt** (to generate the
Manim version like `scenes/yellowstone_intro.py`).

---

## 1) Cinematic prompt (parameterized)

> A cinematic intro in the style of a **classified intelligence-agency
> terminal** ("GLOBAL ANOMALY ARCHIVE"), dark documentary aesthetic. ~15–20s.
>
> **Beat 1 — Scan.** The interface rapidly scans a long index of remote world
> locations (Himalayas, Amazon, Australia, Pacific islands, Japan, Antarctica,
> Alaska, Siberia, Mariana Trench, …). Case windows flash open and closed:
> redacted files, cryptid silhouettes, coordinates, surveillance frames. A live
> REC timecode, a scanning sweep and ticking counters make it feel alive.
>
> **Beat 2 — Lock.** The system flags one entry: a red "ANOMALY DETECTED", a
> targeting reticle snaps onto **{LOCATION}** (status: ENCRYPTED) and everything
> else dims and falls into the background.
>
> **Beat 3 — Decrypt.** An "ENCRYPTED ARCHIVE // {LOCATION}" panel opens. Hex
> streams scramble, authentication layers tick to OK/BYPASSED, a progress bar
> climbs to 100% as tension rises — then "ARCHIVE UNLOCKED" with an impact and a
> flash.
>
> **Beat 4 — Iceberg.** The archive opens into a vast iceberg of information. The
> camera slowly descends through strata of cases — each layer darker and more
> redacted than the last (surface incidents → classified → corrupted → depth
> unknown) — ending staring into the dark abyss of undiscovered mysteries.
>
> **Style:** dark, classified, unsettling, professional. **Palette:** black,
> charcoal grey, white, subtle amber highlights, occasional red warnings.
> **Typography:** technical monospace UI + bold title. Subtle glitch, scanlines,
> volumetric fog, smooth eased camera, glow on the selected entry. No logos, no
> text beyond interface elements, no cartoon style.

**To customize per episode:** change `{LOCATION}`; optionally edit the scanned
index and the iceberg layer labels (e.g. for {LOCATION}: surface incidents,
disappearances, restricted zones, [REDACTED], classified, corrupted, depth
unknown).

---

## 2) Build prompt (for the Manim template in this repo)

> Using `scenes/yellowstone_intro.py` as the template, generate the same
> classified-archive intro for **{LOCATION}**. Keep the 4 beats (scan → lock →
> decrypt → iceberg descent), the dark palette (black/charcoal/white + amber +
> red), the live elements (REC, scan sweep, counters, glowing selected row,
> reticle), and the sound design (drone, scan blips, decrypt riser, unlock boom).
> Set `TARGET` to {LOCATION}'s index, and rewrite the `BERG` iceberg layers with
> {LOCATION}-specific cases. Render 1080p30. Duration ~17–19s.

---

## Notes

- This is realized as **2.5D motion graphics in Manim** (vector UI + eased
  camera), not photoreal 3D. For true 3D/volumetric (Netflix-style) you'd render
  plates in Blender and composite — see `docs/MCP.md`.
- Reuse helpers/look via `scenes/crt_style.py` and the assets in `assets/`.
