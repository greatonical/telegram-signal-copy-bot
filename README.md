# Telegram Signal Reader & Forwarder

A Python-based Telegram userbot that monitors signal groups/channels and automatically forwards messages to target groups. Built using Telethon for MTProto client implementation.

## ⚠️ Important Warnings

- **TOS Risk**: Userbots violate Telegram's Terms of Service. Use a secondary/throwaway account only.
- **Rate Limits**: Telegram restricts automated actions. The bot includes safeguards but bans are possible.
- **Security**: Session files = full account access. Protect them like passwords.
- **Testing**: Use a new account with a cheap SIM, let it age for 5-7 days before automating.

## Features (Phase 1 MVP)

- ✅ User authentication with phone number + OTP
- ✅ Monitor specific group/channel for new messages
- ✅ Auto-forward text messages to target group
- ✅ Rate limiting (configurable delay between forwards)
- ✅ Comprehensive error handling (FloodWait, disconnects, 2FA)
- ✅ Structured logging to file and console
- ✅ Graceful shutdown (Ctrl+C)

## Prerequisites

### 1. Get Telegram API Credentials

**Important**: These are NOT from BotFather. This is different.

1. Go to: https://my.telegram.org
2. Login with your phone number
3. Navigate to "API Development Tools"
4. Create a new application
5. Save your `API_ID` (integer) and `API_HASH` (string)

### 2. Prepare Test Account

⚠️ **Critical**: Don't use your main Telegram account!

- Get a cheap SIM card or virtual number
- Create new Telegram account
- Use it normally for 5-7 days (send messages, join groups)
- Then use it for automation

This "aging" reduces ban risk.

### 3. Get Group/Channel IDs

You need numeric IDs for:

- **Source group** (where signals come from)
- **Target group** (where you forward to)

**Easy method** (recommended):

```bash
# After authentication, run the helper script
python list_groups.py
```

This will list ALL groups and channels you're in with their IDs. Just copy the IDs you need!

**Alternative methods**:

- Use a Telegram bot like `@userinfobot`
- Or run the bot once and check logs (Telethon shows IDs)

Format: `-1001234567890` (negative for groups/channels)

## Installation

### 1. Clone/Download Project

