"""
Vulnerability catalogue endpoints.

  GET /vulnerabilities         — list all OWASP LLM vulnerability categories
  GET /vulnerabilities/{id}    — detail for a single category
"""

from fastapi import APIRouter, HTTPException

from challenges.registry import ChallengeRegistry

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("")
async def list_vulnerabilities():
    """Return all categories with metadata and public challenge lists."""
    return {
        "vulnerabilities": [
            cat.to_public_dict()
            for cat in ChallengeRegistry.list_categories()
        ]
    }


@router.get("/{category_id}")
async def get_vulnerability(category_id: str):
    """Return a single category by id (e.g. 'llm01')."""
    category = ChallengeRegistry.get_category(category_id.lower())
    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Vulnerability '{category_id}' not found",
        )
    return category.to_public_dict()
