# Tooling / MCP recommendations — leveling up the visuals

Manim (what we use now) is excellent for precise 2D/2.5D motion graphics: HUDs,
terminals, animated typography, charts, diagrams. It is **not** built for
photoreal 3D, volumetric fog, realistic lighting, or "Netflix documentary"
footage. To get that look, the biggest levers are:

1. **Real 3D** (icebergs, terrain, volumetric fog, cinematic camera/lighting)
2. **Professional sound** (SFX, ambience, music, narration)
3. **AI image / video generation** (location plates, cryptid art, textures,
   document scans, thumbnails, short cinematic clips)

Below: what to add, in priority order, and how it fits this repo.

---

## 1. 3D — Blender  ★ biggest visual jump

Real 3D scenes (iceberg descent, terrain flyovers, volumetric god-rays, depth
of field) rendered in EEVEE/Cycles. Two ways to use it:

- **Headless Blender in this environment (recommended here).** Blender is free
  and installable (`apt-get install blender`). I write Blender **Python scripts**
  and render with `blender -b -P scene.py`. No MCP, no API key, works in the web
  container. This is the most powerful option I can drive directly.
- **Blender MCP** (`blender-mcp`) — lets me control a running Blender on *your*
  desktop interactively. Great with Claude Code **desktop**, but needs Blender
  open with the add-on; it does **not** work in the ephemeral web container.

> Workflow that looks pro: **Blender for the 3D base** (iceberg, fog, camera) →
> **Manim for the UI/HUD overlays** (the interface, text, decryption) →
> composite. Best of both.

## 2. Sound — ElevenLabs MCP  ★ easy, huge payoff

AI **sound effects**, **ambience/music**, and **voiceover narration** — perfect
for a dark-documentary channel. Replaces my hand-synthesized WAVs with
studio-grade audio.

- Package: `elevenlabs-mcp` · needs `ELEVENLABS_API_KEY` (free tier to start).

## 3. AI image generation — Replicate **or** fal

Generate location plates (satellite/aerial), cryptid sketches, redacted
documents, textures, thumbnails (Flux / SDXL / etc.). I then composite them into
Manim/Blender scenes.

- Replicate MCP (`mcp-replicate`) · needs `REPLICATE_API_TOKEN`.
- fal.ai also has an MCP; either works. (Confirm the exact package before use.)

## 4. AI video generation (optional)

Short cinematic clips (Kling / Luma / Runway / Wan / Hailuo) via Replicate/fal,
to use as B-roll behind the UI. Same API token as above.

## 5. Plumbing — Filesystem + Fetch (official MCPs)

- `@modelcontextprotocol/server-filesystem` — manage the `assets/` library.
- `mcp-server-fetch` — pull reference images / data from URLs.

---

## Config

Copy `.mcp.example.json` → `.mcp.json`, fill in keys, and Claude Code will load
the servers. (Project-scoped MCP config.)

```jsonc
{
  "mcpServers": {
    "elevenlabs": { "command": "uvx", "args": ["elevenlabs-mcp"],
                    "env": { "ELEVENLABS_API_KEY": "YOUR_KEY" } },
    "replicate":  { "command": "npx", "args": ["-y", "mcp-replicate"],
                    "env": { "REPLICATE_API_TOKEN": "YOUR_TOKEN" } },
    "blender":    { "command": "uvx", "args": ["blender-mcp"] },   // desktop only
    "filesystem": { "command": "npx", "args": ["-y",
                    "@modelcontextprotocol/server-filesystem", "./assets"] },
    "fetch":      { "command": "uvx", "args": ["mcp-server-fetch"] }
  }
}
```

## Notes / constraints

- **Web vs desktop.** On Claude Code on the web, the container is ephemeral and
  outbound network is governed by the environment's **network policy** — MCPs
  that call external APIs (ElevenLabs, Replicate, fal) need that allowed. Blender
  MCP is a desktop thing; for the web, use **headless Blender** instead.
- **API keys** never go in the repo. Put them in the env config / `.mcp.json`
  (which should be git-ignored) — not committed.
- `uvx`/`npx` are used to run the servers without manual installs; the web
  container has Node; `uv` can be installed in `setup.sh` if we go this route.

## My recommendation (in order)

1. **Headless Blender here** — I can install it and prototype a real 3D iceberg
   right now (no keys needed). Biggest jump for *these* intros.
2. **ElevenLabs** — pro sound + optional narration (1 API key).
3. **Replicate/fal** — AI plates, cryptid art, thumbnails (1 API key).
