"""
bots/guard/main.py — ยาม
"""
import sys
import os
# root project (เพื่อ import shared/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# bot directory (เพื่อ import config และ cogs/)
sys.path.insert(0, os.path.dirname(__file__))

import discord
from discord.ext import commands
from shared.config import get_token
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True


class Guard(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        for cog in ["cogs.patrol", "cogs.kick"]:
            try:
                await self.load_extension(cog)
                print(f"  ✅ {cog}")
            except Exception as e:
                print(f"  ❌ {cog}: {e}")
        await self.tree.sync()

    async def on_ready(self):
        print(f"🛡️ ยาม [{self.user}] พร้อมแล้ว!")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="🛡️ กำลังลาดตระเวน"
        ))
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"  🔄 Sync {len(synced)} commands → {guild.name}")
            except Exception as e:
                print(f"  ⚠️ Sync ไม่สำเร็จ: {e}")


async def main():
    bot = Guard()
    async with bot:
        await bot.start(get_token("guard"))

if __name__ == "__main__":
    asyncio.run(main())