# comfy-model-daemon

A lightweight, file‑driven daemon that monitors ComfyUI workflow files, resolves required models, downloads missing assets, and maintains a local cache. Designed for hybrid Docker + local development.

## Features
- Watches workflow directories for changes
- Parses ComfyUI workflow JSON
- Resolves model dependencies
- Downloads missing models with retry logic
- Maintains a persistent cache directory
- Runs cleanly in Docker or local dev

## Development
Use the included devcontainer for a fully configured environment:

    devcontainer open .

Or run locally:

    python -m daemon.daemon

## Docker
Build and run:

    docker compose up --build

The daemon code is live‑mounted for rapid iteration.

## Configuration
Edit `daemon/config.yaml` to control:
- watched directories  
- cache location  
- download endpoints  
- retry/backoff behavior  


