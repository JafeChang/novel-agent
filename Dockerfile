# ── Stage 1: build the React/Vue frontend ────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Install dependencies first (better layer caching)
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy the rest of the frontend source and build
COPY frontend/ .
RUN npm run build

# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and Node.js (needed for OpenCode at runtime)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g opencode-ai@latest \
    && rm -rf /var/lib/apt/lists/*

# Ensure the npm global bin directory is on PATH for all subsequent layers
# and for the running container (including Python subprocesses).
ENV PATH="/usr/local/bin:${PATH}"

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy the compiled frontend assets from the builder stage
COPY --from=frontend-builder /frontend/dist /app/dist

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Fly.io uses PORT env var
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
