"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import routers
from backend.routers import config, meal_plans, meals, tasks

app = FastAPI(title="Recipier API", description="Meal planning and task generation API", version="1.0.0")

# CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(meals.router, prefix="/api/meals", tags=["meals"])
app.include_router(meal_plans.router, prefix="/api/meal-plan", tags=["meal-plans"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(config.router, prefix="/api/config", tags=["config"])


@app.get("/api")
def api_root():
    """API root endpoint."""
    return {"status": "ok", "message": "Recipier API is running"}


@app.get("/api/health")
def health_check():
    """API health check."""
    return {"status": "healthy", "version": "1.0.0"}


# Serve frontend static files in production
# Check if frontend dist directory exists (created during Docker build)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    # Mount static files - this must come AFTER API routes
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
