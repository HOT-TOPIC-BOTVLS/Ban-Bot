import aiohttp
import asyncio
import json

class BanBotClient:
    def __init__(self, api_base_url="http://localhost:8080"):
        self.api_base_url = api_base_url

    async def check_user(self, user_id: int):
        """Check if a user is banned in the Ban Bot database."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.api_base_url}/check_user/{user_id}") as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {"error": f"API returned status {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

    async def log_action(self, user_id: int, username: str, mod_id: int, reason: str, action: str, transcript_path: str = None):
        """Send a moderation action to the Ban Bot to be logged."""
        payload = {
            "user_id": user_id,
            "username": username,
            "mod_id": mod_id,
            "reason": reason,
            "action": action,
            "transcript_path": transcript_path
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.api_base_url}/log_action", json=payload) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {"error": f"API returned status {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

# Example usage for Hot Topic Bot or others:
# client = BanBotClient()
# result = await client.check_user(123456789)
# if result.get("is_banned"):
#     print("User is banned!")
