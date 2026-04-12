"""Gemini API client helpers for Streamlit AI features.

How this integration works:
- API key is read from `GEMINI_API_KEY` first, then `GOOGLE_API_KEY`.
- A reusable client instance is created once and cached.
- Model name is centralized in `GEMINI_MODEL_NAME`.

To switch the model used by the app:
- Change `GEMINI_MODEL_NAME` below, or
- set the `GEMINI_MODEL` environment variable.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

# Fast default model for dashboard insight generation and chat interactions.
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def _load_project_dotenv() -> None:
    """Load `.env` from project root into `os.environ` if present.

    This lightweight loader avoids an extra dependency and only sets variables
    that are not already defined in the environment.
    """
    project_root = Path(__file__).resolve().parent.parent
    dotenv_path = project_root / ".env"
    if not dotenv_path.exists():
        return

    try:
        raw_lines = dotenv_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return

    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if not key:
            continue

        os.environ.setdefault(key, value)


def get_gemini_api_key() -> str:
    """Return API key from environment variables.

    Raises:
        RuntimeError: when no supported environment variable is configured.
    """
    _load_project_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment."
        )
    return api_key


def _load_genai_module() -> Any:
    """Load Google GenAI SDK lazily with a clear install error."""
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - depends on local env setup
        raise RuntimeError(
            "The google-genai package is not installed. Install dependencies with `pip install -r requirements.txt`."
        ) from exc
    return genai


@lru_cache(maxsize=1)
def get_gemini_client() -> Any:
    """Create and cache a reusable Gemini client instance."""
    genai = _load_genai_module()
    return genai.Client(api_key=get_gemini_api_key())


def _extract_text_from_response(response: Any) -> str:
    """Extract text safely from Gemini SDK response objects."""
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    collected_parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text.strip():
                collected_parts.append(part_text.strip())

    return "\n".join(collected_parts).strip()


def generate_text(prompt: str, *, model_name: str | None = None) -> str:
    """Generate text from Gemini using the configured model.

    Args:
        prompt: Fully prepared prompt with instructions + context.
        model_name: Optional override for model selection.

    Raises:
        RuntimeError: if the request fails or Gemini returns empty output.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string.")

    _load_project_dotenv()
    model = model_name or os.getenv("GEMINI_MODEL", GEMINI_MODEL_NAME)
    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
    except Exception as exc:  # pragma: no cover - depends on API/network
        raise RuntimeError(f"Gemini request failed: {exc}") from exc

    output_text = _extract_text_from_response(response)
    if not output_text:
        raise RuntimeError("Gemini returned an empty response.")

    return output_text
