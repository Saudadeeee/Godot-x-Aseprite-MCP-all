#!/usr/bin/env bash
set -euo pipefail

# Optional: install Aseprite via Steam if credentials provided
if [[ -n "${STEAM_USERNAME:-}" && -n "${STEAM_PASSWORD:-}" ]]; then
  echo "[entrypoint] Installing Aseprite via SteamCMD..."
  /app/scripts/install-aseprite-steam.sh || echo "[entrypoint] Steam install attempted. Proceeding..."
fi

# If ASEPRITE_PATH not set but default path exists, set it
DEFAULT_ASE="/opt/steamapps/common/Aseprite/aseprite"
if [[ -z "${ASEPRITE_PATH:-}" && -x "$DEFAULT_ASE" ]]; then
  export ASEPRITE_PATH="$DEFAULT_ASE"
fi

# Show what will be used
echo "ASEPRITE_PATH=${ASEPRITE_PATH:-aseprite}"

# Run the MCP server via uv
exec uv run -m aseprite_mcp
