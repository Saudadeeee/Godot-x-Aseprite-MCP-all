# Godot x Aseprite MCP

A monorepo with two extended MCP (Model Context Protocol) servers that together cover the full 2D game asset pipeline — pixel art creation in **Aseprite** and scene/logic building in **Godot Engine** — controlled entirely through natural language via AI assistants.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green)](https://nodejs.org)
[![Godot 4.x](https://img.shields.io/badge/Godot-4.x-blue)](https://godotengine.org)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## What This Is

Two MCP servers run simultaneously. An AI assistant reads [`AGENTS.md`](./AGENTS.md) to understand when to use Aseprite (art) vs Godot (scenes/logic), and routes each task automatically:

```
User request
     │
     ▼
AI reads AGENTS.md
     ├── art / sprite / animation task  →  aseprite MCP tools
     └── scene / node / script task    →  godot-mcp tools
```

**Combined workflow for a game element:**

```
[Aseprite]  create_canvas → add_layer → draw → export PNG
                                                    │
[Godot]                              load_sprite → add_node → build scene → script
```

---

## Projects

### [Godot-MCP](./Godot-MCP/)

Godot 4 plugin + Node.js MCP server. AI assistants interact with your Godot project in real time via a WebSocket bridge.

- **Based on:** [ee0pdt/Godot-MCP](https://github.com/ee0pdt/Godot-MCP)
- **Extended with:** 16 additional modules — animation, animation tree, environment, materials, mesh, navigation, particles, path, playback, project config, skeleton, theme, tilemap, tween, editor script
- **Stack:** TypeScript (server) + GDScript (Godot plugin)

### [aseprite-mcp](./aseprite-mcp/)

Python MCP server. Controls Aseprite programmatically via Lua script injection into its CLI.

- **Based on:** [diivi/aseprite-mcp](https://github.com/diivi/aseprite-mcp)
- **Extended with:** 12 additional modules — advanced drawing, effects, transforms, cel operations, spritesheets, tilemaps, slices, clipboard, AI features, batch file utilities
- **Stack:** Python 3.12+

---

## Quick Start

**Option A — Automated (recommended):**

```bash
# Clone
git clone https://github.com/Saudadeeee/Godot-x-Aseprite-MCP-all.git
cd "Godot-x-Aseprite-MCP-all"

# Windows
.\setup.ps1

# macOS / Linux
chmod +x setup.sh && ./setup.sh
```

The script checks prerequisites, installs dependencies, builds the server, auto-detects Aseprite, and writes a ready-to-use `mcp_config.json`.

**Option B — Manual:**

```bash
# 1. Install Python dependencies
cd aseprite-mcp && uv sync

# 2. Build Node.js server
cd ../Godot-MCP/server && npm install && npm run build

# 3. Enable Godot plugin
# Copy addons/godot_mcp/ to your Godot project → enable in Project Settings → Plugins

# 4. Configure MCP client (see mcp_config.json or SETUP.md)
```

For full instructions, troubleshooting, and platform-specific notes: **[SETUP.md](./SETUP.md)**

---

## MCP Client Config

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["--directory", "/path/to/aseprite-mcp", "run", "-m", "aseprite_mcp"],
      "env": { "ASEPRITE_PATH": "/path/to/aseprite" }
    },
    "godot-mcp": {
      "command": "node",
      "args": ["/path/to/Godot-MCP/server/dist/index.js"],
      "env": { "MCP_TRANSPORT": "stdio" }
    }
  }
}
```

Config file locations:
- **Claude Desktop — Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Claude Desktop — macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Code:** `claude mcp add` command or project settings

---

## Example Prompts

```
Create a 16x16 player sprite with idle and walk animations,
export it as a spritesheet, then set it up in Godot as a
CharacterBody2D with AnimatedSprite2D and CollisionShape2D.
```

```
Draw a 128x128 tileset with grass, dirt, and stone tiles at 16x16px,
then create a TileMap level in Godot and fill it with those tiles.
```

```
Make an enemy sprite with a hit-flash animation in Aseprite,
then create an enemy scene in Godot with health, patrol movement,
and a died signal.
```

---

## Repository Structure

```
Godot x Aseprite MCP/
├── AGENTS.md                       # AI agent instruction file (auto-loaded)
├── SETUP.md                        # Full setup guide
├── setup.sh                        # One-click setup (Linux/macOS)
├── setup.ps1                       # One-click setup (Windows)
├── claude_desktop_config.json      # MCP config template
│
├── Godot-MCP/
│   ├── addons/godot_mcp/           # Godot plugin (copy to your project)
│   │   ├── commands/               # 20 GDScript command modules
│   │   ├── ui/                     # Editor panel
│   │   └── utils/
│   ├── server/src/
│   │   ├── tools/                  # 19 TypeScript MCP tool definitions
│   │   ├── resources/              # MCP resource endpoints
│   │   └── utils/
│   └── docs/
│
└── aseprite-mcp/
    ├── aseprite_mcp/
    │   ├── core/                   # MCP server core
    │   ├── tools/                  # 17 Python tool modules
    │   └── utils/                  # Lua templates, constants
    └── tests/
```

---

## Requirements

| Component | Version | Install |
|---|---|---|
| Python | 3.12+ | [python.org](https://python.org) |
| uv | latest | `pip install uv` or [astral.sh/uv](https://astral.sh/uv) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Godot Engine | 4.x | [godotengine.org](https://godotengine.org) |
| Aseprite | 1.3+ | [aseprite.org](https://aseprite.org) |

---

## Credits

| Project | Original Author | Repository |
|---|---|---|
| Godot-MCP | [@ee0pdt](https://github.com/ee0pdt) | [ee0pdt/Godot-MCP](https://github.com/ee0pdt/Godot-MCP) |
| aseprite-mcp | [@diivi](https://github.com/diivi) | [diivi/aseprite-mcp](https://github.com/diivi/aseprite-mcp) |

Both original projects are MIT licensed. This fork extends them without altering their core architecture.

---

## License

MIT — see individual `LICENSE` files in each subdirectory.
