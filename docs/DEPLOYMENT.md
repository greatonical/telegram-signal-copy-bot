# Deployment Setup Guide

This guide explains how to configure GitHub Actions to automatically deploy your Telegram bot to your VPS.

## Prerequisites

- GitHub repository (must be **PRIVATE** since we're tracking session files)
- VPS with Docker installed
- GitHub account with repository access

## Setup Instructions

### 1. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

| Secret Name | Value |
|------------|-------|
| `VPS_HOST` | `205.209.121.94` |
| `VPS_USERNAME` | `root` |
| `VPS_PORT` | `22` |
| `VPS_PASSWORD` | `iaDanx7WsHF0Cc` |
| `ENV_FILE` | Copy the entire contents of your `.env` file |

**For ENV_FILE secret:**
```
API_ID=28580459
API_HASH=b13303db8471291f05d2b50b12b05b3d
PHONE_NUMBER=+2349161651940
```

### 2. Install Docker on VPS

SSH into your VPS and install Docker:

```bash
ssh root@205.209.121.94

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify installation
docker --version
```

### 3. Install Git on VPS

```bash
# Install git if not already installed
apt-get update
apt-get install -y git

# Configure git (optional but recommended)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Set Up GitHub Access on VPS

For public repositories, no additional setup is needed. For private repositories, you need to set up authentication:

**Option A: Personal Access Token (Recommended)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. On VPS, clone using: `git clone https://YOUR_TOKEN@github.com/username/repo.git`

**Option B: SSH Key**
1. Generate SSH key on VPS: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add public key to GitHub → Settings → SSH and GPG keys
3. Clone using SSH: `git clone git@github.com:username/repo.git`

### 5. Push to GitHub

Commit and push all the deployment files:

```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

The GitHub Action will automatically trigger and deploy to your VPS!

## How It Works

1. **On Push to Main**: GitHub Actions workflow triggers
2. **SSH to VPS**: Connects to your VPS using stored secrets
3. **Clone/Update Code**: Pulls latest code from GitHub
4. **Deploy**: Runs `deploy.sh` which:
   - Creates `.env` file from GitHub secret
   - Stops old container
   - Builds new Docker image
   - Starts new container with volume mounts
5. **Verify**: Checks container status and displays logs

## Volume Mounts

The deployment uses Docker volumes to persist data:

- `sessions/` - Telegram session files (avoids re-authentication)
- `logs/` - Bot logs (preserved across deployments)

## Monitoring

### View Logs
```bash
ssh root@205.209.121.94
docker logs -f telegram-bot
```

### Check Container Status
```bash
docker ps | grep telegram-bot
```

### Restart Container
```bash
docker restart telegram-bot
```

### Manual Deployment
```bash
cd /root/telegram-signal-copy-bot
./deploy.sh
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs telegram-bot

# Check if .env file exists
ls -la /root/telegram-signal-copy-bot/.env

# Manually run container to see errors
docker run --rm -it telegram-bot:latest python bot.py
```

### Session Files Not Persisting
```bash
# Check volume mounts
docker inspect telegram-bot | grep -A 10 Mounts

# Verify files exist on host
ls -la /root/telegram-signal-copy-bot/sessions/
```

### GitHub Action Fails
1. Check GitHub Actions logs in repository
2. Verify all secrets are set correctly
3. Ensure VPS is accessible (SSH connection works)
4. Check VPS has enough disk space: `df -h`

## Security Notes

⚠️ **Important Security Considerations:**

1. **Keep Repository Private**: Session files contain authentication data
2. **Rotate Credentials**: Regularly change VPS password and GitHub tokens
3. **Enable 2FA**: On both GitHub and VPS if possible
4. **Monitor Access**: Check GitHub Actions logs regularly
5. **Firewall**: Consider restricting SSH access to specific IPs

## Auto-Restart

The container is configured with `--restart unless-stopped`, meaning:
- ✅ Restarts automatically if it crashes
- ✅ Starts automatically when VPS reboots
- ❌ Won't restart if manually stopped with `docker stop`

## Next Steps

After successful deployment:
1. Monitor the first deployment in GitHub Actions
2. SSH to VPS and verify bot is running
3. Check logs to ensure bot authenticated successfully
4. Test by sending a message to a monitored group
