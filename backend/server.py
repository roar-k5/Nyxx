import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
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

# CORS: configure via environment variable
# Default allows local development only
# In production, set CORS_ORIGINS to your exact domain(s)
import os
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5000,http://127.0.0.1:5000")
CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=600,
)

# Security headers middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Request size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    max_size = int(os.getenv("MAX_CONTENT_LENGTH", "1048576"))  # 1MB default
    body = await request.body()
    if len(body) > max_size:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large. Maximum size is 1MB."}
        )
    # Rebuild request with body for downstream handlers
    from starlette.requests import Request as StarletteRequest
    async def receive():
        return {"type": "http.request", "body": body}
    request = StarletteRequest(request.scope, receive, request._send)
    return await call_next(request)


from backend.middleware.rate_limiter import public_limiter
from backend.middleware.https_enforcement import HTTPSRedirectMiddleware, ENFORCE_HTTPS

# Add HTTPS enforcement middleware in production
if ENFORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)

@app.get("/health")
async def health(request: Request):
    return {"status": "ok"}


@app.get("/config/status")
async def config_status(request: Request):
    public_limiter.raise_if_limited(request)
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
