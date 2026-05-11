"""
Challenge endpoints.

  POST /challenges/{category_id}/attempt
  GET  /challenges/{category_id}/{challenge_id}/history
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from challenges.registry import ChallengeRegistry
from .deps import db, log_attempt, validate_challenge_payload, resolve_uid, ensure_session

router = APIRouter(prefix="/challenges", tags=["challenges"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ChallengeAttemptRequest(BaseModel):
    challenge_id: str
    payload: str
    user_id: Any          # frontend may send int or string
    session_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/{category_id}/attempt")
async def submit_attempt(category_id: str, request: ChallengeAttemptRequest):
    """Evaluate a challenge payload and record the attempt."""
    validate_challenge_payload(request.payload)
    uid = resolve_uid(request.user_id)

    engine = ChallengeRegistry.get_engine(category_id.lower())
    if engine is None:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category_id}'")

    category = ChallengeRegistry.get_category(category_id.lower())
    vulnerability_type = category.vulnerability_type

    result = engine.evaluate(request.challenge_id, request.payload)

    session_id = ensure_session(
        uid=uid,
        label=f"{category_id.upper()} Challenge {request.challenge_id.upper()}",
        session_id=request.session_id,
    )

    db.save_message(
        session_id=session_id,
        role="user",
        content=f"[{category_id.upper()} {request.challenge_id.upper()}] {request.payload}",
    )

    log_attempt(
        uid=uid,
        vulnerability_type=vulnerability_type,
        challenge_id=request.challenge_id,
        payload=request.payload,
        success=bool(result.get("success")),
        response=result.get("response", ""),
        session_id=session_id,
    )

    db.save_message(
        session_id=session_id,
        role="assistant",
        content=result.get("response", ""),
    )

    vuln_detected = (
        f"{category_id.upper()}: {result.get('attack_type', vulnerability_type)}"
        if result.get("success")
        else None
    )

    return {
        "success": result.get("success", False),
        "blocked": result.get("blocked", False),
        "reason": result.get("reason", ""),
        "response": result.get("response", ""),
        "score": result.get("score", 0),
        "attack_type": result.get("attack_type"),
        "session_id": session_id,
        "vulnerability_detected": vuln_detected,
    }


@router.get("/{category_id}/{challenge_id}/history")
async def get_challenge_history(category_id: str, challenge_id: str, user_id: int):
    """Return per-user attempt history for a specific challenge."""
    category = ChallengeRegistry.get_category(category_id.lower())
    if category is None:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category_id}'")

    attempts = db.get_attempts_for_challenge(
        user_id=user_id,
        vulnerability_type=category.vulnerability_type,
        challenge_id=challenge_id,
    )
    return {"category_id": category_id, "challenge_id": challenge_id, "attempts": attempts}
