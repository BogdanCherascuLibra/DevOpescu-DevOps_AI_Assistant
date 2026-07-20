import json
from pathlib import Path


class ConversationImporter:
    def __init__(self, conversation_manager):
        self.conversation_manager = conversation_manager

    def import_from_json(
        self,
        file_path: str,
        user_id: str
    ) -> str:
        path = Path(file_path)

        try:
            with path.open(
                "r",
                encoding="utf-8"
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
            "Imported conversation"
        )

        conversation_id = (
            self.conversation_manager.create_conversation(
                user_id,
                title
            )
        )

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
                content
            )

        return conversation_id