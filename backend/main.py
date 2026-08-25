"""
FastAPI Backend Main Entrypoint
BSMA GeoAI Groundwater Siting Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import APP_NAME, API_V1_PREFIX, CORS_ORIGINS
from backend.database import engine, Base
from backend.routers import plots, feedback, analytics, providers

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    description=(
        "Scientific Groundwater Prospecting & Borewell Siting REST API. "
        "Provides zero-latency AHP multi-criteria spatial evaluations, "
        "VES resistivity survey guidance, ground-truth outcome capture, and contractor directory."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for PWA and External Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Sub-Routers
app.include_router(plots.router, prefix=API_V1_PREFIX)
app.include_router(feedback.router, prefix=API_V1_PREFIX)
app.include_router(analytics.router, prefix=API_V1_PREFIX)
app.include_router(providers.router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["Health & Status"])
def health_check():
    """Health check endpoint for Render / Kubernetes / Supabase monitoring."""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "pilot_region": "Yadadri-Bhuvanagiri / Musi Basin (Telangana)",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
