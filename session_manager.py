from datetime import datetime, timezone
from uuid import uuid4

from database import get_connection


class SessionManager:
    def create_user(self, username: str) -> str:
        user_id = str(uuid4())

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (id, username)
                VALUES (?, ?)
                """,
                (user_id, username)
            )

        return user_id

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid4())

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO sessions (id, user_id)
                VALUES (?, ?)
                """,
                (session_id, user_id)
            )

        return session_id

    def update_activity(self, session_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET last_activity_at = ?
                WHERE id = ?
                """,
                (now, session_id)
            )

    def close_session(self, session_id: str) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET status = 'closed'
                WHERE id = ?
                """,
                (session_id,)
            )

    def get_session(self, session_id: str) -> dict | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM sessions
                WHERE id = ?
                """,
                (session_id,)
            ).fetchone()

        return dict(row) if row else None
    
    def get_or_create_user(self, username: str) -> str:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM users
                WHERE username = ?
                """,
                (username,)
            ).fetchone()

            if row:
                return row["id"]

            user_id = str(uuid4())

            connection.execute(
                """
                INSERT INTO users (id, username)
                VALUES (?, ?)
                """,
                (user_id, username)
            )

            return user_id