"""Utilidades para generación de IDs (chat gateway, etc.)."""
from datetime import datetime
from uuid import uuid4


def generate_request_id() -> str:
    """Genera un request_id único para el flujo chat (n8n). Formato: req_YYYYMMDDHHMMSS_shortuuid."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short_uuid = uuid4().hex[:8]
    return f"req_{timestamp}_{short_uuid}"
