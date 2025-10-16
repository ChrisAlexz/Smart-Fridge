"""API route definitions for the Smart Fridge service."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from .config import Settings, get_settings
from .models import RecipeResponse
from .services.meal_planner import MealPlannerService

router = APIRouter(prefix="/api", tags=["recipes"])


def get_meal_planner(settings: Settings = Depends(get_settings)) -> MealPlannerService:
    """Dependency that returns a configured MealPlannerService."""

    try:
        return MealPlannerService(settings)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/recipes/from-fridge", response_model=RecipeResponse)
async def generate_recipe_from_fridge(
    files: List[UploadFile] = File(default=[], description="Fridge photos to analyse"),
    manual_ingredients: str | None = Form(default=None, description="Comma separated manual ingredients"),
    dietary_preferences: str | None = Form(
        default=None, description="Comma separated dietary preferences"
    ),
    allergies: str | None = Form(default=None, description="Comma separated allergens to avoid"),
    cuisine: str | None = Form(default=None, description="Optional cuisine inspiration"),
    servings: int | None = Form(default=None, description="Number of servings to target"),
    recipe_index: int | None = Form(default=None, description="Recipe variation number"),
    planner: MealPlannerService = Depends(get_meal_planner),
) -> RecipeResponse:
    """Generate a meal plan using the contents of the uploaded fridge photos and/or manual ingredients."""

    if (not files or len(files) == 0) and not manual_ingredients:
        raise HTTPException(
            status_code=400,
            detail="At least one fridge photo or manual ingredient is required"
        )

    try:
        return planner.plan_meal(
            files,
            manual_ingredients=manual_ingredients,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
            cuisine=cuisine,
            servings=servings,
            recipe_index=recipe_index,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


__all__ = ["router"]