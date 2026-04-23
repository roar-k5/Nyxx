# NYXX — Mental Health AI Companion

A full-stack mental health support application with an empathetic AI chatbot, mood tracking, crisis detection, and safety-first architecture.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Backend](#backend)
  - [Setup](#backend-setup)
  - [Environment Variables](#environment-variables)
  - [Running the Server](#running-the-server)
  - [API Endpoints](#api-endpoints)
  - [Error Resolution Log](#backend-error-resolution-log)
- [Frontend (Flutter)](#frontend-flutter)
  - [Setup](#frontend-setup)
  - [Running the App](#running-the-app)
  - [Screens](#screens)
  - [Error Resolution Log](#frontend-error-resolution-log)
- [Development History](#development-history)
- [Verification Checklist](#verification-checklist)
- [License](#license)

---

## Overview

NYXX is an AI-powered mental health companion designed to provide empathetic, safe, and supportive conversations. It features real-time emotion analysis, crisis detection with helpline resources, mood tracking dashboards, and a dark-themed calming UI.

**Key Capabilities:**
- Empathetic AI chat with emotion detection
- Crisis detection with safety escalation
- Mood tracking and visualization
- User authentication (JWT-based)
- Multi-provider LLM support (Groq, Gemini)
- MongoDB persistence with SQLite fallback

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Chat Screen │  │Crisis Screen│  │ Mood Dashboard      │  │
│  │             │  │             │  │                     │  │
│  │ • Messaging │  │ • Helplines │  │ • Weekly charts     │  │
│  │ • Emotion   │  │ • Safety    │  │ • Entry logging     │  │
│  │   display   │  │   resources │  │ • Trend analysis    │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                      │             │
│         └────────────────┴──────────────────────┘             │
│                            │                                  │
│                    ┌─────────┴──────────┐                      │
│                    │   API Service      │                      │
│                    │ (HTTP client)      │                      │
│                    └─────────┬──────────┘                      │
└──────────────────────────────┼───────────────────────────────┘
                               │ HTTP/JSON
┌──────────────────────────────┼───────────────────────────────┐
│                    BACKEND   │                               │
│  ┌───────────────────────────┴───────────────────────────┐  │
│  │              FastAPI Server (Python)                    │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │  │
│  │  │ /health │ │/chat    │ │/analyze │ │/crisis-info │  │  │
│  │  │/config  │ │/auth    │ │/mood    │ │             │  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘  │  │
│  │       └─────────────┴───────────┴─────────────┘         │  │
│  │                         │                              │  │
│  │              ┌──────────┴──────────┐                   │  │
│  │              │   Chat Controller   │                   │  │
│  │              │  • Safety detection │                   │  │
│  │              │  • Risk assessment  │                   │  │
│  │              │  • Response build   │                   │  │
│  │              └──────────┬──────────┘                   │  │
│  │                         │                              │  │
│  │       ┌─────────────────┼─────────────────┐             │  │
│  │       ▼                 ▼                 ▼             │  │
│  │  ┌─────────┐      ┌──────────┐      ┌──────────┐      │  │
│  │  │  Groq   │      │  Gemini  │      │  Safety  │      │  │
│  │  │  LLM    │      │  LLM     │      │  Filter  │      │  │
│  │  └─────────┘      └──────────┘      └──────────┘      │  │
│  │       │                 │                 │             │  │
│  │       └─────────────────┴─────────────────┘             │  │
│  │                         │                              │  │
│  │              ┌──────────┴──────────┐                   │  │
│  │              │    MongoDB /        │                   │  │
│  │              │    SQLite Fallback   │                   │  │
│  │              └─────────────────────┘                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.12 | Server runtime |
| | FastAPI 0.115.6 | Web framework |
| | Uvicorn 0.34.0 | ASGI server |
| | Groq SDK 0.13.1 | LLM inference (llama-3.3-70b) |
| | Motor 3.6.0 | Async MongoDB driver |
| | Pydantic 2.10.4 | Data validation |
| | Passlib + python-jose | Authentication |
| | python-dotenv | Environment management |
| **Frontend** | Flutter 3.x | Cross-platform UI |
| | Dart 3.x | Language |
| | http ^1.1.0 | HTTP client |
| | shared_preferences ^2.2.2 | Local storage |
| | fl_chart ^0.65.0 | Mood charts |
| **Database** | MongoDB | Primary persistence |
| | SQLite | Fallback (no MongoDB) |
| **External APIs** | Groq API | Primary LLM |
| | Gemini API | Alternative LLM |

---

## Project Structure

```
nyx1/
├── backend/                    # FastAPI Python backend
│   ├── server.py              # Original server (v1)
│   ├── server_v2.py           # Extended server (v2) — AUTH, MOOD, SAFETY
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── .env.example           # Environment template
│   ├── authentication/          # JWT auth system
│   │   ├── auth_controller.py
│   │   ├── auth_model.py
│   │   ├── auth_routes.py
│   │   └── jwt_utils.py
│   ├── config/                # Configuration
│   │   ├── env.py
│   │   └── prompts.py
│   ├── controllers/           # Business logic
│   │   └── chat_controller.py
│   ├── database/              # Database layer
│   │   ├── db.py
│   │   ├── mood_analyzer.py
│   │   └── sqlite_fallback.py
│   ├── models/                # Pydantic models
│   │   ├── analysis.py
│   │   └── message.py
│   ├── routes/                # API route definitions
│   │   ├── analyze.py
│   │   ├── chat.py
│   │   ├── crisis.py
│   │   └── mood.py
│   ├── safety/                # Safety & crisis detection
│   │   ├── crisis_detector.py
│   │   ├── detector.py
│   │   └── response_filter.py
│   └── services/              # Core services
│       ├── analyzer.py
│       ├── llm_service_full.py
│       ├── llm_service_v2.py
│       ├── post_processor.py
│       ├── prompt_builder.py
│       └── risk_engine.py
│
├── frontend_flutter/           # Flutter mobile app
│   ├── pubspec.yaml           # Flutter dependencies
│   ├── lib/
│   │   ├── main.dart          # App entry point
│   │   ├── screens/           # UI screens
│   │   │   ├── chat_screen.dart
│   │   │   ├── crisis_screen.dart
│   │   │   ├── login_screen.dart
│   │   │   ├── mood_dashboard.dart
│   │   │   ├── register_screen.dart
│   │   │   └── splash_screen.dart
│   │   └── services/          # API client
│   │       └── api_service.dart
│   └── build/                 # Build artifacts
│
├── frontend/                   # Original web frontend (legacy)
│
├── docs/                       # Documentation
│   └── API.md                 # API endpoint docs
│
├── README.md                   # This file
└── .gitignore
```

---

## Backend

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or: venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Environment Variables

Create a `.env` file in `backend/`:

```env
PORT=8000
MONGO_URI=mongodb://127.0.0.1:27017/nyx
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=your_gemini_api_key_here  # Optional
LLM_PROVIDER=groq  # or 'gemini'
```

### Running the Server

**Development (with auto-reload):**
```bash
cd /path/to/nyx1
python3 -c "import sys; sys.path.insert(0, '.'); from backend.server_v2 import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)"
```

**Or directly:**
```bash
cd backend
python server_v2.py
```

**Production:**
```bash
uvicorn backend.server_v2:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/config/status` | Configuration status |
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Current user profile |
| POST | `/api/chat/send` | Send chat message |
| GET | `/api/mood/weekly` | Get weekly mood data |
| POST | `/api/mood/store` | Store mood entry |
| POST | `/api/analyze` | Analyze message (standalone) |
| GET | `/api/crisis-info` | Get crisis helplines |

### Backend Error Resolution Log

| # | Error | Cause | Fix |
|---|-------|-------|-----|
| 1 | `ModuleNotFoundError: No module named 'backend'` | Running from wrong directory | Add `sys.path.insert(0, '.')` before import |
| 2 | `ImportError: cannot import name 'ChatMessage' from 'backend.models.analysis'` | Missing model class | Added `ChatMessage` dataclass to `analysis.py` |
| 3 | `Groq API connection timeout` | Invalid API key or network | Validate `.env` GROQ_API_KEY; add fallback message |
| 4 | `MongoDB connection failed` | MONGO_URI not set or MongoDB not running | Graceful fallback — app starts without DB |
| 5 | `Pydantic validation error on history field` | Empty history array type mismatch | Set `history: Optional[List[dict]] = []` with default |

---

## Frontend (Flutter)

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend_flutter
   ```

2. **Get dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run the app:**
   ```bash
   flutter run
   ```

### Screens

| Screen | File | Features |
|--------|------|----------|
| Splash | `splash_screen.dart` | Animated logo, navigation to login |
| Login | `login_screen.dart` | JWT authentication, error display |
| Register | `register_screen.dart` | Account creation |
| Chat | `chat_screen.dart` | Real-time messaging, emotion tags, crisis UI |
| Crisis | `crisis_screen.dart` | Helpline cards, safety resources |
| Mood Dashboard | `mood_dashboard.dart` | Weekly charts, mood logging |

### Frontend Error Resolution Log

| # | Error | Cause | Fix |
|---|-------|-------|-----|
| 1 | `withOpacity is deprecated` (22 instances) | Flutter SDK upgrade deprecated `withOpacity` | Replaced all `.withOpacity(value)` with `.withValues(alpha: value)` across 7 files |
| 2 | `dart: command not found` | CRLF line endings in Windows Flutter install | Ran `sed -i 's/\r$//' flutter/bin/dart` |
| 3 | `dart.exe not found` | Wrong path to Dart SDK | Used full path: `flutter/bin/cache/dart-sdk/bin/dart.exe` |
| 4 | `Too many positional arguments: 0 expected, but 1 found` | `withValues()` requires named parameter | Changed `withValues(0.5)` to `withValues(alpha: 0.5)` |

---

## Development History

### Phase 1: Core Backend (v1)
- Built FastAPI server with basic chat endpoint
- Integrated Groq LLM (llama-3.3-70b-versatile)
- Added MongoDB persistence via Motor
- Created emotion analysis pipeline

### Phase 2: Safety & Crisis Detection
- Implemented `SafetyDetector` class
- Added crisis keyword detection
- Built crisis escalation flow with helpline resources
- Created `RiskEngine` for risk scoring

### Phase 3: Extended Backend (v2)
- Added authentication system (JWT + bcrypt)
- Created mood tracking endpoints
- Added standalone `/analyze` endpoint
- Implemented multi-provider LLM support (Groq + Gemini)
- Built SQLite fallback for offline mode

### Phase 4: Flutter Frontend
- Built 6-screen Flutter application
- Implemented dark theme with purple accents
- Created chat UI with emotion display
- Added mood dashboard with `fl_chart`
- Integrated all backend APIs

### Phase 5: Verification & Cleanup
- Verified all 4 API endpoints return 200
- Fixed 22 Flutter deprecation warnings
- Ran `dart format` on all files
- Achieved `No issues found!` on analyzer

---

## Verification Checklist

### Backend Verification

| Check | Command | Expected Result | Status |
|-------|---------|---------------|--------|
| Import test | `python3 -c "from backend.server_v2 import app"` | `Import OK` | ✅ |
| Health | `GET /health` | `{"status": "ok"}` | ✅ |
| Crisis info | `GET /api/crisis-info` | Helplines JSON | ✅ |
| Analyze | `POST /api/analyze` | Emotion analysis JSON | ✅ |
| Chat | `POST /api/chat/send` | Response + analysis JSON | ✅ |

### Frontend Verification

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| Format code | `dart format lib/` | 3 files formatted | ✅ |
| Analyze code | `dart analyze lib/` | `No issues found!` | ✅ |

---

## License

MIT License — Created for mental health awareness and support.

---

**Note:** This is a demo project. Crisis helpline numbers in the app are placeholders. For production, replace with real helpline numbers (e.g., Tele MANAS: 14416, KIRAN: 1800-599-0019).
