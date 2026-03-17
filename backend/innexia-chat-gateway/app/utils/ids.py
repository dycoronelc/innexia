from datetime import datetime
from uuid import uuid4



def generate_request_id() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short_uuid = uuid4().hex[:8]
    return f"req_{timestamp}_{short_uuid}"
