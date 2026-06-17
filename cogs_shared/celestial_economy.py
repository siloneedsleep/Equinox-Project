import os
import random
import discord
from discord import app_commands
from discord.ext import commands
from database.redis_client import get_redis_connection

class CelestialEconomy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==============================================================================
    # ☀️ LỆNH SLASH: NGUYỆN ƯỚC ÁNH SÁNG (DIỂM DANH HẰNG NGÀY - CA NGÀY)
    # ==============================================================================
    @app_commands.command(name="daily", description="[CA NGÀY] Nhận nguyện ước ánh sáng để tích lũy đồng tiền sạch Aequor (Star)")
    async def daily_reward(self, interaction: discord.Interaction):
        r = await get_redis_connection()
        user_id = str(interaction.user.id)

        # ⏳ 1. KIỂM TRA CHẶN LỆCH CA (Chỉ cho phép nhận ca ngày của Luminous)
        # Đọc chu kỳ ca trực thực tế trên RAM Redis
        cycle_bytes = await r.hget("equinox:system:config", "current_cycle")
        cycle = cycle_bytes.decode('utf-8') if isinstance(cycle_bytes, bytes) else "DAY"
        
        is_overdrive = await r.hget("equinox:system:config", "event_overdrive") == b"ON" or await r.hget("equinox:system:config", "event_overdrive") == "ON"

        if cycle != "DAY" and not is_overdrive:
            await interaction.response.send_message(
                "🌙 Đang là ca đêm của Tenebris! Trạm Ánh Sáng đã khép cửa... "
                "Hệ thống không thể kết nối đến Thần Điện Luminous để phân phát Aequor đâu sếp!", 
                ephemeral=True
            )
            return

        # 📅 2. KIỂM TRA THỜI GIAN CHỜ (Cooldown 24h dựa trên Redis Key)
        cooldown_key = f"equinox:economy:daily_cooldown:{user_id}"
        is_claimed = await r.get(cooldown_key)

        if is_claimed:
            # Lấy thời gian còn lại của key để báo cho người dùng
            ttl = await r.ttl(cooldown_key)
            hours = ttl // 3600
            minutes = (ttl % 3600) // 60
            await interaction.response.send_message(
                f"⏱️ Sếp đã nhận nguyện ước ngày hôm nay rồi! Vui lòng quay lại sau `{hours} giờ {minutes} phút` nữa nha.", 
                ephemeral=True
            )
            return

        # 🎲 3. MẠCH NHÂN PHẨM ĐỘC QUYỀN (BỎ THÔNG BÁO TOÀN SERVER)
        # Random số tiền gốc từ 50 đến 150 Star
        base_amount = random.randint(50, 150)
        final_amount = base_amount
        
        # Tạo số nhân phẩm ngẫu nhiên từ 1 đến 150 để check số lặp
        luck_number = random.randint(1, 150)
        
        # Check xem số may mắn có phải số lặp (Ví dụ: 11, 22, 33, 44, 55, 66, 77, 88, 99, 111) hay không
        luck_str = str(luck_number)
        is_lucky_streak = len(luck_str) > 1 and len(set(luck_str)) == 1

        bonus_text = ""
        if is_lucky_streak:
            final_amount = base_amount * 2 # Nhân đôi số tiền nhận được
            bonus_text = f"\n✨ **✨ HÀO QUANG TINH TÚ ĐÓN CHÀO:** Nhân phẩm bùng nổ, quay trúng số lặp `{luck_number}`! Sếp được Luminous nhân đôi phần thưởng!"

        # 💾 4. CẬP NHẬT KẾT QUẢ VÀO VÍ AEQUOR TRÊN REDIS
        wallet_key = f"equinox:economy:wallets:{user_id}"
        # Tăng số tiền sạch Aequor (trường aequor trong hash ví)
        current_balance = await r.hincrby(wallet_key, "aequor", final_amount)

        # Thiết lập thời gian khóa cooldown đúng 24 tiếng (86400 giây)
        await r.setex(cooldown_key, 86400, "claimed")

        # 📊 5. XUẤT EMBED KẾT QUẢ CHO CÁ NHÂN NGƯỜI GÕ
        embed = discord.Embed(
            title="☀️ NGUYỆN ƯỚC ÁNH SÁNG ĐÃ ĐƯỢC CHỨNG GIÁM ☀️",
            description=f"Thần Điện Luminous vừa truyền năng lượng tinh tú vào tài khoản của sếp.{bonus_text}",
            color=0xFFD700 if is_lucky_streak else 0x00FFFF
        )
        embed.add_field(name="💰 Tiền Sạch Nhận Được", value=f"`+ {final_amount} Aequor (Star)` ☀️", inline=True)
        embed.add_field(name="💳 Tổng Số Dư Ví Hiện Tại", value=f"`{current_balance:,} Aequor`", inline=True)
        embed.set_footer(text="Hệ sinh thái tài chính chính ngạch Luminous")

        # Gửi phản hồi dạng ẩn (ephemeral=True) nếu sếp muốn bảo mật số tiền, hoặc sửa thành False nếu muốn hiện tại chỗ gõ
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(CelestialEconomy(bot))
