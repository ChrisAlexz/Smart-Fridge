"""Utility helpers for parsing Gemini model responses."""
from __future__ import annotations

import json
import re
from typing import Iterable, List


JSON_BLOCK_PATTERN = re.compile(r"\{.*\}|\[.*\]", re.DOTALL)


def extract_json_block(text: str) -> str:
    """Extract the first JSON block found inside *text*.

    Gemini models sometimes wrap JSON payloads with additional commentary. This helper
    looks for the first ``{...}`` or ``[...]`` block in the response so that callers can
    safely parse the relevant data portion.
    """

    match = JSON_BLOCK_PATTERN.search(text)
    if not match:
        raise ValueError("Response does not contain a JSON object or array")
    return match.group(0)


def parse_ingredient_list(text: str) -> List[str]:
    """Parse and sanitize a list of ingredients emitted by Gemini.

    Parameters
    ----------
    text:
        Raw model response. May contain JSON arrays or comma-separated strings.
    """

    cleaned: List[str]
    try:
        json_block = extract_json_block(text)
        data = json.loads(json_block)
        if isinstance(data, dict) and "ingredients" in data:
            ingredients = data["ingredients"]
        else:
            ingredients = data
        if not isinstance(ingredients, Iterable):  # type: ignore[unreachable]
            raise TypeError
        cleaned = [
            item.strip()
            for item in ingredients
            if isinstance(item, str) and item.strip()
        ]
    except (ValueError, json.JSONDecodeError, TypeError):
        parts = re.split(r"[,\n]", text)
        cleaned = [part.strip() for part in parts if part.strip()]

    unique_ingredients = []
    seen = set()
    for ingredient in cleaned:
        lower = ingredient.lower()
        if lower not in seen:
            unique_ingredients.append(ingredient)
            seen.add(lower)
    return unique_ingredients


__all__ = ["extract_json_block", "parse_ingredient_list"]
