"""Core agent orchestration.
The agent coordinates communication between
the conversation context and the language model."""

import json

class Agent:
    def __init__(
            self,
            llm_client, 
            context,
            embeddings_client, 
            tools=None
            ):
        self.llm_client = llm_client
        self.context = context
        self.embeddings_client = embeddings_client
        self.tools = {tool.name: tool for tool in tools} if tools else {}

    def _handle_tool_calls(self, tool_calls):
        results = []
        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            tool_id = tc["id"]

            try:
                arguments = tc["function"]["arguments"]
                tool = self.tools.get(tool_name)
                if not tool:
                    raise ValueError(
                        f"Tool {tool} not found"
                    )
                else:
                    result = tool.callback(**arguments)

            except json.JSONDecodeError:
                result = (
                f"Invalid arguments received for tool '{tool_name}'."
            )

            except TypeError as error:
                result = (
                f"Invalid parameters for tool '{tool_name}': {error}"
            )

            except Exception as error:
                result = (
                f"Tool '{tool_name}' failed: {error}"
            )
                
            results.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "content": str(result)
            })
        return results
    

    def process_message(self, user_message):
        self.context.add_message({
            "role": "user",
            "content": user_message
        })

        self._compress_context_if_needed()

        print("\nCONTEXT:")
        for message in self.context.get_history():
            print(message["role"], ":", message.get("content", ""))
            print("-" * 30)
            
        messages = self.context.get_history().copy()

        rag_message = self._build_rag_message(user_message)

        if rag_message:
            messages.append(rag_message)

        self.context.update_input_tokens(messages)


        try:
            response = self.llm_client.generate_response(
                messages,
                tools=list(self.tools.values())
            )
        except Exception as error:
            print(f"\nLLM error: {error}")

            return (
                "Conectarea la modelul AI nu a putut fi realizata. "
            )


        message = response["message"]

        if not message.get("content") and not message.get("tool_calls"):
            message = {
                "role": "assistant",
                "content": (
                "Nu am suficiente informații pentru un răspuns sigur. "
                "Te rog să oferi mai multe detalii despre problemă."
            )
        }   

        self.context.update_output_tokens(message)

        tool_calls = message.get("tool_calls", [])

        if tool_calls:
            self.context.add_message(message)

            tool_results = self._handle_tool_calls(tool_calls)

            for result in tool_results:
                self.context.add_message(result)

            messages = self.context.get_history().copy()

            if rag_message:
                messages.append(rag_message)

            self.context.update_input_tokens(messages)

            try:
                response = self.llm_client.generate_response(
                    messages,
                    tools=list(self.tools.values())
                )
            except Exception as error:
                print(f"\nLLM error: {error}")
                return (
                    "Tool-ul a fost executat, dar modelul nu a putut "
                    "genera raspunsul final."
                )

            message = response["message"]
            if not message.get("content") and not message.get("tool_calls"):
                message = {
                "role": "assistant",
                "content": (
                "Nu am suficiente informații pentru un răspuns sigur. "
                "Te rog să oferi mai multe detalii despre problemă."
                )
            }

            self.context.update_output_tokens(message)

        self.context.add_message(message)
        return message.get("content", "")
    
    def _build_rag_message(self, user_message: str) -> dict | None:
        try:

            results = self.embeddings_client.semantic_search(user_message)
        except RuntimeError as error:
            print(f"RAG unavailable: {error}")
            return {
                "role": "system",
                "content": (
                "The internal knowledge base is temporarily unavailable. "
                "Answer using your general DevOps knowledge. "
                "Do not pretend that internal documentation was consulted."
            )
        }

        if not results:
            return {
                "role": "system",
                "content": (
                "No relevant information was found in the internal knowledge base. "
                "Answer using your general DevOps knowledge. "
                "If important information is missing, ask the user for details."
            )
        }

        context_parts = []

        print("\nRAG RESULTS:")
        for result in results:
            print(
                result["document_id"],
                round(result["similarity"], 4)
            )

        for result in results:
            context_parts.append(
                f"Document: {result['document_id']}\n"
                f"Content:\n{result['content']}"
            )

        rag_context = "\n\n---\n\n".join(context_parts)

        return {
            "role": "system",
            "content": (
                "Use the following internal knowledge when relevant.\n"
                "You may also use your general knowledge.\n"
                "Do not invent information from these documents.\n\n"
                f"{rag_context}"
            )
        }
    
    def _compress_context_if_needed(self) -> None:
        if not self.context.needs_compression():
            return

        old_messages = self.context.get_messages_to_summarize()

        summary_request = [
            {
                "role": "system",
                "content": (
                    "Summarize the following conversation. "
                    "Preserve technical details, service names, "
                    "errors, commands already executed and conclusions."
                )
            },
            {
                "role": "user",
                "content": str(old_messages)
            }
        ]

        try:
            response = self.llm_client.generate_response(summary_request)
            summary = response["message"].get("content", "")

            if summary:
                self.context.compress_history(summary)

        except Exception as error:
            print(f"\nContext compression failed: {error}")
