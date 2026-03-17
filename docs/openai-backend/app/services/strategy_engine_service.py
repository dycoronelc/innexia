from __future__ import annotations

import httpx

from app.core.config import settings


async def call_n8n_strategy_engine(payload: dict) -> dict:
    timeout = httpx.Timeout(settings.n8n_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(settings.n8n_webhook_url, json=payload)
        response.raise_for_status()
        return response.json()
