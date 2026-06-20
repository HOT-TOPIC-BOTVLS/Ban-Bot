# Ban Bot

A standalone Discord moderation bot focused on logging, context retrieval, and alt detection.

## Features
1. **Ban Logger**: Stores user ID, mod, reason, timestamp, and case ID.
2. **Ticket Trigger**: Automatically fetches message context when a ticket opens.
3. **Context Pull**: Retrieves last 50 messages, stopping at a 5-minute silence gap.
4. **Report Output**: Generates rich embeds and .txt transcripts.
5. **Database**: SQLite storage for cases, transcripts, and user IDs.
6. **HTTP Endpoint**: `/check_user/{id}` for external verification bots.
7. **Verification Check**: Alerts on member join if they are in the ban database.
8. **Cronjobs**: Automated daily cleanup and keep-alive pings.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install discord.py aiohttp`.
3. Set environment variables in `config.py` or your host environment:
   - `BAN_BOT_TOKEN`: Your Discord bot token.
   - `BAN_BOT_LOG_CHANNEL_ID`: Channel ID for alerts.
4. Run the bot: `python main.py`.

## API Usage
- **Check User**: `GET http://localhost:8080/check_user/{user_id}`
- **Log Action**: `POST http://localhost:8080/log_action` (JSON body with `user_id`, `username`, `mod_id`, `reason`, `action`).
