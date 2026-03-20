# Docker Setup for Aseprite MCP

This document describes how to build and run the Aseprite MCP server using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## Quick Start

### Building the Image

#### On Linux/macOS:
```bash
chmod +x build-docker.sh
./build-docker.sh
```

#### On Windows (PowerShell):
```powershell
.\build-docker.ps1
```

#### Manual build:
```bash
docker build -t aseprite-mcp:latest .
```

### Running the Container

#### Basic run:
```bash
docker run -it --rm aseprite-mcp:latest
```

#### Development mode (with volume mount):
```bash
docker run -it --rm -v $(pwd):/app aseprite-mcp:latest
```

#### Interactive shell:
```bash
docker run -it --rm --entrypoint /bin/bash aseprite-mcp:latest
```

### Using Docker Compose

#### Production:
```bash
docker-compose up aseprite-mcp
```

#### Development:
```bash
docker-compose --profile dev up aseprite-mcp-dev
```

## Image Details

- **Base Image**: `ghcr.io/homebrew/brew:latest` (latest Homebrew container)
- **Python Version**: 3.13 (installed via Homebrew)
- **Package Manager**: `uv` (installed via Homebrew)
- **User**: Non-root user `mcpuser` for security
- **Working Directory**: `/app`

## Optional: Install Aseprite via SteamCMD

The image includes SteamCMD to optionally install Aseprite at container startup. This is useful if you own Aseprite on Steam and want the official binary.

Environment variables:
- `STEAM_USERNAME` and `STEAM_PASSWORD` (required to install paid app)
- `STEAM_GUARD_CODE` (optional; if Steam Guard prompts)
- `STEAM_APPID` (default `431730`)
- `STEAM_INSTALL_DIR` (default `/opt/steamapps`)

Run examples:
```powershell
# Windows PowerShell
# Reads credentials from a .env file (recommended)
docker run --rm -i --env-file .env aseprite-mcp:latest

# Or pass inline (not recommended for security)
docker run --rm -i -e STEAM_USERNAME=you -e STEAM_PASSWORD=secret aseprite-mcp:latest
```

On successful install, the binary is placed at:
`/opt/steamapps/common/Aseprite/aseprite`
and `ASEPRITE_PATH` is set automatically if not provided.

## Environment Variables

If you need to pass environment variables, create a `.env` file based on `sample.env` and uncomment the `env_file` section in `docker-compose.yml`.

## Troubleshooting

### Build Issues

1. **Homebrew installation fails**: Ensure you have a stable internet connection as the image downloads and installs packages.

2. **Python 3.13 not found**: The Homebrew image should include Python 3.13. If not, you might need to update the base image.

3. **uv sync fails**: Check that all dependencies in `pyproject.toml` are compatible with Python 3.13.

### Runtime Issues

1. **Permission denied**: The container runs as a non-root user. If you need to modify files, ensure proper permissions.

2. **Module not found**: Ensure the working directory is set correctly and all dependencies are installed.

## Customization

You can modify the `Dockerfile` to:
- Change the base image
- Add additional system dependencies
- Modify the entrypoint or command
- Change the user or working directory

## Security Notes

- The container runs as a non-root user (`mcpuser`) for improved security
- Only necessary files are copied (see `.dockerignore`)
- No unnecessary ports are exposed by default
