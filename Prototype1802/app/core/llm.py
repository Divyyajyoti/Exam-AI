"""
Central LLM Service for Exam AI
- chat generation
- embeddings
- safe fallback for demo
"""

from __future__ import annotations
from typing import List, Optional
import time

from openai import OpenAI
from openai import OpenAIError

from app.core.config import settings

_client: Optional[OpenAI] = None


def _client_instance() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY or None)
    return _client


def chat_completion(system: str, user: str, model: str = None, temperature: float = 0.3) -> str:
    if settings.DEMO_MODE:
        return (
            "DEMO_MODE is ON. No OpenAI calls are made.\n\n"
            "Provide OPENAI_API_KEY (and billing) to enable real predictions."
        )

    c = _client_instance()
    resp = c.chat.completions.create(
        model=model or settings.MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content


def safe_llm(system: str, user: str, model: str = None, temperature: float = 0.3) -> str:
    """
    Never crashes your app. On errors, returns a readable message.
    """
    # very small retry
    for attempt in range(2):
        try:
            return chat_completion(system, user, model=model, temperature=temperature)
        except OpenAIError as e:
            if attempt == 0:
                time.sleep(0.8)
                continue
            return f"[LLM_ERROR] {str(e)}"
        except Exception as e:
            return f"[UNEXPECTED_ERROR] {str(e)}"


def embed(texts):
    """
    Returns list of embeddings. If DEMO_MODE or missing key, returns empty.
    """
    if settings.DEMO_MODE or not settings.OPENAI_API_KEY:
        return []

    if isinstance(texts, str):
        texts = [texts]

    c = _client_instance()
    res = c.embeddings.create(model=settings.EMBEDDING_MODEL, input=texts)
    return [d.embedding for d in res.data]
