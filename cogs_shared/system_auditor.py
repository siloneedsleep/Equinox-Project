import discord
from discord.ext import commands
from database.redis_client import get_redis_connection

class SystemAuditor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="audit")
    async def audit_system(self, ctx):
        r = await get_redis_connection()
        cycle = await r.hget("equinox:system:config", "current_cycle") or "DAY"
        is_correct_cycle = (cycle == "DAY")
        
        # FIX LỖI 3: fxFF9900 -> 0xFF9900
        color = 0x00FF88 if is_correct_cycle else 0xFF9900
        
        embed = discord.Embed(title="⚙️ SYSTEM AUDIT", color=color)
        embed.description = f"Current cycle logic verified: {cycle}"
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SystemAuditor(bot))
