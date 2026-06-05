import discord
from discord.ext import commands
from discord import app_commands
import json
import aiohttp

# ==============================================================================
# 🧰 HÀM TIỆN ÍCH DATABASE
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

def is_supreme_leader():
    def predicate(interaction: discord.Interaction) -> bool:
        data = load_db()
        sys_data = data.get("system", {})
        return interaction.user.id in [sys_data.get("owner_id"), sys_data.get("developer")]
    return app_commands.check(predicate)

# ==============================================================================
# 🌐 COG: MẠNG LƯỚI ĐỐI TÁC & WEBHOOK ENGINE
# ==============================================================================
class PartnerNetwork(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================================================
    # 🤝 LỆNH XIN GIA NHẬP LIÊN MINH (DÀNH CHO ADMIN SERVER NGOÀI)
    # ==========================================================================
    @app_commands.command(name="partner-request", description="[ADMIN SERVER] Xin gia nhập Liên minh Luminous")
    async def partner_req(self, interaction: discord.Interaction, broadcast_channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Chỉ Admin server mới có quyền ký khế ước liên minh!", ephemeral=True)

        data = load_db()
        partners = data.setdefault("system", {}).setdefault("partners", {})
        guild_id = str(interaction.guild.id)

        if guild_id in partners and partners[guild_id].get("status") == "verified":
            return await interaction.response.send_message("⚠️ Server này đã là đối tác chính thức rồi!", ephemeral=True)

        # 🤖 LÕI TỰ ĐỘNG ĐẺ WEBHOOK (Auto-Webhook Generator)
        try:
            webhook = await broadcast_channel.create_webhook(name="Luminous Gateway")
            
            partners[guild_id] = {
                "status": "pending", # Chờ Sếp duyệt
                "tier": "standard",  # Cấp độ mặc định
                "channel_id": broadcast_channel.id,
                "webhook_url": webhook.url,
                "custom_name": "📢 THÔNG TẤN XÃ LUMINOUS",
                "custom_avatar": None
            }
            save_db(data)
            
            await interaction.response.send_message(f"✅ **Đã gửi khế ước liên minh đến Nhà Chính!**\nTrạm thu phát sóng đã được thiết lập tại {broadcast_channel.mention}. Vui lòng chờ Owner duyệt để được kích hoạt kinh tế toàn cầu!", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot không có quyền `Manage Webhooks` tại kênh này để lắp đặt trạm phát sóng!", ephemeral=True)

    # ==========================================================================
    # 👑 LỆNH DUYỆT KHẾ ƯỚC TỪ NHÀ CHÍNH (DÀNH CHO OWNER/DEV)
    # ==========================================================================
    @app_commands.command(name="partner-approve", description="[OWNER/DEV] Duyệt server vào mạng lưới chính thức")
    @is_supreme_leader()
    async def partner_approve(self, interaction: discord.Interaction, guild_id: str):
        data = load_db()
        partners = data.get("system", {}).get("partners", {})
        
        if guild_id not in partners:
            return await interaction.response.send_message("❌ Không tìm thấy hồ sơ xin gia nhập của Server ID này!", ephemeral=True)
            
        partners[guild_id]["status"] = "verified"
        save_db(data)
        await interaction.response.send_message(f"🎉 Đã đóng dấu duyệt Server `{guild_id}` gia nhập Liên minh vĩ mô!", ephemeral=True)

    # ==========================================================================
    # 🌟 LỆNH SẮC PHONG VIP (UPGRADE TIER)
    # ==========================================================================
    @app_commands.command(name="partner-upgrade", description="[OWNER/DEV] Thăng hạng đặc quyền VIP cho Server Đối tác")
    @app_commands.choices(tier=[
        app_commands.Choice(name="✨ VIP Standard (Giảm thuế, Tăng chứng khoán)", value="vip_standard"),
        app_commands.Choice(name="👑 VIP Premium (Thuế 2%, AirDrop x1.5, Phế thầu -20%)", value="vip_premium")
    ])
    @is_supreme_leader()
    async def partner_upgrade(self, interaction: discord.Interaction, guild_id: str, tier: app_commands.Choice[str]):
        data = load_db()
        partners = data.get("system", {}).get("partners", {})
        
        if guild_id not in partners or partners[guild_id].get("status") != "verified":
            return await interaction.response.send_message("❌ Server này chưa được duyệt hoặc không tồn tại!", ephemeral=True)
            
        partners[guild_id]["tier"] = tier.value
        save_db(data)
        await interaction.response.send_message(f"🎖️ Đã sắc phong Server `{guild_id}` lên hàng **{tier.name}**!", ephemeral=True)

    # ==========================================================================
    # 🎨 LỆNH CUSTOM DIỆN MẠO WEBHOOK BIẾN HÌNH (DÀNH CHO VIP)
    # ==========================================================================
    @app_commands.command(name="partner-webhook", description="Tùy biến Tên và Avatar của Webhook phát sóng tại Server này")
    async def partner_webhook(self, interaction: discord.Interaction, name: str, avatar_url: str = None):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Lệnh dành riêng cho Admin Server!", ephemeral=True)

        data = load_db()
        partners = data.get("system", {}).get("partners", {})
        guild_id = str(interaction.guild.id)
        
        if guild_id not in partners or partners[guild_id].get("status") != "verified":
            return await interaction.response.send_message("❌ Server của bạn chưa phải là Đối tác chính thức!", ephemeral=True)
            
        tier = partners[guild_id].get("tier", "standard")
        if tier == "standard" and avatar_url:
            return await interaction.response.send_message("⚠️ Server Partner Thường chỉ được đổi Tên, không được đổi Avatar. Hãy xin thăng hạng VIP!", ephemeral=True)

        partners[guild_id]["custom_name"] = name
        if avatar_url and tier in ["vip_standard", "vip_premium"]:
            partners[guild_id]["custom_avatar"] = avatar_url
            
        save_db(data)
        await interaction.response.send_message(f"✅ Đã cấu hình diện mạo Webhook thành:\n> Tên: **{name}**", ephemeral=True)

    # ==========================================================================
    # 📡 LỆNH PHÁT SÓNG TOÀN CẦU (GLOBAL BROADCAST)
    # ==========================================================================
    @app_commands.command(name="partner-broadcast", description="[ADMIN/OWNER] Phóng tin tức khẩn cấp xuống toàn mạng lưới")
    async def partner_broadcast(self, interaction: discord.Interaction, title: str, message: str):
        data = load_db()
        sys_data = data.get("system", {})
        
        # Quyền hạn: Owner, Dev, Admin hệ thống mới được phát sóng
        user_id = interaction.user.id
        if user_id not in [sys_data.get("owner_id"), sys_data.get("developer")] and user_id not in sys_data.get("admins", []):
            return await interaction.response.send_message("❌ Bạn không có quyền truy cập Trạm Phát Sóng Toàn Cầu!", ephemeral=True)

        partners = sys_data.get("partners", {})
        verified_partners = {k: v for k, v in partners.items() if v.get("status") == "verified"}
        
        if not verified_partners:
            return await interaction.response.send_message("⚠️ Liên minh đang trống rỗng, không có server nào để phát sóng!", ephemeral=True)

        await interaction.response.defer(ephemeral=True) # Tránh bị timeout do gọi API nhiều

        # Đóng gói Embed bản tin
        embed = discord.Embed(title=f"🚨 {title}", description=message, color=discord.Color.red())
        embed.set_footer(text="Phát sóng từ Bộ Tư Lệnh Luminous Network")
        
        success_count = 0
        failed_count = 0

        # Lõi bắn Webhook đa luồng bất đồng bộ (Aiohttp)
        async with aiohttp.ClientSession() as session:
            for g_id, info in verified_partners.items():
                webhook_url = info.get("webhook_url")
                if not webhook_url: continue
                
                try:
                    webhook = discord.Webhook.from_url(webhook_url, session=session)
                    await webhook.send(
                        embed=embed,
                        username=info.get("custom_name", "Luminous Gateway"),
                        avatar_url=info.get("custom_avatar")
                    )
                    success_count += 1
                except discord.NotFound:
                    # LỖI WEBHOOK BỊ XÓA -> Đánh dấu hỏng để tự động heal sau
                    failed_count += 1
                except Exception as e:
                    failed_count += 1

        await interaction.followup.send(f"📡 **BÁO CÁO PHÁT SÓNG HOÀN TẤT:**\n✅ Thành công: `{success_count}` máy chủ.\n❌ Thất bại/Lỗi Webhook: `{failed_count}` máy chủ.")

    # ==========================================================================
    # 🚮 LỆNH TRỤC XUẤT ĐỐI TÁC (TERMINATE)
    # ==========================================================================
    @app_commands.command(name="partner-terminate", description="[OWNER/DEV] Đá một Server khỏi liên minh")
    @is_supreme_leader()
    async def partner_terminate(self, interaction: discord.Interaction, guild_id: str):
        data = load_db()
        partners = data.get("system", {}).get("partners", {})
        
        if guild_id in partners:
            del partners[guild_id]
            save_db(data)
            await interaction.response.send_message(f"🚮 Đã thanh trừng máy chủ `{guild_id}`. Xóa bỏ hoàn toàn liên kết và trạm phát sóng!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Không tìm thấy máy chủ này trong sổ xưng thần!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PartnerNetwork(bot))
