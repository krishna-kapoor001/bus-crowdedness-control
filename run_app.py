import os
import sys
import uvicorn

if __name__ == "__main__":
    print("=====================================================================")
    print("  FLOWPULSE — Intelligent Public Transportation Intelligence Platform")
    print("  Delhi Transit Stack — Crowdedness-Aware Journey Planner")
    print("=====================================================================")
    print("  * Serving Full-Stack Application at: http://localhost:8000")
    print("  * Interactive Swagger API Docs at:   http://localhost:8000/docs")
    print("  * OpenAPI Specification at:          http://localhost:8000/openapi.json")
    print("=====================================================================\n")

    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
