from __future__ import annotations

import asyncio
from typing import Dict, Set

import httpx

# Request queueing: limit concurrent requests per model to prevent overload
MODEL_SEMAPHORES: Dict[str, asyncio.Semaphore] = {}

# Cache for configured capacities (max_concurrent) for each model
MODEL_CAPACITIES: Dict[str, int] = {}

# Cache of GitHub Models that returned "unknown_model".
# Prevents repeated network calls/log spam for invalid IDs.
UNSUPPORTED_GITHUB_MODELS: Set[str] = set()

_UNSUPPORTED_MODELS_LOCK = asyncio.Lock()

# Shared HTTP client for outbound requests
_HTTP_CLIENT: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """Return a shared httpx AsyncClient for outbound requests."""
    global _HTTP_CLIENT
    if _HTTP_CLIENT is None:
        _HTTP_CLIENT = httpx.AsyncClient(
            timeout=600.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )
    return _HTTP_CLIENT


async def close_http_client() -> None:
    """Close the shared httpx AsyncClient if it exists."""
    global _HTTP_CLIENT
    if _HTTP_CLIENT is not None:
        await _HTTP_CLIENT.aclose()
        _HTTP_CLIENT = None


async def mark_model_unsupported(model_id: str) -> None:
    """Mark a GitHub model as unsupported."""
    async with _UNSUPPORTED_MODELS_LOCK:
        UNSUPPORTED_GITHUB_MODELS.add(model_id)
