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
import re
from typing import Any

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
FALLBACK_GEMINI_MODEL = "gemini-2.5-flash"

# Default model for dashboard insight generation and chat interactions.
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)


def _read_project_dotenv() -> dict[str, str]:
    """Read project-root `.env` into a dictionary without mutating `os.environ`."""
    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / ".env"
    if not dotenv_path.exists():
        return {}

    try:
        raw_lines = dotenv_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    values: dict[str, str] = {}

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

        values[key] = value

    return values


def get_gemini_api_key() -> str:
    """Return API key from environment variables.

    Raises:
        RuntimeError: when no supported environment variable is configured.
    """
    dotenv_values = _read_project_dotenv()
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or dotenv_values.get("GEMINI_API_KEY")
        or dotenv_values.get("GOOGLE_API_KEY")
    )
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


@lru_cache(maxsize=8)
def _get_gemini_client_for_key(api_key: str) -> Any:
    """Create and cache Gemini client instances by API key."""
    genai = _load_genai_module()
    return genai.Client(api_key=api_key)


def get_gemini_client() -> Any:
    """Return a Gemini client bound to the current configured API key."""
    api_key = get_gemini_api_key()
    return _get_gemini_client_for_key(api_key)


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


def _extract_retry_seconds(message: str) -> int | None:
    """Extract retry delay in seconds from API error text when present."""
    match = re.search(r"retry in\s+([0-9]+(?:\.[0-9]+)?)s", message, flags=re.IGNORECASE)
    if not match:
        return None
    try:
        return max(1, int(float(match.group(1))))
    except (TypeError, ValueError):
        return None


def _is_resource_exhausted_error(exc: Exception) -> bool:
    upper = str(exc).upper()
    return "RESOURCE_EXHAUSTED" in upper or "QUOTA EXCEEDED" in upper


def _to_friendly_request_error(exc: Exception) -> str:
    """Convert raw SDK exceptions to concise actionable messages."""
    raw = str(exc)
    upper = raw.upper()

    if "RESOURCE_EXHAUSTED" in upper or "QUOTA EXCEEDED" in upper:
        retry_seconds = _extract_retry_seconds(raw)
        retry_text = f" Retry after about {retry_seconds}s." if retry_seconds else ""
        return (
            "Gemini quota exceeded (HTTP 429 RESOURCE_EXHAUSTED). "
            "The API key is valid, but the linked Google project has no remaining quota."
            f"{retry_text} "
            "Check quota/billing in Google AI Studio or switch to a key from a project with available quota."
        )

    if "API_KEY_INVALID" in upper or ("INVALID_ARGUMENT" in upper and "API KEY" in upper):
        return (
            "Gemini API key is invalid for this endpoint. "
            "Use a valid key from Google AI Studio and set GEMINI_API_KEY or GOOGLE_API_KEY."
        )

    if "PERMISSION_DENIED" in upper:
        return (
            "Gemini access is denied for this project/key. "
            "Enable Gemini API access for the project and verify key restrictions."
        )

    return f"Gemini request failed: {raw}"


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

    dotenv_values = _read_project_dotenv()
    model = model_name or os.getenv("GEMINI_MODEL") or dotenv_values.get("GEMINI_MODEL") or GEMINI_MODEL_NAME
    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
    except Exception as exc:  # pragma: no cover - depends on API/network
        # Practical MVP resilience: if a chosen model is quota-exhausted,
        # retry once on a known fallback model.
        if model != FALLBACK_GEMINI_MODEL and _is_resource_exhausted_error(exc):
            try:
                response = client.models.generate_content(
                    model=FALLBACK_GEMINI_MODEL,
                    contents=prompt,
                )
            except Exception as fallback_exc:  # pragma: no cover - depends on API/network
                raise RuntimeError(_to_friendly_request_error(fallback_exc)) from fallback_exc
        else:
            raise RuntimeError(_to_friendly_request_error(exc)) from exc

    output_text = _extract_text_from_response(response)
    if not output_text:
        raise RuntimeError("Gemini returned an empty response.")

    return output_text
