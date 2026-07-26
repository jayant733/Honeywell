import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "http://127.0.0.1:8000/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3-14b-instruct")

client = AsyncOpenAI(
    base_url=QWEN_BASE_URL,
    api_key="sk-no-key-required"
)

async def ask_local_llm_for_setpoint(telemetry: dict):
    """
    Sends the current building state to the local LLM and asks for optimal setpoints.
    Expects a JSON response.
    """
    prompt = f"""
    You are an autonomous Building Management System AI. 
    Current Building State:
    {json.dumps(telemetry, indent=2)}

    Based on the current occupancy, temperature, and carbon intensity, decide the optimal HVAC setpoints for Z1 and Z2 to balance comfort and energy.
    You must return a valid JSON object in the following format exactly, with no markdown or extra text:
    {{
        "Z1_setpoint": 22.0,
        "Z2_setpoint": 21.5,
        "rationale": "Brief reason for your decision"
    }}
    """
    
    try:
        response = await client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": "You are a JSON-only API. You must output raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150,
            # response_format={ "type": "json_object" } # Not all local endpoints support this, so we rely on system prompt
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        return json.loads(content)
        
    except Exception as e:
        print(f"LLM Error: {e}")
        # Fallback to safe defaults if the LLM fails or the user doesn't have it running yet
        return {
            "Z1_setpoint": 22.0,
            "Z2_setpoint": 22.0,
            "rationale": f"Fallback to safe defaults due to model error: {str(e)}"
        }
