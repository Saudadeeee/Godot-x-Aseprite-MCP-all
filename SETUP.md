# Setup Guide

Complete installation guide for **Godot x Aseprite MCP** on Windows, macOS, and Linux.

---

## Requirements

| Tool | Version | Purpose |
|---|---|---|
| [Python](https://python.org) | 3.12+ | Runs aseprite-mcp server |
| [uv](https://github.com/astral-sh/uv) | latest | Python package manager (recommended) |
| [Node.js](https://nodejs.org) | 18+ | Runs Godot-MCP server |
| [Godot Engine](https://godotengine.org) | 4.x | Game engine (editor must be open during use) |
| [Aseprite](https://aseprite.org) | 1.3+ | Pixel art tool (must support `--batch` CLI mode) |

> **Note on Aseprite:** Aseprite is a paid app (~$20 on Steam or direct). The free version compiled from source also works. The MCP server uses Aseprite's built-in Lua scripting via `aseprite --batch`.

---

## Quick Setup (Automated)

Clone the repo and run the setup script for your platform:

### Windows
```powershell
git clone https://github.com/Saudadeeee/Godot-x-Aseprite-MCP-all.git
cd "Godot-x-Aseprite-MCP-all"
.\setup.ps1
```

### macOS / Linux
```bash
git clone https://github.com/Saudadeeee/Godot-x-Aseprite-MCP-all.git
cd "Godot-x-Aseprite-MCP-all"
chmod +x setup.sh && ./setup.sh
```

The script will:
1. Check all prerequisites
2. Install Python dependencies for aseprite-mcp
3. Build the Godot-MCP TypeScript server
4. Auto-detect your Aseprite path
5. Generate a ready-to-use `mcp_config.json` with absolute paths

---

## Manual Setup

### Step 1 — Clone

```bash
git clone https://github.com/Saudadeeee/Godot-x-Aseprite-MCP-all.git
cd "Godot-x-Aseprite-MCP-all"
```

### Step 2 — Install aseprite-mcp dependencies

```bash
cd aseprite-mcp

# Recommended (uv):
uv sync

# Alternative (pip):
pip install -r requirements.txt
```

### Step 3 — Build Godot-MCP server

```bash
cd ../Godot-MCP/server
npm install
npm run build
```

This compiles TypeScript to `Godot-MCP/server/dist/index.js`.

### Step 4 — Enable the Godot plugin

1. Open your Godot 4 project in the editor
2. Copy `Godot-MCP/addons/godot_mcp/` into your Godot project's `addons/` folder
3. Go to **Project → Project Settings → Plugins**
4. Find **Godot MCP** and set it to **Enabled**
5. The plugin starts a WebSocket server on port `6789` automatically

> To use with multiple Godot projects: just copy the `addons/godot_mcp/` folder into each project.

### Step 5 — Configure your MCP client

Create or edit your MCP client config using the template below. Replace all paths with absolute paths on your system.

#### Claude Desktop

**Config file location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/aseprite-mcp",
        "run",
        "-m",
        "aseprite_mcp"
      ],
      "env": {
        "ASEPRITE_PATH": "/absolute/path/to/aseprite"
      }
    },
    "godot-mcp": {
      "command": "node",
      "args": [
        "/absolute/path/to/Godot-MCP/server/dist/index.js"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

#### Claude Code

```bash
# Add aseprite MCP
claude mcp add aseprite uv -- --directory /path/to/aseprite-mcp run -m aseprite_mcp

# Add Godot MCP
claude mcp add godot-mcp node -- /path/to/Godot-MCP/server/dist/index.js
```

Or place the config file at the project root as `mcp_config.json` and import it.

---

## Platform-Specific Notes

### Windows

- Use forward slashes or escaped backslashes in JSON paths:
  ```json
  "ASEPRITE_PATH": "C:/Program Files/Aseprite/Aseprite.exe"
  ```
- If `uv` is not in PATH after install, restart your terminal or add `%LOCALAPPDATA%\Programs\uv\bin` to PATH
- Aseprite via Steam is typically at:
  ```
  C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe
  ```

### macOS

- Aseprite from the App Store or direct download:
  ```
  /Applications/Aseprite.app/Contents/MacOS/aseprite
  ```
- If you get a permission error on `setup.sh`: `chmod +x setup.sh`
- Godot from the official download or Homebrew cask

### Linux

- Aseprite from Steam:
  ```
  ~/.local/share/Steam/steamapps/common/Aseprite/aseprite
  ```
- Aseprite compiled from source: usually `/usr/local/bin/aseprite`
- Make sure Aseprite has execute permission: `chmod +x /path/to/aseprite`

---

## Verifying the Setup

### Test aseprite-mcp

```bash
cd aseprite-mcp
uv run python -c "import aseprite_mcp; print('aseprite_mcp OK')"
```

### Test Godot-MCP server

```bash
node Godot-MCP/server/dist/index.js &
# Should start without errors. Kill with Ctrl+C.
```

### Test WebSocket connection (Godot plugin)

1. Open your Godot project with the plugin enabled
2. Check the bottom panel for "MCP" tab — it should show "Connected" or the port number
3. Alternatively, check the Godot Output panel for `[MCP] WebSocket server started on port 6789`

---

## Troubleshooting

### aseprite-mcp: "aseprite not found" or "command failed"

- Verify `ASEPRITE_PATH` in your config points to the actual Aseprite executable
- Test it manually: `"/path/to/aseprite" --batch --version`
- On macOS/Linux: check execute permission on the binary

### Godot-MCP: "WebSocket connection refused"

- The Godot editor must be open with the project loaded
- The `godot_mcp` plugin must be enabled in that project
- Check that nothing else is using port 6789: `netstat -an | grep 6789`

### Godot-MCP: "Cannot find module dist/index.js"

- Run `npm run build` inside `Godot-MCP/server/`
- The `dist/` folder is not included in the repo (it's generated)

### uv not found

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
winget install astral-sh.uv
# or
pip install uv
```

### Node.js version too old

```bash
# Use nvm (Linux/macOS)
nvm install 20 && nvm use 20

# Windows: download from https://nodejs.org or use nvm-windows
```

---

## Updating

```bash
git pull

# Rebuild Godot-MCP server after updates
cd Godot-MCP/server && npm install && npm run build

# Sync Python dependencies after updates
cd ../../aseprite-mcp && uv sync
```
