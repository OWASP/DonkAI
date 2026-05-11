"""
Session management endpoints (list, create, delete).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .deps import db

router = APIRouter(tags=["sessions"])


class SessionNewRequest(BaseModel):
    user_id: int
    title: str


class SessionHistoryRequest(BaseModel):
    session_id: int
    user_id: int


def _session_payload(session) -> dict:
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
    }


@router.get("/sessions/user/{user_id}")
async def get_user_sessions(user_id: int):
    """Return all sessions for a user."""
    sessions = db.get_user_sessions(user_id)
    return {"sessions": [_session_payload(s) for s in sessions]}


@router.post("/session/new")
async def create_session(request: SessionNewRequest):
    """Create a new chat session."""
    session = db.create_session(user_id=request.user_id, title=request.title)
    return {"session": _session_payload(session)}


@router.post("/session/history")
async def get_session_history(request: SessionHistoryRequest):
    """Return messages for a session."""
    messages = db.get_session_messages(request.session_id)
    return {"messages": messages}


@router.delete("/session/{session_id}")
async def delete_session(session_id: int, user_id: int):
    """Delete a single chat session."""
    try:
        success = db.delete_session(session_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "message": f"Session {session_id} deleted"}


@router.delete("/sessions/user/{user_id}")
async def delete_all_sessions(user_id: int):
    """Delete all sessions for a user."""
    try:
        sessions = db.get_user_sessions(user_id)
        count = sum(1 for s in sessions if db.delete_session(s.id))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"success": True, "deleted": count}
