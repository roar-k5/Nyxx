# NYX — Vercel Deployment Guide

## Architecture

| Service | Platform | Why |
|---------|----------|-----|
| **Frontend** | Vercel | Perfect for React/Vue/Flutter web |
| **Backend** | Render/Railway | Better for Python/FastAPI + MongoDB |

---

## Option 1: Frontend on Vercel + Backend on Render (Recommended)

### Step 1: Deploy Backend to Render

Already done! Your backend is ready at:
- Repo: https://github.com/roar-k5/Nyxx
- Render deploy: See RENDER_DEPLOY.md

Get your backend URL after deploy: `https://nyx-backend.onrender.com`

### Step 2: Prepare Frontend for Vercel

Your frontend is in `frontend/` (vanilla JS). For Vercel, we just need to serve it.

Create `frontend/vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### Step 3: Update Frontend API URL

In `frontend/app.js`, update the API base URL:

```javascript
const API_BASE = 'https://nyx-backend.onrender.com';  // Your Render backend URL
```

### Step 4: Deploy Frontend to Vercel

```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend

# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

Or use GitHub integration:
1. Push `frontend/` to a separate repo (or keep in monorepo)
2. Go to https://vercel.com/new
3. Import your repo
4. Root Directory: `frontend`
5. Deploy

---

## Option 2: Full-Stack on Vercel (Docker - Beta)

Vercel now supports Docker deployments. Your entire app (frontend + backend) can run on Vercel.

### Requirements
- Vercel Pro account (Docker is paid feature)
- `vercel.json` with Docker config

### Setup

Create `vercel.json` at root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "Dockerfile",
      "use": "@vercel/docker"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "http://localhost:5000/api/$1"
    },
    {
      "src": "/health",
      "dest": "http://localhost:5000/health"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ],
  "env": {
    "ENVIRONMENT": "production"
  }
}
```

**Note:** This requires Vercel Pro ($20/mo) and is more complex. Not recommended for free tier.

---

## Option 3: Frontend + Backend Both on Vercel (Serverless)

**⚠️ NOT RECOMMENDED** for this app because:
- Vercel serverless functions have 15MB limit
- FastAPI + ML dependencies exceed this
- MongoDB connections don't persist between cold starts
- LLM API calls may timeout (10s limit on free tier)

---

## Recommended Setup: Vercel + Render

```
User → Vercel (Frontend) → Render (Backend) → MongoDB Atlas
         ↓                      ↓
    Static HTML/JS        FastAPI + LLM
    vercel.app            onrender.com
```

### CORS Configuration

In your Render backend `.env`:
```
CORS_ORIGINS=https://nyx-frontend.vercel.app,https://nyx-frontend-git-main-roar-k5.vercel.app
```

Vercel preview deployments get random URLs, so you may need to:
1. Use `CORS_ORIGINS=*` for development (not production)
2. Or update CORS_ORIGINS each time you deploy

### Environment Variables

**Vercel Dashboard → Project → Settings → Environment Variables:**

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://nyx-backend.onrender.com` |

---

## Flutter Web on Vercel

If you want to deploy the Flutter app instead of vanilla JS:

```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend_flutter

# Build for web
flutter build web

# Deploy build/web to Vercel
cd build/web
vercel --prod
```

---

## Quick Deploy Commands

```bash
# Backend (already ready)
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1
# Follow RENDER_DEPLOY.md

# Frontend (vanilla JS)
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend
vercel --prod

# OR Flutter Web
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend_flutter
flutter build web
cd build/web
vercel --prod
```

---

## Summary

| What | Where | Cost |
|------|-------|------|
| Frontend | Vercel | Free |
| Backend API | Render | Free |
| Database | MongoDB Atlas | Free tier |
| **Total** | | **$0/month** |

This is the most reliable and cost-effective setup for your NYX app.
