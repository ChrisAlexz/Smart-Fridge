"""Integration helpers for talking to the Gemini Generative AI API."""
from __future__ import annotations

import logging
from typing import List, Sequence

from ..config import Settings
from ..utils import parse_ingredient_list

try:  # pragma: no cover - optional dependency when running unit tests
    import google.generativeai as genai
    from google.generativeai.types import Part
except ModuleNotFoundError:  # pragma: no cover - handled gracefully at runtime
    genai = None
    Part = None  # type: ignore

LOGGER = logging.getLogger(__name__)


class GeminiVisionClient:
    """Minimal client encapsulating Gemini Vision interactions."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        if genai is None:
            raise RuntimeError(
                "google-generativeai package is required. Install dependencies before running the service."
            )
        if not settings.gemini_api_key:
            raise RuntimeError(
                "Missing Gemini API key. Set the GEMINI_API_KEY environment variable."
            )
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)

    @staticmethod
    def _encode_image(image_bytes: bytes, mime_type: str) -> Part:  # type: ignore[valid-type]
        if Part is None:  # pragma: no cover - guard for optional dependency
            raise RuntimeError("google-generativeai package not installed")
        return Part.from_bytes(image_bytes, mime_type=mime_type)

    def extract_ingredients(self, image_bytes: bytes, mime_type: str) -> List[str]:
        """Use Gemini to identify fridge ingredients present in *image_bytes*."""

        vision_prompt = (
            "You are assisting with meal planning. "
            "Identify every distinct ingredient visible in this fridge photo. "
            "Return a JSON array of ingredient names in lowercase. Limit the list to "
            f"{self._settings.max_ingredients} items."
        )
        response = self._model.generate_content(
            [self._encode_image(image_bytes, mime_type), vision_prompt]
        )
        text = response.text or ""
        ingredients = parse_ingredient_list(text)
        LOGGER.debug("Extracted ingredients: %s", ingredients)
        return ingredients

    def generate_recipe(
        self,
        ingredients: Sequence[str],
        dietary_preferences: str | None = None,
        allergies: str | None = None,
        cuisine: str | None = None,
        servings: int | None = None,
    ) -> str:
        """Generate a structured recipe response using text-only prompting."""

        if not ingredients:
            raise ValueError("Cannot generate recipe without any ingredients")

        preferences_block = []
        if dietary_preferences:
            preferences_block.append(f"Dietary preferences: {dietary_preferences}.")
        if allergies:
            preferences_block.append(f"Avoid: {allergies}.")
        if cuisine:
            preferences_block.append(f"Cuisine inspiration: {cuisine} cuisine.")
        if servings:
            preferences_block.append(f"Servings: {servings}.")

        joined_ingredients = ", ".join(sorted(ingredients))
        text_prompt = (
            "Create a recipe using the following fridge ingredients: "
            f"{joined_ingredients}. "
            "Provide the answer as a JSON object with keys 'title', 'summary', "
            "'ingredients' (array of strings), and 'steps' (array of objects with 'order' and 'instruction'). "
            "Ensure steps are detailed and actionable. "
        )
        if preferences_block:
            text_prompt += " ".join(preferences_block)

        response = self._model.generate_content(
            text_prompt,
            generation_config={"temperature": self._settings.temperature},
        )
        return response.text or ""


def detect_mime_type(uploaded_file) -> str:
    """Infer the MIME type of an uploaded file."""

    mime_type = getattr(uploaded_file, "content_type", "application/octet-stream")
    if mime_type == "application/octet-stream":
        name = getattr(uploaded_file, "filename", "") or ""
        if name.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        elif name.lower().endswith(".png"):
            mime_type = "image/png"
    return mime_type


def read_upload_bytes(uploaded_file) -> bytes:
    """Read an ``UploadFile`` into raw bytes."""

    data = uploaded_file.file.read()
    if isinstance(data, str):  # pragma: no cover - safeguard only
        data = data.encode()
    return data


__all__ = ["GeminiVisionClient", "detect_mime_type", "read_upload_bytes"]
