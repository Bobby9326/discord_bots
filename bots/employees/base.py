"""
bots/employees/base.py — BaseEmployee class ใช้ร่วมกันทั้ง 3 ตัว
"""
import sys
import os
# root project (เพื่อ import shared/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# bot directory (เพื่อ import config)
sys.path.insert(0, os.path.dirname(__file__))
import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime
from shared.config import get_token
from shared.voice_utils import join_channel, leave_channel
from config import WORK_START, WORK_END, ROAM_INTERVAL_MINUTES, ALLOWED_CHANNELS


class BaseEmployee(commands.Bot):
    """
    Bot พนักงาน — สุ่มย้าย voice channel ในเวลาทำงาน
    ต่อยอดโดย emp1.py / emp2.py / emp3.py
    """
    bot_name:  str = "employee"
    token_key: str = "EMP1"

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.voice_states = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self._roam_task = None

    def _is_on_duty(self) -> bool:
        now = datetime.now().strftime("%H:%M")
        return WORK_START <= now < WORK_END

    async def on_ready(self):
        print(f"👷 {self.bot_name} [{self.user}] พร้อมแล้ว! ({WORK_START}–{WORK_END})")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing, name="💼 ทำงาน"
        ))
        if self._roam_task is None or self._roam_task.done():
            self._roam_task = asyncio.create_task(self._roam_loop())

    async def _roam_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            if self._is_on_duty():
                await self._roam()
            else:
                # นอกเวลางาน — ออกจาก voice
                for guild in self.guilds:
                    vc = discord.utils.get(self.voice_clients, guild=guild)
                    if vc and vc.is_connected():
                        await leave_channel(self, guild)
                        print(f"👷 {self.bot_name}: เลิกงานแล้ว ออกจาก voice")

            await asyncio.sleep(ROAM_INTERVAL_MINUTES * 60)

    async def _roam(self):
        for guild in self.guilds:
            valid = [
                guild.get_channel(ch_id)
                for ch_id in ALLOWED_CHANNELS
                if guild.get_channel(ch_id)
                and isinstance(guild.get_channel(ch_id), discord.VoiceChannel)
            ]
            if not valid:
                print(f"👷 {self.bot_name}: ไม่พบห้องใน ALLOWED_CHANNELS")
                continue
            target = random.choice(valid)
            await join_channel(self, target)
            print(f"👷 {self.bot_name}: ย้ายไป → {target.name}")

    async def start_bot(self):
        async with self:
            await self.start(get_token(self.token_key))