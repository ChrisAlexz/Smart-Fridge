"""Pydantic models used by the FastAPI service."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RecipeStep(BaseModel):
    """Represents an individual instruction step for the generated recipe."""

    order: int = Field(..., ge=1, description="Step number in the recipe workflow")
    instruction: str = Field(..., description="Human-friendly step description")


class RecipeMetadata(BaseModel):
    """Additional context for the generated recipe."""

    cuisine: Optional[str] = Field(
        default=None,
        description="Cuisine inspiration supplied by the end user or model.",
    )
    servings: Optional[int] = Field(
        default=None,
        ge=1,
        description="Requested number of servings for the generated recipe.",
    )
    dietary_preferences: Optional[str] = Field(
        default=None,
        description="Optional dietary preferences (vegan, gluten-free, etc.).",
    )
    allergies: Optional[str] = Field(
        default=None,
        description="Allergy information to avoid problematic ingredients.",
    )


class RecipeResponse(BaseModel):
    """API response returned to clients after meal generation."""

    title: str = Field(..., description="Generated recipe title")
    summary: str = Field(..., description="Short overview of the generated meal")
    ingredients: List[str] = Field(..., description="List of cleaned ingredients")
    steps: List[RecipeStep] = Field(..., description="Ordered step-by-step instructions")
    metadata: RecipeMetadata = Field(
        default_factory=RecipeMetadata,
        description="Supplementary metadata provided by the user or model.",
    )


__all__ = ["RecipeResponse", "RecipeStep", "RecipeMetadata"]
