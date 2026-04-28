# NYXX Project Guide

## Overview

NYXX is a mental health support application built with a FastAPI backend and a Flutter frontend. The project focuses on supportive chat, emotional analysis, crisis detection, and mood tracking.

The codebase currently includes both active code and older/duplicate folders, so this document marks the practical source of truth and explains how the app is organized today.

## Architecture

```text
Flutter App
  -> HTTP API client
  -> FastAPI backend
     -> analysis + safety services
     -> LLM provider integration
     -> auth and mood routes
     -> MongoDB or partial SQLite fallback
```

## Source Of Truth

Use these folders/files as the main app:

- `backend/`
- `frontend_flutter/`
- `backend/server_v2.py`

Treat these as secondary or legacy until cleaned up:

- `frontend/`
- `backend/server.py`
- `temp_nyx_repo/`

## Backend Structure

### App Entry

- `backend/server_v2.py`

This file creates the FastAPI app, registers middleware, manages startup/shutdown DB lifecycle, and includes the main routers.

### Key Backend Modules

- `backend/routes/`
  Defines API endpoints for chat, auth, analysis, crisis info, and mood features.

- `backend/controllers/chat_controller.py`
  Main chat orchestration layer. It handles request parsing, analysis, risk assessment, response generation, post-processing, and persistence attempts.

- `backend/services/`
  Contains analysis, risk, prompt, and LLM-related logic.

- `backend/safety/`
  Safety checks and response filtering for risky content.

- `backend/authentication/`
  JWT auth routes, models, controller logic, and token utilities.

- `backend/database/`
  MongoDB connection helpers, mood utilities, and SQLite fallback code.

- `backend/config/prompts.py`
  Nyx persona and guidance prompts.

### Important Backend Flows

#### Chat Flow

1. frontend posts a message to `/api/chat/send`
2. message is analyzed for emotion/intent/risk
3. risk is assessed by the risk engine
4. a prompt is built for response generation
5. LLM output is post-processed for safety
6. a JSON response is sent back to the frontend

#### Auth Flow

1. user registers or logs in via `/api/auth/*`
2. backend validates credentials
3. backend returns a bearer token
4. frontend stores token locally and uses it for protected requests

#### Mood Flow

1. frontend requests weekly mood data
2. backend reads stored entries
3. backend returns summary stats and trend information

## Frontend Structure

### App Entry

- `frontend_flutter/lib/main.dart`

This sets the app routes and now includes both light and dark themes with `ThemeMode.system`.

### Key Screens

- `splash_screen.dart`
  Startup routing based on whether a token exists.

- `login_screen.dart`
  User sign-in UI.

- `register_screen.dart`
  User registration UI.

- `chat_screen.dart`
  Main conversation UI.

- `crisis_screen.dart`
  Crisis escalation and helpline UI.

- `mood_dashboard.dart`
  Mood insights and charts.

### Frontend Services

- `frontend_flutter/lib/services/api_service.dart`
  Central API client for chat, analysis, crisis info, and health checks.

### Current UI Direction

The recent UI update moved the app away from the older dull dark-purple look to:

- a brighter pastel light theme
- a matching dark theme
- shared color tokens in `frontend_flutter/lib/theme/app_colors.dart`

## API Summary

### Public Utility Endpoints

- `GET /health`
- `GET /config/status`

### Auth Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Chat And Safety Endpoints

- `POST /api/chat/send`
- `POST /api/analyze`
- `GET /api/crisis-info`

### Mood Endpoints

- `GET /api/mood/weekly`
- `POST /api/mood/store`

For endpoint-level payload details, see `docs/API.md`.

## Environment Setup

Create `backend/.env` with values like:

```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/nyx
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=optional_key_here
LLM_PROVIDER=groq
```

## Running The Project

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..
python -m uvicorn backend.server_v2:app --host 0.0.0.0 --port 5000 --reload
```

### Flutter

```bash
cd frontend_flutter
flutter pub get
flutter run
```

## Known Limitations

- crisis helplines are demo values, not production-certified data
- the SQLite fallback is not fully consistent across all backend features
- the repo contains duplicate or legacy code paths
- final Flutter formatting/analyze verification was interrupted during recent UI work
- some prompt and runtime layers are more duplicated than they should be

## Recommended Cleanup Roadmap

### High Priority

- standardize one backend path around `server_v2.py`
- remove or archive duplicate app copies
- unify persistence so MongoDB and SQLite follow one repository interface
- connect runtime response generation to the central prompt builder more consistently

### Medium Priority

- add tests for crisis, auth, and chat flows
- tighten CORS and production config
- clean build artifacts and duplicate folders from the repo

### Low Priority

- refresh old docs after code cleanup
- improve visual consistency further after final Flutter verification

## Ownership Notes

If someone new joins the project, the easiest starting points are:

- backend API and route flow: `backend/server_v2.py`
- chat orchestration: `backend/controllers/chat_controller.py`
- prompts/persona: `backend/config/prompts.py`
- mobile UI entry: `frontend_flutter/lib/main.dart`
