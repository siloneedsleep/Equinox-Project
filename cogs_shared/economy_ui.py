import discord
from discord.ext import commands
from discord import app_commands
import json
from backend.database import EquinoxDatabase
from backend.economy_engine import EconomyEngine

class EconomyUI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = EquinoxDatabase(bot.redis)
        self.engine = EconomyEngine(self.db)

    @app_commands.command(name="bag", description="Xem túi đồ và tài sản hiện có của bạn")
    async def view_bag(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        
        aequor = await self.bot.redis.hget(f"user:{user_id}:economy", "aequor") or 0
        aequis = await self.bot.redis.hget(f"user:{user_id}:economy", "aequis") or 0
        bag_raw = await self.bot.redis.hgetall(f"bag:{user_id}")
        
        embed = discord.Embed(title=f"🎒 Túi Đồ Của {interaction.user.display_name}", color=self.bot.theme_color)
        embed.add_field(name="Tiền Sạch (Aequor)", value=f"☀️ {int(aequor):,}", inline=True)
        embed.add_field(name="Tiền Bẩn (Aequis)", value=f"🌙 {int(aequis):,}", inline=True)
        
        if bag_raw:
            items_text = ""
            for item_id, item_str in bag_raw.items():
                item_data = json.loads(item_str)
                items_text += f"• **{item_data['type']}** (Mã: `{item_id[:8]}`)\n"
            embed.add_field(name="Vật Phẩm", value=items_text, inline=False)
        else:
            embed.add_field(name="Vật Phẩm", value="Túi của bạn đang trống rỗng.", inline=False)
            
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="open", description="Mở vật phẩm (VD: Star Pouch) trong túi đồ")
    async def open_item(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.defer()
        user_id = interaction.user.id
        
        bag_raw = await self.bot.redis.hgetall(f"bag:{user_id}")
        target_item_id = None
        target_item_data = None
        
        for full_id, item_str in bag_raw.items():
            if full_id.startswith(item_id):
                target_item_id = full_id
                target_item_data = json.loads(item_str)
                break
                
        if not target_item_id:
            await interaction.followup.send("❌ Không tìm thấy vật phẩm này trong túi của bạn.", ephemeral=True)
            return
            
        if target_item_data["type"] == "Star Pouch":
            result = await self.engine.open_star_pouch(user_id, self.bot.persona)
            await self.bot.redis.hdel(f"bag:{user_id}", target_item_id)
            
            embed = discord.Embed(title="✨ MỞ TÚI MAY MẮN (STAR POUCH)", color=self.bot.theme_color)
            currency_name = "Tiền Sạch (Aequor)" if result["currency"] == "aequor" else "Tiền Bẩn (Aequis)"
            icon = "☀️" if result["currency"] == "aequor" else "🌙"
            embed.description = f"Bạn đã nhận được **{result['amount']:,}** {icon} {currency_name}!\n\n*(Loại tiền được hệ thống tự động nội suy theo sự hiện diện của {result['persona']})*"
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("⚠️ Vật phẩm này không thể mở được bằng lệnh này.", ephemeral=True)

    @app_commands.command(name="trade", description="Khởi tạo phiên giao dịch an toàn với người khác")
    async def trade_start(self, interaction: discord.Interaction, target_user: discord.Member):
        if target_user.id == interaction.user.id or target_user.bot:
            await interaction.response.send_message("❌ Bạn không thể giao dịch với chính mình hoặc Bot.", ephemeral=True)
            return
            
        session_id = await self.engine.create_trade_session(interaction.user.id, target_user.id)
        short_session = session_id.split(':')[-1]
        
        embed = discord.Embed(title="🤝 PHIÊN GIAO DỊCH ĐƯỢC KHỞI TẠO", color=self.bot.theme_color)
        embed.description = f"<@{interaction.user.id}> đã gửi yêu cầu giao dịch đến <@{target_user.id}>.\n\nMã phiên: `{short_session}`\n*Phiên giao dịch sẽ tự động hủy sau 5 phút nếu không có tương tác.*"
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Chấp nhận", style=discord.ButtonStyle.success, emoji="✅", custom_id=f"trade_accept_{short_session}"))
        view.add_item(discord.ui.Button(label="Từ chối", style=discord.ButtonStyle.danger, emoji="❌", custom_id=f"trade_decline_{short_session}"))
        
        await interaction.response.send_message(content=target_user.mention, embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(EconomyUI(bot))
