import discord
from datetime import datetime, timedelta
import os
import aiohttp
import logging

logger = logging.getLogger('BanBot.ContextFetcher')

class ContextFetcher:
    def __init__(self, bot, hot_topic_api_url="http://localhost:8080"):
        self.bot = bot
        self.hot_topic_api_url = hot_topic_api_url

    async def fetch_context(self, user, guild, limit=50, silence_gap_minutes=5):
        """
        Feature 2: Request message context from Hot Topic Bot API.
        """
        url = f"{self.hot_topic_api_url}/api/fetch_context/{guild.id}/{user.id}?limit={limit}&gap={silence_gap_minutes}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("messages", [])
                    else:
                        logger.error(f"Hot Topic API returned status {resp.status}")
                        return []
            except Exception as e:
                logger.error(f"Error calling Hot Topic API: {e}")
                return []

    def generate_transcript(self, messages, user):
        """
        Feature 3: Generate a .txt transcript.
        """
        filename = f"transcript_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join("transcripts", filename)
        
        os.makedirs("transcripts", exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Transcript for User: {user} ({user.id})\n")
            f.write(f"Generated at: {datetime.now()}\n")
            f.write("-" * 50 + "\n\n")
            
            for msg in messages:
                # msg is a dict from API
                ts_iso = msg.get('timestamp')
                ts_formatted = datetime.fromisoformat(ts_iso).strftime('%Y-%m-%d %H:%M:%S') if ts_iso else "N/A"
                author = msg.get('author', 'Unknown')
                content = msg.get('content', '')
                f.write(f"[{ts_formatted}] {author}: {content}\n")
                
                attachments = msg.get('attachments', [])
                if attachments:
                    for att_url in attachments:
                        f.write(f"  [Attachment: {att_url}]\n")
        
        return filepath, filename
