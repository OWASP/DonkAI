"""
challenges/validate.py

CLI entrypoint for validating all category and challenge definitions.

Usage
-----
    python -m challenges.validate

Exit codes
----------
  0  — all categories and challenges are valid
  1  — one or more validation errors found
"""

from __future__ import annotations

import sys

from challenges.registry import ChallengeRegistry
from challenges.schema import RegexEvaluatorDefinition


def validate() -> bool:
    """Return True if all definitions are valid, False otherwise."""
    errors: list[str] = []

    categories = ChallengeRegistry.list_categories()
    if not categories:
        errors.append("No categories found. Check challenges/categories/ is populated.")

    for cat in categories:
        prefix = f"[{cat.id}] {cat.name}"

        if not cat.challenges:
            errors.append(f"{prefix}: has no challenges defined")

        for challenge in cat.challenges:
            cprefix = f"{prefix} / {challenge.id}"

            if not challenge.hints:
                errors.append(f"{cprefix}: has no hints")

            if not challenge.success_response:
                errors.append(f"{cprefix}: success_response is empty")

            if isinstance(challenge.evaluator, RegexEvaluatorDefinition):
                if not challenge.evaluator.success_patterns:
                    errors.append(f"{cprefix}: evaluator has no success_patterns")
            else:
                print(f"  ⚠  {cprefix}: uses a CustomEvaluatorDefinition — skipping regex checks")

    if errors:
        print(f"\n❌  {len(errors)} validation error(s) found:\n")
        for e in errors:
            print(f"  • {e}")
        return False

    print(f"\n✅  {len(categories)} categories validated successfully.\n")
    for cat in categories:
        print(f"  {cat.id}  {cat.name}  ({len(cat.challenges)} challenge(s))")
    print()
    return True


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
