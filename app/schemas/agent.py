# backend/app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Dict, Any, Literal

class AgentConfigBase(BaseModel):
    name: str = Field(..., max_length=100)
    system_prompt: str
    scenario_fields: Dict[str, Literal['text', 'boolean']] = Field(..., description="A dictionary containing the names of the fields to extract and their types.")

class AgentConfig(AgentConfigBase):
    id: int
    retell_agent_id: str | None = None

    class Config:
        from_attributes = True