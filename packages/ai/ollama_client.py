"""Ollama Local Integration Client."""
import httpx
import json
import time
import traceback
from pathlib import Path
from typing import Any
from packages.ai.schemas import DecisionProposalV1

class OllamaClient:
    def __init__(self, config_path: Path):
        self.base_url = "http://localhost:11434"
        self.models_to_bench = ["llama3:latest", "qwen3:4b", "gemma:7b"]
        self.selected_model = None
        self.config_path = config_path

        # 1. Detect Ollama
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            resp.raise_for_status()
            tags = resp.json().get("models", [])
            self.installed_models = [m["name"] for m in tags]
            print(f"[Ollama] Detected installed models: {self.installed_models}")
        except Exception as e:
            print(f"[Ollama] Failed to detect Ollama at {self.base_url}: {e}")
            raise

        # 2. Benchmark
        self.selected_model = self._benchmark_and_select()
        if not self.selected_model:
            raise RuntimeError("No model passed the benchmark!")

    def _benchmark_and_select(self):
        # We need a quick prompt to test valid JSON
        # Give the schema strictly
        test_prompt = "You are a test AI. Output ONLY a JSON object with 'rationale' (string), 'actuator_id' (string), 'target_value' (float), and 'confidence_score' (float)."
        
        results = []
        for model in self.models_to_bench:
            if model not in self.installed_models:
                print(f"[Ollama] Skipping {model}, not installed.")
                continue
                
            print(f"[Ollama] Benchmarking {model}...")
            start_time = time.time()
            payload = {
                "model": model,
                "prompt": test_prompt,
                "format": "json",
                "stream": False
            }
            try:
                resp = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=60.0)
                resp.raise_for_status()
                data = resp.json()
                latency = time.time() - start_time
                response_text = data.get("response", "")
                eval_tokens = data.get("eval_count", 1)
                
                # Check valid JSON
                parsed = json.loads(response_text)
                DecisionProposalV1.model_validate(parsed)
                tps = eval_tokens / latency if latency > 0 else 0
                results.append((latency, model, tps))
                print(f"  [OK] {model}: {latency:.2f}s, {tps:.1f} tok/s")
            except Exception as e:
                print(f"  [FAIL] {model}: {e}")
                
        if results:
            results.sort(key=lambda x: x[0]) # sort by latency ascending
            best_model = results[0][1]
            print(f"[Ollama] Selected best model: {best_model}")
            return best_model
        return None

    def complete_structured(self, system_prompt: str, user_prompt: str, critic_feedback: str | None = None) -> DecisionProposalV1:
        # Schema definition to help the model
        schema_def = '{"rationale": "string", "actuator_id": "string", "target_value": "float", "confidence_score": "float"}'
        prompt = f"{system_prompt}\n\n{user_prompt}\n\nYou MUST respond in pure JSON matching this exact schema:\n{schema_def}"
        if critic_feedback:
            prompt += f"\n\nCRITIC FEEDBACK: {critic_feedback}. Please correct your proposal."

        payload = {
            "model": self.selected_model,
            "prompt": prompt,
            "format": "json",
            "stream": False
        }

        while True:
            start_time = time.time()
            print("-" * 48)
            print("LLM DIAGNOSTICS")
            print("-" * 48)
            print(f"Runtime detected: Ollama")
            print(f"API URL: {self.base_url}")
            print(f"Endpoint used: /api/generate")
            print(f"Selected model: {self.selected_model}")
            print(f"Prompt length: {len(prompt)} chars")
            print(f"Inference started: {time.strftime('%H:%M:%S')}")
            
            try:
                resp = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=120.0)
                resp.raise_for_status()
                
                data = resp.json()
                latency = time.time() - start_time
                
                print(f"Inference finished: {time.strftime('%H:%M:%S')}")
                print(f"Latency: {latency:.2f}s")
                print("Response received: YES")
                
                raw_response = data.get("response", "")
                print(f"Raw response: {raw_response}")
                
                parsed_json = json.loads(raw_response)
                print(f"Parsed JSON: {parsed_json}")
                
                validated = DecisionProposalV1.model_validate(parsed_json)
                print("Validation status: SUCCESS")
                
                # We can grab eval info if it's there
                eval_count = data.get("eval_count", 0)
                tps = eval_count / latency if latency > 0 else 0
                print(f"GPU utilization: Active ({tps:.1f} tok/s)")
                print("VRAM usage: Allocated by Ollama")
                print("-" * 48)
                
                return validated
                
            except Exception as e:
                latency = time.time() - start_time
                print(f"Inference finished: {time.strftime('%H:%M:%S')}")
                print(f"Latency: {latency:.2f}s")
                print(f"Validation status: FAILED")
                print(f"HTTP status: {getattr(resp, 'status_code', 'N/A') if 'resp' in locals() else 'N/A'}")
                print(f"response body: {getattr(resp, 'text', 'N/A') if 'resp' in locals() else 'N/A'}")
                print(f"URL requested: {self.base_url}/api/generate")
                print(f"headers: {payload}")
                print(f"request payload: {json.dumps(payload)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                print("-" * 48)
                print("Inference failed. The AI loop will NOT silently fall back. Retrying...")
                time.sleep(2)

    def generate_json(self, prompt: str) -> dict:
        """Fallback method for general JSON generation, used by operator chat."""
        payload = {
            "model": self.selected_model,
            "prompt": prompt,
            "format": "json",
            "stream": False
        }
        resp = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=60.0)
        resp.raise_for_status()
        return json.loads(resp.json().get("response", "{}"))
