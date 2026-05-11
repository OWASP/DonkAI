"""
challenges/registry.py

The single source of truth for all OWASP LLM categories.

Usage
-----
    from challenges.registry import ChallengeRegistry

    category = ChallengeRegistry.get_category("llm01")
    engine   = ChallengeRegistry.get_engine("llm01")
    all_cats = ChallengeRegistry.list_categories()

Discovery
---------
The registry auto-discovers every module inside challenges/categories/
that exports a module-level ``CATEGORY`` object of type CategoryDefinition.
No manual registration is needed — adding a new file is sufficient.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Dict, List, Optional

from .engine import BaseChallengeEngine, RegexChallengeEngine
from .schema import CategoryDefinition, CustomEvaluatorDefinition


class _Registry:
    def __init__(self) -> None:
        self._categories: Dict[str, CategoryDefinition] = {}
        self._engines: Dict[str, BaseChallengeEngine] = {}
        self._loaded = False

    # ------------------------------------------------------------------
    # Bootstrap
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self._loaded:
            return

        from challenges import categories as _cat_pkg

        for module_info in pkgutil.iter_modules(_cat_pkg.__path__):
            module = importlib.import_module(
                f"challenges.categories.{module_info.name}"
            )
            category: Optional[CategoryDefinition] = getattr(module, "CATEGORY", None)
            if category is None or not isinstance(category, CategoryDefinition):
                continue
            self._register(category)

        # Sort by id so that list_categories() returns a stable order
        self._categories = dict(
            sorted(self._categories.items(), key=lambda kv: kv[0])
        )
        self._loaded = True

    def _register(self, category: CategoryDefinition) -> None:
        self._categories[category.id] = category
        self._engines[category.id] = self._build_engine(category)

    @staticmethod
    def _build_engine(category: CategoryDefinition) -> BaseChallengeEngine:
        # If every challenge uses a RegexEvaluatorDefinition the shared
        # engine is sufficient.  A category that needs custom logic should
        # implement its own BaseChallengeEngine subclass and override this
        # method, or set CUSTOM_ENGINE on the module level.
        needs_custom = any(
            isinstance(c.evaluator, CustomEvaluatorDefinition)
            for c in category.challenges
        )
        if needs_custom:
            # Fall back to RegexChallengeEngine for now; custom evaluators
            # will be skipped during evaluation with an informative error.
            pass
        return RegexChallengeEngine(category)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_category(self, category_id: str) -> Optional[CategoryDefinition]:
        self._load()
        return self._categories.get(category_id.lower())

    def get_engine(self, category_id: str) -> Optional[BaseChallengeEngine]:
        self._load()
        return self._engines.get(category_id.lower())

    def list_categories(self) -> List[CategoryDefinition]:
        self._load()
        return list(self._categories.values())


# Module-level singleton
ChallengeRegistry = _Registry()
