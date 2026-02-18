# Easy Deployment Guide

This guide covers deploying your Telegram bot to platforms that auto-detect Dockerfiles.

## 🚀 Supported Platforms

All these platforms will automatically detect your `Dockerfile` and deploy:

- **Fly.io** (Recommended - generous free tier)
- **Railway** (Simple, $5/month)
- **Render** (Free tier available)
- **DigitalOcean App Platform** ($5/month)
- **Google Cloud Run** (Pay per use)
- **Azure Container Apps** (Pay per use)

---

## 🎯 Fly.io Deployment (Recommended)

### Why Fly.io?
- ✅ Generous free tier (3 shared VMs)
- ✅ Persistent volumes for session files
- ✅ Global deployment
- ✅ Perfect for background bots

### Prerequisites
1. [Install Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Create account: `fly auth signup` or `fly auth login`

### Deployment Steps

#### 1. Initialize Fly App
```bash
cd /path/to/telegram-signal-copy-bot
fly launch --no-deploy
```

When prompted:
- **App name**: Press Enter (use generated name) or choose your own
- **Region**: Choose closest to you (e.g., `iad` for US East, `lhr` for London)
- **PostgreSQL**: No
- **Redis**: No

#### 2. Create Persistent Volumes
```bash
# Volume for session files (prevents re-authentication)
fly volumes create telegram_sessions --size 1

# Volume for logs
fly volumes create telegram_logs --size 1
```

#### 3. Set Environment Variables
```bash
# Set your Telegram API credentials
fly secrets set API_ID=your_api_id
fly secrets set API_HASH=your_api_hash
fly secrets set PHONE_NUMBER=your_phone_number
```

**Get your credentials from**: https://my.telegram.org/apps

> [!NOTE]
> Session files are already included in your Git repository, so the bot will use your existing authenticated session automatically. No additional authentication needed!

#### 4. Deploy!
```bash
fly deploy
```

#### 5. Monitor Your Bot
```bash
# View logs
fly logs

# Check status
fly status

# SSH into container
fly ssh console
```

### Auto-Deploy on Git Push

Fly.io has **built-in GitHub integration** (just like Render)! No GitHub Actions needed.

#### Option A: Built-in GitHub Integration (Recommended)

```bash
# Link your GitHub repo to auto-deploy
fly apps create your-app-name
fly deploy

# Then in Fly.io dashboard:
# 1. Go to your app → Settings → GitHub
# 2. Connect your repository
# 3. Enable auto-deploy on push to main
```

Now every push to `main` automatically deploys! ✨

#### Option B: GitHub Actions (Alternative)

If you prefer GitHub Actions or need more control:

```bash
# Get a deploy token
fly tokens create deploy -x 999999h

# Add to GitHub Secrets:
# GitHub repo → Settings → Secrets → Actions
# Secret name: FLY_API_TOKEN
```

The `.github/workflows/fly-deploy.yml` file is already created for you!

---

## 🚂 Railway Deployment

### Prerequisites
1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI (optional): `npm i -g @railway/cli`

### Deployment Steps

#### Option A: Via Dashboard (Easiest)
1. Go to [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Dockerfile ✨
5. Add environment variables:
   - `API_ID`
   - `API_HASH`
   - `PHONE_NUMBER`
6. Click "Deploy"

#### Option B: Via CLI
```bash
# Login
railway login

# Initialize
railway init

# Add environment variables
railway variables set API_ID=your_api_id
railway variables set API_HASH=your_api_hash
railway variables set PHONE_NUMBER=your_phone_number

# Deploy
railway up
```

### Persistent Storage
Railway automatically persists volumes defined in your Dockerfile.

---

## 🎨 Render Deployment

### Prerequisites
1. Create account at [render.com](https://render.com)

### Deployment Steps

1. Click "New +" → "Background Worker"
2. Connect your GitHub repository
3. Configure:
   - **Name**: telegram-signal-copy-bot
   - **Environment**: Docker
   - **Docker Command**: (leave empty, uses Dockerfile CMD)
4. Add environment variables:
   - `API_ID`
   - `API_HASH`
   - `PHONE_NUMBER`
5. Add persistent disk:
   - **Mount Path**: `/app/sessions`
   - **Size**: 1GB
6. Click "Create Background Worker"

Render auto-deploys on every git push! 🎉

---

## 🌊 DigitalOcean App Platform

### Prerequisites
1. Create account at [digitalocean.com](https://digitalocean.com)

### Deployment Steps

1. Go to Apps → "Create App"
2. Select GitHub repository
3. Configure:
   - **Resource Type**: Worker
   - **Dockerfile Path**: `Dockerfile`
4. Add environment variables
5. Add volume:
   - **Mount Path**: `/app/sessions`
   - **Size**: 1GB
6. Click "Create Resources"

---

## 📋 Environment Variables

All platforms need these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API Hash | `abcdef1234567890` |
| `PHONE_NUMBER` | Your phone number | `+1234567890` |

**Get credentials**: https://my.telegram.org/apps

---

## 🔍 Troubleshooting

### Bot keeps asking for authentication code
**Problem**: Session files not persisting

**Solution**: Ensure persistent volumes are mounted to `/app/sessions`

### Bot crashes on startup
**Problem**: Missing environment variables

**Solution**: 
```bash
# Check environment variables are set
fly ssh console -C "env | grep API"  # Fly.io
railway variables                     # Railway
```

### "Unable to open database file" error
**Problem**: Session directory not writable

**Solution**: Dockerfile already creates the directory with correct permissions

---

## 🎯 Comparison Table

| Platform | Free Tier | Monthly Cost | Setup Time | Auto-Deploy | Method |
|----------|-----------|--------------|------------|-------------|--------|
| **Fly.io** | ✅ 3 VMs | Free-$5 | 5 min | ✅ | Built-in GitHub integration |
| **Railway** | ❌ | $5+ | 2 min | ✅ | Built-in GitHub integration |
| **Render** | ✅ Limited | Free-$7 | 3 min | ✅ | Built-in GitHub integration |
| **DigitalOcean** | ❌ | $5+ | 5 min | ✅ | Built-in GitHub integration |

**All platforms auto-deploy on git push** - no GitHub Actions required! 🎉

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use secrets management** - All platforms support encrypted secrets
3. **Keep repository private** - Session files contain auth data
4. **Rotate credentials** - Periodically regenerate API tokens
5. **Monitor logs** - Watch for unauthorized access attempts

---

## 📚 Next Steps

After deployment:
1. Monitor first deployment logs
2. Verify bot authenticated successfully
3. Test message forwarding
4. Set up monitoring/alerts (optional)

---

## 🆘 Getting Help

- **Fly.io**: https://fly.io/docs
- **Railway**: https://docs.railway.app
- **Render**: https://render.com/docs
- **Telegram API**: https://core.telegram.org/api
