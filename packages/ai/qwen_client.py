"""Qwen Local Integration Client."""

from pathlib import Path
from typing import Any

import httpx
import yaml
from openai import APIConnectionError, APITimeoutError, OpenAI

from packages.ai.schemas import DecisionProposalV1


class QwenClient:
    """Bounded client for a local Qwen model using OpenAI API compatibility."""

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)

        # We explicitly configure a hard timeout to avoid hanging the control loop
        timeout = httpx.Timeout(self.config.get("timeout_seconds", 30.0))
        self.client = OpenAI(
            base_url=self.config.get("base_url", "http://localhost:8000/v1"),
            api_key=self.config.get("api_key", "dummy"),
            timeout=timeout,
            max_retries=self.config.get("max_retries", 2),
        )
        self.model_name = self.config.get("model_name", "qwen")

    def _load_config(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def health(self) -> bool:
        """Check if the local Qwen endpoint is accessible."""
        try:
            # We fetch models to see if the server responds
            self.client.models.list()
            return True
        except (APIConnectionError, APITimeoutError):
            return False
        except Exception:
            return False

    def complete_structured(self, system_prompt: str, user_prompt: str) -> DecisionProposalV1:
        """
        Forces the model to return a structured output matching DecisionProposalV1.
        Uses OpenAI's response_format logic. Falls closed on timeouts.
        """
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.config.get("temperature", 0.1),
                response_format=DecisionProposalV1,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                raise ValueError("Qwen response did not contain a structured proposal.")
            return parsed
        except Exception as e:
            # Fail closed: if the model times out, crashes, or gives bad JSON,
            # we return a safe NO-OP decision.
            return DecisionProposalV1(
                rationale=f"Safety Fallback triggered due to AI client error: {str(e)}",
                actuator_id="NONE",
                target_value=None,
                confidence_score=0.0,
            )
