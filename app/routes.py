"""API route definitions for the Smart Fridge service."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from .config import Settings, get_settings
from .models import RecipeResponse
from .services.meal_planner import MealPlannerService

router = APIRouter(prefix="/api", tags=["recipes"])


def get_meal_planner(settings: Settings = Depends(get_settings)) -> MealPlannerService:
    """Dependency that returns a configured MealPlannerService."""

    return MealPlannerService(settings)


@router.post("/recipes/from-fridge", response_model=RecipeResponse)
async def generate_recipe_from_fridge(
    file: UploadFile = File(..., description="Fridge photo to analyse"),
    dietary_preferences: str | None = Form(
        default=None, description="Comma separated dietary preferences"
    ),
    allergies: str | None = Form(default=None, description="Comma separated allergens to avoid"),
    cuisine: str | None = Form(default=None, description="Optional cuisine inspiration"),
    servings: int | None = Form(default=None, description="Number of servings to target"),
    planner: MealPlannerService = Depends(get_meal_planner),
) -> RecipeResponse:
    """Generate a meal plan using the contents of the uploaded fridge photo."""

    try:
        return planner.plan_meal(
            file,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
            cuisine=cuisine,
            servings=servings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


__all__ = ["router"]
