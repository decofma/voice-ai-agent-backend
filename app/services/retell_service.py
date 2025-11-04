# backend/app/services/retell_service.py
from retell import Retell, APIError 
from app.core.config import settings
from fastapi import HTTPException
from typing import Dict, Any

AGENT_DEFAULTS = {
    "enable_backchannel": True,
    "backchannel_frequency": 0.9, 
    "interruption_sensitivity": 0.05, 
}

class RetellService:
    def __init__(self):
        self.client = Retell(api_key=settings.RETELL_API_KEY)

    def create_agent(self, name: str, system_prompt: str) -> str:
        
        """
        Creates a Retell LLM (brain) and an associated Retell Agent (voice)
        given a system prompt and a name for the agent.

        Args:
            name (str): The name of the agent to be created.
            system_prompt (str): The system prompt to be used by the LLM.

        Returns:
            str: The ID of the created Retell Agent.

        Raises:
            HTTPException: If the Retell API returns an error or if a general exception occurs.
        """
        try:
            llm = self.client.llm.create(
                general_prompt=system_prompt,
                start_speaker="agent" 
            )
            
            print(f"DEBUG: (Passo 1) Cérebro LLM criado. LLM ID: {llm.llm_id}")

            response_engine = {
                "type": "retell-llm",
                "llm_id": llm.llm_id,
            }

            agent = self.client.agent.create(
                agent_name=name,
                response_engine=response_engine,
                voice_id="11labs-Adrian", 
                **AGENT_DEFAULTS
            )
            
            print(f"DEBUG: (Passo 2) Agente Retell criado. ID: {agent.agent_id}")
            return agent.agent_id
            
        except APIError as e:
            error_message = str(e)
            print(f"RETELL API ERROR (create_agent): {error_message}") 
            raise HTTPException(status_code=500, detail=f"Retell API Error (create_agent): {error_message}")
        except Exception as e:
            error_message = str(e)
            print(f"GENERAL ERROR (create_agent): {e}")
            raise HTTPException(status_code=500, detail=f"General Error (create_agent): {e}")
        
    def trigger_web_call(self, agent_id: str, dynamic_vars: dict) -> Dict[str, str]:
        """
        Triggers a web call for the given Retell Agent ID and dynamic variables.

        Args:
            agent_id (str): The ID of the Retell Agent to trigger the web call for.
            dynamic_vars (dict): A dictionary containing the dynamic variables to be passed to the Retell Agent.

        Returns:
            dict: A dictionary containing the call ID and access token for the triggered web call.

        Raises:
            HTTPException: If the Retell API returns an error or if a general exception occurs.
        """
        try:
            web_call_response = self.client.call.create_web_call(
                agent_id=agent_id, 
                retell_llm_dynamic_variables=dynamic_vars,
            )
            
            return {
                "call_id": web_call_response.call_id,
                "access_token": web_call_response.access_token
            }
            
        except APIError as e:
            error_message = str(e)
            print(f"RETELL API ERROR (trigger_web_call): {error_message}") 
            raise HTTPException(status_code=500, detail=f"Retell API Error (trigger_web_call): {error_message}")
        except Exception as e:
            error_message = str(e)
            print(f"GENERAL ERROR (trigger_web_call): {error_message}")
            raise HTTPException(status_code=500, detail=f"General Error (trigger_web_call): {error_message}")

    def verify_signature(self, payload: bytes, signature: str):
        """
        Verifies the signature of a Retell Webhook payload.

        Args:
            payload (bytes): The payload of the Retell Webhook.
            signature (str): The signature of the Retell Webhook.

        Raises:
            HTTPException: If the signature is invalid.
        """
        try:
             self.client.verify_webhook_signature(payload, settings.RETELL_API_KEY, signature)
        except Exception as e:
            raise HTTPException(status_code=403, detail="Invalid Webhook Signature")