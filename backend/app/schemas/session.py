from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionResponse(BaseModel):
    id: str
    user_id: int
    device_info: Optional[str] = None
    device_name: Optional[str] = None
    is_trusted_device: bool
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True
