import discord
from discord.ext import commands
from discord import app_commands
import os
from ai_labs.persona_engine import AIEngine

class InteractionLabs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_engine = AIEngine(bot.redis)

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        owner_id = int(os.environ.get("OWNER_ID", 0))
        if interaction.user.id != owner_id:
            await interaction.response.send_message("❌ Từ chối truy cập. Tính năng độc quyền Level 4.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="ai-chat", description="Trò chuyện với AI (Nhân cách thay đổi theo ca trực)")
    async def ai_chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        
        persona = self.bot.persona 
        reply = await self.ai_engine.generate_response(interaction.user.id, message, persona)
        
        embed = discord.Embed(description=reply, color=self.bot.theme_color)
        embed.set_author(name=f"{persona} System", icon_url=self.bot.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="chat", description="Điều khiển bot nhắn tin hoặc dùng Webhook ẩn danh (Độc quyền Owner)")
    async def spy_chat(
        self, interaction: discord.Interaction, 
        message: str, 
        channel_id: str, 
        reply_to: str = None, 
        use_webhook: bool = False, 
        avatar_url: str = None, 
        name: str = None
    ):
        if not await self.check_owner(interaction): return
        await interaction.response.defer(ephemeral=True)

        try:
            channel = await self.bot.fetch_channel(int(channel_id))
        except Exception:
            await interaction.followup.send("❌ Không tìm thấy Kênh (Channel ID sai hoặc Bot không có quyền đọc).")
            return

        if use_webhook:
            webhooks = await channel.webhooks()
            webhook = discord.utils.get(webhooks, name="EquinoxSpy")
            if not webhook:
                webhook = await channel.create_webhook(name="EquinoxSpy")
            
            await webhook.send(
                content=message,
                username=name or self.bot.user.name,
                avatar_url=avatar_url or self.bot.user.display_avatar.url
            )
            await interaction.followup.send("✅ Đã bắn tin nhắn ẩn danh qua Webhook.")
        else:
            if reply_to:
                try:
                    target_msg = await channel.fetch_message(int(reply_to))
                    await target_msg.reply(content=message)
                    await interaction.followup.send(f"✅ Đã Reply tin nhắn {reply_to} thành công.")
                    return
                except Exception:
                    await interaction.followup.send("⚠️ Không tìm thấy tin nhắn để Reply. Sẽ gửi như tin nhắn thường.")
            
            await channel.send(content=message)
            await interaction.followup.send("✅ Đã điều khiển thực thể Bot gửi tin nhắn thành công.")

async def setup(bot):
    await bot.add_cog(InteractionLabs(bot))
