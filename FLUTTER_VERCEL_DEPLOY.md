# NYX — Flutter Web + Backend Deployment Guide

## Architecture

| Service | Platform | Type | URL |
|---------|----------|------|-----|
| **Flutter Web** | Vercel | Static web app | `https://nyx-flutter.vercel.app` |
| **Backend API** | Render | FastAPI server | `https://nyx-backend.onrender.com` |
| **Database** | MongoDB Atlas | Cloud DB | `mongodb+srv://...` |

---

## Step 1: Deploy Backend to Render

Already configured! See `RENDER_DEPLOY.md` for details.

**After deploy, note your backend URL:**
```
https://nyx-backend.onrender.com
```

---

## Step 2: Build Flutter for Web

### Prerequisites
```bash
# Make sure Flutter is installed and web support is enabled
flutter doctor
flutter config --enable-web
```

### Configure the API URL

`frontend_flutter/lib/services/api_service.dart` now supports two modes:

- Same-origin hosting: if the Flutter web app is served by the same Render service as the API, no extra change is needed.
- Separate frontend hosting: pass your Render backend URL at build time with `--dart-define`.

### Build
```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend_flutter

# Get dependencies
flutter pub get

# Build for web against a separate Render backend
flutter build web --release --dart-define=NYX_API_BASE_URL=https://your-backend.onrender.com
```

This creates `frontend_flutter/build/web/` with all static files.

---

## Step 3: Deploy Flutter Web to Vercel

### Option A: Vercel CLI
```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend_flutter/build/web

# Install Vercel CLI if needed
npm install -g vercel

# Login (first time only)
vercel login

# Deploy
vercel --prod
```

### Option B: GitHub Integration (Recommended)

1. Create a new repo for just the Flutter web build:
```bash
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend_flutter/build/web
git init
git add .
git commit -m "Flutter web build"
git remote add origin https://github.com/YOUR_USERNAME/nyx-flutter-web.git
git push -u origin main
```

2. Go to https://vercel.com/new
3. Import `nyx-flutter-web` repo
4. Framework: **Other** (static)
5. Deploy

### Option C: Vercel Config in Main Repo

Create `frontend_flutter/vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "build/web/**",
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

Then use GitHub Actions to auto-build and deploy (see below).

---

## Step 4: CORS Configuration

In your Render backend `.env`:
```
CORS_ORIGINS=https://nyx-flutter.vercel.app,https://nyx-flutter-git-main-roar-k5.vercel.app
```

Or allow all for development:
```
CORS_ORIGINS=*
```

---

## Auto-Deploy with GitHub Actions

Create `.github/workflows/deploy-flutter.yml` in your main repo:

```yaml
name: Deploy Flutter Web

on:
  push:
    branches: [main]
    paths:
      - 'frontend_flutter/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.0'
          channel: 'stable'
      
      - name: Get dependencies
        working-directory: frontend_flutter
        run: flutter pub get
      
      - name: Build web
        working-directory: frontend_flutter
        run: flutter build web --release
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: frontend_flutter/build/web
```

**Required secrets in GitHub:**
- `VERCEL_TOKEN` — from https://vercel.com/account/tokens
- `VERCEL_ORG_ID` — from project settings
- `VERCEL_PROJECT_ID` — from project settings

---

## Vercel Configuration Files

### `frontend_flutter/vercel.json`
Already created — tells Vercel to serve `build/web` as static.

### `frontend_flutter/.vercelignore`
```
.dart_tool/
build/
*.iml
.idea/
.vscode/
android/
ios/
linux/
macos/
windows/
test/
```

---

## Local Development

```bash
# Terminal 1: Backend
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/backend
.venv/bin/python -m uvicorn server_v2:app --reload

# Terminal 2: Flutter
cd /mnt/c/Users/rudra/Desktop/project/hermes/nyx1/frontend_flutter
flutter run -d chrome
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS errors | Update `CORS_ORIGINS` in backend `.env` |
| API calls failing | Rebuild with `--dart-define=NYX_API_BASE_URL=https://your-backend.onrender.com` |
| Build fails | Run `flutter clean` then `flutter pub get` |
| Vercel 404 | Make sure `vercel.json` has catch-all route |
| Images not loading | Use `Image.network()` with full URLs |

---

## Summary

| Step | Command |
|------|---------|
| Build Flutter Web | `flutter build web --release` |
| Deploy to Vercel | `cd build/web && vercel --prod` |
| Deploy Backend | Follow `RENDER_DEPLOY.md` |
| Update API URL | Build with `--dart-define=NYX_API_BASE_URL=...` |
| Configure CORS | Edit backend `.env` |

**Total cost: $0/month** (Vercel free + Render free + MongoDB Atlas free)

---

## Files Created

- `frontend_flutter/vercel.json` — Vercel static hosting config
- `FLUTTER_VERCEL_DEPLOY.md` — This guide

**Ready to deploy?**
1. Build with `flutter build web --release --dart-define=NYX_API_BASE_URL=https://your-backend.onrender.com`
2. `cd build/web && vercel --prod`
3. Done!
