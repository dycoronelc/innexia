import os
from openai import AsyncOpenAI
from ..config import settings

# Cliente asíncrono para OpenAI (v2.x: api_key solo en el constructor)
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None) or "",
    base_url="https://api.openai.com/v1"
)

