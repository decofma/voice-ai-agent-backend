# backend/app/api/routers/agents.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.agent import AgentConfig, AgentConfigBase
from app.services import data_store
from app.services.retell_service import RetellService 

router = APIRouter(prefix="/agents", tags=["Agents"])

def get_retell_service():
    return RetellService()

@router.post("/", response_model=AgentConfig, status_code=status.HTTP_201_CREATED)
async def create_agent_config(
    config: AgentConfigBase,
    retell: RetellService = Depends(get_retell_service) 
):
    """
    Creates a new agent configuration.

    Parameters:
    config (AgentConfigBase): The base configuration data for the agent.
    retell (RetellService): The RetellService instance used for creating the agent.

    Returns:
    AgentConfig: The created agent configuration.
    """
    retell_agent_id = retell.create_agent(
        name=config.name, 
        system_prompt=config.system_prompt
    )
    
    new_config_data = config.model_dump()
    new_config_data["retell_agent_id"] = retell_agent_id
    
    new_config = data_store.create_agent(new_config_data) 
    
    return AgentConfig.model_validate(new_config)

@router.get("/", response_model=list[AgentConfig])
async def get_all_agents():
    """
    Retrieves all existing agent configurations.

    Returns:
    list[AgentConfig]: A list of all existing agent configurations.
    """
    return [AgentConfig.model_validate(a) for a in data_store.get_all_agents()]