"""
bots/secretary/cogs/ai.py — AI ตอบเมื่อถูก mention (Groq)
"""
import discord
from discord.ext import commands
from groq import Groq
from shared.config import GROQ_API_KEY
from config import GROQ_MODEL, AI_SYSTEM_PROMPT, AI_MAX_HISTORY
from collections import defaultdict

_history: dict[int, list] = defaultdict(list)


class AICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not GROQ_API_KEY:
            print("  ⚠️  ไม่พบ GROQ_API_KEY — AI จะไม่ทำงาน")
            self.client = None
        else:
            self.client = Groq(api_key=GROQ_API_KEY)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if self.bot.user not in message.mentions:
            return
        if not self.client:
            await message.reply("❌ AI ยังไม่ได้ตั้งค่า GROQ_API_KEY")
            return

        content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
        if not content:
            await message.reply("มีอะไรให้ช่วยไหมครับ? 😊")
            return

        history = _history[message.channel.id]
        history.append({"role": "user", "content": content})

        if len(history) > AI_MAX_HISTORY:
            history = history[-AI_MAX_HISTORY:]
            _history[message.channel.id] = history

        async with message.channel.typing():
            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": AI_SYSTEM_PROMPT},
                        *history,
                    ],
                    max_tokens=512,
                )
                reply = response.choices[0].message.content
                history.append({"role": "assistant", "content": reply})

                if len(reply) <= 2000:
                    await message.reply(reply)
                else:
                    for i in range(0, len(reply), 2000):
                        await message.channel.send(reply[i:i+2000])

            except Exception as e:
                await message.reply(f"❌ เกิดข้อผิดพลาด: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(AICog(bot))