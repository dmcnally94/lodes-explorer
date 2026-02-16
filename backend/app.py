from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

app = FastAPI(
    title="LODES Explorer",
    description="Explore LODES workplace area characteristics by block group",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from .routes import cbsa

# Include routers
app.include_router(cbsa.router)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "0.1.0"}


# Helpful API index to avoid 404 on GET /api/
@app.get("/api/", include_in_schema=False)
def api_index():
    return {
        "message": "LODES Explorer API",
        "endpoints": [
            "/api/cbsas",
            "/api/cbsa/{cbsa_code}",
            "/api/blockgroups/{cbsa_code}",
            "/api/filters",
        ],
    }


# Serve favicon if present to avoid 404 noise
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    frontend_dir = Path(__file__).parent.parent / "frontend"
    fav = frontend_dir / "favicon.ico"
    if fav.exists():
        return FileResponse(fav)
    return JSONResponse(status_code=204, content=None)


# Serve static files (frontend)
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
