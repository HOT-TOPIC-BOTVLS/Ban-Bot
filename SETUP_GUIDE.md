# Ban Bot Setup & Integration Guide

This guide explains how to set up the standalone Ban Bot and integrate it with your other bots (like Hot Topic Bot).

## 1. Ban Bot Setup
1. **Environment**: Ensure you have Python 3.8+ installed.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure**:
   - Open `config.py` and set your `BAN_BOT_TOKEN`.
   - Set `BAN_BOT_LOG_CHANNEL_ID` to the channel where you want alerts sent.
   - Adjust `BAN_BOT_PORT` if 8080 is occupied.
4. **Run**:
   ```bash
   python main.py
   ```

## 2. Standalone Features
- **Ban Logger**: Use `b!log <user> <action> <reason>` to manually log cases.
- **Ticket Context**: Automatically triggers on channels named `ticket-*`. It fetches the last 50 messages from the user, stops at 5-minute gaps, and posts a report + .txt transcript.
- **Verification Check**: When a member joins, the bot checks if their ID is in the ban database and alerts staff.
- **API**: The bot runs a web server that allows other bots to query ban data.

## 3. Integration with Hot Topic Bot
To make your Hot Topic Bot (or any other bot) compatible with the Ban Bot, you can use the provided `integration_example.py`.

### Example: Adding a check to Hot Topic Bot's Verification
In `verification.py` of your Hot Topic Bot, you can add this check before allowing a user to verify:

```python
from integration_example import BanBotClient

ban_client = BanBotClient(api_base_url="http://YOUR_BAN_BOT_IP:8080")

# Inside the verify_button logic:
history = await ban_client.check_user(user.id)
if history.get("is_banned"):
    await interaction.response.send_message("❌ Verification denied: You are in the ban database.", ephemeral=True)
    return
```

### Example: Logging bans from Hot Topic Bot
In `moderation.py` of your Hot Topic Bot, after a successful ban:

```python
await ban_client.log_action(
    user_id=user.id,
    username=str(user),
    mod_id=ctx.author.id,
    reason=situation,
    action="BAN"
)
```

## 4. Maintenance
- **Database**: All data is stored in `ban_bot.db` (SQLite).
- **Transcripts**: Generated transcripts are stored in the `transcripts/` folder.
- **Cleanup**: The bot automatically deletes records older than 365 days (configurable in `config.py`).
