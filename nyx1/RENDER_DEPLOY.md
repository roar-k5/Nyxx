# NYX Backend — Render Deployment Guide

## Option 1: Blueprint Deploy (Fastest — 2 minutes)

Render supports "Blueprints" — deploy from a YAML file with one click.

### Step 1: Push code to GitHub

```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1

# Initialize git (if not already)
git init
git add .
git commit -m "Ready for Render deploy"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/nyx-backend.git
git branch -M main
git push -u origin main
```

### Step 2: Update render.yaml

Edit `render.yaml` line 6:
```yaml
repo: https://github.com/YOUR_USERNAME/nyx-backend
```

### Step 3: One-Click Deploy

1. Go to https://dashboard.render.com/blueprint
2. Paste your GitHub repo URL: `https://github.com/YOUR_USERNAME/nyx-backend`
3. Render reads `render.yaml` and creates everything automatically
4. **Set your secrets** in the dashboard when prompted:
   - `MONGO_URI`
   - `GROQ_API_KEY`
   - `CORS_ORIGINS` (your frontend URL)
5. Click "Apply" — done!

---

## Option 2: Manual Deploy (More Control)

### Step 1: Sign Up
- https://render.com — free tier, no credit card

### Step 2: New Web Service
1. Dashboard → "New +" → "Web Service"
2. Connect your GitHub repo
3. Configure:
   - **Name:** `nyx-backend`
   - **Runtime:** `Docker`
   - **Branch:** `main`
   - **Root Directory:** `.`
   - **Dockerfile Path:** `./Dockerfile`

### Step 3: Set Environment Variables

In Dashboard → Your Service → Environment:

| Variable | Value | Source |
|----------|-------|--------|
| `ENVIRONMENT` | `production` | Plain text |
| `PORT` | `10000` | Plain text (Render default) |
| `UVICORN_WORKERS` | `1` | Plain text |
| `MONGO_URI` | `mongodb+srv://...` | Secret |
| `GROQ_API_KEY` | `gsk_...` | Secret |
| `JWT_SECRET_KEY` | random string | Secret |
| `LLM_PROVIDER` | `groq` | Plain text |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Plain text |
| `CORS_ORIGINS` | `https://your-frontend.onrender.com` | Plain text |

**Generate JWT secret:**
```bash
openssl rand -base64 48
```

### Step 4: Deploy

Click "Create Web Service" — Render builds the Docker image and deploys.

---

## Option 3: Render CLI (For Updates)

```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Link to existing service
render services
render link --service srv-xxxxxxxx

# Deploy latest code
render deploy
```

---

## Free Tier Details

| Feature | Limit |
|---------|-------|
| RAM | 512MB |
| CPU | Shared |
| Disk | 1GB |
| Bandwidth | 100GB/month |
| Sleep | After 15 min idle (wakes on request ~30 sec cold start) |
| Custom domains | Yes, free SSL |

**For no sleep:** Upgrade to Starter ($7/mo) — never sleeps, more resources.

---

## Health Checks & Monitoring

Render auto-checks `/health` every few seconds. If it fails 3 times, service restarts.

View logs:
- Dashboard → Service → Logs
- Or: `render logs --service nyx-backend`

---

## MongoDB Atlas Setup

Render apps have dynamic outbound IPs. In MongoDB Atlas:
1. Network Access → Add IP Address
2. Click "Allow Access from Anywhere" → `0.0.0.0/0`
3. **Security note:** This is acceptable for development. For production, use MongoDB Atlas's "Private Endpoint" or IP Access List with Render's static outbound IP (Starter plan feature).

---

## Custom Domain (Free)

1. Dashboard → Service → Settings → Custom Domains
2. Add your domain (e.g., `api.nyxapp.com`)
3. Render gives you a CNAME target
4. Add CNAME record in your DNS provider
5. Render auto-provisions SSL certificate

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails | Check `Dockerfile` path is `./Dockerfile` |
| `Port already in use` | Don't hardcode port — use `$PORT` env var (we handle this) |
| MongoDB timeout | Add `0.0.0.0/0` to Atlas IP allowlist |
| CORS errors | Update `CORS_ORIGINS` with your exact frontend URL |
| Out of memory | Reduce `UVICORN_WORKERS` to 1, or upgrade plan |
| Cold start slow | Normal on free tier — upgrade to Starter for always-on |

---

## Files Used by Render

- `Dockerfile` — Multi-stage build
- `render.yaml` — Blueprint config (auto-deploy, env vars, health checks)
- `backend/requirements.txt` — Python deps
- `backend/server_v2.py` — FastAPI app

**NOT used:** `backend/.env` — secrets go in Render dashboard instead

---

## Quick Reference

```bash
# Check if service is up
curl https://nyx-backend.onrender.com/health

# View logs via CLI
render logs --service nyx-backend

# Restart service
render deploy --service nyx-backend
```

---

**Deploy now:**
1. Push to GitHub
2. Go to https://dashboard.render.com/blueprint
3. Paste repo URL
4. Set 3 secrets (MONGO_URI, GROQ_API_KEY, CORS_ORIGINS)
5. Click Apply → Live in 2 minutes!
