import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from backend.app.config import settings
from backend.app.routers import (
    overview, journey, analytics, network, simulation, models_info
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="BusRoute: High-Concurrency Crowdedness-Aware Journey Planning & Transit Demand Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend development and enterprise deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Register API routers under /api/v1
app.include_router(overview.router, prefix="/api/v1/overview", tags=["Overview"])
app.include_router(journey.router, prefix="/api/v1/journey", tags=["Journey Planner"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Crowd Intelligence & Operator Analytics"])
app.include_router(network.router, prefix="/api/v1/network", tags=["Network Explorer"])
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["CrowdShift Simulator"])
app.include_router(models_info.router, prefix="/api/v1/models", tags=["Model Methodology & Benchmark"])

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "BusRoute Backend Core",
        "dataset": "Delhi Transit Electronic Ticketing (ETM) Dataset",
        "records_processed": 2559897
    }

# Serve static frontend if built
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(
            os.path.join(frontend_dist, "index.html"),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
