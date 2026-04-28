# NYX Vercel Deployment Guide

This repo is now set up for a single Vercel project that serves:

- the static web frontend from `frontend/`
- the FastAPI backend as a Python serverless function

## What Changed

- `api/index.py` is the Vercel entrypoint for FastAPI.
- `vercel.json` routes `/api/*`, `/health`, and `/config/status` to the backend.
- `/`, `/app.js`, and `/styles.css` are served from `frontend/`.
- Root `requirements.txt` points Vercel at `backend/requirements.txt`.
- SQLite fallback is disabled by default in production and on Vercel.

## Important Constraint

Do not deploy this to Vercel without a real `MONGO_URI`.

Your backend can fall back to SQLite during local development, but Vercel's filesystem is ephemeral. If you skip MongoDB in production, auth and mood data will not persist reliably. The repo now avoids that by refusing SQLite fallback on Vercel unless you explicitly override it.

## Deploy Steps

### 1. Push the repo to GitHub

Make sure the latest changes are committed and pushed.

### 2. Create a Vercel project

In Vercel:

1. Import the GitHub repository
2. Keep the **Root Directory** as the repo root
3. Framework preset can stay **Other**
4. Deploy

### 3. Add environment variables in Vercel

Project Settings -> Environment Variables:

```env
ENVIRONMENT=production
PYTHONPATH=.
MONGO_URI=your_mongodb_atlas_connection_string
JWT_SECRET_KEY=your_strong_secret
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
ALLOWED_ORIGINS=https://your-project-name.vercel.app
TRUSTED_HOSTS=your-project-name.vercel.app,*.vercel.app
```

Add provider-specific variables only for the LLM you actually use:

- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `OLLAMA_BASE_URL`
- `LMSTUDIO_BASE_URL`

### 4. Redeploy

After saving env vars, trigger a redeploy from the Vercel dashboard.

## Expected Routes

After deployment:

- `https://your-project.vercel.app/` -> frontend
- `https://your-project.vercel.app/health` -> backend health
- `https://your-project.vercel.app/config/status` -> backend config
- `https://your-project.vercel.app/api/auth/register` -> backend auth
- `https://your-project.vercel.app/api/chat/send` -> backend chat

## Local Behavior

- Opening `frontend/index.html` directly still targets `http://localhost:5000`
- Vercel deploys use same-origin requests automatically
- You only need `window.API_BASE_URL` if frontend and backend are split across different domains

## If Deployment Fails

Check these first:

1. `MONGO_URI` is set
2. `JWT_SECRET_KEY` is set
3. your LLM API key is set for the selected `LLM_PROVIDER`
4. `TRUSTED_HOSTS` includes your Vercel hostname
5. the project was deployed from the repo root, not from `frontend/`

## CLI Deploy

If you want to deploy from the terminal:

```bash
vercel
vercel --prod
```

Run those from the repo root.
