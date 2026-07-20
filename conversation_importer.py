"""
Conversation import service.

This module validates a conversation export file and recreates
the conversation and its messages for the selected user.
"""

import json
from pathlib import Path


class ConversationImporter:
    """Import conversations from JSON files into the database."""

    def __init__(self, conversation_manager):
        self.conversation_manager = conversation_manager

    def import_from_json(
        self,
        file_path: str,
        user_id: str,
    ) -> str:
        """Import a JSON conversation and return its new conversation ID."""
        path = Path(file_path)

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except FileNotFoundError as error:
            raise ValueError(
                "Fișierul nu există."
            ) from error

        except json.JSONDecodeError as error:
            raise ValueError(
                "Fișierul JSON este invalid."
            ) from error

        conversation_data = data.get("conversation")
        messages = data.get("messages")

        # Validate the required sections before creating database records.
        if not conversation_data:
            raise ValueError(
                "Lipsește secțiunea conversation."
            )

        if not isinstance(messages, list):
            raise ValueError(
                "Secțiunea messages este invalidă."
            )

        title = conversation_data.get(
            "title",
            "Imported conversation",
        )

        # Create a new conversation instead of reusing the exported ID.
        conversation_id = (
            self.conversation_manager.create_conversation(
                user_id,
                title,
            )
        )

        # Import only supported roles with non-empty text content.
        for message in messages:
            role = message.get("role")
            content = message.get("content")

            if role not in {"user", "assistant"}:
                continue

            if not isinstance(content, str) or not content.strip():
                continue

            self.conversation_manager.add_message(
                conversation_id,
                role,
                content,
            )

        return conversation_id