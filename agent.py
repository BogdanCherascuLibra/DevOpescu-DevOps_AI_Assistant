"""
Core agent orchestration.

This module coordinates the conversation context, language model,
knowledge retrieval, tool execution, token tracking, and context
compression.
"""

import json


class Agent:
    """Coordinate the main chatbot workflow."""

    def __init__(
        self,
        llm_client,
        context,
        embeddings_client,
        knowledge_base,
        tools=None,
    ):
        self.llm_client = llm_client
        self.context = context
        self.embeddings_client = embeddings_client
        self.knowledge_base = knowledge_base

        self.tools = (
            {tool.name: tool for tool in tools}
            if tools
            else {}
        )

    def _handle_tool_calls(
        self,
        tool_calls: list[dict],
    ) -> list[dict]:
        """Execute requested tools and return their results."""
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_id = tool_call["id"]

            try:
                arguments = json.loads(
                    tool_call["function"]["arguments"]
                )

                tool = self.tools.get(tool_name)

                if not tool:
                    raise ValueError(
                        f"Tool '{tool_name}' not found."
                    )

                result = tool.callback(**arguments)

            except json.JSONDecodeError:
                result = (
                    f"Invalid JSON arguments for tool '{tool_name}'."
                )

            except TypeError as error:
                result = (
                    f"Invalid parameters for tool '{tool_name}': "
                    f"{error}"
                )

            except Exception as error:
                result = (
                    f"Tool '{tool_name}' failed: {error}"
                )

            results.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": str(result),
                }
            )

        return results

    def process_message(self, user_message: str) -> str:
        """Process a user message and return the assistant response."""
        self.context.add_message(
            {
                "role": "user",
                "content": user_message,
            }
        )

        self._compress_context_if_needed()

        # Use a copy so the temporary RAG message is not stored
        # permanently in the conversation history.
        messages = self.context.get_history().copy()

        rag_message = (
            self.knowledge_base.build_context_message(
                user_message
            )
        )

        if rag_message:
            messages.append(rag_message)

        self.context.update_input_tokens(messages)

        try:
            response = self.llm_client.generate_response(
                messages,
                tools=list(self.tools.values()),
            )

        except Exception as error:
            print(f"\nLLM error: {error}")

            return (
                "Conectarea la modelul AI nu a putut fi realizată."
            )

        message = response["message"]

        if (
            not message.get("content")
            and not message.get("tool_calls")
        ):
            message = {
                "role": "assistant",
                "content": (
                    "Nu am suficiente informații pentru un răspuns sigur. "
                    "Te rog să oferi mai multe detalii despre problemă."
                ),
            }

        self.context.update_output_tokens(message)

        tool_calls = message.get("tool_calls", [])

        if tool_calls:
            # Store the assistant tool request before adding tool results.
            self.context.add_message(message)

            tool_results = self._handle_tool_calls(
                tool_calls
            )

            for result in tool_results:
                self.context.add_message(result)

            messages = self.context.get_history().copy()

            if rag_message:
                messages.append(rag_message)

            self.context.update_input_tokens(messages)

            try:
                response = self.llm_client.generate_response(
                    messages,
                    tools=list(self.tools.values()),
                )

            except Exception as error:
                print(f"\nLLM error: {error}")

                return (
                    "Tool-ul a fost executat, dar modelul nu a putut "
                    "genera răspunsul final."
                )

            message = response["message"]

            if (
                not message.get("content")
                and not message.get("tool_calls")
            ):
                message = {
                    "role": "assistant",
                    "content": (
                        "Nu am suficiente informații pentru un răspuns sigur. "
                        "Te rog să oferi mai multe detalii despre problemă."
                    ),
                }

            self.context.update_output_tokens(message)

        self.context.add_message(message)

        return message.get("content", "")

    def _compress_context_if_needed(self) -> None:
        """Summarize older messages when the context becomes too large."""
        if not self.context.needs_compression():
            return

        old_messages = (
            self.context.get_messages_to_summarize()
        )

        summary_request = [
            {
                "role": "system",
                "content": (
                    "Summarize the following conversation. "
                    "Preserve technical details, service names, "
                    "errors, commands already executed and conclusions."
                ),
            },
            {
                "role": "user",
                "content": str(old_messages),
            },
        ]

        try:
            response = self.llm_client.generate_response(
                summary_request
            )

            summary = response["message"].get(
                "content",
                "",
            )

            if summary:
                self.context.compress_history(summary)

        except Exception as error:
            print(
                f"\nContext compression failed: {error}"
            )