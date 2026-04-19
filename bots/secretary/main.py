"""
bots/secretary/main.py — เลขา (Bot หลัก)
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


class Secretary(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        cogs = ["cogs.roles", "cogs.points", "cogs.reward", "cogs.ai"]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"  ✅ {cog}")
            except Exception as e:
                print(f"  ❌ {cog}: {e}")
        # sync global (อาจใช้เวลา ~1 ชม.)
        synced = await self.tree.sync()
        print(f"  🔄 Sync {len(synced)} slash commands (global)")

    async def on_ready(self):
        print(f"📋 เลขา [{self.user}] พร้อมแล้ว!")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="📋 พร้อมรับใช้"
        ))
        # sync กับทุก guild ทันที (instant)
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"  🔄 Sync {len(synced)} commands → {guild.name}")
            except Exception as e:
                print(f"  ⚠️ Sync ไม่สำเร็จ {guild.name}: {e}")

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        self.tree.copy_global_to(guild=ctx.guild)
        synced = await self.tree.sync(guild=ctx.guild)
        await ctx.send(f"🔄 Sync {len(synced)} slash commands แล้ว")


async def main():
    bot = Secretary()
    async with bot:
        await bot.start(get_token("secretary"))

if __name__ == "__main__":
    asyncio.run(main())