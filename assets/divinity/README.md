# Divinity entity images

These 10 images fill the cards in `scenes/divinity_index.py`
(**ARTIFICIAL DIVINITY INDEX**).

## How to add your own gods

Drop your 10 images here, named exactly:

```
entity_01.png   entity_02.png   ...   entity_10.png
```

(`.jpg` also works — the scene globs `entity_NN.*`.)

- **Any aspect ratio is fine.** Each image is automatically centre-cropped to
  the card's 4:3 slot at render time, so it fills the card with no letterboxing.
- Card order on screen = file number. `entity_01` is the first card (top-left),
  `entity_10` is the last (bottom-right). Selection runs 01 → 10.
- The files shipped here now are **placeholders** ("AWAITING IMAGE"). Overwrite
  them with your real art and re-render.

## Names + short info per god (the lower "SELECT SUBJECT" panel)

Edit the `ENTITIES` list at the top of `scenes/divinity_index.py`:

```python
ENTITIES = [
    {"label": "ENTITY 01", "name": "AM", "info": "A machine god that kept five humans alive only to torture them."},
    ...
]
```

- `name` → shown next to the entity number:  `ENTITY 01 // AM`
- `info` → the short description line under it.
- Leave `name` / `info` as `""` to fall back to the default
  `ENTITY 01 // DOSSIER READY` line.

Then re-render:

```bash
./.venv/bin/manim -pqh --fps 30 scenes/divinity_index.py DivinityIndex
```
