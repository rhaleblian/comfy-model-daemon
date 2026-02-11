#!/usr/bin/env bash
set -euo pipefail

echo "[daemon] starting comfy-model-daemon..."
exec python -m daemon.daemon

