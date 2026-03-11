"""
Cliente OpenAI opcional. Si openai no está instalado (ej. cuando se usa n8n), openai_client será None.
"""
import os
from ..config import settings

openai_client = None

try:
    from openai import AsyncOpenAI
    openai_client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None) or "",
        base_url="https://api.openai.com/v1"
    )
except ImportError:
    pass  # OpenAI se usa vía n8n; el backend no necesita el cliente
