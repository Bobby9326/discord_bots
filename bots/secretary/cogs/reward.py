"""
bots/secretary/cogs/reward.py — ระบบแลกรางวัล (slash commands + ปุ่มกด)
/reward, /points
"""
import discord
from discord import app_commands
from discord.ext import commands
from shared.database import get_points, add_points, log_reward
from config import REWARDS
from datetime import datetime


class RewardView(discord.ui.View):
    def __init__(self, user: discord.Member, points: int):
        super().__init__(timeout=60)
        self.user = user
        self.points = points

        for i, r in enumerate(REWARDS, 1):
            can_afford = points >= r["cost"]
            btn = discord.ui.Button(
                label=f"{r['role']} — {r['cost']} แต้ม",
                style=discord.ButtonStyle.green if can_afford else discord.ButtonStyle.gray,
                disabled=not can_afford,
                custom_id=f"redeem_{i}",
                row=(i - 1) // 3,
            )
            btn.callback = self._make_callback(i, r)
            self.add_item(btn)

    def _make_callback(self, index: int, reward: dict):
        async def callback(interaction: discord.Interaction):
            # เช็คว่าคนกดคือคนที่ใช้คำสั่ง
            if interaction.user.id != self.user.id:
                await interaction.response.send_message(
                    "❌ นี่ไม่ใช่ร้านค้าของคุณ", ephemeral=True
                )
                return

            points = get_points(str(interaction.user.id))

            if points < reward["cost"]:
                await interaction.response.send_message(
                    f"❌ แต้มไม่พอ มี **{points}** ต้องการ **{reward['cost']}** แต้ม",
                    ephemeral=True,
                )
                return

            role = discord.utils.get(interaction.guild.roles, name=reward["role"])
            if not role:
                await interaction.response.send_message(
                    f"❌ ไม่พบ Role `{reward['role']}` กรุณาแจ้ง Admin", ephemeral=True
                )
                return

            if role in interaction.user.roles:
                await interaction.response.send_message(
                    f"❌ คุณมี Role `{reward['role']}` อยู่แล้ว", ephemeral=True
                )
                return

            add_points(str(interaction.user.id), -reward["cost"])
            await interaction.user.add_roles(role)
            log_reward(
                str(interaction.user.id),
                reward["role"],
                reward["cost"],
                datetime.now().isoformat(),
            )

            remaining = points - reward["cost"]
            embed = discord.Embed(title="🎉 แลกรางวัลสำเร็จ!", color=discord.Color.green())
            embed.add_field(name="Role ที่ได้", value=f"`{reward['role']}`", inline=True)
            embed.add_field(name="แต้มที่ใช้", value=f"`{reward['cost']}`", inline=True)
            embed.add_field(name="แต้มคงเหลือ", value=f"`{remaining}`", inline=True)

            # ปิดปุ่มทั้งหมดหลังแลกสำเร็จ
            for item in self.children:
                item.disabled = True

            await interaction.response.edit_message(embed=interaction.message.embeds[0], view=self)
            await interaction.followup.send(embed=embed, ephemeral=True)

        return callback


class RewardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reward", description="🎁 ดูและแลกรางวัลด้วยแต้ม")
    async def reward(self, interaction: discord.Interaction):
        points = get_points(str(interaction.user.id))

        embed = discord.Embed(
            title="🏪 ร้านค้า",
            description=f"💰 แต้มของคุณ: **{points} แต้ม**\n\nกดปุ่มด้านล่างเพื่อแลกรางวัล",
            color=discord.Color.gold(),
        )

        if not REWARDS:
            embed.add_field(name="⚠️", value="ยังไม่ได้ตั้งค่า REWARDS ใน config.py")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        for r in REWARDS:
            status = "✅" if points >= r["cost"] else "❌"
            embed.add_field(
                name=f"{status} {r['role']}",
                value=f"{r['cost']} แต้ม",
                inline=True,
            )

        view = RewardView(user=interaction.user, points=points)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="points", description="💰 ดูแต้มสะสมของคุณ")
    async def points(self, interaction: discord.Interaction):
        pts = get_points(str(interaction.user.id))
        embed = discord.Embed(
            title="💰 แต้มสะสม",
            description=f"{interaction.user.mention} มี **{pts} แต้ม**",
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RewardCog(bot))