# Godot x Aseprite MCP

A monorepo containing two extended MCP (Model Context Protocol) servers for game development workflows — one for **Godot Engine** and one for **Aseprite**. Together they allow AI assistants to control the full 2D game asset pipeline, from sprite creation in Aseprite to scene building in Godot.

---

## Projects

### [Godot-MCP](./Godot-MCP/)

A Godot 4 plugin + Node.js MCP server that lets AI assistants interact with your Godot project in real time.

- **Based on:** [ee0pdt/Godot-MCP](https://github.com/ee0pdt/Godot-MCP)
- **Extended with:** 16 additional command modules covering animation, materials, navigation, particles, skeleton, tilemap, environment, tween, and more
- **Transport:** WebSocket bridge between Godot editor and MCP server (stdio)
- **Language:** TypeScript (server) + GDScript (plugin)

### [aseprite-mcp](./aseprite-mcp/)

A Python MCP server that provides programmatic control of Aseprite via Lua script injection.

- **Based on:** [diivi/aseprite-mcp](https://github.com/diivi/aseprite-mcp)
- **Extended with:** 12 additional tool modules covering advanced drawing, effects, transforms, animation cels, spritesheets, tilemaps, AI features, and batch file utilities
- **Transport:** stdio (runs Aseprite CLI with embedded Lua scripts)
- **Language:** Python 3.12+

---

## How the Two Servers Work Together

Both MCPs run simultaneously. The AI assistant knows automatically when to use Aseprite (art) and when to use Godot (scenes/logic) based on the task — this is defined in [`AGENTS.md`](./AGENTS.md), a universal instruction file auto-loaded by Claude Code, Gemini CLI, Cursor, and other AI agents.

```
User request → Claude reads CLAUDE.md → routes to correct MCP
                                          ├─ art task → aseprite tools
                                          └─ scene/logic task → godot-mcp tools
```

The combined workflow for a typical game element:

```
[Aseprite] create_canvas → draw → export PNG
                                        ↓
[Godot]              load_sprite → add_node → build scene → add script
```

---

## Quick Setup

### Step 1 — Install dependencies

```bash
# Aseprite MCP (Python)
cd aseprite-mcp
uv sync

# Godot MCP (Node.js)
cd ../Godot-MCP/server
npm install
npm run build
```

### Step 2 — Enable the Godot plugin

Copy `Godot-MCP/addons/godot_mcp/` into your Godot project's `addons/` folder, then enable it via **Project → Project Settings → Plugins → Godot MCP**.

### Step 3 — Configure your MCP client

Copy [`claude_desktop_config.json`](./claude_desktop_config.json) from this repo and update the paths:

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/aseprite-mcp", "run", "-m", "aseprite_mcp"],
      "env": {
        "ASEPRITE_PATH": "/absolute/path/to/aseprite"
      }
    },
    "godot-mcp": {
      "command": "node",
      "args": ["/absolute/path/to/Godot-MCP/server/dist/index.js"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

**Windows paths:** `C:\\Users\\you\\...` or use forward slashes `C:/Users/you/...`

**Config file location:**
- Claude Desktop (macOS): `~/Library/Application Support/Claude/claude_desktop_config.json`
- Claude Desktop (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
- Claude Code: configured via `claude mcp add` or settings

### Step 4 — Open Godot and start

Open your Godot project in the editor. The plugin connects automatically on port 6789. Both MCP servers are now available.

---

## Example Prompts

Once set up, you can use natural language:

```
Create a 16x16 player character sprite with idle and walk animations,
export it as a spritesheet, and set it up in Godot as a CharacterBody2D
with AnimatedSprite2D and CollisionShape2D.
```

```
Draw a 128x128 tileset with grass, dirt, and stone tiles at 16x16px,
then create a TileMap level in Godot using those tiles.
```

```
Make an enemy sprite with a hit animation in Aseprite,
then create an enemy scene in Godot with health, movement, and a death signal.
```

---

## Repository Structure

```
Godot x Aseprite MCP/
├── Godot-MCP/
│   ├── addons/godot_mcp/       # Godot plugin (GDScript)
│   │   ├── commands/           # 20 command modules
│   │   ├── ui/                 # Editor panel
│   │   └── utils/              # Shared utilities
│   ├── server/                 # Node.js MCP server (TypeScript)
│   │   └── src/
│   │       ├── tools/          # 19 MCP tool definitions
│   │       ├── resources/      # MCP resource endpoints
│   │       └── utils/          # Connection and type utilities
│   └── docs/                   # Documentation
│
└── aseprite-mcp/
    ├── aseprite_mcp/
    │   ├── core/               # MCP server core
    │   ├── tools/              # 17 tool modules
    │   └── utils/              # Lua templates, constants
    └── tests/                  # Test infrastructure
```

---

## Credits

| Project | Original Author | Repository |
|---|---|---|
| Godot-MCP | [@ee0pdt](https://github.com/ee0pdt) | [ee0pdt/Godot-MCP](https://github.com/ee0pdt/Godot-MCP) |
| aseprite-mcp | [@diivi](https://github.com/diivi) | [diivi/aseprite-mcp](https://github.com/diivi/aseprite-mcp) |

Both original projects are licensed under the MIT License. This repository extends them without modifying the original intent or architecture.

---

## Requirements

| Component | Requirement |
|---|---|
| Godot Engine | 4.x |
| Node.js | 18+ |
| Python | 3.12+ |
| uv | latest |
| Aseprite | 1.3+ (CLI scripting support) |

---

## License

MIT License. See individual project LICENSE files for details.
