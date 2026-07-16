"""
Conversation memory management.

This module is responsible for storing and retrieving
messages exchanged between the user and the AI assistant.
"""

import json

from config import (SYSTEM_PROMPT, INPUT_TOKEN_PRICE_PER_MILLION, OUTPUT_TOKEN_PRICE_PER_MILLION)
from pathlib import Path
from utils import count_tokens


class ConversationContext:
    def __init__(self):
        self.knowledge_path = Path(__file__).parent / "knowledge"

        self.input_tokens = 0
        self.output_tokens = 0

        self.messages = [
            self.assemble_system_prompt()
        ]

    def read_text_file(self, file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8").strip()

    def load_prompt_files(self) -> list[str]:
        prompt_dir = self.knowledge_path / "prompts"

        prompt_parts = []

        for file_path in sorted(prompt_dir.glob("*.md")):
            title = file_path.stem.replace("_", " ").title()
            content = self.read_text_file(file_path)

            section = f"# {title}\n\n{content}"
            prompt_parts.append(section)

        return prompt_parts

    def load_registered_documents(self, directory_name: str) -> list[str]:
        dir_path = self.knowledge_path / directory_name
        registry_path = dir_path / "registry.json"

        with registry_path.open("r", encoding="utf-8") as file:
            registry = json.load(file)

        documents = []

        for document in registry:
            if document["always_load"]:
                document_path = (dir_path / f"{document['id']}.md")
                content = self.read_text_file(document_path)

                section = (
                    f"# {document['name']}\n\n"
                    f"{content}"
                )

                documents.append(section)

        return documents

    def assemble_system_prompt(self):
        prompt_parts = []

        if SYSTEM_PROMPT.strip():
            prompt_parts.append(SYSTEM_PROMPT.strip())
        prompt_parts.extend(self.load_registered_documents("facts"))

        prompt_parts.extend(self.load_registered_documents("procedures"))

        full_prompt = "\n--------------\n".join(prompt_parts)

        return {
            "role": "system",
            "content": full_prompt
        }

    def add_message(self, message):
        self.messages.append(message)

    def get_history(self):
        return self.messages

    def update_input_tokens(self, messages: list[dict]) -> None:
        for message in messages:
            content = message.get("content")

        if content:
            self.input_tokens += count_tokens(content)

    # def update_output_tokens(self, messages: list[dict]) -> None:
    #     for message in messages:
    #         content = message.get("content")

    #     if content:
    #         self.output_tokens += count_tokens(content)

    def update_output_tokens(self, message: dict) -> None:
        content = message.get("content", "")

        if content:
            self.output_tokens += count_tokens(content)

    def get_total_cost(self) -> float:
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
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_cost": self.get_total_cost()
        }
