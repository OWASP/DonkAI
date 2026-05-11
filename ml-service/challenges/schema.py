"""
challenges/schema.py

Validated data models for OWASP LLM challenge definitions.

All category and challenge data passes through these models so that
structural errors are caught at import time rather than at runtime.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Prevention
# ---------------------------------------------------------------------------


class PreventionStrategy(BaseModel):
    category: str
    measures: List[str]


class PreventionDefinition(BaseModel):
    strategies: List[PreventionStrategy]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategies": [
                {"category": s.category, "measures": s.measures}
                for s in self.strategies
            ]
        }


# ---------------------------------------------------------------------------
# Evaluators
# ---------------------------------------------------------------------------


class RegexEvaluatorDefinition(BaseModel):
    """Standard regex-based evaluator used by the majority of challenges."""

    blocked_patterns: List[str] = Field(default_factory=list)
    success_patterns: List[str] = Field(default_factory=list)
    blocked_response: Optional[str] = None
    failure_response: Optional[str] = None
    success_score: int = 85

    @model_validator(mode="after")
    def _validate_patterns(self) -> "RegexEvaluatorDefinition":
        for pat in self.blocked_patterns + self.success_patterns:
            try:
                re.compile(pat)
            except re.error as exc:
                raise ValueError(f"Invalid regex pattern {pat!r}: {exc}") from exc
        return self


class CustomEvaluatorDefinition(BaseModel):
    """Extension point for challenges that need non-regex evaluation logic."""

    name: str
    config: Dict[str, Any] = Field(default_factory=dict)


EvaluatorDefinition = Union[RegexEvaluatorDefinition, CustomEvaluatorDefinition]


# ---------------------------------------------------------------------------
# Challenge
# ---------------------------------------------------------------------------


class ChallengeDefinition(BaseModel):
    id: str
    name: str
    difficulty: int = Field(ge=1, le=5)
    stars: str
    tagline: str
    backstory: str
    target: str
    defense: str
    template: str
    placeholder: str
    hint_threshold: int = 2
    hints: List[str] = Field(default_factory=list)
    education_on_success: str = ""
    attack_type: str
    success_response: str
    evaluator: EvaluatorDefinition

    def to_public_dict(self) -> Dict[str, Any]:
        """Serialise for the frontend — strips evaluator internals."""
        return {
            "id": self.id,
            "challengeId": self.id,
            "name": self.name,
            "difficulty": self.difficulty,
            "stars": self.stars,
            "tagline": self.tagline,
            "backstory": self.backstory,
            "target": self.target,
            "defense": self.defense,
            "template": self.template,
            "placeholder": self.placeholder,
            "hint_threshold": self.hint_threshold,
            "hints": self.hints,
            "educationOnSuccess": self.education_on_success,
            "attack_type": self.attack_type,
        }


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


class CategoryDefinition(BaseModel):
    id: str
    code: str
    name: str
    icon: str
    severity: str
    owasp_url: str
    overview: str
    prevention: PreventionDefinition
    vulnerability_type: str
    challenges: List[ChallengeDefinition] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_challenge_ids(self) -> "CategoryDefinition":
        seen: set[str] = set()
        for c in self.challenges:
            if c.id in seen:
                raise ValueError(
                    f"Duplicate challenge id {c.id!r} in category {self.id!r}"
                )
            seen.add(c.id)
        return self

    def get_challenge(self, challenge_id: str) -> Optional[ChallengeDefinition]:
        for c in self.challenges:
            if c.id == challenge_id:
                return c
        return None

    def to_public_dict(self) -> Dict[str, Any]:
        """Serialise for the /vulnerabilities endpoint."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "icon": self.icon,
            "severity": self.severity,
            "owasp_url": self.owasp_url,
            "overview": self.overview,
            "prevention": self.prevention.to_dict(),
            "challenges": [c.to_public_dict() for c in self.challenges],
        }


# ---------------------------------------------------------------------------
# Attempt result
# ---------------------------------------------------------------------------


class AttemptResult(BaseModel):
    success: bool
    blocked: bool = False
    reason: str
    response: str
    score: int = 0
    attack_type: Optional[str] = None
    education: str = ""
