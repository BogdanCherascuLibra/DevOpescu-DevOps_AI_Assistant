"""
LLM integration layer.

This module handles communication with the configured
language model and converts tool definitions into the
format expected by the API.
"""

from openai import OpenAI

from config import (
    MODEL_NAME,
    AZURE_ENDPOINT,
    API_KEY
)

from tools.tool import Tool


class LLMClient:
    """Client responsible for sending requests to the language model."""

    def __init__(self):
        # Create the OpenAI-compatible client using the configured endpoint.
        self.client = OpenAI(
            base_url=AZURE_ENDPOINT,
            api_key=API_KEY
        )

    def _tool_to_dict(self, tool: Tool):
        """
        Convert a Tool object into the function schema
        required by the language model API.
        """
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        }

    def generate_response(self, messages, tools=None):
        """
        Send the conversation history to the model
        and return a normalized response dictionary.
        """

        # Base request arguments.
        kwargs = {
            "model": MODEL_NAME,
            "messages": messages
        }

        # Include available tools only when they are provided.
        if tools:
            kwargs["tools"] = [
                self._tool_to_dict(tool)
                for tool in tools
            ]

        # Send the request to the language model.
        response = self.client.chat.completions.create(
            **kwargs
        )

        message = response.choices[0].message

        # Normalize the assistant response.
        result = {
            "message": {
                "role": "assistant",
                "content": message.content
            }
        }

        # Preserve tool calls when the model requests them.
        if getattr(message, "tool_calls", None):

            result["message"]["tool_calls"] = []

            for tc in message.tool_calls:

                result["message"]["tool_calls"].append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })

        return result