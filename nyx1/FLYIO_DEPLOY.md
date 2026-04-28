# NYX Backend — Fly.io Deployment Guide

## Why Fly.io?

| Feature | Fly.io | Render (Free) |
|---------|--------|---------------|
| Sleep after idle | **No** | Yes (15 min) |
| Cold start | **None** | ~30 sec |
| Global edge | **Yes** | No |
| Docker native | **Yes** | Yes |
| Free tier | **$5/mo credit** | $5/mo credit |
| Bandwidth | **160GB/mo** | 100GB/mo |

**For a mental health app, never sleeping is critical.**

---

## Prerequisites

```bash
# Install Fly.io CLI (flyctl)
curl -L https://fly.io/install.sh | sh

# Or on Ubuntu/Debian
sudo apt install flyctl

# Login
fly auth login
```

---

## Step 1: Create App

```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1

# Launch new app (creates fly.toml if not exists)
fly launch --name nyx-backend --region bom --dockerfile Dockerfile --no-deploy

# Or if fly.toml already exists:
# fly apps create nyx-backend
```

**Regions:** `bom` (Mumbai), `sin` (Singapore), `lhr` (London), `iad` (Virginia)

---

## Step 2: Set Secrets

```bash
# Required secrets
fly secrets set MONGO_URI="your-mongodb-atlas-connection-string"
fly secrets set GROQ_API_KEY="your-groq-api-key"
fly secrets set JWT_SECRET_KEY="$(openssl rand -base64 48)"

# Optional
fly secrets set LLM_PROVIDER="groq"
fly secrets set GROQ_MODEL="llama-3.3-70b-versatile"
fly secrets set CORS_ORIGINS="https://nyx-flutter.vercel.app"
fly secrets set UVICORN_WORKERS="1"
```

**Note:** Secrets are encrypted and only available to your app. Never commit them.

---

## Step 3: Deploy

```bash
# Deploy
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1
fly deploy

# Or with specific config
fly deploy --config fly.toml --dockerfile Dockerfile
```

**What happens:**
1. Fly builds Docker image from Dockerfile
2. Pushes to Fly's registry
3. Deploys to edge servers
4. Health check on `/health`
5. Traffic routed to healthy instances

---

## Step 4: Verify

```bash
# Check status
fly status

# View logs
fly logs

# Open app in browser
fly open

# Or curl
curl https://nyx-backend.fly.dev/health
```

---

## Step 5: Custom Domain (Optional)

```bash
# Add custom domain
fly certs add api.nyxapp.com

# Then add CNAME in your DNS:
# CNAME api.nyxapp.com → nyx-backend.fly.dev
```

---

## MongoDB Atlas + Fly.io

Fly.io apps have dynamic IPs. In MongoDB Atlas:
1. Network Access → Add IP Address
2. Allow `0.0.0.0/0` (for development)
3. **For production:** Use MongoDB Atlas Private Endpoint or VPC Peering

---

## Scaling

```bash
# Scale up (more memory)
fly scale memory 1024

# Scale out (more instances)
fly scale count 2

# Scale down
fly scale count 1
fly scale memory 512
```

---

## Monitoring

```bash
# Metrics dashboard
fly dashboard

# App metrics
fly metrics

# Instance status
fly status --all
```

---

## Updates

```bash
# After code changes, just redeploy
fly deploy

# Zero-downtime deploys are automatic
```

---

## Free Tier Limits

| Resource | Limit |
|----------|-------|
| RAM | 256MB per VM |
| CPU | Shared |
| Disk | 3GB |
| Bandwidth | 160GB/mo |
| Requests | Unlimited |
| **Cost** | **$0** (within $5 credit) |

**To stay free:** Use 1 VM, 256MB RAM, shared CPU.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `fly auth login` fails | Run `fly auth signup` first |
| Deploy fails | Check `fly logs` for build errors |
| MongoDB timeout | Add `0.0.0.0/0` to Atlas IP allowlist |
| Out of memory | Reduce `UVICORN_WORKERS` to 1, or scale memory |
| App crashes | Check `fly logs`, likely missing env var |

---

## Files Used by Fly.io

- `Dockerfile` — Multi-stage build
- `fly.toml` — App config (region, scaling, health checks)
- `backend/requirements.txt` — Python deps
- `backend/server_v2.py` — FastAPI app

---

## Quick Reference

```bash
fly auth login          # Login
fly launch              # Create new app
fly deploy              # Deploy
fly status              # Check status
fly logs                # View logs
fly open                # Open app URL
fly secrets set KEY=VAL # Set secret
fly scale count 2       # Scale instances
fly apps destroy        # Delete app
```

---

## Architecture with Fly.io

```
User → Vercel (Flutter Web) → Fly.io (Backend API) → MongoDB Atlas
         ↓                        ↓
    Static Hosting           FastAPI + Docker
    vercel.app               fly.dev
```

**Total cost: $0/month** (Fly.io free + Vercel free + MongoDB Atlas free)

---

**Ready to deploy?**
1. `fly auth login`
2. `fly launch --name nyx-backend --region bom`
3. `fly secrets set MONGO_URI=... GROQ_API_KEY=...`
4. `fly deploy`
5. Done! App live at `https://nyx-backend.fly.dev`
