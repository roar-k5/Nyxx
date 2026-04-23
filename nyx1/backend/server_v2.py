"""NYX v2 Server — extended app with auth, mood, safety, multi-provider LLM."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.authentication.auth_routes import router as auth_router
from backend.config.env import FRONTEND_DIR
from backend.database.db import close_db, get_db
from backend.routes.chat import router as chat_router
from backend.routes.mood import router as mood_router
from backend.routes.analyze import router as analyze_router
from backend.routes.crisis import router as crisis_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await get_db()
    if db is not None:
        print("MongoDB connected via db.py")
    else:
        print("MONGO_URI is not set. Starting without MongoDB.")

    try:
        yield
    finally:
        await close_db()


app = FastAPI(title="NYXX Backend v2", version="2.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/config/status")
async def config_status():
    return {
        "groqConfigured": bool(os.getenv("GROQ_API_KEY")),
        "geminiConfigured": bool(os.getenv("GEMINI_API_KEY")),
        "mongoConfigured": bool(os.getenv("MONGO_URI")),
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "llmProvider": os.getenv("LLM_PROVIDER", "groq"),
    }


app.include_router(auth_router, prefix="/api/auth")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(mood_router, prefix="/api/mood")
app.include_router(analyze_router, prefix="/api")
app.include_router(crisis_router, prefix="/api")

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.server_v2:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        reload=True,
    )
