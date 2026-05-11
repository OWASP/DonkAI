"""
challenges/__init__.py

Package entry-point.

Public re-exports kept for backward compatibility with any code that
still imports directly from the `challenges` namespace.
"""

from .detector import PromptValidator as PromptValidator
from .detector import simulate_attack_response as simulate_attack_response
from .registry import ChallengeRegistry as ChallengeRegistry

__all__ = [
    "PromptValidator",
    "simulate_attack_response",
    "ChallengeRegistry",
]
