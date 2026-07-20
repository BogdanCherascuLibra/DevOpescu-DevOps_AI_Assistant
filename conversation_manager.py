import json
from uuid import uuid4
from database import get_connection



class ConversationManager:
    def create_conversation(
        self,
        user_id: str,
        title: str = "New conversation"
    ) -> str:
        conversation_id = str(uuid4())

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO conversations (id, user_id, title)
                VALUES (?, ?, ?)
                """,
                (conversation_id, user_id, title)
            )

        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO messages (
                    conversation_id,
                    role,
                    content
                )
                VALUES (?, ?, ?)
                """,
                (conversation_id, role, content)
            )

            connection.execute(
                """
                UPDATE conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (conversation_id,)
            )

    def get_messages(
        self,
        conversation_id: str
    ) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id
                """,
                (conversation_id,)
            ).fetchall()

        return [dict(row) for row in rows]

    def get_user_conversations(
        self,
        user_id: str
    ) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id,)
            ).fetchall()

        return [dict(row) for row in rows]
    
    def get_conversation(self,
                        conversation_id: str,
                        user_id: str
                        ) -> dict | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM conversations
                WHERE id = ? AND user_id = ?
                """,
                (conversation_id, user_id)
            ).fetchone()

        return dict(row) if row else None
    
    def delete_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                """
             DELETE FROM conversations
                WHERE id = ? AND user_id = ?
                """,
                (conversation_id, user_id)
            )

        return cursor.rowcount > 0
    
    def update_usage(
        self,
        conversation_id: str,
        input_tokens: int,
        output_tokens: int,
        total_cost: float
        ) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE conversations
                SET
                    input_tokens = input_tokens + ?,
                    output_tokens = output_tokens + ?,
                    total_cost = total_cost + ?
                WHERE id = ?
                """,
                (
                    input_tokens,
                    output_tokens,
                    total_cost,
                    conversation_id
                )
            )
            
    def get_usage(
        self,
        conversation_id: str
    ) -> dict:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    input_tokens,
                    output_tokens,
                    total_cost
                FROM conversations
                WHERE id = ?
                """,
                (conversation_id,)
            ).fetchone()

        if not row:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_cost": 0.0
            }

        return dict(row)