import os

BAN_BOT_TOKEN = os.getenv("BAN_BOT_TOKEN")
BAN_BOT_PREFIX = os.getenv("BAN_BOT_PREFIX", "b!")
BAN_BOT_DB_PATH = os.getenv("BAN_BOT_DB_PATH", "ban_bot.db")
BAN_BOT_PORT = int(os.getenv("BAN_BOT_PORT", 8080))
BAN_BOT_LOG_CHANNEL_ID = int(os.getenv("BAN_BOT_LOG_CHANNEL_ID", 0)) # Channel to send ban logs
BAN_BOT_CLEANUP_DAYS = int(os.getenv("BAN_BOT_CLEANUP_DAYS", 365)) # Days after which to clean old records