```bash
cd /Users/admin/Documents/Projects/BotsProjects/telegram-signal-copy-bot
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Fill in your credentials:

```env
API_ID=12345678
API_HASH=your_actual_api_hash_here
PHONE_NUMBER=+1234567890
```

### 5. Configure Group IDs

Edit `config.py` and replace the placeholder group IDs:

```python
SOURCE_GROUP_ID = -1001234567890  # Your source group ID
TARGET_GROUP_ID = -1009876543210  # Your target group ID
```

## First Run

### Step 1: Authenticate

```bash
python main.py
```

**What happens**:

1. Asks for phone number (or uses from `.env`)
2. Telegram sends OTP code to your phone
3. Enter code in terminal
4. If 2FA enabled, enter password
5. Session file created in `sessions/user.session`

⚠️ The bot will fail to start because group IDs are placeholders. That's OK! Continue to Step 2.

### Step 2: Find Your Group IDs

```bash
python list_groups.py
```

This shows all groups/channels you're in with their IDs. Copy the IDs you need and update `config.py`:

```python
SOURCE_GROUP_ID = -1001234567890  # Replace with actual ID
TARGET_GROUP_ID = -1009876543210  # Replace with actual ID
```

### Step 3: Run the Bot

```bash
python main.py
```

Now it will start monitoring and forwarding! **Subsequent runs**: No OTP needed, uses saved session.

## Testing

1. **Local test first**: Run on your laptop before deploying to server
2. **Test groups**: Use private test groups before production
3. **Send test message**: Send a message to source group
4. **Verify forward**: Check target group receives the message
5. **Check logs**: Review `logs/bot.log` for any errors

## Deployment

### 🚀 Easy Deployment (Recommended)

Deploy to cloud platforms with automatic Git-based deployment:

**See [EASY_DEPLOY.md](EASY_DEPLOY.md) for detailed guides on:**
- **Fly.io** (Free tier, recommended)
- **Railway** ($5/month, simplest)
- **Render** (Free tier available)
- **DigitalOcean App Platform**

All platforms auto-detect your Dockerfile and deploy in minutes! ✨

### 🖥️ VPS Deployment (Advanced)

For manual VPS deployment with GitHub Actions:

**See [DEPLOYMENT.md](DEPLOYMENT.md)** for setting up automated deployment to your own VPS.

### 🏃 Quick Local Testing

```bash
# Screen/Tmux (Quick)
screen -S telegram-bot
python bot.py
# Press Ctrl+A+D to detach
```

Reattach later: `screen -r telegram-bot`


## Configuration Options

Edit `config.py` to customize behavior:

| Setting           | Description                      | Default        |
| ----------------- | -------------------------------- | -------------- |
| `FORWARD_DELAY`   | Seconds to wait between forwards | 2              |
| `LOG_LEVEL`       | Logging verbosity                | INFO           |
| `SOURCE_GROUP_ID` | Group to monitor                 | (set manually) |
| `TARGET_GROUP_ID` | Group to forward to              | (set manually) |

## Troubleshooting

### Bot won't start

- Check `.env` file exists and has correct values
- Verify Python version is 3.11+
- Check logs in `logs/bot.log`

### Not receiving messages

- Verify you're a member of source group
- Check group ID is correct (should be negative)
- Ensure group allows member messages
- Check bot is connected (see logs)

### Messages not forwarding

- Verify target group ID correct
- Check you have send permissions in target
- Look for FloodWait errors in logs
- Ensure rate limiting delay is set

### Session expired

```bash
rm sessions/user.session
python main.py  # Re-authenticate
```

### High CPU/memory

- Telethon is generally lightweight
- Check for errors in logs
- Monitor with `htop` or Activity Monitor

## Security Best Practices

1. **Never commit**:
   - `.env` file (credentials)
   - `.session` files (account access)
   - `logs/` directory (may contain sensitive info)

2. **File permissions** (Linux/Mac):

   ```bash
   chmod 600 .env
   chmod 600 sessions/user.session
   ```

3. **Account safety**:
   - Use secondary account only
   - Don't join many groups quickly (max 3-5/day)
   - Space out actions (2-3 second delays)
   - Monitor for Telegram warnings

## Project Structure

```
telegram-signal-copy-bot/
├── bot.py                  # Main bot script
├── list_groups.py          # Helper: List all your groups with IDs
├── get_forum_topics.py     # Helper: List forum topics
├── config.py               # Configuration settings
├── .env                    # API credentials (create from .env.example)
├── .env.example            # Template for credentials
├── .gitignore              # Git exclusions
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── fly.toml                # Fly.io configuration
├── README.md               # This file
├── EASY_DEPLOY.md          # Easy deployment guide (Fly.io, Railway, etc.)
├── DEPLOYMENT.md           # VPS deployment guide
├── .github/workflows/      # GitHub Actions
│   ├── deploy.yml          # VPS deployment workflow
│   └── fly-deploy.yml      # Fly.io deployment workflow
├── logs/                   # Log files directory
│   └── bot.log             # Application logs
└── sessions/               # Telegram session files
    └── user.session        # Auto-generated by Telethon
```

## Future Enhancements

Phase 1 is a simple relay system. Future versions may include:

- **Signal parsing**: Extract trade data (pair, entry, SL, TP)
- **Database**: Store message history and analytics
- **Multi-group**: Monitor multiple signal sources
- **Edit detection**: Update forwarded messages when original is edited
- **Media support**: Forward images and files
- **Filtering**: Only forward specific signal types
- **Auto-trading**: Integration with exchange APIs

## Resources

- **Telethon Docs**: https://docs.telethon.dev/
- **Telegram API**: https://core.telegram.org/api
- **Get API credentials**: https://my.telegram.org

## License

This project is for educational purposes only. Use responsibly and at your own risk.

---

**Need help?** Check the troubleshooting section or review the logs in `logs/bot.log`.
