from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent

_frontend_candidates = (
    ROOT_DIR / "frontend",
    ROOT_DIR / "frontend" / "build",
    ROOT_DIR / "frontend" / "build" / "web",
    ROOT_DIR / "frontend_flutter" / "build" / "web",
)
FRONTEND_DIR = next((path for path in _frontend_candidates if path.exists()), ROOT_DIR / "frontend")

load_dotenv(BACKEND_DIR / ".env")
