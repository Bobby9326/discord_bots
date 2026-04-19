"""
bots/guard/cogs/patrol.py — ยาม: ลาดตระเวนวนไปเรื่อยๆ 24 ชั่วโมง
flow: อยู่ห้องหลัก (MINUTES_AT_HOME) → สุ่มห้องลาดตระเวน (MINUTES_AWAY) → วนซ้ำ
"""
import discord
from discord.ext import commands
from shared.voice_utils import join_channel
from config import HOME_CHANNEL_ID, AWAY_CHANNELS, MINUTES_AT_HOME, MINUTES_AWAY
import asyncio
import random


class PatrolCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._patrol_task = None

    @commands.Cog.listener()
    async def on_ready(self):
        if self._patrol_task is None or self._patrol_task.done():
            self._patrol_task = asyncio.create_task(self._patrol_loop())
            print("🛡️ ยาม: เริ่มลาดตระเวนแล้ว")

    async def _patrol_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                # กลับห้องหลัก
                home = guild.get_channel(HOME_CHANNEL_ID)
                if home and isinstance(home, discord.VoiceChannel):
                    await join_channel(self.bot, home)
                    print(f"🛡️ ยาม: กลับห้องหลัก → {home.name}")

                await asyncio.sleep(MINUTES_AT_HOME * 60)

                # ออกลาดตระเวน
                valid = [
                    guild.get_channel(ch_id)
                    for ch_id in AWAY_CHANNELS
                    if guild.get_channel(ch_id)
                    and isinstance(guild.get_channel(ch_id), discord.VoiceChannel)
                ]
                if valid:
                    target = random.choice(valid)
                    await join_channel(self.bot, target)
                    print(f"🛡️ ยาม: ออกลาดตระเวน → {target.name}")

                await asyncio.sleep(MINUTES_AWAY * 60)

    def cog_unload(self):
        if self._patrol_task:
            self._patrol_task.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(PatrolCog(bot))
