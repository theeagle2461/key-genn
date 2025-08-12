# 🔑 Discord Key Management Bot

A comprehensive Discord bot for generating, managing, and validating keys with machine ID locking and role management.

## ✨ Features

- **Key Generation**: Create unique keys for users with customizable duration
- **Machine ID Locking**: Keys are locked to specific machines (MAC address)
- **Role Management**: Automatically assign roles when keys are activated
- **Channel Locking**: Restrict keys to specific Discord channels
- **Key Revocation**: Revoke keys at any time
- **Usage Tracking**: Monitor key usage and activation history
- **Backup System**: Create and restore key backups
- **24/7 Hosting**: Designed for free hosting platforms

## 🚀 Quick Start

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token
5. Enable these intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent

### 2. Invite Bot to Server

Use this URL (replace YOUR_BOT_ID):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot
```

### 3. Setup Files

1. Rename `env_example.txt` to `.env`
2. Add your bot token to `.env`:
   ```
   BOT_TOKEN=your_actual_bot_token_here
   ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Bot

```bash
python bot.py
```

## 📋 Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!help` | Show help information | `!help` |
| `!generate` | Generate a new key | `!generate @user [channel_id] [days]` |
| `!revoke` | Revoke a key | `!revoke [key]` |
| `!keys` | Show user's keys | `!keys [@user]` |
| `!info` | Get key details | `!info [key]` |
| `!backup` | Create backup | `!backup` |
| `!restore` | Restore from backup | `!restore [file]` |
| `!status` | Show bot stats | `!status` |

## 🌐 Free Hosting Options

### Option 1: Railway (Recommended)
1. Go to [Railway](https://railway.app/)
2. Sign up with GitHub
3. Create new project
4. Connect your GitHub repository
5. Add environment variables
6. Deploy

### Option 2: Render
1. Go to [Render](https://render.com/)
2. Sign up and create account
3. Create new Web Service
4. Connect your GitHub repository
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `python bot.py`
7. Add environment variables

### Option 3: Heroku (Free tier discontinued)
- Note: Heroku no longer offers free hosting

## 🔧 Configuration

### Environment Variables
- `BOT_TOKEN`: Your Discord bot token

### Server Configuration
- `GUILD_ID`: Your Discord server ID
- `ROLE_ID`: Role ID to assign when keys are activated
- `ADMIN_ROLE_ID`: Role ID required to use bot commands

### Key Settings
- `DEFAULT_KEY_DURATION`: Default key validity (30 days)
- `MAX_KEY_DURATION`: Maximum key validity (365 days)
- `MIN_KEY_DURATION`: Minimum key validity (1 day)

## 📁 File Structure

```
├── bot.py              # Main bot file
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── env_example.txt    # Environment variables template
├── README.md          # This file
├── keys.json          # Key storage (auto-generated)
├── key_usage.json     # Usage tracking (auto-generated)
└── keys_backup.json   # Backup files (auto-generated)
```

## 🔐 Security Features

- **Machine ID Locking**: Keys are tied to specific MAC addresses
- **Role-Based Access**: Only users with specific roles can use commands
- **Key Expiration**: Automatic key expiration after set duration
- **Usage Tracking**: Monitor and log all key activations
- **Backup Protection**: Secure backup and restore functionality

## 🚨 Important Notes

1. **Never share your bot token** - Keep it in `.env` file
2. **Backup regularly** - Use `!backup` command frequently
3. **Monitor usage** - Check `!status` regularly
4. **Secure your server** - Only give admin role to trusted users

## 🆘 Troubleshooting

### Bot not responding
- Check if bot is online in Discord
- Verify bot has correct permissions
- Check console for error messages

### Commands not working
- Ensure user has required role
- Check bot permissions in server
- Verify command syntax

### Keys not working
- Check if key is expired
- Verify machine ID matches
- Ensure key hasn't been revoked

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Discord bot permissions
3. Verify configuration settings
4. Check console logs for errors

## 🔄 Updates

To update the bot:
1. Pull latest changes from repository
2. Restart the bot process
3. Check for any new configuration options

---

**Made with ❤️ for secure Discord key management**
