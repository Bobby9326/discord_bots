"""
bots/secretary/cogs/points.py — Voice Tracking + แต้มสะสม (Supabase)
"""
import discord
from discord.ext import commands
from shared.database import get_points, add_points, start_session, get_session, end_session
from config import AFK_CHANNEL_ID, POINTS_PER_MINUTE
from datetime import datetime


class PointsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.bot and member != self.bot.user:
            # บันทึก session ของ bot อื่นเพื่อ keep Supabase active แต่ไม่คิดแต้ม
            user_id = str(member.id)
            now = datetime.now().isoformat()
            if before.channel is None and after.channel is not None:
                start_session(user_id, now)
            elif before.channel is not None and after.channel is None:
                end_session(user_id)
            return

        user_id = str(member.id)
        now = datetime.now().isoformat()

        # เข้า voice channel
        if before.channel is None and after.channel is not None:
            if after.channel.id == AFK_CHANNEL_ID:
                return
            start_session(user_id, now)

        # ออกจาก voice channel
        elif before.channel is not None and after.channel is None:
            self._calculate_and_award(user_id, before.channel.id)

        # ย้ายห้อง
        elif before.channel and after.channel and before.channel.id != after.channel.id:
            self._calculate_and_award(user_id, before.channel.id)
            if after.channel.id != AFK_CHANNEL_ID:
                start_session(user_id, now)

    def _calculate_and_award(self, user_id: str, channel_id: int):
        if channel_id == AFK_CHANNEL_ID:
            return
        joined_at = get_session(user_id)
        if not joined_at:
            return
        minutes = int((datetime.now() - datetime.fromisoformat(joined_at)).total_seconds() / 60)
        earned = minutes * POINTS_PER_MINUTE
        if earned > 0:
            add_points(user_id, earned)
            print(f"💰 {user_id} ได้รับ {earned} แต้ม ({minutes} นาที)")
        end_session(user_id)


async def setup(bot: commands.Bot):
    await bot.add_cog(PointsCog(bot))