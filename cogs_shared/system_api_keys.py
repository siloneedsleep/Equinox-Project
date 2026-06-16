import discord
from discord.ext import commands
from discord import app_commands

from config.settings import COLORS
from database.redis_client import get_redis_connection

class SystemApiKeys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_supreme_leader(self, user_id):
        r = await get_redis_connection()
        return await r.sismember("equinox:staff:owners", str(user_id)) or await r.sismember("equinox:staff:devs", str(user_id))

    @commands.hybrid_command(name="system-addkey", description="[Owner/Dev] Nạp API Key cho Trạm AI Labs")
    @app_commands.describe(key="Mã API Key", provider="Nhà cung cấp (VD: gemini, openai)")
    async def add_key(self, ctx, key: str, provider: str = "gemini"):
        if not await self.is_supreme_leader(ctx.author.id):
            return await ctx.send("🚫 Quyền truy cập bị từ chối!", ephemeral=True)

        r = await get_redis_connection()
        await r.sadd(f"equinox:ai_keys:{provider.lower()}", key)
        await ctx.send(f"✅ Đã nạp thành công 1 API Key cho hãng `{provider.upper()}` vào Pool gánh tải đa luồng!", ephemeral=True)

    @commands.hybrid_command(name="system-listkeys", description="[Owner/Dev] Kiểm tra số lượng API Key trong Pool")
    async def list_keys(self, ctx):
        if not await self.is_supreme_leader(ctx.author.id):
            return await ctx.send("🚫 Quyền truy cập bị từ chối!", ephemeral=True)

        r = await get_redis_connection()
        providers = ["gemini", "openai", "anthropic"]
        desc = "Số lượng Token Keys đang hoạt động tải luồng:\n\n"
        
        for p in providers:
            count = await r.scard(f"equinox:ai_keys:{p}")
            desc += f"🔌 Hãng **{p.upper()}**: `{count}` Keys\n"
            
        embed = discord.Embed(title="🔑 TRẠM KIỂM SOÁT API POOL", description=desc, color=COLORS["luminous_main"])
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SystemApiKeys(bot))
