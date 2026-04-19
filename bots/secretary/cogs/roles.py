"""
bots/secretary/cogs/roles.py — Role Management (slash commands, admin only)
"""
import discord
from discord import app_commands
from discord.ext import commands
from config import TICKET_ROLES, MUTE_ROLES, MUTE_DURATION
import asyncio


class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /ticket ───────────────────────────────
    @app_commands.command(name="ticket", description="🟨 ให้ใบเตือนแก่ผู้ใช้")
    @app_commands.describe(member="ผู้ใช้ที่ต้องการให้ใบเตือน")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction, member: discord.Member):
        guild = interaction.guild
        roles = [discord.utils.get(guild.roles, name=name) for name in TICKET_ROLES]

        missing = [TICKET_ROLES[i] for i, r in enumerate(roles) if r is None]
        if missing:
            await interaction.response.send_message(
                f"❗ ไม่พบ Role: {', '.join(missing)}", ephemeral=True
            )
            return

        current = [r for r in roles if r in member.roles]
        if len(current) >= len(TICKET_ROLES):
            await interaction.response.send_message(
                f"❌ {member.mention} ได้รับครบทุกใบเตือนแล้ว", ephemeral=True
            )
            return

        next_role = roles[len(current)]
        await member.add_roles(next_role)

        muted = False
        duration = MUTE_DURATION.get(next_role.name, 0)

        if next_role.name in MUTE_ROLES:
            try:
                await member.edit(mute=True)
                muted = True
            except discord.Forbidden:
                pass

        is_red = next_role.name.startswith("RedCard") or next_role.name == "BlackCard"
        color = discord.Color.red() if is_red else discord.Color.yellow()
        emoji = "🟥" if is_red else "🟨"

        embed = discord.Embed(title=f"{emoji} ออกใบเตือน", color=color)
        embed.add_field(name="ผู้รับ", value=member.mention, inline=True)
        embed.add_field(name="ใบเตือน", value=f"`{next_role.name}`", inline=True)
        if muted:
            mute_text = "🔇 ปิดไมค์ถาวร" if duration == -1 else f"🔇 ปิดไมค์ {duration} นาที"
            embed.add_field(name="โทษ", value=mute_text, inline=True)

        await interaction.response.send_message(embed=embed)

        if muted and duration > 0:
            self.bot.loop.create_task(self._unmute_after(member, duration))

    async def _unmute_after(self, member: discord.Member, minutes: int):
        await asyncio.sleep(minutes * 60)
        try:
            m = member.guild.get_member(member.id)
            if m:
                await m.edit(mute=False)
                print(f"🔊 เปิดไมค์ {m.display_name} คืนแล้ว ({minutes} นาที)")
        except Exception as e:
            print(f"⚠️ เปิดไมค์ไม่สำเร็จ: {e}")

    # ── /clearticket ──────────────────────────
    @app_commands.command(name="clearticket", description="🧹 ลบใบเตือนทั้งหมด (ยกเว้น BlackCard)")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        roles_to_clear = [
            discord.utils.get(guild.roles, name=name)
            for name in TICKET_ROLES if name != "BlackCard"
        ]
        roles_to_clear = [r for r in roles_to_clear if r]

        await interaction.response.send_message("⏳ กำลังลบใบเตือน โปรดรอ...")
        count = 0
        unmuted = 0
        blackcard = discord.utils.get(guild.roles, name="BlackCard")

        for member in guild.members:
            to_remove = [r for r in roles_to_clear if r in member.roles]
            if to_remove:
                await member.remove_roles(*to_remove)
                count += 1
            if member.voice and member.voice.mute:
                if not blackcard or blackcard not in member.roles:
                    try:
                        await member.edit(mute=False)
                        unmuted += 1
                    except Exception:
                        pass

        embed = discord.Embed(title="🧹 ล้างใบเตือนเรียบร้อย", color=discord.Color.green())
        embed.add_field(name="ลบใบเตือนจาก", value=f"`{count}` คน", inline=True)
        embed.add_field(name="เปิดไมค์คืน", value=f"`{unmuted}` คน", inline=True)
        embed.add_field(name="หมายเหตุ", value="BlackCard ไม่ถูกลบ", inline=False)
        await interaction.followup.send(embed=embed)

    # ── /show ─────────────────────────────────
    @app_commands.command(name="show", description="📋 แสดง role ทั้งหมด + จำนวนคน")
    @app_commands.checks.has_permissions(administrator=True)
    async def show(self, interaction: discord.Interaction):
        roles = sorted(
            [r for r in interaction.guild.roles if r.name != "@everyone"],
            key=lambda r: r.position, reverse=True
        )
        embed = discord.Embed(title="📋 Role ทั้งหมดในเซิร์ฟ", color=discord.Color.blurple())
        lines = [f"`{r.name}` — {len(r.members)} คน" for r in roles[:30]]
        embed.description = "\n".join(lines) or "ไม่มี Role"
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /count ────────────────────────────────
    @app_commands.command(name="count", description="🔢 นับคนที่มี role")
    @app_commands.describe(role="role ที่ต้องการนับ")
    @app_commands.checks.has_permissions(administrator=True)
    async def count(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(
            f'มี **{len(role.members)}** คนที่มี Role `{role.name}`', ephemeral=True
        )

    # ── /listrole ─────────────────────────────
    @app_commands.command(name="listrole", description="📝 แสดงรายชื่อคนที่มี role")
    @app_commands.describe(role="role ที่ต้องการดู")
    @app_commands.checks.has_permissions(administrator=True)
    async def listrole(self, interaction: discord.Interaction, role: discord.Role):
        members = [m.display_name for m in role.members]
        if members:
            await interaction.response.send_message(
                f'สมาชิกที่มี Role `{role.name}`:\n' + "\n".join(members), ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'ไม่มีสมาชิกที่มี Role `{role.name}`', ephemeral=True
            )

    # ── /addrole ──────────────────────────────
    @app_commands.command(name="addrole", description="➕ เพิ่ม role ให้ member")
    @app_commands.describe(member="สมาชิก", role="role ที่ต้องการเพิ่ม")
    @app_commands.checks.has_permissions(administrator=True)
    async def addrole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await interaction.response.send_message(
                f"❌ {member.display_name} มี `{role.name}` อยู่แล้ว", ephemeral=True
            )
            return
        await member.add_roles(role)
        await interaction.response.send_message(
            f"✅ เพิ่ม `{role.name}` ให้ {member.display_name} แล้ว"
        )

    # ── /removerole ───────────────────────────
    @app_commands.command(name="removerole", description="➖ ถอด role จาก member")
    @app_commands.describe(member="สมาชิก", role="role ที่ต้องการถอด")
    @app_commands.checks.has_permissions(administrator=True)
    async def removerole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role not in member.roles:
            await interaction.response.send_message(
                f"❌ {member.display_name} ไม่มี `{role.name}`", ephemeral=True
            )
            return
        await member.remove_roles(role)
        await interaction.response.send_message(
            f"✅ ถอด `{role.name}` จาก {member.display_name} แล้ว"
        )

    @ticket.error
    @clearticket.error
    @show.error
    @count.error
    @listrole.error
    @addrole.error
    @removerole.error
    async def admin_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ Administrator", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RolesCog(bot))