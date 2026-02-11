FROM python:3.11-slim

# System dependencies for development
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl bash build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for dev
RUN useradd -m -u 1000 appuser

WORKDIR /workspace

# Copy requirements for installation
COPY ../requirements.txt /workspace/requirements.txt

# Install runtime dependencies
RUN pip install --no-cache-dir -r /workspace/requirements.txt

# Install dev-only tools
RUN pip install --no-cache-dir \
    black \
    isort \
    flake8 \
    mypy

USER appuser

