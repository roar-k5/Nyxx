# NYXX

NYXX is a full-stack mental health companion project with:

- a FastAPI backend for chat, auth, analysis, mood tracking, and crisis info
- a Flutter frontend for mobile-style chat and mood flows
- safety-focused response handling for distress and crisis cases

## What This Repo Contains

```text
backend/            FastAPI app and business logic
frontend_flutter/   Flutter client
frontend/           legacy web frontend
docs/               project and API documentation
temp_nyx_repo/      extra copied workspace snapshot
```

## Main Features

- empathetic AI chat flow
- emotion and risk analysis
- crisis escalation with helpline payloads
- JWT-based auth
- mood tracking endpoints and dashboard
- light and dark mode Flutter UI

## Main Backend Entry

The main backend app is:

```text
backend/server_v2.py
```

Key routes exposed there:

- `GET /health`
- `GET /config/status`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/chat/send`
- `GET /api/mood/weekly`
- `POST /api/mood/store`
- `POST /api/analyze`
- `GET /api/crisis-info`

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example`, then run:

```bash
cd ..
python -m uvicorn backend.server_v2:app --host 0.0.0.0 --port 5000 --reload
```

### Flutter Frontend

```bash
cd frontend_flutter
flutter pub get
flutter run
```

## Configuration

Typical backend environment variables:

```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/nyx
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=optional_key_here
LLM_PROVIDER=groq
```

## Documentation

- Project guide: `docs/PROJECT_GUIDE.md`
- API reference: `docs/API.md`

## Important Notes

- Crisis helplines in the current app are demo values.
- `frontend/` is legacy compared to `frontend_flutter/`.
- `temp_nyx_repo/` looks like a duplicate snapshot rather than the main working app.
- The latest UI work added brighter light mode styling plus dark mode support in Flutter.

## Current Gaps

- final Flutter verification (`dart format`, `flutter analyze`) was interrupted and should be rerun
- some repo duplication and storage-layer inconsistencies still need cleanup
- documentation was cleaned up here, but the codebase still has older parallel versions in places
