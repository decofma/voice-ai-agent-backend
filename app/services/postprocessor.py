# backend/app/services/postprocessor.py
import json
from google import genai
from google.genai import types
from app.core.config import settings
from typing import Dict, Any, Literal
from fastapi import HTTPException

class PostProcessor:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
             raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured.")
        self.llm_client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def extract_structured_summary(self, transcript: str, required_fields: Dict[str, Literal['text', 'boolean']]) -> Dict[str, Any]:
               
        """
        Extracts structured summary from a call transcript using the Google Gemini AI model.

        Args:
            transcript (str): The call transcript to extract the structured summary from.
            required_fields (Dict[str, Literal['text', 'boolean']]): A dictionary containing the names of the fields to extract and their types.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted structured summary.

        Raises:
            HTTPException: If the Gemini AI model returns an error or if a general exception occurs.
        """
        properties_schema = {}
        for k, v in required_fields.items():
             properties_schema[k] = {
                 "type": "boolean" if v == "boolean" else "string",
                 "description": f"Extracted value for {k}. Must be 'true' or 'false' for boolean types."
             }
        
        response_schema = types.Schema(
            type=types.Type.OBJECT,
            properties=properties_schema,
            required=list(required_fields.keys())
        )
        
        extraction_prompt = f"""
        You are an expert logistics data extractor. Your sole task is to analyze the call transcript
        and extract all requested fields in JSON format.

        - **STRICTLY ADHERE to the provided JSON schema. DO NOT add extra text.**
        - RULE: If a field cannot be determined from the transcript, use "N/A", "None", or 'false' (if boolean).

        # Call Transcript:
        ---
        {transcript}
        ---
        """
        
        try:
            response = self.llm_client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=extraction_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.0
                ),
            )
            
            raw_json_string = response.text.strip()
            return json.loads(raw_json_string)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail={"call_outcome": "FAILED_GEMINI_EXTRACTION", "error_details": str(e)})