# Render.com Deployment

This project is configured to deploy to [Render](https://render.com/).

## Quick Deploy

1. **Push your code to GitHub** (if not already done)

2. **Sign up/Login to Render**: https://render.com

3. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `telegram-signal-copy-bot` repository

4. **Configure the service**:
   - **Name**: `telegram-signal-copy-bot` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Plan**: Free (or your preferred plan)

5. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable" and add:
   - `API_ID` - Your Telegram API ID
   - `API_HASH` - Your Telegram API Hash
   - `PHONE_NUMBER` - Your phone number
   - `PORT` - 8080 (Render will provide this automatically)

6. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait for the build to complete

## Post-Deployment

### First Run - Phone Verification
The first time you deploy, you'll need to verify your phone number:

1. Check the logs in Render dashboard
2. Look for the verification code prompt
3. You may need to SSH into the container or redeploy after creating a session file locally

**Recommended approach**: Run the bot locally first to create the session file, then upload it.

### Health Check Endpoint

Your service will have a health check endpoint at:
```
https://your-app-name.onrender.com/health
```

### Setting up Cronjob

To keep your service alive (Render free tier sleeps after 15 min of inactivity), set up a cronjob:

**Using cron-job.org** (easiest):
1. Go to https://cron-job.org
2. Create a free account
3. Create a new cronjob:
   - Title: "Telegram Bot Health Check"
   - URL: `https://your-app-name.onrender.com/health`
   - Schedule: Every 10 minutes

**Using your own server**:
```bash
# Add to crontab (crontab -e)
*/10 * * * * curl https://your-app-name.onrender.com/health
```

## Available Endpoints

- `/` - API information
- `/health` - Health check (returns JSON with status and timestamp)
- `/ping` - Simple ping endpoint (returns "pong")

## Logs

View logs in the Render dashboard:
- Go to your service
- Click "Logs" tab
- See real-time bot and API activity

## Updating

Render automatically deploys when you push to your GitHub repository:
```bash
git add .
git commit -m "Update bot"
git push
```

## Troubleshooting

### Bot not starting
- Check environment variables are set correctly
- View logs for error messages
- Ensure session file is present (or remove to re-authenticate)

### Health check failing
- Verify PORT environment variable is set to 8080
- Check if the API server started (look for "Starting API server" in logs)
- Ensure Dockerfile builds successfully

### Service keeps sleeping
- Set up a cronjob to ping the `/health` endpoint every 10 minutes
- Consider upgrading to a paid Render plan for always-on service
