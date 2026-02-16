# Quick Start Guide - CI/CD Deployment

## 🚀 Quick 5-Step Deployment

### 1️⃣ Setup VPS (One-time)
```bash
./setup-vps.sh
```
Password: `iaDanx7WsHF0Cc`

---

### 2️⃣ Configure GitHub Secrets (One-time)

Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

Add these 5 secrets:

```
VPS_HOST = 205.209.121.94
VPS_USERNAME = root
VPS_PORT = 22
VPS_PASSWORD = iaDanx7WsHF0Cc
ENV_FILE = (paste contents of .env file)
```

Run `./setup-secrets.sh` to see the exact values.

---

### 3️⃣ Make Repository Private ⚠️

**CRITICAL:** Settings → General → Danger Zone → Change visibility → Make private

---

### 4️⃣ Deploy
```bash
git add .
git commit -m "Add CI/CD deployment"
git push origin main
```

---

### 5️⃣ Verify

Watch deployment: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`

Check bot:
```bash
ssh root@205.209.121.94
docker logs -f telegram-bot
```

---

## 📁 Files Created

- ✅ `Dockerfile` - Docker image configuration
- ✅ `.dockerignore` - Build optimization
- ✅ `deploy.sh` - VPS deployment script
- ✅ `.github/workflows/deploy.yml` - GitHub Actions
- ✅ `setup-vps.sh` - VPS setup helper
- ✅ `setup-secrets.sh` - Secrets helper
- ✅ `DEPLOYMENT.md` - Full documentation

**Modified:**
- ✅ `.gitignore` - Now tracks sessions/logs/.env

---

## 🔄 How It Works

```
Push to GitHub → GitHub Actions → SSH to VPS → Deploy → Done!
```

**Auto-deploys on every push to main branch!**

---

## 🛠️ Common Commands

### View logs
```bash
ssh root@205.209.121.94 "docker logs -f telegram-bot"
```

### Restart bot
```bash
ssh root@205.209.121.94 "docker restart telegram-bot"
```

### Check status
```bash
ssh root@205.209.121.94 "docker ps | grep telegram-bot"
```

---

## 📚 Full Documentation

See [DEPLOYMENT.md](file:///Users/admin/Documents/Projects/BotsProjects/telegram-signal-copy-bot/DEPLOYMENT.md) for complete guide.
