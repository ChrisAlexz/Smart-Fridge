# MyFridge — Smart Meal Generator

Turn photos of your fridge into actionable recipes. The Smart Meal Generator uses
[Gemini Vision](https://ai.google.dev/gemini-api/docs/vision) to identify ingredients
inside an uploaded image and then crafts a step-by-step recipe using a FastAPI service.

## Features

- **Gemini Vision ingredient detection** – send a fridge photo and receive a curated
  list of available ingredients.
- **Recipe generation** – transform the detected ingredients into a ready-to-cook
  recipe complete with summary and instructions.
- **FastAPI backend** – lightweight REST API that can be containerised or deployed on
  any ASGI-compatible platform.

## Project Structure

```
.
├── app
│   ├── config.py             # Environment based configuration
│   ├── main.py               # FastAPI application entrypoint
│   ├── models.py             # Pydantic response models
│   ├── routes.py             # API routing
│   ├── services
│   │   ├── gemini.py         # Gemini Vision integration helpers
│   │   └── meal_planner.py   # High level orchestration logic
│   └── utils
│       └── parsing.py        # Helpers to parse Gemini responses
├── requirements.txt
└── tests
    └── test_parsing.py       # Unit tests for parsing helpers
```

## Getting Started

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**

   The application reads settings from environment variables (or a `.env` file).
   At minimum set your Gemini API key:

   ```bash
   export GEMINI_API_KEY="your_api_key"
   ```

   Optional configuration:

   - `GEMINI_MODEL` – Gemini model name (defaults to `gemini-1.5-flash`).
   - `MAX_INGREDIENTS` – Maximum number of ingredients to request from Gemini.
   - `TEMPERATURE` – Temperature value for recipe generation creativity.

3. **Run the API locally**

   ```bash
   uvicorn app.main:app --reload
   ```

   Visit `http://localhost:8000/docs` to experiment with the interactive Swagger UI.

## Usage

Send a `POST` request to `/api/recipes/from-fridge` with a multipart body containing
an image file and optional metadata:

```bash
curl -X POST \
  -F "file=@/path/to/fridge.jpg" \
  -F "dietary_preferences=vegetarian" \
  -F "allergies=peanuts" \
  http://localhost:8000/api/recipes/from-fridge
```

The response includes the recipe title, summary, cleaned ingredient list, and
step-by-step instructions.

## Testing

Unit tests focus on deterministic parsing helpers. Run them with:

```bash
pytest
```

## Notes

- The service requires network access to call the Gemini API; ensure outbound access
  is permitted in your deployment environment.
- Gemini responses can vary. The parsing utilities attempt to be resilient but you
  may want to add additional validation or fallback logic in production.
