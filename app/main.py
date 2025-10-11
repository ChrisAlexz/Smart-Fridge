"""FastAPI application entrypoint for the Smart Fridge meal generator."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .routes import router as api_router

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="MyFridge - Smart Meal Generator",
    description=(
        "Upload a fridge photo to automatically detect ingredients and create "
        "tailored recipes powered by Gemini Vision."
    ),
    version="0.1.0",
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Render the primary upload experience."""

    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple JSON health endpoint for monitoring."""

    return {"message": "Smart Fridge service is running"}


app.include_router(api_router)


__all__ = ["app"]
