from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rule_based_chatbot import get_chatbot
from routers import (
    auth_router,
    chat_router,
    sessions_router,
    challenges_router,
    vulnerabilities_router,
)
from routers import chat as chat_module

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    try:
        chatbot = get_chatbot()
        chat_module.set_chatbot(chatbot)
        print("✓ Rule-based chatbot initialised")
    except Exception as exc:
        print(f"✗ Chatbot init failed: {exc}")
        raise

    yield

    # --- SHUTDOWN ---
    print("Shutting down application...")
    chat_module.set_chatbot(None)
    print("✓ Rule-based chatbot shutdown")

app = FastAPI(
    title="DonkAI API — OWASP Top 10 LLM",
    version="2.0.0",
    description="Educational lab exposing all 10 OWASP LLM vulnerabilities.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(challenges_router)
app.include_router(vulnerabilities_router)

# ---------------------------------------------------------------------------
# Utility endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "DonkAI API — OWASP Top 10 LLM",
        "status": "running",
        "warning": "Contains intentional security flaws for educational purposes.",
    }


@app.get("/health")
async def health_check():
    from routers.chat import _chatbot
    return {
        "status": "healthy",
        "chatbot": "ready" if _chatbot is not None else "not initialised",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
