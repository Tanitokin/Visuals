---
name: geo-led-map
description: Build accurate dotted-LED maps (any country/continent/region) from real geography for Manim CRT scenes. Use when a scene needs a recognizable real map — coastlines, borders — instead of hand-drawn shapes, and needs to place markers at real lon/lat that line up with the map.
---

# Accurate LED maps from real geography

Hand-drawing continents with ellipses looks cheap. Instead, rasterize **real
country polygons** into the LED-dot style. The reference implementation is
`scenes/geo_europe.py` (Europe) used by `scenes/cryptid_registry.py`.

## Pipeline

1. **Data** — fetch a GeoJSON of country polygons (public domain, Natural Earth).
   Cache it under `assets/<scene>/`. Sources that work behind the agent proxy:
   - Europe only: `https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson`
   - World (filter by `properties.CONTINENT` / name): the `nvkelso/natural-earth-vector` repo, e.g. `geojson/ne_50m_admin_0_countries.geojson`.
   Download with `curl` (proxy env is already set) or the `urllib` + `ProxyHandler`
   + `/root/.ccr/ca-bundle.crt` helper in `geo_europe._download`.

2. **Geometry** — `shapely` (`pip install shapely`; it's in `setup.sh`):
   ```python
   geom = shapely.ops.unary_union([shape(f["geometry"]) for f in feats])
   pg = shapely.prepared.prep(geom)          # fast point-in-polygon
   ```

3. **Projection** — Mercator keeps shapes natural (don't use raw equirectangular,
   it stretches). Pick a lon/lat window, expose a single `to_uv(lon,lat) -> (u,v)`
   in `[0,1]²` and its inverse. **The scene imports the SAME `to_uv`** so markers
   placed by real lon/lat land exactly on the rendered coastline.
   ```python
   merc   = lambda lat: math.log(math.tan(math.pi/4 + math.radians(lat)/2))
   inv    = lambda y:   math.degrees(2*math.atan(math.exp(y)) - math.pi/2)
   ```

4. **Rasterize** to a high-res PNG (PIL), drawing in this order so the coast pops:
   - dark land **fill** (exterior rings) — gives body between dots,
   - **LED dots** on a grid *uniform in projected space* (invert each cell to
     lon/lat, test `pg.contains(Point(lon,lat))`),
   - **coast/border lines** (all rings) drawn LAST, bright, so they frame the land.
   Render big (cell≈30px → ~3.8k px wide) so it stays crisp after the 4K→1080p
   downscale. Cache by `cols×rows×cell` in the filename.

5. **Scene placement** — `ImageMobject(png).stretch_to_fit_width(MAPW)
   .stretch_to_fit_height(MAPH)`. Derive `MAPW = MAPH * iw/ih` from the PNG so the
   map isn't distorted. `to_screen(lon,lat)` = map `to_uv` into the MAPW×MAPH rect.

## Gotchas

- Generated PNG + the `.geojson` are committed so renders don't need network/shapely;
  `build_*` only runs when the PNG is missing. Keep the shapely import lazy (inside
  the build fn) so cached renders work without it.
- A uniform lon/lat grid projected to Mercator bunches dots toward the top — grid
  in **projected** space and invert, so dots are evenly spaced on screen.
- Markers/labels are vector mobjects on top; never bake them into the PNG (you want
  them animatable and crisp from the 4K render).

## Finishing (shared with the other archive scenes)

Render `-qk --fps 60`, then bloom + downscale to 1080p (keeps small text sharp):
```
ffmpeg -i <raw4k> -t <len> -filter_complex \
 "[0:v]format=gbrp,split=2[a][b];[b]gblur=sigma=18[bl];\
  [a][bl]blend=all_mode=screen:all_opacity=0.38[o];\
  [o]scale=1920:1080:flags=lanczos,unsharp=5:5:0.8:5:5:0.0,eq=contrast=1.06:saturation=1.16,format=yuv420p[v]" \
 -map "[v]" -map 0:a -af "afade=t=out:st=<len-0.4>:d=0.35" \
 -r 60 -c:v libx264 -crf 12 -pix_fmt yuv420p -c:a aac -b:a 192k <final>
```
`format=gbrp` BEFORE the blend is mandatory — screen-blending in YUV greys the
whole frame (chroma sits at 128). With it, pure black stays `(0,0,0)`.
