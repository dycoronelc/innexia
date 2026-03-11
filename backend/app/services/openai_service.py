import os
import openai
from openai import AsyncOpenAI
from ..config import settings

# Configurar OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cliente asíncrono para OpenAI
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"
)

