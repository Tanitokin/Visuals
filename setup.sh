#!/usr/bin/env bash
# Idempotent environment setup for the Manim CRT-terminal repo.
# Installs: system libs (cairo/pango/ffmpeg), a ./.venv with Manim, and the
# project fonts into the user font dir. Safe to run repeatedly.
set -uo pipefail
cd "$(dirname "$0")"

# 1) System libraries (only if ffmpeg is missing) -------------------------
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[setup] installing system libs (cairo/pango/ffmpeg)..."
  sudo apt-get update -qq || true
  sudo apt-get install -y -qq \
    libcairo2-dev libpango1.0-dev pkg-config ffmpeg build-essential python3-dev || true
fi

# 2) Python venv + Manim (only if missing) --------------------------------
if [ ! -x .venv/bin/manim ]; then
  echo "[setup] creating .venv and installing Manim..."
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip setuptools wheel
  ./.venv/bin/pip install -q manim
fi

# 2b) extra deps for the accurate Europe map builder (geo_europe.py) ------
if [ -x .venv/bin/python ]; then
  ./.venv/bin/python -c "import shapely" 2>/dev/null || ./.venv/bin/pip install -q shapely
fi

# 3) Fonts (cheap; needed in every fresh container) -----------------------
echo "[setup] installing fonts..."
mkdir -p "$HOME/.local/share/fonts"
cp -f assets/fonts/*.ttf "$HOME/.local/share/fonts/" 2>/dev/null || true
cp -f assets/fonts/*.otf "$HOME/.local/share/fonts/" 2>/dev/null || true
fc-cache -f "$HOME/.local/share/fonts" >/dev/null 2>&1 || true

echo "[setup] done. Render with: ./.venv/bin/manim -pqh --fps 30 scenes/boot.py WorstCitiesBoot"
