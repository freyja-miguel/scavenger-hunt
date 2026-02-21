"""Treasure Hunt API - FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="Treasure Hunt API",
    description="Backend for kids treasure hunt activities - activities, photo validation, rewards",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check / root."""
    return {"status": "ok", "app": "Treasure Hunt API"}


@app.get("/health")
async def health():
    """Health check for load balancers."""
    return {"status": "healthy"}


from app.routes import activities, children

app.include_router(activities.router, prefix=settings.api_prefix)
app.include_router(children.router, prefix=settings.api_prefix)
