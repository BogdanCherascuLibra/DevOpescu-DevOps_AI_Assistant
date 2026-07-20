"""
Conversation import and export API routes.

This module exposes endpoints for exporting stored conversations
as JSON files and importing conversation history from JSON files.
"""

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

from api_dependencies import (
    conversation_exporter,
    conversation_importer,
    conversation_manager,
    session_manager,
)


router = APIRouter(
    prefix="/users/{username}/conversations",
    tags=["Import / Export"],
)


@router.get("/{conversation_id}/export")
def export_conversation(
    username: str,
    conversation_id: str,
):
    """Export one conversation as a downloadable JSON file."""
    user_id = session_manager.get_or_create_user(
        username
    )

    conversation = conversation_manager.get_conversation(
        conversation_id,
        user_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    try:
        file_path = conversation_exporter.export_to_json(
            conversation_id,
            user_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=Path(file_path).name,
    )


@router.post("/import")
def import_conversation(
    username: str,
    file: UploadFile = File(...),
) -> dict:
    """Import a conversation from an uploaded JSON file."""
    if (
        not file.filename
        or not file.filename.lower().endswith(".json")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are accepted.",
        )

    user_id = session_manager.get_or_create_user(
        username
    )

    temporary_path: Path | None = None

    try:
        # Store the uploaded file temporarily so the importer
        # can process it using a normal filesystem path.
        with NamedTemporaryFile(
            delete=False,
            suffix=".json",
        ) as temporary_file:
            shutil.copyfileobj(
                file.file,
                temporary_file,
            )

            temporary_path = Path(
                temporary_file.name
            )

        conversation_id = (
            conversation_importer.import_from_json(
                str(temporary_path),
                user_id,
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    finally:
        file.file.close()

        if temporary_path:
            temporary_path.unlink(
                missing_ok=True
            )

    return {
        "conversation_id": conversation_id,
        "message": "Conversation imported successfully.",
    }