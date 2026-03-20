# Aseprite MCP

A Python MCP (Model Context Protocol) server that provides programmatic control of Aseprite for pixel art creation, animation, and game asset workflows.

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-green)](https://python.org/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com/)

---

## Credits

This project is based on **[aseprite-mcp](https://github.com/diivi/aseprite-mcp)** by [@diivi](https://github.com/diivi), which pioneered MCP integration with Aseprite using Lua script injection.

The original project provided the core architecture and foundational drawing tools. This fork extends it significantly with additional tool modules, AI-assisted features, and a more complete automation pipeline.

---

## What's New in This Fork

The following tool modules were added on top of the original:

| Module | Description |
|---|---|
| `drawing_advanced.py` | Polygons, Bezier curves, gradients, brush strokes, patterns |
| `layer_advanced.py` | Layer groups, blend modes, opacity control |
| `cel_operations.py` | Frame/cel management, linking, opacity |
| `effects.py` | Blur, HSL adjust, posterize, pixelate, outline, drop shadow |
| `transform.py` | Flip, rotate, resize, crop with pixel-perfect precision |
| `selection.py` | Selection control, invert, delete operations |
| `clipboard.py` | Copy/paste, layer merge, clipboard workflows |
| `spritesheet.py` | Sprite sheet generation with JSON metadata |
| `tilemap.py` | Tileset creation, import/export, tile placement |
| `slices.py` | Sprite slice management |
| `file_utils.py` | Batch processing, optimization, backup/restore |
| `ai_features.py` | Auto colorization, AI-guided upscaling, smart palette extraction |

---

## Tool Overview

### Core (from original)
- **Canvas** - Create and manage canvases
- **Drawing** - Basic pixel drawing, lines, rectangles, circles, fills
- **Layer** - Layer creation and management
- **Palette** - Palette loading and color management
- **Export** - Export to PNG and other formats
- **Brush** - Brush configuration

### Extended (this fork)
- **Advanced Drawing** - Bezier curves, polygons, gradients, patterns
- **Layer Advanced** - Groups, blend modes, opacity
- **Cel Operations** - Animation cel management
- **Effects** - Non-destructive image effects
- **Transform** - Geometric transformations
- **Selection** - Selection tools
- **Clipboard** - Clipboard operations
- **Spritesheet** - Sprite sheet + JSON export
- **Tilemap** - Tileset and tilemap support
- **Slices** - Sprite slices
- **File Utilities** - Batch processing and file management
- **AI Features** - AI-assisted colorization and upscaling

---

## Installation

### Prerequisites
- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) package manager
- Aseprite (installed separately)

### Local Setup

Set the `ASEPRITE_PATH` environment variable to point to your Aseprite executable:

```bash
# Windows
set ASEPRITE_PATH=C:\Program Files\Aseprite\Aseprite.exe

# macOS
export ASEPRITE_PATH=/Applications/Aseprite.app/Contents/MacOS/aseprite

# Linux
export ASEPRITE_PATH=/usr/bin/aseprite
```

### Claude Desktop / Claude Code Config

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/aseprite-mcp",
        "run",
        "-m",
        "aseprite_mcp"
      ],
      "env": {
        "ASEPRITE_PATH": "/path/to/aseprite"
      }
    }
  }
}
```

---

## Docker

### Quick Start

```bash
docker build -t aseprite-mcp:latest .
docker run -it --rm aseprite-mcp:latest
```

Or use the provided scripts:

```bash
# Linux/macOS
chmod +x build-docker.sh && ./build-docker.sh

# Windows
.\build-docker.ps1
```

### Docker Compose

```bash
# Production
docker-compose up aseprite-mcp

# Development
docker-compose --profile dev up aseprite-mcp-dev
```

To install Aseprite via Steam inside the container, provide credentials via `.env`:

```bash
docker run --rm -i --env-file .env aseprite-mcp:latest
```

See [DOCKER.md](DOCKER.md) for full Docker setup details.

---

## Usage Examples

### Basic Pixel Art

```python
# Create a canvas and draw
await create_canvas(64, 64, "sprite.aseprite")
await add_layer("sprite.aseprite", "Body")
await draw_rectangle("sprite.aseprite", 10, 10, 40, 40, "#FF0000")
await export_sprite("sprite.aseprite", "sprite.png")
```

### Animation Workflow

```python
await create_canvas(32, 32, "anim.aseprite")
await add_frame("anim.aseprite")
await add_frame("anim.aseprite")
# Draw different content per frame
await export_sprite_sheet("anim.aseprite", "anim_sheet.png", "horizontal")
```

### Tileset Creation

```python
await create_canvas(128, 128, "tileset.aseprite")
await setup_tileset("tileset.aseprite", 16, 16)
await export_sprite_sheet_with_json("tileset.aseprite", "tileset.png", "tileset.json")
```

---

## Troubleshooting

**Aseprite not found** — Verify `ASEPRITE_PATH` points to the correct executable and that it can be run in headless/CLI mode (`aseprite --batch`).

**Lua script errors** — This server works by injecting Lua scripts into Aseprite's CLI. Ensure your Aseprite version supports scripting (1.3+).

**Permission errors on Windows** — Run your terminal as Administrator or ensure Aseprite is not running when the MCP server executes commands.

---

## License

MIT License — see [LICENSE](LICENSE).

Original project by [@diivi](https://github.com/diivi) — MIT License.
