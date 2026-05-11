from .auth import router as auth_router
from .chat import router as chat_router
from .sessions import router as sessions_router
from .challenges import router as challenges_router
from .vulnerabilities import router as vulnerabilities_router

__all__ = [
    "auth_router",
    "chat_router",
    "sessions_router",
    "challenges_router",
    "vulnerabilities_router",
]
