"""
SQLite database configuration and initialization.

This module creates database connections and initializes
the tables required for users, sessions, conversations,
messages, and conversation usage statistics.
"""

import sqlite3

from config import DATABASE_FILE


def get_connection() -> sqlite3.Connection:
    """Create and return a configured SQLite connection."""
    # Ensure that the database directory exists.
    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DATABASE_FILE)

    # Allow database rows to be accessed using column names.
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    """Create the required database tables and usage columns."""
    with get_connection() as connection:
        # Create the initial database structure.
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_activity_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'active',

                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            );
            """
        )

        # Read the existing conversation columns so older databases
        # can be upgraded without deleting stored data.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(conversations)"
            ).fetchall()
        }

        # Add usage columns when they do not exist yet.
        if "input_tokens" not in columns:
            connection.execute(
                """
                ALTER TABLE conversations
                ADD COLUMN input_tokens INTEGER NOT NULL DEFAULT 0
                """
            )

        if "output_tokens" not in columns:
            connection.execute(
                """
                ALTER TABLE conversations
                ADD COLUMN output_tokens INTEGER NOT NULL DEFAULT 0
                """
            )

        if "total_cost" not in columns:
            connection.execute(
                """
                ALTER TABLE conversations
                ADD COLUMN total_cost REAL NOT NULL DEFAULT 0
                """
            )