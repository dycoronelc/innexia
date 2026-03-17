import httpx

from app.core.config import settings


class N8NService:
    async def trigger_strategy_workflow(self, payload: dict) -> None:
        timeout = httpx.Timeout(settings.N8N_TIMEOUT_SECONDS)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(settings.N8N_WEBHOOK_URL, json=payload)
            response.raise_for_status()
