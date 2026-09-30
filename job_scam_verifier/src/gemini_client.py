"""
Thin wrapper around google-generativeai so the rest of the app doesn't
need to know SDK details. Centralizing this also makes it easy to swap
models or add retry/error-handling logic in one place.
"""

import os
import json
import google.generativeai as genai

# NOTE: Gemini model names change over time. If this model errors out
# ("not found" / 404), check https://ai.google.dev/gemini-api/docs/models
# for the current list and update the sidebar / this default.
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


class GeminiClient:
    def __init__(self, api_key: str, model_name: str = None):
        if not api_key:
            raise ValueError("Gemini API key is required.")
        genai.configure(api_key=api_key)
        self.model_name = model_name or DEFAULT_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    def generate_json(self, prompt: str, temperature: float = 0.2) -> dict:
        """Ask Gemini for structured JSON output and parse it defensively."""
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "response_mime_type": "application/json",
            },
        )
        text = (response.text or "").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: strip markdown code fences if the model added them anyway.
            cleaned = text.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            return json.loads(cleaned)

    def generate_text(self, prompt: str, temperature: float = 0.3) -> str:
        response = self.model.generate_content(
            prompt, generation_config={"temperature": temperature}
        )
        return (response.text or "").strip()
