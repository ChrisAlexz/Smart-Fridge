"""Tests for response parsing utilities."""
from __future__ import annotations

import json

import pytest

from app.utils import extract_json_block, parse_ingredient_list


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Here is JSON: [\"milk\", \"eggs\"]", ["milk", "eggs"]),
        (json.dumps({"ingredients": ["Milk", "Eggs", "Butter", "milk"]}), ["Milk", "Eggs", "Butter"]),
        ("Milk, Eggs, Butter", ["Milk", "Eggs", "Butter"]),
    ],
)
def test_parse_ingredient_list(text, expected):
    assert parse_ingredient_list(text) == expected


def test_extract_json_block_first_object():
    payload = """
    Commentary before JSON
    {
        "title": "Example"
    }
    Extra details after JSON
    """
    result = extract_json_block(payload)
    assert json.loads(result)["title"] == "Example"


@pytest.mark.parametrize(
    "text",
    [
        "No JSON here",
        "Random text without braces",
    ],
)
def test_extract_json_block_errors(text):
    with pytest.raises(ValueError):
        extract_json_block(text)
