import discord
from discord.ext import commands, tasks
import asyncio
import os
from aiohttp import web
from datetime import datetime, timedelta
import json
import logging

from config import BAN_BOT_TOKEN, BAN_BOT_PREFIX, BAN_BOT_DB_PATH, BAN_BOT_PORT, BAN_BOT_LOG_CHANNEL_ID, BAN_BOT_CLEANUP_DAYS
from database import BanBotDatabase
from context_fetcher import ContextFetcher

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('BanBot')

# Initialize Database
db = BanBotDatabase(BAN_BOT_DB_PATH)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=BAN_BOT_PREFIX, intents=intents)
fetcher = ContextFetcher(bot)

# --- HTTP Endpoint (Aiohttp) ---
async def handle_check_user(request):
    user_id_str = request.match_info.get('user_id')
    if not user_id_str or not user_id_str.isdigit():
        return web.json_response({"error": "Invalid user ID"}, status=400)
    
    user_id = int(user_id_str)
    bans = db.get_user_bans(user_id)
    alts = db.get_alts_for_user(user_id)
    
    return web.json_response({
        "user_id": user_id,
        "is_banned": len(bans) > 0,
        "ban_history": [dict(b) for b in bans],
        "possible_alts": [dict(a) for a in alts]
    })

async def handle_log_action(request):
    try:
        data = await request.json()
        required = ['user_id', 'username', 'mod_id', 'reason', 'action']
        if not all(k in data for k in required):
            return web.json_response({"error": "Missing required fields"}, status=400)
        
        case_id = db.log_ban(
            user_id=data['user_id'],
            username=data['username'],
            mod_id=data['mod_id'],
            reason=data['reason'],
            action=data['action'],
            transcript_path=data.get('transcript_path')
        )
        return web.json_response({"status": "success", "case_id": case_id})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

app = web.Application()
app.router.add_get('/check_user/{user_id}', handle_check_user)
app.router.add_post('/log_action', handle_log_action)
app.router.add_post('/ticket_opened', handle_ticket_opened)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', BAN_BOT_PORT)
    await site.start()
    logger.info(f"HTTP Server started on port {BAN_BOT_PORT}")

# --- Tasks ---
@tasks.loop(hours=24)
async def daily_cleanup():
    logger.info("Running daily database cleanup...")
    db.cleanup_old_records(BAN_BOT_CLEANUP_DAYS)

@tasks.loop(minutes=5)
async def keep_alive():
    logger.info("Keep-alive heartbeat.")

# --- Events ---
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    daily_cleanup.start()
    keep_alive.start()
    asyncio.create_task(start_web_server())

# --- API Extension for Remote Triggers ---

async def handle_ticket_opened(request):
    """
    Called by Hot Topic Bot when a ticket opens.
    Expects JSON: {guild_id, user_id, username, messages: [...]}
    """
    try:
        data = await request.json()
        user_id = data['user_id']
        username = data['username']
        messages = data['messages']
        
        if messages:
            # Create a mock user object for transcript generator
            class MockUser:
                def __init__(self, name, id):
                    self.name = name
                    self.id = id
                def __str__(self): return self.name

            filepath, filename = fetcher.generate_transcript(messages, MockUser(username, user_id))
            
            # Get history
            history = db.get_all_cases(user_id)
            history_bullets = "\n".join([f"• {h['action']} - {h['reason']}" for h in history[:3]]) if history else "None"
            
            with open(filepath, 'r') as f:
                content = f.read()

            # Log the case in the Ban Server database
            db.log_ban(
                user_id=user_id,
                username=username,
                mod_id=0, # System triggered
                reason="Ticket Context Fetch",
                action="CONTEXT",
                transcript_path=filepath
            )
            
            return web.json_response({
                "status": "success",
                "transcript_filename": filename,
                "transcript_content": content,
                "history_bullets": history_bullets,
                "message_count": len(messages)
            })
        return web.json_response({"status": "no_context"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# --- Commands ---
@bot.command(name="log")
@commands.has_permissions(ban_members=True)
async def log_manual(ctx, user: discord.User, action: str, *, reason: str):
    """Feature 1: Ban Logger (Manual Entry)."""
    case_id = db.log_ban(user.id, str(user), ctx.author.id, reason, action.upper())
    await ctx.send(f"✅ Case #{case_id} logged: {action.upper()} for {user}.")

@bot.command(name="check")
@commands.has_permissions(kick_members=True)
async def check_user(ctx, user: discord.User):
    """Check a user's history in the Ban Bot database."""
    cases = db.get_all_cases(user.id)
    if not cases:
        await ctx.send(f"No history found for {user}.")
        return
    
    embed = discord.Embed(title=f"History for {user}", color=discord.Color.blue())
    for case in cases[:5]: # Show last 5 cases
        embed.add_field(
            name=f"Case #{case['case_id']} - {case['action']}",
            value=f"Reason: {case['reason']}\nDate: {case['timestamp']}",
            inline=False
        )
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if BAN_BOT_TOKEN and BAN_BOT_TOKEN != "YOUR_TOKEN_HERE":
        bot.run(BAN_BOT_TOKEN)
    else:
        logger.warning("No token provided. Bot will not start.")
