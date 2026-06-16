import discord
from discord.ext import commands
from discord import app_commands
import datetime

from config.settings import LUMINOUS_ID, COLORS
from database.redis_client import get_redis_connection

class ProfileSys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # 🪪 1. XEM HỒ SƠ CÁ NHÂN (PROFILE)
    # ==========================================
    @commands.hybrid_command(name="profile", aliases=["pf"], description="Xem thẻ căn cước / hồ sơ cá nhân")
    @app_commands.describe(user="Chọn người muốn xem hồ sơ")
    async def view_profile(self, ctx, user: discord.Member = None):
        target = user or ctx.author
        r = await get_redis_connection()
        user_key = f"equinox:user:{target.id}"
        
        # 1. Bốc toàn bộ dữ liệu từ Redis
        data = await r.hgetall(user_key)
        clean_bal = int(data.get("balance_clean", 0))
        bank_saving = int(data.get("bank_saving", 0))
        dirty_bal = int(data.get("balance_dirty", 0))
        danger_level = int(data.get("danger_level", 0))
        partner_id = data.get("partner_id")
        ring_type = data.get("ring_type")
        
        # 2. Check Chức Vụ Ngầm (SISMEMBER)
        role_title = None
        if await r.sismember("equinox:staff:owners", str(target.id)):
            role_title = "Sếp Tổng (Owner)" if self.bot.user.id == LUMINOUS_ID else "Trùm Cuối (Owner)"
        elif await r.sismember("equinox:staff:devs", str(target.id)):
            role_title = "Nhà Phát Triển (Dev)" if self.bot.user.id == LUMINOUS_ID else "Đầu Sỏ Code (Dev)"
        elif await r.sismember("equinox:staff:admins", str(target.id)):
            role_title = "Quản Trị Viên (Admin)" if self.bot.user.id == LUMINOUS_ID else "Bảo Kê Cấp Cao (Admin)"
        elif await r.sismember("equinox:staff:event_managers", str(target.id)):
            role_title = "Quản Trị Sự Kiện (EM)" if self.bot.user.id == LUMINOUS_ID else "Cai Quản Sòng Bạc (EM)"
        elif await r.sismember("equinox:staff:moderators", str(target.id)):
            role_title = "Điều Phối Viên (Staff)" if self.bot.user.id == LUMINOUS_ID else "Đệ Tử Thực Địa (Staff)"

        # 3. Phân nhánh hiển thị theo Bot
        if self.bot.user.id == LUMINOUS_ID:
            # GIAO DIỆN LUMINOUS (Văn minh, Hoàng gia)
            color = COLORS["luminous_love"] if role_title else COLORS["luminous_info"]
            embed = discord.Embed(title="💳 THẺ CƯ DÂN EQUINOX NETWORK", color=color)
            embed.set_thumbnail(url=target.display_avatar.url)
            
            desc = f"Tên cư dân: <@{target.id}>\n"
            if role_title:
                desc += f"👑 **Chức vụ:** {role_title}\n"
                
            desc += f"\n🪙 **Ví tiền mặt (Aequor):** {clean_bal:,} Star\n"
            desc += f"🏦 **Ngân hàng tiết kiệm:** {bank_saving:,} Star\n"
            
            if partner_id:
                desc += f"💞 **Khế ước phu thê:** Đã kết hôn với <@{partner_id}> ({ring_type.capitalize() if ring_type else 'Chưa rõ'})\n"
            else:
                desc += f"💞 **Khế ước phu thê:** Chưa kết hôn\n"
                
            embed.description = desc

        else:
            # GIAO DIỆN TENEBRIS (Hắc ám, Giang hồ)
            embed = discord.Embed(title="💀 HỒ SƠ TỘI PHẠM CHỢ ĐEN", color=COLORS["tenebris_main"])
            embed.set_thumbnail(url=target.display_avatar.url)
            
            desc = f"Đối tượng: <@{target.id}>\n"
            if role_title:
                desc += f"⛓️ **Danh tính ngầm:** {role_title}\n"
                
            desc += f"\n🚨 **Tiền bẩn tích trữ (Aequis):** {dirty_bal:,} Star\n"
            
            danger_title = "Dân Thường"
            if danger_level > 50: danger_title = "Sát Thủ Máu Lạnh"
            elif danger_level > 20: danger_title = "Đầu Gấu Chợ Đen"
            elif danger_level > 5: danger_title = "Lưu Manh Thôn"
            
            desc += f"🩸 **Mức độ nguy hiểm:** {danger_title} (Điểm: {danger_level})\n"
            
            if partner_id:
                desc += f"🔒 **Trạng thái phu thê:** Đã bị xích bởi <@{partner_id}>\n"
                
            embed.description = desc

        await ctx.send(embed=embed)

    # ==========================================
    # 🐳 2. BẢNG XẾP HẠNG TỶ PHÚ (LEADERBOARD)
    # ==========================================
    @commands.hybrid_command(name="leaderboard", aliases=["top"], description="Xem bảng xếp hạng phú hào toàn mạng lưới")
    async def leaderboard(self, ctx):
        r = await get_redis_connection()
        
        # Quét toàn bộ user để tính tổng tài sản
        # Lưu ý: Trong thực tế với DB lớn, nên dùng Sorted Set (ZSET) trên Redis để update real-time thay vì quét KEYS
        cursor = 0
        users_wealth = []
        
        while True:
            cursor, keys = await r.scan(cursor, match="equinox:user:*", count=100)
            for key in keys:
                user_id = key.split(":")[-1]
                data = await r.hgetall(key)
                
                clean = int(data.get("balance_clean", 0))
                bank = int(data.get("bank_saving", 0))
                dirty = int(data.get("balance_dirty", 0))
                
                total = clean + bank + dirty
                if total > 0:
                    users_wealth.append({
                        "id": user_id,
                        "total": total,
                        "clean": clean + bank,
                        "dirty": dirty
                    })
            
            if cursor == 0:
                break
                
        # Sắp xếp từ cao xuống thấp và lấy top 10
        users_wealth.sort(key=lambda x: x["total"], reverse=True)
        top_10 = users_wealth[:10]
        
        if not top_10:
            return await ctx.send("Vương quốc hiện tại chưa có ai có tiền!")

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        if self.bot.user.id == LUMINOUS_ID:
            embed = discord.Embed(title="🐳 BẢNG VÀNG PHÚ HÀO VƯƠNG QUỐC EQUINOX", color=0xE5E4E2)
            desc = "Vinh danh 10 đại phú hào có đóng góp ngân khố vĩ mô lớn nhất vương quốc thời điểm hiện tại:\n\n"
            
            for i, u in enumerate(top_10):
                desc += f"{medals[i]} Top {i+1}: <@{u['id']}> — **{u['total']:,}** Toàn Cục ({u['clean']:,} Sạch | {u['dirty']:,} Bẩn)\n"
                
            embed.description = desc
            
        else:
            embed = discord.Embed(title="🎰 DANH SÁCH ĐẠI LÀO CÀY TIỀN CHỢ ĐEN", color=0xB8860B)
            desc = "Ngó xem những cái bóp dày nhất server để chuẩn bị lệnh t!rob (Móc túi) hoặc thuê t!hitman (Sát thủ) đi thảm sát vặt lông tụi nó đi lũ cái bang:\n\n"
            
            for i, u in enumerate(top_10):
                desc += f"{medals[i]} Top {i+1}: <@{u['id']}> — **{u['total']:,}** Toàn Cục ({u['clean']:,} Sạch | {u['dirty']:,} Bẩn)\n"
                
            desc += "\n🗡️ *Nhẫn cưới tụi nó lấp lánh quá, bật định vị cho Hội Sát Thủ đi săn đêm nay đi anh em!*"
            embed.description = desc

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileSys(bot))
