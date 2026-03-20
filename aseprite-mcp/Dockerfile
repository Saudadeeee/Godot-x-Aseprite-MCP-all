# Use the latest Homebrew Docker image
FROM ghcr.io/homebrew/brew:latest

# Install Python 3.13 and uv via Homebrew
RUN brew install python@3.13 uv

# Add Homebrew binaries to PATH
ENV PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"

# --- Optional Steam/Aseprite support ---
# Install steamcmd and minimal dependencies (Ubuntu base)
USER root
RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	   steamcmd lib32gcc-s1 ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Steam/Aseprite environment knobs (no secrets baked!)
ENV STEAM_APPID=431730 \
	STEAM_INSTALL_DIR=/opt/steamapps

# Set the working directory
WORKDIR /app

# Copy the project files (including helper scripts)
COPY . .

# Install Python dependencies using uv
RUN uv sync

# Ensure helper scripts are executable
RUN chmod +x scripts/*.sh || true

# Use a wrapper entrypoint that can install Aseprite via Steam at runtime if requested
ENTRYPOINT ["/bin/bash", "/app/scripts/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD []
