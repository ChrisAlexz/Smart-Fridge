from __future__ import annotations

import json
import logging
from typing import List, Optional

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
        uploaded_files: List,
        *,
        dietary_preferences: Optional[str] = None,
        allergies: Optional[str] = None,
        cuisine: Optional[str] = None,
        servings: Optional[int] = None,
        recipe_index: Optional[int] = None,
    ) -> RecipeResponse:
        """Generate a recipe from multiple fridge photos."""
        
        all_ingredients = []
        
        # Extract ingredients from all uploaded images
        for uploaded_file in uploaded_files:
            image_bytes = read_upload_bytes(uploaded_file)
            mime_type = detect_mime_type(uploaded_file)
            ingredients = self._gemini.extract_ingredients(image_bytes, mime_type)
            all_ingredients.extend(ingredients)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_ingredients = []
        for ingredient in all_ingredients:
            lower = ingredient.lower()
            if lower not in seen:
                unique_ingredients.append(ingredient)
                seen.add(lower)
        
        if not unique_ingredients:
            raise ValueError(
                "No ingredients detected in the provided images. Try clearer fridge photos."
            )

        # Generate varied recipes by adding variety hints
        variety_hint = ""
        if recipe_index is not None and recipe_index > 0:
            variety_hints = [
                "Create a completely different recipe with a unique cooking style.",
                "Make something with a different flavor profile and cuisine influence.",
                "Design a recipe that uses different cooking techniques.",
                "Create a meal with a different complexity level and preparation time.",
                "Make something suitable for a different meal time or occasion.",
            ]
            variety_hint = variety_hints[recipe_index % len(variety_hints)]

        raw_recipe = self._gemini.generate_recipe(
            unique_ingredients,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
            cuisine=cuisine,
            servings=servings,
            variety_hint=variety_hint,
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
        except (ValueError, json.JSONDecodeError) as exc:
            LOGGER.error("Failed to parse recipe response: %s", exc)
            return {}


__all__ = ["MealPlannerService"]