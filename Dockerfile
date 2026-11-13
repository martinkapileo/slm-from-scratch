# Dashboard image: React UI + FastAPI API in one container.
# Multi-stage build: Node only exists in the build stage, so the final image stays small.

# ---- Stage 1: build the React app ----
FROM node:22-slim AS ui
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python runtime ----
FROM python:3.12-slim
WORKDIR /app

# CPU-only PyTorch (~200 MB) instead of the default CUDA build (~3 GB).
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir torch --index-url ${TORCH_INDEX_URL}

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir ".[dashboard]"

COPY --from=ui /ui/dist ./static

# Run as a non-root user.
RUN useradd --create-home --uid 1000 app
USER app

ENV SLM_RUNS_DIR=/app/runs \
    SLM_STATIC_DIR=/app/static \
    PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"
CMD ["uvicorn", "slm.dashboard.api:app", "--host", "0.0.0.0", "--port", "8000"]
