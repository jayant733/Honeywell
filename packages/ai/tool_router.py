"""Tool router ensuring Qwen only accesses safe functions."""

import json

from openai.types.chat import ChatCompletionMessageToolCall

from packages.ai.tools import ToolRegistry


class ToolRouter:
    """Routes tool calls from the LLM strictly to read-only evidence tools."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def handle_tool_calls(
        self, tool_calls: list[ChatCompletionMessageToolCall]
    ) -> list[dict[str, str]]:
        """
        Executes a list of tool calls securely.
        Returns a list of messages formatted for OpenAI tool responses.
        """
        results = []
        for call in tool_calls:
            # We enforce a strict boundary here: No 'propose_action' or actuation
            # should ever be registered in this registry.

            try:
                args = json.loads(call.function.arguments)
            except json.JSONDecodeError:
                args = {}

            output = self.registry.execute(call.function.name, args)

            results.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.function.name,
                    "content": output,
                }
            )

        return results
