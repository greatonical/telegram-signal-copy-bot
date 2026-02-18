# Fly.io Deployment Cheat Sheet

This guide documents the exact method we used to successfully deploy the Telegram bot, ensuring the session file works and preventing the "multiple IP" conflict.

## ✅ Prerequisites (Crucial)

1. **`fly.toml`**: Must have `min_machines_running = 1` and `strategy = "immediate"` to prevent running 2 machines.
2. **`.dockerignore`**: Must **NOT** contain `sessions/` (so the session file is uploaded).
3. **`sessions/user.session`**: A valid, authenticated session file must exist in your local project.

---

## 🚀 Standard Deployment

Use this command for normal code updates or configuration changes:

```bash
# Run from the project root directory
fly deploy -a telegram-signal-copy-bot
```

*This respects your local `fly.toml` and ensures only 1 machine is updated.*

---

## 🔄 How to Refresh/Update the Session

If the bot fails to login or the session expires, follow these steps to generate a new one and deploy it:

1. **Re-authenticate Locally:**
   ```bash
   # Run the bot locally to generate a fresh session
   python3 bot.py
   # Enter your phone number and OTP code when prompted
   # Once confirmed connected, press Ctrl+C to stop it
   ```

2. **Commit the New Session:**
   ```bash
   git add sessions/user.session
   git commit -m "Update Telegram session file"
   git push
   ```

3. **Deploy:**
   ```bash
   fly deploy -a telegram-signal-copy-bot
   ```

---

## 🛠 Troubleshooting

### "The authorization key was used under two different IP addresses"
This means Fly.io accidentally started a second machine. Telegram blocks the session if used from 2 IPs at once.

**Fix:**
1. List machines:
   ```bash
   fly machines list -a telegram-signal-copy-bot
   ```
2. Destroy the extra machine (keep the one with state "started" if possible, or destroy the oldest):
   ```bash
   fly machines destroy <MACHINE_ID> -a telegram-signal-copy-bot --force
   ```
3. If the session was revoked by Telegram, follow the **"Refresh/Update the Session"** steps above.

### "App not found" or "Authorization failed"
Ensure you are logged in to Fly CLI:
```bash
fly auth login
```
