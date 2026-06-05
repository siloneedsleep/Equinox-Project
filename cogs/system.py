import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import time

# ==============================================================================
# 🧰 HÀM TIỆN ÍCH: ĐỌC & GHI DATABASE AN TOÀN
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

# Hàm kiểm tra quyền tối cao (Chỉ Owner và Dev)
def is_supreme_leader():
    def predicate(interaction: discord.Interaction) -> bool:
        data = load_db()
        sys_data = data.get("system", {})
        owner_id = sys_data.get("owner_id")
        dev_id = sys_data.get("developer")
        
        # Nếu chưa cấu hình Owner ID trong json, lấy từ Discord bot owner
        if not owner_id:
            owner_id = interaction.client.owner_id
            
        if interaction.user.id in [owner_id, dev_id]:
            return True
        return False
    return app_commands.check(predicate)

# ==============================================================================
# 👑 COG QUẢN TRỊ HỆ THỐNG VĨ MÔ
# ==============================================================================
class SystemAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_boot_task.start() # Khởi động Task đếm ngược mở khóa bảo trì

    def cog_unload(self):
        self.auto_boot_task.cancel()

    # ⏳ TASK NGẦM: KIỂM TRA THỜI GIAN BẢO TRÌ ĐỂ TỰ ĐỘNG BẬT BOT
    @tasks.loop(seconds=30)
    async def auto_boot_task(self):
        data = load_db()
        sys_data = data.get("system", {})
        
        if sys_data.get("maintenance", False) and sys_data.get("maintenance_until"):
            if time.time() >= sys_data["maintenance_until"]:
                # Đã hết thời gian bảo trì -> Tự động Boot
                sys_data["maintenance"] = False
                sys_data["maintenance_until"] = None
                save_db(data)
                
                # Khôi phục diện mạo
                s_map = {"online": discord.Status.online, "idle": discord.Status.idle, "dnd": discord.Status.dnd}
                saved_status = sys_data.get("bot_settings", {}).get("saved_status", "online")
                act_text = sys_data.get("bot_settings", {}).get("activity_text", "Luminous Network ⭐")
                await self.bot.change_presence(status=s_map.get(saved_status, discord.Status.online), activity=discord.Game(act_text))
                print("🟢 [AUTO-BOOT] Đã tự động mở khóa hệ thống sau thời gian bảo trì ngầm!")

    @auto_boot_task.before_loop
    async def before_auto_boot(self):
        await self.bot.wait_until_ready()

    # ==============================================================================
    # 🛑 LỆNH ĐÓNG BĂNG MẠNG LƯỚI ẢO (SHUTDOWN)
    # ==============================================================================
    @app_commands.command(name="system-shutdown", description="[OWNER/DEV] Bật khiên bảo trì, đóng băng toàn bộ giao dịch mạng lưới")
    @app_commands.describe(reason="Lý do bảo trì", duration="Thời gian bảo trì (Phút). Để trống là tắt vô hạn.")
    @is_supreme_leader()
    async def sys_shutdown(self, interaction: discord.Interaction, reason: str, duration: int = None):
        data = load_db()
        if "system" not in data: data["system"] = {}
        
        until_time = int(time.time() + (duration * 60)) if duration else None
        
        data["system"]["maintenance"] = True
        data["system"]["maintenance_reason"] = reason
        data["system"]["maintenance_until"] = until_time
        save_db(data)

        # Chuyển Bot sang chế độ Đỏ (DND)
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game("⚠️ HỆ THỐNG ĐANG BẢO TRÌ"))
        
        time_msg = f"trong **{duration} phút**." if duration else "**vô thời hạn**."
        await interaction.response.send_message(f"🔒 **Bật Khiên Bảo Trì Thành Công!**\n> 📝 Lý do: `{reason}`\n> ⏳ Thời gian: {time_msg}\n*Tất cả dân đen hiện tại gọi lệnh sẽ bị chặn đứng.*", ephemeral=True)

    # ==============================================================================
    # 🟢 LỆNH KHỞI ĐỘNG LẠI (BOOT)
    # ==============================================================================
    @app_commands.command(name="system-boot", description="[OWNER/DEV] Khởi động lại hệ thống, mở khóa lệnh")
    @is_supreme_leader()
    async def sys_boot(self, interaction: discord.Interaction):
        data = load_db()
        if "system" in data:
            data["system"]["maintenance"] = False
            data["system"]["maintenance_until"] = None
            save_db(data)
            
        # Khôi phục trạng thái
        bot_settings = data.get("system", {}).get("bot_settings", {})
        s_map = {"online": discord.Status.online, "idle": discord.Status.idle, "dnd": discord.Status.dnd}
        await self.bot.change_presence(
            status=s_map.get(bot_settings.get("saved_status", "online"), discord.Status.online),
            activity=discord.Game(bot_settings.get("activity_text", "Luminous Network ⭐"))
        )
        
        await interaction.response.send_message("🔓 **Đã gỡ bỏ Khiên Bảo Trì!** Hệ thống mạng lưới đã hoạt động trở lại bình thường.", ephemeral=True)

    # ==============================================================================
    # 🏛️ LỆNH SẮC PHONG NHÀ CHÍNH (HQ)
    # ==============================================================================
    @app_commands.command(name="system-hq", description="[OWNER/DEV] Thiết lập Máy chủ hiện tại làm Nhà Chính (Miễn thuế 100%)")
    @is_supreme_leader()
    async def sys_hq(self, interaction: discord.Interaction):
        data = load_db()
        if "system" not in data: data["system"] = {}
        
        data["system"]["hq_guild_id"] = interaction.guild.id
        save_db(data)
        await interaction.response.send_message(f"🏰 Đã đóng dấu sắc phong **{interaction.guild.name}** làm Nhà Chính Tối Cao!", ephemeral=True)

    # ==============================================================================
    # 🛡️ LỆNH QUẢN TRỊ NHÂN SỰ GẮN SLOT
    # ==============================================================================
    @app_commands.command(name="system-staff", description="[OWNER] Quản lý nhân sự mạng lưới")
    @app_commands.choices(role_type=[
        app_commands.Choice(name="💻 Lập Trình Viên (Dev) - 1 Slot", value="developer"),
        app_commands.Choice(name="💼 Quản Trị Viên (Admin) - 3 Slots", value="admins"),
        app_commands.Choice(name="🛡️ Điều Phối Viên (Staff) - 10 Slots", value="staffs")
    ])
    async def sys_staff(self, interaction: discord.Interaction, action: discord.app_commands.Choice[int], user: discord.User, role_type: app_commands.Choice[str]):
        # Chặn cứng: Chỉ Owner (Sếp) mới được bổ nhiệm, Dev không được phép xài lệnh này
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Hỗn xược! Chỉ Sếp Tổng (Owner) mới được quyền sắc phong nhân sự!", ephemeral=True)
            return

        data = load_db()
        sys_data = data.setdefault("system", {})
        sys_data.setdefault("admins", [])
        sys_data.setdefault("staffs", [])

        action_val = action.name # add hoặc remove
        r_val = role_type.value

        if action_val == "add":
            if r_val == "developer":
                sys_data["developer"] = user.id
            elif r_val == "admins":
                if len(sys_data["admins"]) >= 3:
                    return await interaction.response.send_message("❌ Slot Admin đã đầy (Tối đa 3). Vui lòng phế truất người cũ trước!", ephemeral=True)
                if user.id not in sys_data["admins"]: sys_data["admins"].append(user.id)
            elif r_val == "staffs":
                if len(sys_data["staffs"]) >= 10:
                    return await interaction.response.send_message("❌ Slot Staff đã đầy (Tối đa 10).", ephemeral=True)
                if user.id not in sys_data["staffs"]: sys_data["staffs"].append(user.id)
            
            save_db(data)
            await interaction.response.send_message(f"✅ Đã sắc phong chức vụ **{role_type.name}** cho {user.mention}!", ephemeral=True)

        elif action_val == "remove":
            if r_val == "developer":
                sys_data["developer"] = None
            elif r_val == "admins" and user.id in sys_data["admins"]:
                sys_data["admins"].remove(user.id)
            elif r_val == "staffs" and user.id in sys_data["staffs"]:
                sys_data["staffs"].remove(user.id)
                
            save_db(data)
            await interaction.response.send_message(f"🚮 Đã phế truất {user.mention} khỏi chức vụ **{role_type.name}**!", ephemeral=True)

    @sys_staff.autocomplete('action')
    async def action_autocomplete(self, interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name="add", value=1), app_commands.Choice(name="remove", value=2)]

    # ==============================================================================
    # 🧠 LỆNH QUẢN LÝ KHO KEY AI ĐA NỀN TẢNG (AI VAULT)
    # ==============================================================================
    @app_commands.command(name="system-addkey", description="[OWNER/DEV] Nạp API Key AI vào kho chứa bí mật")
    @app_commands.choices(provider=[
        app_commands.Choice(name="OpenAI (ChatGPT)", value="openai"),
        app_commands.Choice(name="Google (Gemini)", value="gemini"),
        app_commands.Choice(name="Anthropic (Claude)", value="claude"),
        app_commands.Choice(name="Groq (Tốc độ siêu tốc)", value="groq")
    ])
    @is_supreme_leader()
    async def add_ai_key(self, interaction: discord.Interaction, provider: app_commands.Choice[str], api_key: str):
        data = load_db()
        sys_data = data.setdefault("system", {})
        vault = sys_data.setdefault("ai_vault", {})
        
        # Lưu vào kho
        vault[provider.value] = api_key
        save_db(data)
        
        await interaction.response.send_message(f"🔐 Đã nạp thành công Key sinh mệnh cho **{provider.name}** vào Kho bảo mật Luminous!", ephemeral=True)

    @app_commands.command(name="system-listkeys", description="[OWNER/DEV] Xem danh sách các mỏ Key AI đang hoạt động")
    @is_supreme_leader()
    async def list_ai_keys(self, interaction: discord.Interaction):
        data = load_db()
        vault = data.get("system", {}).get("ai_vault", {})
        
        if not vault:
            return await interaction.response.send_message("텅 Kho Key AI hiện đang trống rỗng!", ephemeral=True)
            
        msg = "🗄️ **KHO LƯU TRỮ API KEY AI (ĐÃ MÃ HÓA)**\n\n"
        for prov, key in vault.items():
            # Mã hóa che key (Ví dụ: sk-proj-12345...XYZ -> sk-proj-***...***XYZ)
            masked_key = f"{key[:7]}...[ĐÃ CHE]...{key[-4:]}" if len(key) > 15 else "[KEY QUÁ NGẮN HOẶC LỖI]"
            msg += f"🔹 **{prov.upper()}**: `{masked_key}`\n"
            
        await interaction.response.send_message(msg, ephemeral=True)

# Nạp Cog vào Bot
async def setup(bot):
    await bot.add_cog(SystemAdmin(bot))
