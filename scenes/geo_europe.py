"""geo_europe.py - build an accurate dotted-LED map of Europe from real data.

Uses Natural-Earth-style country polygons (GeoJSON) + shapely + a Mercator
projection to rasterize a high-resolution "LED" map: dark land fill, dim
coast/border lines, and a grid of bright LED dots on land.  No manim import, so
it is fast to test on its own:

    ./.venv/bin/python -c "import sys;sys.path.insert(0,'scenes');import geo_europe as g;print(g.build_europe_map())"

The same projection (LON/LAT window + `to_uv`) is shared with the scene so
markers placed by real lon/lat line up exactly with the rendered coastline.
"""

import json
import math
import os

# ---- geographic window (Mercator) -----------------------------------------
LON0, LON1 = -25.0, 40.0
LAT0, LAT1 = 34.0, 72.0


def merc(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def inv_merc(y):
    return math.degrees(2 * math.atan(math.exp(y)) - math.pi / 2)


MY0, MY1 = merc(LAT0), merc(LAT1)
ASPECT = math.radians(LON1 - LON0) / (MY1 - MY0)   # width / height


def to_uv(lon, lat):
    """lon/lat -> (u,v) in [0,1]x[0,1], v=0 at LAT0 (bottom), v=1 at LAT1 (top)."""
    return ((lon - LON0) / (LON1 - LON0), (merc(lat) - MY0) / (MY1 - MY0))


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(BASE, "assets", "cryptid")
GEOJSON = os.path.join(ASSET, "europe.geojson")
GEOJSON_URL = ("https://raw.githubusercontent.com/leakyMirror/map-of-europe/"
               "master/GeoJSON/europe.geojson")

# palette (RGB)
C_FILL   = (8, 16, 30)        # land fill, very dark blue
C_BORDER = (96, 156, 224)     # coast / country borders (bright, frames the land)
C_DOT    = (56, 102, 178)     # LED dots
C_DOT_HI = (120, 175, 255)

# curated major-country labels (name, lon, lat) - hand-placed for clean reading
COUNTRY_LABELS = [
    ("ICELAND", -19.0, 64.9), ("UNITED KINGDOM", -2.2, 53.2), ("IRELAND", -8.2, 53.3),
    ("FRANCE", 2.2, 47.2), ("SPAIN", -3.7, 40.2), ("PORTUGAL", -8.2, 39.6),
    ("GERMANY", 10.2, 51.1), ("ITALY", 12.6, 42.8), ("NORWAY", 9.0, 61.5),
    ("SWEDEN", 15.5, 62.5), ("FINLAND", 26.0, 64.0), ("POLAND", 19.4, 52.0),
    ("UKRAINE", 31.5, 49.3), ("GREECE", 22.2, 39.4), ("ROMANIA", 25.0, 45.9),
]

# famous European cryptids (name, tag, lon, lat) - real-ish locations
CRYPTIDS = [
    ("LOCH NESS MONSTER", "EU-01", -4.42, 57.32),   # Scotland
    ("BLACK SHUCK",       "EU-02",  1.30, 52.60),   # East Anglia
    ("THE KRAKEN",        "EU-03",  6.50, 64.50),   # Norwegian Sea
    ("BEAST OF GEVAUDAN", "EU-04",  3.50, 44.60),   # Lozere, France
    ("TATZELWURM",        "EU-05", 11.00, 47.30),   # the Alps
    ("WAWEL DRAGON",      "EU-06", 19.94, 50.05),   # Krakow, Poland
]


def _download(url, dest):
    import ssl
    import urllib.request
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    ctx = ssl.create_default_context()
    cab = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(cab):
        ctx.load_verify_locations(cab)
    handlers = [urllib.request.HTTPSHandler(context=ctx)]
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"https": proxy, "http": proxy}))
    op = urllib.request.build_opener(*handlers)
    with op.open(url, timeout=60) as r:
        open(dest, "wb").write(r.read())


def _load_features():
    if not os.path.exists(GEOJSON):
        os.makedirs(ASSET, exist_ok=True)
        _download(GEOJSON_URL, GEOJSON)
    return json.load(open(GEOJSON))["features"]


def build_europe_map(cols=128, cell=30):
    """Rasterize the LED Europe map.  Returns the PNG path (cached)."""
    rows = round(cols / ASPECT)
    out = os.path.join(ASSET, f"europe_real_{cols}x{rows}_{cell}.png")
    if os.path.exists(out):
        return out

    from PIL import Image, ImageDraw
    from shapely.geometry import shape
    from shapely.ops import unary_union
    from shapely.prepared import prep

    feats = _load_features()
    geom = unary_union([shape(f["geometry"]) for f in feats])
    pg = prep(geom)

    W, H = cols * cell, rows * cell
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    def px(lon, lat):
        u, v = to_uv(lon, lat)
        return (u * W, (1 - v) * H)

    # 1) dark land fill (rough, for body) -- exterior rings only
    def rings(g):
        if g["type"] == "Polygon":
            return [g["coordinates"][0]]
        if g["type"] == "MultiPolygon":
            return [poly[0] for poly in g["coordinates"]]
        return []
    for f in feats:
        for ring in rings(f["geometry"]):
            pts = [px(lon, lat) for lon, lat in ring]
            d.polygon(pts, fill=C_FILL)

    # 2) LED dots on land (grid uniform in projected space)
    sq = cell * 0.56
    for c in range(cols):
        u = (c + 0.5) / cols
        lon = LON0 + u * (LON1 - LON0)
        for r in range(rows):
            v = 1 - (r + 0.5) / rows
            lat = inv_merc(MY0 + v * (MY1 - MY0))
            if not pg.contains(_pt(lon, lat)):
                continue
            cx, cy = (c + 0.5) * cell, (r + 0.5) * cell
            b = 0.78 + 0.22 * (((c * 13 + r * 7) % 11) / 11)
            col = (int(C_DOT[0] * b), int(C_DOT[1] * b), int(C_DOT[2] * b), 255)
            d.rectangle([cx - sq / 2, cy - sq / 2, cx + sq / 2, cy + sq / 2], fill=col)

    # 3) coast / country borders drawn ON TOP so they frame the land crisply
    def all_rings(g):
        if g["type"] == "Polygon":
            return list(g["coordinates"])
        if g["type"] == "MultiPolygon":
            return [r for poly in g["coordinates"] for r in poly]
        return []
    for f in feats:
        for ring in all_rings(f["geometry"]):
            pts = [px(lon, lat) for lon, lat in ring]
            if len(pts) > 1:
                d.line(pts, fill=C_BORDER, width=3, joint="curve")

    img.save(out)
    return out


# tiny shapely Point cache helper (avoids importing at module top)
def _pt(lon, lat):
    from shapely.geometry import Point
    return Point(lon, lat)
