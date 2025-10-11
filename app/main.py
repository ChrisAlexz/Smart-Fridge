"""FastAPI application entrypoint for the Smart Fridge meal generator."""
from __future__ import annotations

from fastapi import FastAPI

from .routes import router as api_router

app = FastAPI(
    title="MyFridge - Smart Meal Generator",
    description=(
        "Upload a fridge photo to automatically detect ingredients and create "
        "tailored recipes powered by Gemini Vision."
    ),
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Simple health endpoint."""

    return {"message": "Smart Fridge service is running"}


app.include_router(api_router)


__all__ = ["app"]
