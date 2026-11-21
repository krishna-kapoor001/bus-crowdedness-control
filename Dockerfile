# Multi-stage production build for BusRoute high-concurrency deployment

# Stage 1: Build Frontend Assets
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend
FROM python:3.12-slim AS runner
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn uvloop httptools

# Copy backend code, models, and processed data
COPY backend/ ./backend/
COPY data/processed/ ./data/processed/
COPY data/stops_meta.json data/routes_meta.json data/transit_edges.json ./data/
COPY models_artifacts/ ./models_artifacts/
COPY gunicorn_conf.py ./
COPY run.py ./

# Copy built frontend assets into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run high-concurrency Gunicorn with Uvicorn workers
CMD ["gunicorn", "-c", "gunicorn_conf.py", "backend.app.main:app"]
