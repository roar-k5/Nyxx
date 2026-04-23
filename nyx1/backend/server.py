import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient

from backend.config.env import FRONTEND_DIR
from backend.routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_uri = os.getenv("MONGO_URI")
    app.state.mongo_client = None
    app.state.database = None

    if mongo_uri:
        try:
            client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
            await client.admin.command("ping")
            app.state.mongo_client = client
            app.state.database = client.get_default_database(default="nyx")
            print("MongoDB connected")
        except Exception as exc:
            print(f"MongoDB connection failed: {exc}")
            raise
    else:
        print("MONGO_URI is not set. Starting without MongoDB.")

    try:
        yield
    finally:
        if app.state.mongo_client:
            app.state.mongo_client.close()


app = FastAPI(title="NYXX Backend", version="1.0.0", lifespan=lifespan)

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
        "mongoConfigured": bool(os.getenv("MONGO_URI")),
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    }


app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
