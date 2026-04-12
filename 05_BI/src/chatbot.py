"""Gemini-powered chatbot logic for dashboard Q&A.

The chatbot answers from compact dashboard context only. It does not use web
search, external retrieval, or hidden data sources.
"""

from __future__ import annotations

from typing import Any

from src.gemini_client import generate_text
from src.insights_engine import context_to_json


def _format_chat_history(chat_history: list[dict[str, str]], *, max_messages: int = 8) -> str:
    """Format recent chat history into a compact text transcript."""
    if not chat_history:
        return "No prior chat history."

    recent_history = chat_history[-max_messages:]
    lines: list[str] = []
    for message in recent_history:
        role = str(message.get("role", "user")).strip().lower()
        content = str(message.get("content", "")).strip()
        if not content:
            continue
        role_label = "User" if role == "user" else "Assistant"
        lines.append(f"{role_label}: {content}")

    return "\n".join(lines) if lines else "No prior chat history."


def _build_chat_prompt(
    *,
    context: dict[str, Any],
    chat_history: list[dict[str, str]],
    user_question: str,
) -> str:
    """Build the chatbot prompt with strict grounding constraints."""
    history_text = _format_chat_history(chat_history)

    return f"""
You are an analytics copilot for a Tunisia real-estate demand intelligence platform.

Response rules:
1. Use only the provided dashboard context.
2. Never invent numbers, projects, cities, or outcomes.
3. If data is insufficient, explicitly say what is missing.
4. Be concise and practical (roughly 80-140 words unless user asks for detail).
5. Prefer bullets when comparing options.

Dashboard context (JSON):
{context_to_json(context)}

Recent conversation:
{history_text}

User question:
{user_question}
""".strip()


def answer_question_from_context(
    *,
    user_question: str,
    context: dict[str, Any],
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    """Answer a user question using only dashboard context + recent history."""
    question = (user_question or "").strip()
    if not question:
        raise ValueError("User question cannot be empty.")

    prompt = _build_chat_prompt(
        context=context,
        chat_history=chat_history or [],
        user_question=question,
    )
    return generate_text(prompt)
