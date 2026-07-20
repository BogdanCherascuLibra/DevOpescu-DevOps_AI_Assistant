"""
User session management.

This module handles user creation, session lifecycle,
activity tracking, and session retrieval using SQLite.
"""

from datetime import datetime, timezone
from uuid import uuid4

from database import get_connection


class SessionManager:
    """Manage application users and their sessions."""

    def create_user(self, username: str) -> str:
        """Create a new user and return its generated ID."""
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError("Username cannot be empty.")

        user_id = str(uuid4())

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (id, username)
                VALUES (?, ?)
                """,
                (user_id, normalized_username),
            )

        return user_id

    def get_or_create_user(self, username: str) -> str:
        """Return an existing user ID or create a new user."""
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError("Username cannot be empty.")

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM users
                WHERE username = ?
                """,
                (normalized_username,),
            ).fetchone()

            if row:
                return row["id"]

            user_id = str(uuid4())

            connection.execute(
                """
                INSERT INTO users (id, username)
                VALUES (?, ?)
                """,
                (user_id, normalized_username),
            )

        return user_id

    def create_session(self, user_id: str) -> str:
        """Create a new active session for a user."""
        session_id = str(uuid4())

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO sessions (id, user_id)
                VALUES (?, ?)
                """,
                (session_id, user_id),
            )

        return session_id

    def update_activity(self, session_id: str) -> bool:
        """Update the last activity timestamp for a session."""
        current_time = datetime.now(timezone.utc).isoformat()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE sessions
                SET last_activity_at = ?
                WHERE id = ?
                """,
                (current_time, session_id),
            )

        return cursor.rowcount > 0

    def close_session(self, session_id: str) -> bool:
        """Mark a session as closed."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE sessions
                SET status = 'closed'
                WHERE id = ?
                """,
                (session_id,),
            )

        return cursor.rowcount > 0

    def get_session(self, session_id: str) -> dict | None:
        """Return a session by ID, or None when it does not exist."""
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            ).fetchone()

        return dict(row) if row else None
    