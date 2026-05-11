"""
Shared dependencies and helpers used across all routers.
"""

from fastapi import HTTPException
from database import Database
from challenges.detector import PromptValidator

db = Database()
prompt_validator = PromptValidator()


def resolve_uid(raw_user_id) -> int:
    """Coerce user_id (int or string) to int, raising 400 on failure."""
    if raw_user_id is None:
        raise HTTPException(status_code=400, detail="user_id is required")
    try:
        return int(raw_user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid user_id: {raw_user_id}")


def log_attempt(uid: int, vulnerability_type: str, challenge_id, payload: str,
                success: bool, response: str = "", session_id=None):
    """Log every challenge attempt. Errors are swallowed so they never break a response."""
    try:
        db.log_exploit_attempt(
            user_id=uid,
            vulnerability_type=vulnerability_type,
            payload=payload,
            success=success,
            response=response,
            session_id=session_id,
            challenge_id=challenge_id,
        )
    except Exception:
        pass


def ensure_session(uid: int, label: str, session_id=None) -> int:
    """Return session_id, creating a new session if none provided."""
    if session_id:
        return session_id
    session = db.create_session(user_id=uid, title=label)
    return session.id


def validate_challenge_payload(payload: str, max_len: int = 2000):
    """Raise 400 if payload is empty or too long."""
    if not payload.strip():
        raise HTTPException(status_code=400, detail="Payload cannot be empty")
    if len(payload) > max_len:
        raise HTTPException(status_code=400, detail=f"Payload too long (max {max_len} chars)")
