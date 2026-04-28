# NYX Backend — Railway Deployment Guide

## 1. Sign Up & Install CLI

```bash
# Sign up at https://railway.app (GitHub login, free $5/mo credit)

# Install Railway CLI
npm install -g @railway/cli

# Login
railway login
```

## 2. Create Project & Link

```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1

# Create a new Railway project (or link existing)
railway init --name nyx-backend

# Or if project already exists:
# railway link
```

## 3. Set Environment Variables (Secrets)

**CRITICAL:** Set these in Railway Dashboard (Project → Variables) or via CLI:

```bash
# Required
railway variables set MONGO_URI="your-mongodb-atlas-connection-string"
railway variables set GROQ_API_KEY="your-groq-api-key"
railway variables set JWT_SECRET_KEY="$(openssl rand -base64 48)"
railway variables set ENVIRONMENT="production"

# Optional
railway variables set LLM_PROVIDER="groq"
railway variables set GROQ_MODEL="llama-3.3-70b-versatile"
railway variables set CORS_ORIGINS="https://your-frontend-domain.com"
railway variables set UVICORN_WORKERS="1"   # Start with 1 on free tier
```

**IMPORTANT:** Never commit `.env` with real keys to git. Railway variables are encrypted and separate from your repo.

## 4. Deploy

```bash
# Deploy from current directory (uses Dockerfile)
railway up

# Or deploy specific directory
# railway up --detach
```

## 5. Verify Deployment

```bash
# Get deployed URL
railway domain

# Check logs
railway logs

# Check health
curl https://your-app-url.railway.app/health
```

## 6. Custom Domain (Optional)

In Railway Dashboard:
1. Go to your service → Settings → Domains
2. Click "Generate Domain" for free `*.railway.app` subdomain
3. Or add your custom domain and configure DNS

## 7. MongoDB Atlas IP Allowlist

Railway apps have dynamic IPs. In MongoDB Atlas:
- Go to Network Access → Add IP Address
- Add `0.0.0.0/0` (allow all) for simplicity
- **OR** use MongoDB Atlas VPC peering for security (paid feature)

## 8. Monitoring & Logs

```bash
# Live logs
railway logs -f

# View all variables
railway variables

# Restart service
railway restart
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Check `requirements.txt` is committed, rebuild |
| `Port already in use` | Railway sets `$PORT` automatically — we handle it in Dockerfile |
| `MongoDB connection timeout` | Allow `0.0.0.0/0` in Atlas, or check `MONGO_URI` |
| `CORS errors` | Update `CORS_ORIGINS` env var with your frontend URL |
| Out of memory | Reduce `UVICORN_WORKERS` to 1, or upgrade Railway plan |

## Files Used by Railway

- `Dockerfile` — Multi-stage build, production-ready
- `railway.json` / `railway.yaml` — Railway deploy config
- `backend/requirements.txt` — Python dependencies
- `backend/.env` — **NOT used in production** (use Railway Variables instead)

## Free Tier Limits

- $5/month credit (~1 small web service running 24/7)
- 512MB RAM, shared CPU
- Apps sleep after 15 min idle (wake on request ~5-10 sec cold start)
- For no sleep + more resources: upgrade to Hobby ($5/mo fixed) or Pro

---

**Next Steps:**
1. Sign up at https://railway.app
2. Run `railway login` and `railway init`
3. Set variables via dashboard or CLI
4. Run `railway up`
5. Done!
