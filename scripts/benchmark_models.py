import urllib.request
import time
import json
import sys

# The models available based on your screenshot
MODELS = ["qwen3:4b", "llama3:latest", "gemma:7b"]
OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT = """
You are an AI assistant for a Building Management System. 
The user says: "cool down the conference room".
Output a JSON object with this exact structure:
{
  "action_type": "HVAC_SETPOINT_UPDATE",
  "proposal": {
    "zone_id": "Z2",
    "setpoint": 20.0,
    "hvac_mode": "COOLING"
  },
  "confidence": 0.85
}
Return ONLY valid JSON.
"""

def test_model(model_name):
    print(f"\n--- Testing {model_name} ---")
    start_time = time.time()
    
    try:
        req = urllib.request.Request(
            OLLAMA_URL, 
            data=json.dumps({
                "model": model_name,
                "prompt": PROMPT,
                "stream": False,
                "format": "json"
            }).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response_obj:
            response_data = response_obj.read().decode('utf-8')
    except Exception as e:
        print(f"Error calling model: {e}")
        return False
        
    end_time = time.time()
    latency = end_time - start_time
    
    data = json.loads(response_data)
    output_text = data.get("response", "").strip()
    
    print(f"Latency: {latency:.2f} seconds")
    print(f"Response:\n{output_text}")
    
    # Verify if it's valid JSON
    try:
        parsed = json.loads(output_text)
        if "action_type" in parsed:
            print("[PASS] Valid JSON Schema!")
            return True
        else:
            print("[FAIL] Invalid Schema")
            return False
    except json.JSONDecodeError:
        print("[FAIL] Not valid JSON")
        return False

def check_gpu():
    print("\n--- Checking Running Models (GPU Usage) ---")
    try:
        # ollama ps shows if models are loaded in memory/VRAM
        import subprocess
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Could not run 'ollama ps': {e}")

if __name__ == "__main__":
    print("Starting Model Benchmark...")
    results = {}
    for model in MODELS:
        success = test_model(model)
        results[model] = success
        
    print("\n=== Summary ===")
    for model, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{model}: {status}")
        
    check_gpu()
