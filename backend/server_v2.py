import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

# Load environment variables FIRST, before any backend modules that need them
from backend.config.env import FRONTEND_DIR

from backend.authentication.auth_routes import router as auth_router
from backend.database.db import close_db, get_db
from backend.middleware.rate_limiter import auth_limiter, chat_limiter, public_limiter, rate_limit
from backend.routes.chat import router as chat_router
from backend.routes.mood import router as mood_router
from backend.routes.analyze import router as analyze_router
from backend.routes.crisis import router as crisis_router

# CORS: configure allowed origins via env, default to localhost only
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5000,http://localhost:3000,http://10.0.2.2:5000")
CORS_ORIGINS: List[str] = [origin.strip() for origin in ALLOWED_ORIGINS.split(",") if origin.strip()]

# In development, Flutter web runs on a random localhost port (e.g. http://localhost:51834),
# so we allow localhost/127.0.0.1 on any port via regex.
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
DEV_ORIGIN_REGEX = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$" if ENVIRONMENT != "production" else None

# Allow all origins wildcard if explicitly set (useful for Vercel/Render multi-domain)
_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "").lower() in {"1", "true", "yes", "on"}
if _ALLOW_ALL:
    CORS_ORIGINS = ["*"]
    DEV_ORIGIN_REGEX = None


from backend.services.health_checker import llm_health_checker


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await get_db()
    if db is not None:
        print("MongoDB connected via db.py")
    else:
        print("MONGO_URI is not set. Starting without MongoDB.")

    # Check LLM provider health
    llm_health = await llm_health_checker.check()
    if llm_health["healthy"]:
        print(f"LLM provider ({llm_health['provider']}) is healthy.")
    else:
        print(f"WARNING: LLM provider ({llm_health['provider']}) health check failed: {llm_health['message']}")

    try:
        yield
    finally:
        await close_db()


app = FastAPI(title="NYXX Backend v2", version="2.1.0", lifespan=lifespan)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=DEV_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Optional: enforce trusted hosts in production
if ENVIRONMENT == "production":
    TRUSTED_HOSTS = os.getenv("TRUSTED_HOSTS", "")
    if TRUSTED_HOSTS:
        allowed_hosts = [host.strip() for host in TRUSTED_HOSTS.split(",") if host.strip()]
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts,
        )
    else:
        print("WARNING: ENVIRONMENT=production but TRUSTED_HOSTS not set. Skipping TrustedHostMiddleware.")


@app.get("/health")
async def health(request: Request):
    public_limiter.raise_if_limited(request)
    llm_health = await llm_health_checker.check()
    return {
        "status": "ok",
        "llm_provider": llm_health["provider"],
        "llm_healthy": llm_health["healthy"],
    }


@app.get("/config/status")
async def config_status(request: Request):
    public_limiter.raise_if_limited(request)
    return {
        "status": "ok",
        "llmProvider": os.getenv("LLM_PROVIDER", "groq"),
    }


app.include_router(auth_router, prefix="/api/auth")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(mood_router, prefix="/api/mood")
app.include_router(analyze_router, prefix="/api")
app.include_router(crisis_router, prefix="/api")

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


if __name__ == "__main__":
    import uvicorn

    reload = ENVIRONMENT != "production"
    workers = 1 if reload else int(os.getenv("UVICORN_WORKERS", "2"))
    
    uvicorn.run(
        "backend.server_v2:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        reload=reload,
        workers=workers,
    )
