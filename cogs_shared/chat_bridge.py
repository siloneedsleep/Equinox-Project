import os
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
    @app_commands.command(name="chat", description="[OWNER] Nhập vai bot để nhắn tin vào kênh được chỉ định")
    @app_commands.describe(
        noidung="Nội dung sếp muốn con bot thốt ra",
        kenh="Kênh sếp muốn bot gửi tin nhắn vào (Để trống nếu muốn chat tại kênh hiện tại)",
        reply_id="ID của tin nhắn muốn bot trả lời (Phải thuộc kênh đã chọn)"
    )
    async def proxy_chat(
        self, 
        interaction: discord.Interaction, 
        noidung: str, 
        kenh: discord.abc.GuildChannel = None, # Cho phép chọn bất kỳ kênh nào trong server
        reply_id: str = None
    ):
        r = await get_redis_connection()
        
        # 👑 1. MẠCH KIỂM TRA QUYỀN OWNER TỐI CAO (ĐỒNG BỘ 2 LỚP)
        is_owner = False
        env_owner = os.getenv("OWNER_DISCORD_ID")
        if env_owner and interaction.user.id == int(env_owner):
            is_owner = True
            
        if not is_owner:
            is_owner = await r.sismember("equinox:staff:owners", interaction.user.id)
            
        if not is_owner:
            await interaction.response.send_message(
                "❌ Tính giả mạo thế thiên hành đạo à? Lệnh này chỉ dành cho Owner tối cao thôi!", 
                ephemeral=True
            )
            return

        # ⏳ 2. KIỂM TRA CA TRỰC NGHIÊM NGẶT
        is_overdrive = await r.hget("equinox:system:config", "event_overdrive") == b"ON" or await r.hget("equinox:system:config", "event_overdrive") == "ON"
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

        # 📍 3. XÁC ĐỊNH KÊNH ĐÍCH VÀ KIỂM TRA ĐIỀU KIỆN
        # Nếu sếp không chọn kênh, mặc định lấy kênh hiện tại
        target_channel = kenh if kenh else interaction.channel
        
        # Kiểm tra xem kênh đó có phải kênh Text không (tránh gửi vào kênh Voice/Category)
        if not isinstance(target_channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message(
                "❌ Bot chỉ có thể múa phím ở kênh Văn Bản hoặc Luồng (Thread) thôi sếp ơi!", 
                ephemeral=True
            )
            return

        # Phản hồi ẩn để sếp biết lệnh đã thông qua
        await interaction.response.send_message(f"⏳ Đang hòa nhập linh hồn vào kênh {target_channel.mention}... bắt đầu múa phím!", ephemeral=True)

        # ⌨️ 4. GIẢ LẬP GÕ PHÍM NHƯ NGƯỜI THẬT TRÊN KÊNH ĐÍCH
        typing_time = min(len(noidung) * 0.05, 4.0)
        async with target_channel.typing():
            await asyncio.sleep(typing_time)

        # 📨 5. QUĂNG TIN NHẮN VÀO KÊNH ĐÍCH (KÈM CHECK REPLY CHÉO KÊNH)
        if reply_id:
            try:
                # Ép fetch tin nhắn ngay tại kênh đích được chọn để xác thực
                target_msg = await target_channel.fetch_message(int(reply_id))
                await target_msg.reply(noidung)
                await interaction.edit_original_response(content=f"✅ Nhập hồn thành công! Đã phản hồi tin nhắn trong kênh {target_channel.mention}.")
            except discord.NotFound:
                # Nếu tin nhắn tồn tại ở server nhưng KHÔNG nằm trong kênh đã chọn, discord.NotFound sẽ kích hoạt
                await interaction.edit_original_response(
                    content=f"❌ Không tìm thấy ID tin nhắn này trong kênh {target_channel.mention}! Sếp kiểm tra lại xem có chép nhầm tin nhắn của kênh khác qua không nha."
                )
            except ValueError:
                await interaction.edit_original_response(content="❌ ID tin nhắn phải là một chuỗi số cơ mà sếp!")
            except discord.Forbidden:
                await interaction.edit_original_response(content=f"❌ Bot thiếu quyền đọc lịch sử tin nhắn hoặc gửi bài tại kênh {target_channel.mention} rồi sếp.")
        else:
            try:
                await target_channel.send(noidung)
                await interaction.edit_original_response(content=f"✅ Nhập hồn thành công! Bot đã gửi tin nhắn vào kênh {target_channel.mention}.")
            except discord.Forbidden:
                await interaction.edit_original_response(content=f"❌ Bot bị chặn quyền gửi tin nhắn tại kênh {target_channel.mention} rồi sếp.")

async def setup(bot):
    await bot.add_cog(ChatBridge(bot))
