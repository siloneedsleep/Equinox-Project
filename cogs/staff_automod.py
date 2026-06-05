import discord
from discord.ext import commands
from discord import app_commands
import json
import time
import re
from collections import defaultdict
import datetime

# ==============================================================================
# 🧰 HÀM TIỆN ÍCH & XÁC THỰC QUYỀN LỰC
# ==============================================================================
def load_db():
    try:
        with open("storage.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(data):
    with open("storage.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def is_staff_or_higher(user_id, data):
    sys_data = data.get("system", {})
    if user_id in [sys_data.get("owner_id"), sys_data.get("developer")]: return True
    if user_id in sys_data.get("admins", []): return True
    if user_id in sys_data.get("staffs", []): return True
    return False

# ==============================================================================
# ⚖️ GIAO DIỆN NÚT BẤM DUYỆT ÂN XÁ (GỬI VÀO DMs OWNER)
# ==============================================================================
class UnblacklistApprovalView(discord.ui.View):
    def __init__(self, target_id, bot):
        super().__init__(timeout=None) # Lệnh của sếp không bao giờ hết hạn
        self.target_id = target_id
        self.bot = bot

    @discord.ui.button(label="✅ Duyệt Ân Xá", style=discord.ButtonStyle.success)
    async def btn_approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_db()
        users = data.get("users", {})
        target_str = str(self.target_id)
        
        if target_str in users:
            users[target_str]["blacklisted"] = False
            users[target_str]["warns"] = 0 # Xóa án tích
            save_db(data)
            
        await interaction.response.edit_message(content=f"✅ Sếp Tổng đã ký lệnh ân xá cho ID `{self.target_id}`. Đã mở khóa ví Star và dọn dẹp án tích!", embed=None, view=None)

    @discord.ui.button(label="❌ Từ Chối", style=discord.ButtonStyle.danger)
    async def btn_deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"❌ Sếp Tổng đã từ chối ân xá cho ID `{self.target_id}`. Tiếp tục giam giữ!", embed=None, view=None)

# ==============================================================================
# 🛡️ COG: QUẢN LÝ KỶ LUẬT & AUTOMOD LÕI CỨNG
# ==============================================================================
class StaffAutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # In-Memory Cache để xử lý Spam siêu tốc (Chỉ dùng RAM, không ghi JSON)
        self.spam_cache = defaultdict(list)
        # Regex Biểu thức chính quy cản phá mồm độc (Sếp có thể tự add thêm sau)
        self.invite_regex = re.compile(r"(discord\.gg/|discordapp\.com/invite/)", re.IGNORECASE)
        self.banned_words = re.compile(r"(l[oòóỏõọôồốổỗộơờớởỡợ]+[n|z]|c[aàáảãạăằắẳẵặâầấẩẫậ]+[c]|đ[iìíỉĩị]+[t])", re.IGNORECASE)

    # ==========================================================================
    # 🚨 LÕI QUÉT TIN NHẮN TỰ ĐỘNG (IN-MEMORY ENGINE)
    # ==========================================================================
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return

        data = load_db()
        # Nếu là Staff trở lên -> Được quyền vượt tường lửa AutoMod
        if is_staff_or_higher(message.author.id, data): return

        # 1. Quét Link Mời Server (Anti-Invite)
        if self.invite_regex.search(message.content):
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention} Tội phạm bị bắt quả tang! Chống lôi kéo member dưới mọi hình thức!", delete_after=5)
            return

        # 2. Quét Mass Mention (Ping trên 4 người 1 tin)
        if len(message.mentions) > 4:
            await message.delete()
            try:
                # Phạt thẻ đỏ: Tịch thu mồm 10 phút
                await message.author.timeout(datetime.timedelta(minutes=10), reason="AutoMod: Mass Mention (Spam Ping)")
                await message.channel.send(f"🔨 {message.author.mention} đã bị dán băng keo vào mồm 10 phút vì Ping quá nhiều người cùng lúc!")
            except discord.Forbidden:
                pass
            return

        # 3. Quét Từ Cấm (Banned Words)
        if self.banned_words.search(message.content):
            await message.delete()
            await message.channel.send(f"🤬 {message.author.mention} Ngôn từ thô tục đã bị rếch lại! Gõ đàng hoàng lại xem nào.", delete_after=3)
            return

        # 4. Quét Tốc Độ Spam (5 tin / 3 giây)
        user_id = message.author.id
        now = time.time()
        
        # Lọc những tin nhắn trong vòng 3 giây qua
        self.spam_cache[user_id] = [t for t in self.spam_cache[user_id] if now - t < 3.0]
        self.spam_cache[user_id].append(now)

        if len(self.spam_cache[user_id]) >= 5:
            await message.delete()
            try:
                # Cách ly Timeout 5 phút tự động
                await message.author.timeout(datetime.timedelta(minutes=5), reason="AutoMod: Spam tin nhắn")
                await message.channel.send(f"🚨 {message.author.mention} Đã bị cách ly 5 phút vì chat quá nhanh gây nghẽn mạch mạng lưới!")
            except discord.Forbidden:
                pass
            # Xóa cache để khỏi bị phạt đè
            self.spam_cache[user_id].clear()

    # ==========================================================================
    # 🔨 LỆNH KỶ LUẬT NHANH (STAFF WARN)
    # ==========================================================================
    @commands.command(name="staff-warn", aliases=["warn"])
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Không có lý do cụ thể."):
        data = load_db()
        if not is_staff_or_higher(ctx.author.id, data):
            return await ctx.send("❌ Bạn không thuộc Lực lượng Trị An Luminous!")
            
        if is_staff_or_higher(member.id, data):
            return await ctx.send("❌ Hỗn xược! Sao dám bắt bớ cả cán bộ?")

        users = data.setdefault("users", {})
        target_str = str(member.id)
        if target_str not in users:
            users[target_str] = {"cash": 0, "bank": 0, "warns": 0}
            
        # Tăng gậy cảnh cáo
        users[target_str]["warns"] = users[target_str].get("warns", 0) + 1
        warn_count = users[target_str]["warns"]
        
        # Ghi log mờ ám cho Hộp đen
        sys_data = data.setdefault("system", {})
        audit_logs = sys_data.setdefault("audit_logs", [])
        audit_logs.append(f"[{time.strftime('%Y-%m-%d %H:%M')}] Cán bộ {ctx.author.name} phạt gậy {member.name} | Lý do: {reason}")
        if len(audit_logs) > 50: audit_logs.pop(0) # Giữ lại 50 log gần nhất
        
        # LOGIC XỬ LÝ 3 GẬY -> BLACKLIST
        if warn_count >= 3:
            users[target_str]["blacklisted"] = True
            save_db(data)
            embed = discord.Embed(title="☠️ ĐÓNG BĂNG TÀI KHOẢN TOÀN CẦU!", color=discord.Color.dark_red())
            embed.description = f"{member.mention} đã thu thập đủ 3 gậy cảnh cáo. Tài khoản và ví Star (⭐) đã bị niêm phong vĩnh viễn trên mọi mặt trận!"
            return await ctx.send(embed=embed)
            
        save_db(data)
        await ctx.send(f"⚠️ {member.mention} đã nhận một gậy cảnh báo! (Án tích: **{warn_count}/3**)\n> 📝 Lý do: `{reason}`")

    # ==========================================================================
    # ⚖️ LỆNH NỘP ĐƠN XIN ÂN XÁ (DÀNH CHO STAFF CẤP CỨU)
    # ==========================================================================
    @app_commands.command(name="staff-unblacklist", description="[STAFF] Trình đơn xin ân xá cho tài khoản bị khóa lên Sếp Tổng")
    async def unblacklist(self, interaction: discord.Interaction, target_id: str, reason: str):
        data = load_db()
        if not is_staff_or_higher(interaction.user.id, data):
            return await interaction.response.send_message("❌ Bạn không có quyền đệ đơn ân xá!", ephemeral=True)

        users = data.get("users", {})
        if target_id not in users or not users[target_id].get("blacklisted", False):
            return await interaction.response.send_message("⚠️ Người này có bị khóa tài khoản đâu mà xin ân xá?", ephemeral=True)

        # Trích xuất ID Sếp Tổng và gửi DMs
        owner_id = data.get("system", {}).get("owner_id")
        if not owner_id:
            owner_id = self.bot.owner_id
            
        try:
            owner = await self.bot.fetch_user(owner_id)
            embed = discord.Embed(title="📩 ĐƠN XIN ÂN XÁ KHẨN CẤP", color=discord.Color.yellow())
            embed.add_field(name="Từ Cán Bộ Trị An", value=f"{interaction.user.mention} (ID: {interaction.user.id})", inline=False)
            embed.add_field(name="Xin thả cho User ID", value=f"`{target_id}`", inline=False)
            embed.add_field(name="Lý do & Lời biện hộ", value=f"*{reason}*", inline=False)
            
            view = UnblacklistApprovalView(target_id, self.bot)
            await owner.send(embed=embed, view=view)
            
            await interaction.response.send_message("✅ Đơn ân xá đã được bay thẳng vào DMs của Sếp Tổng. Hãy chờ sếp duyệt!", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Sếp Tổng đang khóa DMs nên không thể gửi đơn xin ân xá được!", ephemeral=True)

    # ==========================================================================
    # 🗃️ LỆNH TRA CỨU HỘP ĐEN (AUDIT LOGS)
    # ==========================================================================
    @commands.command(name="staff-auditlog", aliases=["log"])
    async def auditlog(self, ctx):
        data = load_db()
        # Lệnh này chỉ dành cho Admin và Sếp
        sys_data = data.get("system", {})
        if ctx.author.id not in [sys_data.get("owner_id"), sys_data.get("developer")] and ctx.author.id not in sys_data.get("admins", []):
            return await ctx.send("❌ Mật vụ cấp Admin trở lên mới được phép xem Hộp Đen!")

        logs = sys_data.get("audit_logs", [])
        if not logs:
            return await ctx.send("🗄️ Hộp đen hiện đang trống rỗng, không có lịch sử trị an nào!")
            
        # In ra 10 dòng log gần nhất
        log_text = "\n".join(logs[-10:])
        embed = discord.Embed(title="🗃️ HỘP ĐEN: LỊCH SỬ TRỊ AN (10 Log Gần Nhất)", description=f"```ini\n{log_text}\n```", color=discord.Color.light_grey())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StaffAutoMod(bot))
