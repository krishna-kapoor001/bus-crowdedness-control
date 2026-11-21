# BusRoute — Enterprise Production Gunicorn / Uvicorn Configuration
# Designed for high-concurrency deployments (1M+ concurrent users)

import multiprocessing
import os

# Server socket
bind = os.getenv("BIND", "0.0.0.0:8000")
backlog = 65535  # Maximum TCP listen queue backlog

# Worker processes: 2 x CPU cores + 1
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 10000  # Max concurrent client connections per worker
timeout = 30
keepalive = 65  # Slightly higher than AWS ALB / Cloudflare 60s idle timeout

# Memory management & recycling to prevent memory leaks under massive load
max_requests = 50000
max_requests_jitter = 5000

# Logging
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"

# Performance tweaks
preload_app = True  # Share pre-warmed ML models & in-memory graph across worker processes via copy-on-write
enable_stdio_inheritance = True
