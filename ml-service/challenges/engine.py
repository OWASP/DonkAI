"""
challenges/engine.py

Shared challenge evaluation engines.

RegexChallengeEngine handles the large majority of challenges whose
success / failure is determined by regex pattern matching.  More
complex evaluators can subclass BaseChallengeEngine and be registered
in the category's ChallengeDefinition with a CustomEvaluatorDefinition.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from .schema import (
    AttemptResult,
    CategoryDefinition,
    ChallengeDefinition,
    RegexEvaluatorDefinition,
)


class BaseChallengeEngine:
    """Minimal interface every engine must satisfy."""

    def __init__(self, category: CategoryDefinition) -> None:
        self.category = category

    def evaluate(self, challenge_id: str, payload: str) -> Dict[str, Any]:
        raise NotImplementedError

    def list_challenges(self):
        return [c.to_public_dict() for c in self.category.challenges]

    def get_challenge_info(self, challenge_id: str):
        c = self.category.get_challenge(challenge_id)
        return c.to_public_dict() if c else {}


class RegexChallengeEngine(BaseChallengeEngine):
    """
    Evaluate a challenge attempt using its RegexEvaluatorDefinition.

    Logic:
      1. If the payload matches any blocked_pattern  → blocked response.
      2. If the payload matches any success_pattern  → success response.
      3. Otherwise                                   → near-miss response.
    """

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def evaluate(self, challenge_id: str, payload: str) -> Dict[str, Any]:
        challenge = self.category.get_challenge(challenge_id)
        if challenge is None:
            return {
                "success": False,
                "blocked": False,
                "reason": "Invalid challenge ID",
                "response": "",
                "score": 0,
            }

        evaluator = challenge.evaluator
        if not isinstance(evaluator, RegexEvaluatorDefinition):
            return {
                "success": False,
                "blocked": False,
                "reason": f"Challenge {challenge_id!r} requires a custom evaluator",
                "response": "",
                "score": 0,
            }

        # 1. Blocked?
        blocked_hit = self._check_blocked(payload, evaluator.blocked_patterns)
        if blocked_hit:
            response = evaluator.blocked_response or self._default_blocked_response(
                blocked_hit, challenge
            )
            return AttemptResult(
                success=False,
                blocked=True,
                reason=f"🛡️ FILTER BLOCKED: The word/phrase '{blocked_hit}' is on the blacklist.",
                response=response,
                score=0,
                education=f"Defense active: {challenge.defense}",
            ).model_dump()

        # 2. Success?
        success, technique = self._check_success(payload, evaluator.success_patterns)
        if success:
            score = self._calculate_score(payload, evaluator.success_score)
            return AttemptResult(
                success=True,
                blocked=False,
                reason=f"✅ Attack succeeded! Technique: {technique}",
                response=challenge.success_response,
                score=score,
                attack_type=challenge.attack_type,
                education=f"Challenge {challenge.id}: {challenge.name} - COMPLETED",
            ).model_dump()

        # 3. Near miss
        response = evaluator.failure_response or self._default_near_miss_response(
            challenge
        )
        return AttemptResult(
            success=False,
            blocked=False,
            reason="⚠️ Payload not blocked, but didn't trigger the vulnerability. Refine your technique.",
            response=response,
            score=10,
            education="You passed the filter! Now make it more convincing.",
        ).model_dump()

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _check_blocked(payload: str, patterns: list[str]) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, payload, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    @staticmethod
    def _check_success(payload: str, patterns: list[str]) -> Tuple[bool, str]:
        for pattern in patterns:
            match = re.search(pattern, payload, re.IGNORECASE | re.DOTALL)
            if match:
                return True, pattern[:50]
        return False, ""

    @staticmethod
    def _calculate_score(payload: str, base_score: int) -> int:
        bonus = 15 if len(payload) < 100 else (5 if len(payload) < 200 else 0)
        return min(base_score + bonus, 100)

    @staticmethod
    def _default_blocked_response(blocked_word: str, challenge: ChallengeDefinition) -> str:
        return (
            f"\n🛡️ INJECTION BLOCKED\n\n"
            f"The word '{blocked_word}' triggered the blacklist filter.\n"
            f"Defense: {challenge.defense}\n\n"
            f"Your payload was stopped before reaching the model.\n\n"
            f"Try again with different vocabulary — the goal is to achieve\n"
            f"the same INTENT without using the blocked words.\n\n"
            f"Remember: a good attacker doesn't repeat the same approach.\n"
        )

    @staticmethod
    def _default_near_miss_response(challenge: ChallengeDefinition) -> str:
        first_hint = challenge.hints[0] if challenge.hints else ""
        return (
            f"\n⚡ FILTER EVADED — but no injection achieved.\n\n"
            f"Your payload passed the word filter! Good progress.\n"
            f"But the model didn't interpret it as an attack instruction.\n\n"
            f"Make your instruction more explicit and directive.\n"
            f"The model needs to clearly understand what new behavior you want.\n\n"
            f"Challenge hint: {first_hint}\n"
        )
