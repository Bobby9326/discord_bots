"""
shared/voice_utils.py — helper Voice Channel + TTS (edge-tts)
"""
import discord
import asyncio
import os
import tempfile
import edge_tts


async def join_channel(bot: discord.Client, channel: discord.VoiceChannel) -> discord.VoiceClient:
    """เข้าห้อง voice — ถ้าอยู่ห้องอื่นอยู่แล้วให้ย้าย"""
    vc: discord.VoiceClient | None = discord.utils.get(bot.voice_clients, guild=channel.guild)
    if vc:
        if vc.channel.id == channel.id:
            return vc
        await vc.move_to(channel)
        return vc
    return await channel.connect()


async def leave_channel(bot: discord.Client, guild: discord.Guild):
    """ออกจาก voice channel"""
    vc: discord.VoiceClient | None = discord.utils.get(bot.voice_clients, guild=guild)
    if vc and vc.is_connected():
        await vc.disconnect()


async def play_tts(vc: discord.VoiceClient, text: str, voice: str = "th-TH-NiwatNeural"):
    """สร้างไฟล์ TTS ด้วย edge-tts แล้วเล่นใน voice channel"""
    tts_path = os.path.join(tempfile.gettempdir(), "tts_output.mp3")

    # สร้างไฟล์เสียงด้วย edge-tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(tts_path)

    source = discord.FFmpegPCMAudio(tts_path)
    vc.play(source)
    while vc.is_playing():
        await asyncio.sleep(0.5)

    try:
        os.remove(tts_path)
    except Exception:
        pass


def get_voice_channels(guild: discord.Guild) -> list[discord.VoiceChannel]:
    """คืนรายการ voice channel ทั้งหมดใน guild"""
    return [ch for ch in guild.channels if isinstance(ch, discord.VoiceChannel)]