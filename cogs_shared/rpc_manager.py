import os
import datetime
import pytz
import json
import discord
from discord import app_commands
from discord.ext import commands
from database.redis_client import get_redis_connection # Hàm kết nối Redis có sẵn của sếp

class EquinoxRPCManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tz = pytz.timezone("Asia/Ho_Chi_Minh")

    # ========================================================================
    # 🏰 LỆNH ĐẶT NHÀ CHÍNH (Chỉ dành riêng cho OWNER tối cao)
    # ========================================================================
    @app_commands.command(name="set_nhachinh", description="[OWNER] Thiết lập Link mời của Tổng Hành Dinh (Nhà Chính) hệ thống")
    @app_commands.describe(link_invite="Đường dẫn invite của Server Nhà Chính (Ví dụ: https://discord.gg/xxxx)")
    async def set_main_hq(self, interaction: discord.Interaction, link_invite: str):
        await interaction.response.defer(ephemeral=True)

        # 👑 Thọc bộ lọc check Owner tối cao bọc lót qua biến môi trường
        owner_id = int(os.getenv("OWNER_ID", 0))
        if interaction.user.id != owner_id:
            await interaction.followup.send("🚨 *Trục xuất thần thức:* Lệnh này là đại quyền tối cao của Thực Thể Sáng Tạo!", ephemeral=True)
            return

        if not link_invite.startswith("https://discord.gg/") and not link_invite.startswith("https://discord.com/invite/"):
            await interaction.followup.send("⚠️ Định dạng link mời Discord không hợp lệ!", ephemeral=True)
            return

        r = await get_redis_connection()
        # Găm cứng link nhà chính toàn hệ thống vào Redis
        await r.set("equinox:system:main_guild_invite", link_invite)

        await interaction.followup.send(f"🏰 Đã đồng bộ Linh Mạch! Trục tọa độ Tổng Hành Dinh (Nhà Chính) hiện tại được găm về: `{link_invite}`", ephemeral=True)


    # ========================================================================
    # ⚙️ LỆNH THIẾT LẬP TRẠNG THÁI (SLASH COMMAND HYBRID / USER APP)
    # ========================================================================
    @app_commands.command(name="status", description="Cấu hình chuyên sâu diện mạo Rich Presence găm thẳng vào Profile Discord thật")
    @app_commands.contexts(guild=True, dm_channel=True, private_channel=True) # Mở rộng không gian gọi lệnh
    @app_commands.integration_types(guild_install=True, user_install=True)   # Cho phép cài thẳng vào Account cá nhân
    @app_commands.describe(
        action="Hành động thiết lập trạng thái",
        loai_hoat_dong="Loại hoạt động ảo (Bỏ trống nếu xài Fallback tối giản)",
        noi_dung="Nội dung tùy biến chữ (Bỏ trống nếu xài Fallback tối giản)",
        pham_vi="Phạm vi áp dụng kho dữ liệu"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add (Kích hoạt / Cập nhật trạng thái)", value="add"),
        app_commands.Choice(name="Clear (Xóa sạch trạng thái ảo)", value="clear")
    ])
    @app_commands.choices(loai_hoat_dong=[
        app_commands.Choice(name="Đang chơi...", value="playing"),
        app_commands.Choice(name="Đang xem...", value="watching"),
        app_commands.Choice(name="Đang nghe...", value="listening"),
        app_commands.Choice(name="Đang phát trực tiếp...", value="streaming")
    ])
    @app_commands.choices(pham_vi=[
        app_commands.Choice(name="Server (Chỉ hiển thị tại không gian server này)", value="server"),
        app_commands.Choice(name="Account (Áp dụng toàn cầu trên mọi ma trận)", value="account")
    ])
    async def manage_status(
        self, 
        interaction: discord.Interaction, 
        action: app_commands.Choice[str],
        loai_hoat_dong: app_commands.Choice[str] = None,
        noi_dung: str = None,
        pham_vi: app_commands.Choice[str] = None
    ):
        await interaction.response.defer()
        
        r = await get_redis_connection()
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id) if interaction.guild else "dm"
        
        # Mặc định pham_vi là account nếu user lười không chọn
        target_scope = pham_vi.value if pham_vi else "account"
        
        # Xác định chính xác Hash Key dựa trên tham số pham_vi sếp yêu cầu
        if target_scope == "server" and guild_id != "dm":
            redis_key = f"equinox:user:{user_id}:guild:{guild_id}:profile"
            scope_desc = "tại Server này"
        else:
            redis_key = f"equinox:user:{user_id}:global:profile"
            scope_desc = "trên toàn bộ tài khoản cá nhân"

        # ========================================================================
        # ❌ XỬ LÝ LỆNH CLEAR STATUS
        # ========================================================================
        if action.value == "clear":
            await r.delete(redis_key)
            embed = discord.Embed(
                title="🌌 ĐỒNG BỘ LẠI DIỆN MẠO",
                description=f"Hệ thống đã xóa sạch cấu hình trạng thái ảo {scope_desc}.\nProfile thật của bạn sẽ tự động quay về chế độ quét thông thường.",
                color=0x36393F
            )
            await interaction.followup.send(embed=embed)
            return

        # ========================================================================
        # ⚡ XỬ LÝ LỆNH ADD STATUS (Có bọc lót mạch Fallback khi gõ enter trống)
        # ========================================================================
        # Lấy link nhà chính từ Redis, nếu chưa có thì bốc tạm biến môi trường làm bệ đỡ
        main_hq_invite = await r.get("equinox:system:main_guild_invite")
        if main_hq_invite:
            main_hq_invite = main_hq_invite.decode("utf-8")
        else:
            main_hq_invite = os.getenv("MAIN_GUILD_INVITE", "https://discord.gg/equinox")

        luminous_invite = os.getenv("LUMINOUS_INVITE_URL", "https://discord.com")
        tenebris_invite = os.getenv("TENEBRIS_INVITE_URL", "https://discord.com")

        # 🕵️ MẠCH KHỞI CHẠY FALLBACK TỐI GIẢN (Khi user chỉ gõ /status add và Enter)
        if not loai_hoat_dong and not noi_dung:
            now_vn = datetime.datetime.now(self.tz)
            fallback_text = now_vn.strftime("⏰ %H:%M | %d/%m/%Y")
            
            # Đóng gói cấu trúc layout Rich Presence phẳng
            rpc_data = {
                "app_name": "Equinox Network",       # Găm cứng tên app ở giữa
                "status_text": fallback_text,        # Ô chữ trạng thái hiện giờ giấc tự động
                "activity_type": "custom",           # Ép kiểu custom status
                "buttons": [                         # Dàn 3 nút bất tử bên dưới
                    {"label": "☀️ Mời Thần Quan Luminous", "url": luminous_invite},
                    {"label": "🔮 Mời Chúa Tể Tenebris", "url": tenebris_invite},
                    {"label": "🏰 Equinox Network", "url": main_hq_invite}
                ]
            }
            
            await r.set(redis_key, json.dumps(rpc_data))
            
            embed = discord.Embed(
                title="🌌 THAO TÚNG ĐỊNH DẠNG TỐI GIẢN",
                description=f"Kích hoạt thành công diện mạo Fallback {scope_desc}!",
                color=0x00FFFF
            )
            embed.add_field(name="💬 Trạng thái hiện tại", value=fallback_text, inline=False)
            embed.add_field(name="🔗 Liên kết găm kèm", value="• ☀️ Luminous Invite\n• 🔮 Tenebris Invite\n• 🏰 Equinox Network (Nhà Chính)", inline=False)
            await interaction.followup.send(embed=embed)
            
        # 🛠️ TRƯỜNG HỢP USER ĐỘ CHUYÊN SÂU (Có điền tham số loại và nội dung)
        else:
            act_type = loai_hoat_dong.value if loai_hoat_dong else "custom"
            act_name = noi_dung if noi_dung else "Đang lẩn trốn ma trận"
            
            rpc_data = {
                "app_name": "Equinox Network",
                "status_text": act_name,
                "activity_type": act_type,
                "buttons": [
                    {"label": "☀️ Mời Thần Quan Luminous", "url": luminous_invite},
                    {"label": "🔮 Mời Chúa Tể Tenebris", "url": tenebris_invite},
                    {"label": "🏰 Equinox Network", "url": main_hq_invite}
                ]
            }
            
            await r.set(redis_key, json.dumps(rpc_data))
            
            act_desc_map = {"playing": "Đang chơi", "watching": "Đang xem", "listening": "Đang nghe", "streaming": "Đang live", "custom": ""}
            display_prefix = act_desc_map.get(act_type, "")
            
            embed = discord.Embed(
                title="🌌 ĐỘ PROFILE CHUYÊN SÂU SUÔN SẺ",
                description=f"Đồng bộ cấu hình trang phục ảo {scope_desc} thành công!",
                color=0x9900FF
            )
            embed.add_field(name="🕹️ Diện mạo hiển thị", value=f"**Equinox Network**\n{display_prefix} {act_name}", inline=False)
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EquinoxRPCManager(bot))
