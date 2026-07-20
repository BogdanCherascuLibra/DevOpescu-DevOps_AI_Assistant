"""
Shared API dependencies.

This module creates the manager and service instances reused
by the FastAPI routers.
"""

from conversation_exporter import ConversationExporter
from conversation_importer import ConversationImporter
from conversation_manager import ConversationManager
from session_manager import SessionManager


# Shared managers used by the conversation endpoints.
session_manager = SessionManager()
conversation_manager = ConversationManager()

# Services responsible for conversation transfer operations.
conversation_exporter = ConversationExporter(
    conversation_manager
)

conversation_importer = ConversationImporter(
    conversation_manager
)