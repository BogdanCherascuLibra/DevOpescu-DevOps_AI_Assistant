"""
Conversation memory management.

This module is responsible for storing and retrieving
messages exchanged between the user and the AI assistant.
"""

import json

from config import SYSTEM_PROMPT
from pathlib import Path

class ConversationContext:
    def __init__(self):
        self.knowledge_path = Path(__file__).parent / "knowledge"
        self.messages = [
            self.assemble_system_prompt()
        ]

    def read_text_file(self, file_path : Path) -> str:
        return file_path.read_text(encoding="utf-8").strip()
    
    def load_prompt_files(self) -> list[str]:
        prompt_dir = self.knowledge_path / "prompts"

        prompt_parts = []

        for file_path in sorted(prompt_dir.glob("*.md")):
            prompt_parts.append(self.read_text_file(file_path))

        return prompt_parts
    
    def load_registered_documents(self, directory_name : str) -> list[str]:
        dir_path = self.knowledge_path / directory_name
        registry_path = dir_path / "registry.json"

        with registry_path.open("r", encoding="utf-8") as file:
            registry = json.load(file)

        documents = []

        for document in registry:
            if document["always_load"]:
                document_path = (dir_path / f"{document['id']}.md")

                documents.append(self.read_text_file(document_path))
        
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
