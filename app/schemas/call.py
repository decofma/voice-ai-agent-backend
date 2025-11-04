# backend/app/schemas/call.py
from pydantic import BaseModel
from typing import Dict, Any, Literal

class CallTrigger(BaseModel):
    agent_config_id: int
    driver_name: str
    driver_phone: str 
    load_number: str

class CallRecord(BaseModel):
    id: int
    agent_config_id: int
    driver_name: str
    driver_phone: str
    load_number: str
    retell_call_id: str
    call_status: Literal['PENDING', 'ANALYZING', 'COMPLETED', 'FAILED'] = 'PENDING'
    call_outcome: str | None = None
    structured_summary: Dict[str, Any] | None = None
    full_transcript: str | None = None

    class Config:
        from_attributes = True