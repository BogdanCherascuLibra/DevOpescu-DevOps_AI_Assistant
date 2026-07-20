"""
Conversation context and memory management.

This module builds the dynamic system prompt, stores conversation
messages, tracks token usage and cost, and compresses long histories.
"""

import json
from pathlib import Path

from config import (
    INPUT_TOKEN_PRICE_PER_MILLION,
    MAX_CONTEXT_TOKENS,
    OUTPUT_TOKEN_PRICE_PER_MILLION,
    RECENT_MESSAGES_TO_KEEP,
    SYSTEM_PROMPT,
)
from utils import count_tokens


class ConversationContext:
    """Manage the active conversation context and its usage statistics."""

    def __init__(self):
        self.knowledge_path = Path(__file__).parent / "knowledge"

        self.input_tokens = 0
        self.output_tokens = 0

        self.messages = [
            self.assemble_system_prompt()
        ]

    def read_text_file(self, file_path: Path) -> str:
        """Read and return the content of a UTF-8 text file."""
        return file_path.read_text(
            encoding="utf-8"
        ).strip()

    def load_prompt_files(self) -> list[str]:
        """Load all prompt files in filename order."""
        prompt_directory = self.knowledge_path / "prompts"
        prompt_parts = []

        for file_path in sorted(
            prompt_directory.glob("*.md")
        ):
            title = (
                file_path.stem
                .replace("_", " ")
                .title()
            )

            content = self.read_text_file(
                file_path
            )

            prompt_parts.append(
                f"# {title}\n\n{content}"
            )

        return prompt_parts

    def load_registered_documents(
        self,
        directory_name: str,
    ) -> list[str]:
        """
        Load documents marked with always_load=true
        from a knowledge registry.
        """
        directory_path = (
            self.knowledge_path / directory_name
        )

        registry_path = (
            directory_path / "registry.json"
        )

        with registry_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            registry = json.load(file)

        documents = []

        for document in registry:
            if not document["always_load"]:
                continue

            document_path = (
                directory_path
                / f"{document['id']}.md"
            )

            content = self.read_text_file(
                document_path
            )

            documents.append(
                f"# {document['name']}\n\n"
                f"{content}"
            )

        return documents

    def assemble_system_prompt(self) -> dict:
        """
        Build the system prompt from the configured prompt,
        prompt files, facts, and procedures.
        """
        prompt_parts = []

        if SYSTEM_PROMPT.strip():
            prompt_parts.append(
                SYSTEM_PROMPT.strip()
            )

        prompt_parts.extend(
            self.load_prompt_files()
        )

        prompt_parts.extend(
            self.load_registered_documents("facts")
        )

        prompt_parts.extend(
            self.load_registered_documents(
                "procedures"
            )
        )

        full_prompt = (
            "\n--------------\n"
            .join(prompt_parts)
        )

        return {
            "role": "system",
            "content": full_prompt,
        }

    def add_message(self, message: dict) -> None:
        """Add a message to the active conversation."""
        self.messages.append(message)

    def get_history(self) -> list[dict]:
        """Return the complete active conversation history."""
        return self.messages

    def update_input_tokens(
        self,
        messages: list[dict],
    ) -> None:
        """Add the token count of an input payload."""
        for message in messages:
            content = message.get("content")

            if content:
                self.input_tokens += count_tokens(
                    content
                )

    def update_output_tokens(
        self,
        message: dict,
    ) -> None:
        """Add the token count of an assistant response."""
        content = message.get("content", "")

        if content:
            self.output_tokens += count_tokens(
                content
            )

    def get_total_cost(self) -> float:
        """Return the estimated cumulative API cost."""
        input_cost = (
            self.input_tokens
            / 1_000_000
            * INPUT_TOKEN_PRICE_PER_MILLION
        )

        output_cost = (
            self.output_tokens
            / 1_000_000
            * OUTPUT_TOKEN_PRICE_PER_MILLION
        )

        return input_cost + output_cost

    def get_tokens_usage(self) -> dict:
        """Return cumulative token and cost statistics."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_cost": self.get_total_cost(),
        }

    def needs_compression(self) -> bool:
        """
        Check whether the conversation exceeds
        the configured context token limit.
        """
        conversation = self.messages[1:]

        if (
            len(conversation)
            <= RECENT_MESSAGES_TO_KEEP
        ):
            return False

        total_tokens = sum(
            count_tokens(
                message.get("content", "")
            )
            for message in conversation
            if message.get("content")
        )

        return total_tokens > MAX_CONTEXT_TOKENS

    def get_messages_to_summarize(
        self,
    ) -> list[dict]:
        """
        Return older messages that should be included
        in the conversation summary.
        """
        conversation = self.messages[1:]

        return conversation[
            :-RECENT_MESSAGES_TO_KEEP
        ]

    def compress_history(
        self,
        summary: str,
    ) -> None:
        """
        Replace older messages with a summary while
        preserving the system prompt and recent messages.
        """
        system_message = self.messages[0]
        conversation = self.messages[1:]

        recent_messages = conversation[
            -RECENT_MESSAGES_TO_KEEP:
        ]

        summary_message = {
            "role": "system",
            "content": (
                "Summary of the previous conversation:\n"
                f"{summary}"
            ),
        }

        self.messages = [
            system_message,
            summary_message,
            *recent_messages,
        ]