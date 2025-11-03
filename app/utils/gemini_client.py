"""
Gemini API client wrapper for LLM operations with model fallback
"""
import google.generativeai as genai
import os
import json
import logging
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from a local .env file if present
# This allows running the app without exporting variables system-wide
load_dotenv()

DEFAULT_GEMINI_MODELS: List[str] = [
    # Newest to oldest, fastest to safest
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    # Final fallback to existing default used in project
    "gemini-1.5-flash",
]

def _get_candidate_models_from_env() -> List[str]:
    """Parse GEMINI_MODELS env var as a comma-separated list, or return defaults."""
    env_value = os.getenv("GEMINI_MODELS")
    if not env_value:
        return DEFAULT_GEMINI_MODELS
    models = [m.strip() for m in env_value.split(",") if m.strip()]
    return models or DEFAULT_GEMINI_MODELS

class GeminiClient:
    """Wrapper for Google Gemini API with automatic model fallback."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.candidate_models: List[str] = _get_candidate_models_from_env()
        logger.info(
            "✅ Gemini client initialized with model candidates: %s",
            ", ".join(self.candidate_models),
        )

    def _generate_with_fallback(self, prompt: str) -> Tuple[str, str]:
        """Try models in order until one succeeds. Returns (text, model_used)."""
        last_error: str | None = None
        for model_name in self.candidate_models:
            try:
                logger.debug("Trying Gemini model %s", model_name)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = (response.text or "").strip()
                if not text:
                    raise ValueError("Empty response text")
                return text, model_name
            except Exception as e:
                last_error = str(e)
                logger.warning("Model %s failed: %s. Trying next...", model_name, e)
        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    async def generate_text(self, prompt: str) -> str:
        """Generate text using Gemini with model fallback."""
        text, model_used = self._generate_with_fallback(prompt)
        logger.info("🧠 Gemini text generated via model: %s", model_used)
        return text

    async def generate_json(self, prompt: str) -> Dict[str, Any]:
        """Generate JSON using Gemini with model fallback and robust parsing."""
        # Enforce JSON-only response
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON, no additional text."
        raw_text, model_used = self._generate_with_fallback(json_prompt)

        # Clean response (remove markdown code blocks if present)
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            logger.info("🧠 Gemini JSON generated via model: %s", model_used)
            return parsed
        except json.JSONDecodeError as e:
            logger.error("❌ JSON parsing error: %s", e)
            logger.error("Raw response from %s: %s", model_used, raw_text)
            return {}

# Singleton instance
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client singleton"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client