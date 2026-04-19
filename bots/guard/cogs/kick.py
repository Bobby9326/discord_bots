"""
bots/guard/cogs/kick.py — ยาม: เตะ member ด้วย TTS
คำสั่ง: /เตะ @member (admin only)
flow: เข้าห้อง member → TTS → ย้าย member → อยู่ด้วย 5 วิ → กลับห้องหลัก
"""
import discord
from discord import app_commands
from discord.ext import commands
from shared.voice_utils import join_channel, play_tts
from config import HOME_CHANNEL_ID, KICK_CHANNEL_ID, KICK_MESSAGE, KICK_STAY_SECONDS
import asyncio


class KickCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="เตะ", description="🦵 เตะสมาชิกออกจากห้อง")
    @app_commands.describe(member="สมาชิกที่ต้องการเตะ")
    @app_commands.checks.has_permissions(administrator=True)
    async def kick_member(self, interaction: discord.Interaction, member: discord.Member):

        if not member.voice or not member.voice.channel:
            await interaction.response.send_message(
                f"❌ {member.mention} ไม่ได้อยู่ใน Voice Channel", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"🛡️ กำลังดำเนินการกับ {member.mention}...", ephemeral=True
        )

        try:
            # 1. เข้าห้องที่ member อยู่
            vc = await join_channel(self.bot, member.voice.channel)

            # 2. TTS พูดชื่อ member
            message = KICK_MESSAGE.format(member=member.display_name)
            await play_tts(vc, message)

            # 3. ย้าย member ไปห้องเตะ
            kick_ch = interaction.guild.get_channel(KICK_CHANNEL_ID)
            if kick_ch and isinstance(kick_ch, discord.VoiceChannel):
                await member.move_to(kick_ch)
                # 4. ยามตามไปอยู่ด้วย
                await join_channel(self.bot, kick_ch)
                await asyncio.sleep(KICK_STAY_SECONDS)
            else:
                await interaction.followup.send("⚠️ ไม่พบ KICK_CHANNEL_ID ใน config", ephemeral=True)

            # 5. กลับห้องหลัก
            home_ch = interaction.guild.get_channel(HOME_CHANNEL_ID)
            if home_ch and isinstance(home_ch, discord.VoiceChannel):
                await join_channel(self.bot, home_ch)

            await interaction.followup.send(
                f"✅ เตะ {member.mention} เรียบร้อยแล้ว", ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send("❌ บอทไม่มีสิทธิ์ `Move Members`", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

    @kick_member.error
    async def kick_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ Administrator", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(KickCog(bot))