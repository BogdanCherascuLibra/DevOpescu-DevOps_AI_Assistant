import json
from datetime import datetime, timezone

from config import EXPORTS_DIR


class ConversationExporter:
    def __init__(self, conversation_manager):
        self.conversation_manager = conversation_manager

    def export_to_json(
        self,
        conversation_id: str,
        user_id: str
    ) -> str:
        conversation = self.conversation_manager.get_conversation(
            conversation_id,
            user_id
        )

        if not conversation:
            raise ValueError("Conversația nu există.")

        messages = self.conversation_manager.get_messages(
            conversation_id
        )

        export_data = {
            "format_version": 1,
            "exported_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "conversation": {
                "title": conversation["title"],
                "created_at": conversation["created_at"],
                "updated_at": conversation["updated_at"]
            },
            "messages": [
                {
                    "role": message["role"],
                    "content": message["content"],
                    "created_at": message["created_at"]
                }
                for message in messages
            ]
        }

        EXPORTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = EXPORTS_DIR / f"{conversation_id}.json"

        with file_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                export_data,
                file,
                indent=2,
                ensure_ascii=False
            )

        return str(file_path)