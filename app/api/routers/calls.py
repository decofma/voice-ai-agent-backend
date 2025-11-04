# backend/app/api/routers/calls.py
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, status, WebSocket, WebSocketDisconnect
from app.schemas.call import CallTrigger, CallRecord
from app.services import data_store
from app.services.retell_service import RetellService, AGENT_DEFAULTS
from app.services.postprocessor import PostProcessor
import json
from app.core.config import settings
from google import genai
from google.genai import types
import traceback 

router = APIRouter(prefix="/calls", tags=["Calls"])

genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_retell_service():
    return RetellService()
def get_post_processor():
    return PostProcessor()

async def handle_call_analysis_in_background(post_processor: PostProcessor, call_data: dict):
    """
    Handle a Retell call analysis in the background.

    When a call analysis is finished, Retell sends a webhook to the `/retell-webhook` endpoint.
    This function is called by the FastAPI framework when it receives this webhook.
    It will fetch the call record associated with the given `retell_call_id` and update its status to "COMPLETED" and its outcome to the structured summary of the call.
    If any error occurs during the post-processing, it will update the call record status to "FAILED" and its outcome to an error message.

    Parameters:
    post_processor (PostProcessor): The PostProcessor instance used for extracting structured summaries from transcripts.
    call_data (dict): The data received from Retell's webhook, containing the call ID and the transcript of the call.

    Returns:
    None
    """
    retell_call_id = call_data.get('call_id')
    record = data_store.get_call_record_by_retell_id(retell_call_id)
    if not record: 
        print(f"ERRO (Post-Process): call_id {retell_call_id} não encontrado no data_store.")
        return
    agent_config = data_store.get_agent(record['agent_config_id'])
    if not agent_config: 
        print(f"ERRO (Post-Process): agent_config_id {record['agent_config_id']} não encontrado.")
        return
    
    transcript = "\n".join([f"{turn.get('role').upper()}: {turn.get('content')}" for turn in call_data.get('transcript', []) if turn.get('role') in ['agent', 'user']])
    try:
        structured_summary = await post_processor.extract_structured_summary(transcript=transcript, required_fields=agent_config['scenario_fields'])
        data_store.update_call_record(retell_call_id, {"call_status": "COMPLETED", "call_outcome": structured_summary.get("call_outcome", "UNKNOWN"), "full_transcript": transcript, "structured_summary": structured_summary})
    except HTTPException as e:
        data_store.update_call_record(retell_call_id, {"call_status": "FAILED", "call_outcome": "LLM_EXTRACTION_ERROR", "full_transcript": transcript, "structured_summary": e.detail})

@router.post("/trigger", status_code=status.HTTP_200_OK)
async def trigger_test_call(
    trigger: CallTrigger,
    retell: RetellService = Depends(get_retell_service)
):
    """
    Trigger a test call to the Retell API.

    Parameters:
    trigger (CallTrigger): The CallTrigger object containing the agent config ID, driver name, and load number.
    retell (RetellService): The RetellService instance used for triggering the web call.

    Returns:
    dict: A dictionary containing the message "Web call registered", the local call ID, the call ID, the access token, and the sample rate.

    Raises:
    HTTPException: If the agent is not found or not registered with Retell.
    """
    agent_config = data_store.get_agent(trigger.agent_config_id)
    if not agent_config or not agent_config.get("retell_agent_id"):
        raise HTTPException(status_code=404, detail="Agent not found or not registered with Retell.")
        
    retell_agent_id = agent_config["retell_agent_id"]
    dynamic_vars = {"driver_name": trigger.driver_name, "load_number": trigger.load_number}
    
    call_data = retell.trigger_web_call(
        agent_id=retell_agent_id, 
        dynamic_vars=dynamic_vars
    )
    
    new_call = data_store.create_call_record(
        trigger.model_dump() | {
            "retell_call_id": call_data["call_id"], 
            "call_status": "PENDING"
        }
    )
    
    return {
        "message": "Web call registered", 
        "local_call_id": new_call['id'], 
        "call_id": call_data["call_id"],
        "access_token": call_data["access_token"], 
        "sample_rate": 24000
    }

@router.post("/retell-webhook", status_code=status.HTTP_204_NO_CONTENT)
async def retell_webhook(request: Request, background_tasks: BackgroundTasks, retell: RetellService = Depends(get_retell_service), post_processor: PostProcessor = Depends(get_post_processor)):
    """
    Handles a Retell Webhook.

    Retell sends webhooks to this endpoint with event types "call_analyzed".
    When a call analysis is finished, Retell sends a webhook to this endpoint.
    This function is called by the FastAPI framework when it receives this webhook.
    It will fetch the call record associated with the given `retell_call_id` and update its status to "COMPLETED" and its outcome to the structured summary of the call.
    If any error occurs during the post-processing, it will update the call record status to "FAILED" and its outcome to an error message.

    Parameters:
    request (Request): The FastAPI request object.
    background_tasks (BackgroundTasks): The FastAPI background tasks object.
    retell (RetellService): The RetellService instance used for triggering the web call.
    post_processor (PostProcessor): The PostProcessor instance used for extracting structured summaries from transcripts.

    Returns:
    None
    """
    body = await request.body()
    signature = request.headers.get("x-retell-signature")
    
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event = payload.get("event")
    call_data = payload.get("call", {})

    if event == "call_analyzed":
        background_tasks.add_task(handle_call_analysis_in_background, post_processor, call_data)
        
    return

@router.get("/results", response_model=list[CallRecord])
async def get_call_results():
    return [CallRecord.model_validate(r) for r in data_store.get_all_call_records()]
