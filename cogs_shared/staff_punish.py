import discord
from discord.ext import commands
from discord import app_commands
import datetime

from config.settings import LUMINOUS_ID, TENEBRIS_ID, COLORS
from database.redis_client import get_redis_connection

class StaffPunish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Hàm kiểm tra quyền hạn ngầm từ Redis
    async def is_staff(self, user_id):
        r = await get_redis_connection()
        for role in ["owners", "devs", "admins", "event_managers", "moderators"]:
            if await r.sismember(f"equinox:staff:{role}", str(user_id)):
                return True
        return False

    # ==========================================
    # 🪓 1. LỆNH WARN (Phạt gậy cảnh cáo)
    # ==========================================
    @commands.hybrid_command(name="warn", aliases=["staff-warn"], description="[Staff+] Phạt gậy cảnh cáo thành viên")
    async def warn_user(self, ctx, user: discord.Member, *, reason: str):
        if not await self.is_staff(ctx.author.id):
            return await ctx.send("🚫 Bạn không có quyền sử dụng lệnh trị an!", ephemeral=True)
            
        r = await get_redis_connection()
        warns = await r.hincrby("equinox:punish:warns", str(user.id), 1)
        
        # Ghi log vào Hộp Đen
        log_entry = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] Cán bộ {ctx.author.name} phạt gậy {user.name} | Lý do: {reason}"
        await r.lpush("equinox:punish:logs", log_entry)
        await r.ltrim("equinox:punish:logs", 0, 9) # Chỉ giữ 10 log gần nhất
        
        color = COLORS["luminous_error"] if self.bot.user.id == LUMINOUS_ID else COLORS["tenebris_error"]
        
        if warns >= 3:
            # Đóng băng tài khoản
            await r.hset(f"equinox:user:{user.id}", "frozen", "TRUE")
            embed = discord.Embed(title="☠️ ĐÓNG BĂNG TÀI KHOẢN TOÀN CẦU!", color=0x8B0000)
            embed.description = f"<@{user.id}> đã thu thập đủ 3 gậy cảnh cáo. Tài khoản và ví Star đã bị niêm phong vĩnh viễn trên mọi mặt trận!"
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="⚠️ CẢNH CÁO THÀNH VIÊN", color=color)
            embed.description = f"<@{user.id}> đã bị phạt 1 gậy cảnh cáo. (Hiện tại: {warns}/3 gậy)\n📝 Lý do: {reason}"
            await ctx.send(embed=embed)

    # ==========================================
    # 🗃️ 2. TRA CỨU NHẬT KÝ HỘP ĐEN
    # ==========================================
    @commands.hybrid_command(name="log", aliases=["staff-auditlog"], description="[Admin+] Tra cứu 10 log trị an gần nhất")
    async def audit_log(self, ctx):
        if not await self.is_staff(ctx.author.id):
            return await ctx.send("🚫 Bạn không có quyền truy cập Hộp Đen!", ephemeral=True)
            
        r = await get_redis_connection()
        logs = await r.lrange("equinox:punish:logs", 0, 9)
        
        if not logs:
            return await ctx.send("🗃️ Hộp Đen hiện đang trống rỗng.")
            
        log_text = "\n".join(logs)
        embed = discord.Embed(title="🗃️ HỘP ĐEN: LỊCH SỬ TRỊ AN (10 Log Gần Nhất)", color=0xD3D3D3)
        embed.description = f"```ini\n{log_text}\n```"
        await ctx.send(embed=embed)

    # ==========================================
    # 🏛️ 3. XEM DANH SÁCH NHÂN SỰ ĐIỀU HÀNH
    # ==========================================
    @commands.hybrid_command(name="staff", description="Xem danh sách đội ngũ quản trị mạng lưới")
    async def staff_list(self, ctx):
        r = await get_redis_connection()
        owners = await r.smembers("equinox:staff:owners")
        devs = await r.smembers("equinox:staff:devs")
        admins = await r.smembers("equinox:staff:admins")
        ems = await r.smembers("equinox:staff:event_managers")
        mods = await r.smembers("equinox:staff:moderators")
        
        # Hàm format ID thành chuỗi tag
        format_list = lambda s: ", ".join([f"<@{i}>" for i in s]) if s else "Trống"
        
        if self.bot.user.id == LUMINOUS_ID:
            embed = discord.Embed(title="🏛️ TÒA THÁP THẦN ĐIỆN - DANH SÁCH NHÂN SỰ ĐIỀU HÀNH", color=COLORS["luminous_main"])
            embed.description = (
                f"Chào mừng cư dân đến với Thần Điện Equinox Network! Dưới đây là danh sách các thực thể đang nắm giữ mạch lệnh trị an và vận hành hệ thống:\n\n"
                f"👑 **Sếp Tổng (Owner):** {format_list(owners)} (Hạn ngạch: {len(owners)}/1)\n"
                f"⚙️ **Developer Tối Cao:** {format_list(devs)} (Hạn ngạch: {len(devs)}/2)\n"
                f"🏛️ **Quản Trị Viên (Admin):** {format_list(admins)} (Hạn ngạch: {len(admins)}/3)\n"
                f"⚡ **Quản Trị Sự Kiện (EM):** {format_list(ems)} (Hạn ngạch: {len(ems)}/2)\n"
                f"🪓 **Điều Phối Viên (Staff):** {format_list(mods)} (Hạn ngạch: {len(mods)}/10)\n\n"
                f"📌 Mọi hành vi lạm dụng quyền lực hoặc sai phạm nhân sự, cư dân vui lòng gửi trình đơn kèm bằng chứng trực tiếp lên Hội Đồng Tối Cao!"
            )
        else:
            embed = discord.Embed(title="🔒 SỔ ĐEN THẾ GIỚI NGẦM - ĐỘI NGŨ BẢO KÊ", color=COLORS["tenebris_main"])
            embed.description = (
                f"Xem cái gì mà xem? Định check xem đêm nay đứa nào bảo kê Chợ Đen để đi báo cáo Thần Điện à? Khôn hồn thì nhìn cho kỹ mấy cái tên máu mặt đứng sau Equinox Network đây này:\n\n"
                f"👑 **Trùm Cuối (Owner):** {format_list(owners)}\n"
                f"⚙️ **Đầu sỏ Code (Dev):** {format_list(devs)}\n"
                f"⛓️ **Bảo Kê Cấp Cao (Admin):** {format_list(admins)}\n"
                f"🚨 **Cai Quản Sòng Bạc (EM):** {format_list(ems)}\n"
                f"💀 **Đệ Tử Thực Địa (Staff):** {format_list(mods)}\n\n"
                f"💬 Đấy, có oan ức hay dính gậy warn dằn mặt thì tìm đúng người đòi ân xá. Đứa nào spam nhảm lệnh này tế thần ca đêm, tao xua Hội Sát Thủ xiên bay bóp tiền bây giờ!"
            )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StaffPunish(bot))
