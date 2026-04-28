# NYX Mind - Mental Health Companion

> An AI-powered mental health companion with crisis detection, mood tracking, and empathetic conversational support.

---

## Overview

NYX Mind is a full-stack mental health companion application that combines:
- **AI-powered chat** with emotional analysis and empathetic responses
- **Crisis detection** with safety escalation protocols
- **User authentication** (JWT-based)
- **Mood tracking** with data visualization
- **Multi-LLM support** (Groq, Gemini, Ollama, LM Studio, Mock mode)
- **Dual frontend**: Vanilla JS web + Flutter mobile app

---

## Project Structure

```
nyx1/
├── backend/                    # FastAPI Python backend
│   ├── server.py              # Main FastAPI server (v1)
│   ├── server_v2.py           # Alternative server (v2)
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (NOT in git)
│   ├── .env.example          # Environment template
│   │
│   ├── authentication/        # JWT auth system
│   │   ├── auth_controller.py # Login/register logic
│   │   ├── auth_model.py      # User models
│   │   ├── auth_routes.py     # FastAPI auth endpoints
│   │   ├── jwt_utils.py       # JWT create/decode
│   │   └── password_validator.py
│   │
│   ├── config/                # Configuration
│   │   ├── env.py             # Environment loader
│   │   └── prompts.py         # LLM prompts
│   │
│   ├── controllers/           # Business logic
│   │   └── chat_controller.py # Main chat flow
│   │
│   ├── database/              # Database layer
│   │   ├── db.py              # MongoDB connection
│   │   ├── sqlite_fallback.py # SQLite fallback
│   │   ├── nyx.sqlite         # SQLite database file
│   │   └── mood_analyzer.py   # Mood analytics
│   │
│   ├── middleware/            # Security middleware
│   │   ├── rate_limiter.py    # In-memory rate limiting
│   │   └── security_logging.py # Security event logging
│   │
│   ├── models/                # Pydantic data models
│   │   ├── analysis.py        # AnalysisResult model
│   │   └── message.py         # Message model
│   │
│   ├── routes/                # API route handlers
│   │   ├── chat.py            # Chat endpoints
│   │   ├── analyze.py         # Analysis endpoints
│   │   ├── crisis.py          # Crisis endpoints
│   │   └── mood.py            # Mood endpoints
│   │
│   ├── safety/                # Safety layer
│   │   ├── detector.py        # Safety signal detection
│   │   ├── crisis_detector.py # Crisis detection
│   │   ├── prompt_injection_filter.py # Prompt injection protection
│   │   └── response_filter.py # Response filtering
│   │
│   └── services/              # Core services
│       ├── analyzer.py         # Message analyzer
│       ├── llm_service_v2.py  # LLM service (v2)
│       ├── llm_service_full.py # LLM service (full)
│       ├── post_processor.py  # Response post-processing
│       ├── prompt_builder.py  # Prompt construction
│       ├── risk_engine.py     # Risk assessment
│       └── health_checker.py  # Health checks
│
├── frontend/                  # Vanilla JS web frontend
│   ├── index.html            # Main HTML
│   ├── app.js                # Frontend logic
│   └── styles.css            # Styling
│
├── frontend_flutter/          # Flutter mobile app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/          # UI screens
│   │   │   ├── chat_screen.dart
│   │   │   ├── crisis_screen.dart
│   │   │   ├── login_screen.dart
│   │   │   ├── register_screen.dart
│   │   │   ├── splash_screen.dart
│   │   │   └── mood_dashboard.dart
│   │   ├── services/
│   │   │   └── api_service.dart
│   │   └── theme/
│   │       └── app_colors.dart
│   └── pubspec.yaml
│
├── docs/
│   ├── API.md                # API documentation
│   └── PROJECT_GUIDE.md      # Project guide
│
└── temp_nyx_repo/            # Temporary git repo (can be removed)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11+) |
| Database | MongoDB (primary) / SQLite (fallback) |
| LLM APIs | Groq, Gemini, Ollama, LM Studio |
| Auth | JWT + bcrypt |
| Web Frontend | Vanilla HTML/CSS/JS |
| Mobile | Flutter (Dart) |
| Deployment | Uvicorn (ASGI server) |

---

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Environment Variables

Create `backend/.env`:

```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/nyx
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=groq
JWT_SECRET_KEY=generate_a_strong_random_secret_here
```

### 3. Run the Server

```bash
# From backend directory
python -m uvicorn backend.server:app --reload --port 5000

# Or directly
python backend/server.py
```

### 4. Open the Frontend

Open `frontend/index.html` in a browser, or serve it:

```bash
cd frontend
python -m http.server 3000
```

Visit: `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| GET | `/config/status` | Config status | No |
| POST | `/api/auth/register` | Register user | No |
| POST | `/api/auth/login` | Login user | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/chat/send` | Send chat message | Yes |
| GET | `/api/mood/history` | Get mood history | Yes |
| POST | `/api/mood/log` | Log mood | Yes |
| GET | `/api/crisis/resources` | Crisis resources | No |

---

## LLM Providers

Set `LLM_PROVIDER` in `.env`:

| Provider | Requirements | Use Case |
|----------|-------------|----------|
| `groq` | GROQ_API_KEY | Fast, production |
| `gemini` | GEMINI_API_KEY | Google's models |
| `ollama` | Ollama running locally | Local, private |
| `lmstudio` | LM Studio running locally | Local, private |
| `mock` | None | Testing, offline |

---

## Features

### Mental Health Chat
- Real-time emotional analysis of user messages
- Crisis detection with automatic escalation
- Emppathetic, Gen-Z style responses
- Safety guardrails against harmful content

### Crisis Detection
- Keyword-based crisis signal detection
- Automatic helpline suggestions (demo mode)
- Safety logging for crisis events

### Mood Tracking
- Log emotions and intensity
- View mood history and trends
- Data visualization (Flutter app)

### Authentication
- JWT-based secure authentication
- Password strength validation
- Rate-limited login/register endpoints

### Safety Features
- Prompt injection filtering
- Response content filtering
- Rate limiting per endpoint
- Security event logging

---

## Development

### Run Tests
```bash
cd backend
pytest
```

### Code Style
```bash
black backend/
ruff check backend/
```

### Flutter App
```bash
cd frontend_flutter
flutter pub get
flutter run
```

---

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions for:
- Docker
- Railway/Render
- AWS/GCP/Azure
- Self-hosted

---

## Security Considerations

This project handles sensitive mental health data. See [SECURITY.md](docs/SECURITY.md) for:
- Data privacy guidelines
- HIPAA/GDPR considerations
- Security best practices
- Vulnerability reporting

---

## License

MIT License - See LICENSE file

---

## Disclaimer

NYX Mind is an AI companion, **not a replacement for professional mental health care**. If you or someone you know is in crisis, please contact emergency services or a mental health professional immediately.

**Demo helpline numbers in the codebase are NOT real.** Replace with actual local helplines before production use.

---

## Contributors

Built with care for mental health support.
