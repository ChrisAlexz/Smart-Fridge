"""High level meal planning orchestration."""
from __future__ import annotations

import json
import logging
from typing import Optional

from ..config import Settings
from ..models import RecipeMetadata, RecipeResponse, RecipeStep
from ..utils import extract_json_block, parse_ingredient_list
from .gemini import GeminiVisionClient, detect_mime_type, read_upload_bytes

LOGGER = logging.getLogger(__name__)


class MealPlannerService:
    """Coordinates ingredient detection and recipe generation."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._gemini = GeminiVisionClient(settings)

    def plan_meal(
        self,
        uploaded_file,
        *,
        dietary_preferences: Optional[str] = None,
        allergies: Optional[str] = None,
        cuisine: Optional[str] = None,
        servings: Optional[int] = None,
    ) -> RecipeResponse:
        image_bytes = read_upload_bytes(uploaded_file)
        mime_type = detect_mime_type(uploaded_file)
        ingredients = self._gemini.extract_ingredients(image_bytes, mime_type)
        if not ingredients:
            raise ValueError(
                "No ingredients detected in the provided image. Try a clearer fridge photo."
            )

        raw_recipe = self._gemini.generate_recipe(
            ingredients,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
            cuisine=cuisine,
            servings=servings,
        )

        recipe_payload = self._parse_recipe_payload(raw_recipe)
        metadata = RecipeMetadata(
            cuisine=cuisine,
            servings=servings,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
        )
        return RecipeResponse(
            title=recipe_payload.get("title", "Untitled Recipe"),
            summary=recipe_payload.get(
                "summary",
                "A tasty meal created from the available fridge ingredients.",
            ),
            ingredients=parse_ingredient_list(
                json.dumps(recipe_payload.get("ingredients", []))
            ),
            steps=[
                RecipeStep(order=step.get("order", idx + 1), instruction=step["instruction"])
                for idx, step in enumerate(recipe_payload.get("steps", []))
                if isinstance(step, dict) and step.get("instruction")
            ],
            metadata=metadata,
        )

    @staticmethod
    def _parse_recipe_payload(raw_recipe: str) -> dict:
        """Parse the recipe JSON returned by Gemini."""

        if not raw_recipe:
            LOGGER.warning("Gemini returned an empty recipe payload")
            return {}
        try:
            json_block = extract_json_block(raw_recipe)
            return json.loads(json_block)
        except (ValueError, json.JSONDecodeError) as exc:  # pragma: no cover
            LOGGER.error("Failed to parse recipe response: %s", exc)
            return {}


__all__ = ["MealPlannerService"]
