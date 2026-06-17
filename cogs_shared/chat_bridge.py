import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from database.redis_client import get_redis_connection
from config.settings import LUMINOUS_ID, TENEBRIS_ID

class ChatBridge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==============================================================================
    # 🎭 LỆNH SLASH: NHẬP HỒN BOT (CHỈ DÀNH CHO OWNER)
    # ==============================================================================
    @app_commands.command(name="chat", description="[OWNER] Nhập vai bot để nhắn tin vào kênh (giả lập người thật)")
    @app_commands.describe(
        noidung="Nội dung sếp muốn con bot thốt ra",
        reply_id="ID của tin nhắn muốn bot trả lời (Để trống nếu chỉ chat bình thường)"
    )
    async def proxy_chat(self, interaction: discord.Interaction, noidung: str, reply_id: str = None):
        r = await get_redis_connection()
        
        # 👑 1. CHỈ OWNER MỚI ĐƯỢC PHÉP "NHẬP HỒN"
        role_bytes = await r.hget("equinox:system:staff_roles", str(interaction.user.id))
        role = role_bytes.decode('utf-8') if isinstance(role_bytes, bytes) else str(role_bytes)
        
        if role != "owner":
            await interaction.response.send_message(
                "❌ Tính giả mạo thế thiên hành đạo à? Lệnh này chỉ dành cho Owner tối cao thôi!", 
                ephemeral=True
            )
            return

        # ⏳ 2. KIỂM TRA CA TRỰC NGHIÊM NGẶT
        is_overdrive = await r.hget("equinox:system:config", "event_overdrive") == "ON"
        if not is_overdrive:
            cycle_bytes = await r.hget("equinox:system:config", "current_cycle")
            cycle = cycle_bytes.decode('utf-8') if isinstance(cycle_bytes, bytes) else str(cycle_bytes)
            
            if self.bot.user.id == LUMINOUS_ID and cycle != "DAY":
                await interaction.response.send_message(
                    "🌙 Đang là ca đêm của Tenebris! Cô vợ Luminous đang đắp chăn ngủ say, sếp không nhập hồn bắt bả dậy chat được đâu!", 
                    ephemeral=True
                )
                return
            if self.bot.user.id == TENEBRIS_ID and cycle != "NIGHT":
                await interaction.response.send_message(
                    "☀️ Đang là ca ngày của Luminous! Ông chồng Tenebris sợ cháy nắng không chịu ló mặt ra chat đâu sếp!", 
                    ephemeral=True
                )
                return

        # Phản hồi ẩn cho sếp biết là lệnh đã ăn
        await interaction.response.send_message("⏳ Đang hòa nhập linh hồn... bắt đầu múa phím!", ephemeral=True)

        # ⌨️ 3. GIẢ LẬP GÕ PHÍM NHƯ NGƯỜI THẬT
        # Công thức: Mỗi 1 ký tự tốn 0.05 giây để gõ. Max là 4 giây để mem không phải đợi quá lâu
        typing_time = min(len(noidung) * 0.05, 4.0)
        
        # Bật trạng thái "Đang nhập dữ liệu..." (Typing...) ở dưới kênh
        async with interaction.channel.typing():
            await asyncio.sleep(typing_time)

        # 📨 4. QUĂNG TIN NHẮN VÀO KÊNH
        if reply_id:
            try:
                target_msg = await interaction.channel.fetch_message(int(reply_id))
                await target_msg.reply(noidung)
                await interaction.edit_original_response(content="✅ Nhập hồn thành công! Đã Reply thẳng mặt đối tượng.")
            except discord.NotFound:
                await interaction.edit_original_response(content="❌ Cười ẻ, sếp chép nhầm ID tin nhắn rồi! Chả tìm thấy cái tin nhắn đó trong kênh này.")
            except ValueError:
                await interaction.edit_original_response(content="❌ ID tin nhắn phải là một chuỗi số cơ mà sếp!")
        else:
            await interaction.channel.send(noidung)
            await interaction.edit_original_response(content="✅ Nhập hồn thành công! Bot đã gửi tin nhắn.")

async def setup(bot):
    await bot.add_cog(ChatBridge(bot))
