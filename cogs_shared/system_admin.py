import discord
from discord.ext import commands
from discord import app_commands

from config.settings import COLORS, LUMINOUS_ID, TENEBRIS_ID
from database.redis_client import get_redis_connection

class SystemAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Hàm kiểm tra quyền Sếp Tổng / Dev
    async def is_supreme_leader(self, user_id):
        r = await get_redis_connection()
        is_owner = await r.sismember("equinox:staff:owners", str(user_id))
        is_dev = await r.sismember("equinox:staff:devs", str(user_id))
        return is_owner or is_dev

    # ==========================================
    # 👑 1. QUẢN TRỊ NHÂN SỰ ĐỘNG (/system-promote)
    # ==========================================
    @commands.hybrid_command(name="system-promote", aliases=["system-staff"], description="[Owner/Dev] Cấp quyền hoặc phế truất nhân sự")
    @app_commands.describe(user="Thành viên", action="Hành động", role="Chức vụ")
    @app_commands.choices(action=[
        app_commands.Choice(name="Cấp Quyền (Promote)", value="PROMOTE"),
        app_commands.Choice(name="Phế Truất (Demote)", value="DEMOTE")
    ], role=[
        app_commands.Choice(name="Developer (Tối đa 2)", value="devs"),
        app_commands.Choice(name="Admin (Tối đa 3)", value="admins"),
        app_commands.Choice(name="Event Manager (Tối đa 2)", value="event_managers"),
        app_commands.Choice(name="Staff (Tối đa 10)", value="moderators")
    ])
    async def system_promote(self, ctx, user: discord.Member, action: str, role: str):
        if not await self.is_supreme_leader(ctx.author.id):
            return await ctx.send("🚫 Quyền truy cập bị từ chối! Lệnh này chỉ dành cho Sếp Tổng và Dev.", ephemeral=True)

        r = await get_redis_connection()
        role_key = f"equinox:staff:{role}"
        
        limits = {"devs": 2, "admins": 3, "event_managers": 2, "moderators": 10}

        if action == "PROMOTE":
            current_count = await r.scard(role_key)
            if current_count >= limits[role]:
                return await ctx.send(f"🚫 Hạn ngạch chức vụ này đã đầy ({limits[role]}/{limits[role]})!", ephemeral=True)
                
            await r.sadd(role_key, str(user.id))
            
            if self.bot.user.id == LUMINOUS_ID:
                embed = discord.Embed(title="⚖️ SẮC LỆNH HOÀNG GIA: THAY ĐỔI CẤP BẬC", color=COLORS["luminous_main"])
                embed.description = f"Thực thi sắc lệnh tối cao từ Thượng Đế!\n\n- 👤 Nhân sự: <@{user.id}>\n- 📊 Hành động: SẮC PHONG\n- 👑 Chức vụ mới: {role.upper()}\n\nToàn bộ quyền hạn đã được mở khóa trên Redis Cloud!"
            else:
                embed = discord.Embed(title="⛓️ THANH TRỪNG NỘI BỘ THỦ PHỦ", color=COLORS["tenebris_action"])
                embed.description = f"Lệnh từ Sếp Tổng đã đóng dấu máu!\n\n- 👤 Đối tượng: <@{user.id}>\n- 💀 Bản án: THĂNG CẤP làm {role.upper()}.\n\nThằng này chính thức được cấp chìa khóa hệ thống. Làm bậy là ta thả sát thủ xử bắn!"

        else: # DEMOTE
            await r.srem(role_key, str(user.id))
            
            if self.bot.user.id == LUMINOUS_ID:
                embed = discord.Embed(title="⚖️ SẮC LỆNH HOÀNG GIA: PHẾ TRUẤT", color=COLORS["luminous_error"])
                embed.description = f"👤 Nhân sự <@{user.id}> đã bị PHẾ TRUẤT khỏi chức vụ {role.upper()}.\nĐã hạ cấp xuống thành Cư dân thường."
            else:
                embed = discord.Embed(title="⛓️ TỊCH THU QUYỀN LỰC CHỢ ĐEN", color=COLORS["tenebris_error"])
                embed.description = f"👤 <@{user.id}> đã bị ĐÁ ĐÍT khỏi ghế {role.upper()}.\nToàn bộ token truy cập phòng điều khiển đã bị phong tỏa!"

        await ctx.send(embed=embed)

    # ==========================================
    # 💰 2. CAN THIỆP TÀI CHÍNH VĨ MÔ (/system-adjust-bal)
    # ==========================================
    @commands.hybrid_command(name="system-adjust-bal", description="[Owner/Dev] Bơm/Hút tiền trực tiếp")
    @app_commands.choices(action=[
        app_commands.Choice(name="Bơm Tiền (ADD)", value="ADD"),
        app_commands.Choice(name="Tịch Thu (REMOVE)", value="REMOVE")
    ])
    async def adjust_bal(self, ctx, user: discord.Member, action: str, amount: int):
        if not await self.is_supreme_leader(ctx.author.id):
            return await ctx.send("🚫 Quyền truy cập bị từ chối!", ephemeral=True)

        r = await get_redis_connection()
        user_key = f"equinox:user:{user.id}"

        if self.bot.user.id == LUMINOUS_ID:
            # Luminous xử lý tiền sạch
            if action == "ADD":
                await r.hincrby(user_key, "balance_clean", amount)
                embed = discord.Embed(title="🏛️ ĐIỀU CHỈNH QUỐC KHỐ TỐI CAO", color=COLORS["luminous_main"])
                embed.description = f"Sắc lệnh Hoàng gia đã thực thi bởi <@{ctx.author.id}>!\n\n- 👤 Đối tượng: <@{user.id}>\n- 📈 Hành động: CỘNG THÊM **+{amount:,} Aequor 🪙** vào ví sạch.\n- 📝 Lý do: Thưởng sự kiện cống hiến Mạng lưới."
            else:
                await r.hincrby(user_key, "balance_clean", -amount)
                embed = discord.Embed(title="🏛️ ĐIỀU CHỈNH QUỐC KHỐ TỐI CAO", color=COLORS["luminous_error"])
                embed.description = f"Sắc lệnh Hoàng gia đã thực thi bởi <@{ctx.author.id}>!\n\n- 👤 Đối tượng: <@{user.id}>\n- 📉 Hành động: TRỪ **-{amount:,} Aequor 🪙** từ ví sạch."
        else:
            # Tenebris xử lý tiền bẩn
            if action == "ADD":
                await r.hincrby(user_key, "balance_dirty", amount)
                embed = discord.Embed(title="⛓️ BƠM TIỀN CHỢ ĐEN", color=COLORS["tenebris_action"])
                embed.description = f"Lệnh từ Bóng Tối đã thực thi!\n\n- 👤 Đối tượng: <@{user.id}>\n- 📈 Hành động: BƠM **+{amount:,} Aequis 🚨** vào két sắt ngầm."
            else:
                await r.hincrby(user_key, "balance_dirty", -amount)
                embed = discord.Embed(title="⛓️ THU HỒI TÀI SẢN CHỢ ĐEN", color=COLORS["tenebris_error"])
                embed.description = f"Lệnh trừng phạt từ Bóng Tối đã thực thi bởi <@{ctx.author.id}>!\n\n- 👤 Đối tượng: <@{user.id}>\n- 📉 Hành động: TỊCH THU KHẨN CẤP **-{amount:,} Aequis 🚨** từ két ngầm.\n- 📝 Lý do: Trừng phạt vi phạm."
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SystemAdmin(bot))
