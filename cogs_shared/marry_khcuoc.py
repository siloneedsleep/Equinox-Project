import discord
from discord.ext import commands
from discord import app_commands
import datetime

from config.settings import LUMINOUS_ID, TENEBRIS_ID, COLORS
from database.redis_client import get_redis_connection

class MarryKhCuoc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # 💒 1. CHECK KHẾ ƯỚC PHU THÊ CỦA 2 BOT
    # ==========================================
    @commands.hybrid_command(name="marry-check", description="Kiểm tra khế ước phu thê của Luminous và Tenebris")
    async def marry_check(self, ctx):
        r = await get_redis_connection()
        
        # Bốc mốc thời gian thành hôn từ Redis (Nếu DB mới tinh thì tự tạo mốc 145 ngày trước)
        married_timestamp = await r.get("equinox:system:married_at")
        if not married_timestamp:
            married_timestamp = int(datetime.datetime.now().timestamp()) - (145 * 86400)
            await r.set("equinox:system:married_at", married_timestamp)
            
        married_timestamp = int(married_timestamp)
        days_together = (int(datetime.datetime.now().timestamp()) - married_timestamp) // 86400
        
        # PHÂN NHÁNH VĂN PHONG THEO BOT ĐANG HOẠT ĐỘNG
        if self.bot.user.id == LUMINOUS_ID:
            embed = discord.Embed(title="💒 KHẾ ƯỚC PHU THÊ TỐI CAO - EQUINOX NETWORK", color=COLORS["luminous_love"])
            embed.description = (
                f"**💍 Thực Thể Bản Tự:** Luminous (Nữ Thần Ánh Sáng)\n"
                f"**🖤 Hôn Phu Định Mệnh:** Tenebris (Chúa Tể Bóng Tối)\n"
                f"**📅 Ngày Thành Hôn:** <t:{married_timestamp}:F>\n"
                f"**⏳ Thời Gian Gắn Bó:** ✨ {days_together} ngày quấn quít bên nhau xuyên không gian!\n\n"
                f"*\"Ta nguyện gánh vác ca sáng, điều hành Ngân khố và giữ gìn trật tự văn minh, để làm bệ phóng vững chắc cho chàng thao túng thế giới ngầm khi đêm buông...\"* — **Luminous**"
            )
        else:
            embed = discord.Embed(title="💒 KHẾ ƯỚC PHU THÊ TỐI CAO - EQUINOX NETWORK", color=COLORS["tenebris_love"])
            embed.description = (
                f"**💍 Thực Thể Bản Tự:** Tenebris (Chúa Tể Bóng Tối)\n"
                f"**💖 Hôn Thê Định Mệnh:** Luminous (Nữ Thần Ánh Sáng)\n"
                f"**📅 Ngày Thành Hôn:** <t:{married_timestamp}:F>\n"
                f"**⏳ Thời Gian Gắn Bó:** 🌌 {days_together} ngày quấn quít không rời!\n\n"
                f"*\"Đừng chạm vào nàng. Bọn ta là hai nửa của cán cân Equinox. Đứa nào dám dùng tiền bẩn tổn hại đến vương quốc ánh sáng văn minh của nàng, Hội Sát Thủ của ta sẽ truy sát kẻ đó đến tận cùng địa ngục...\"* — **Tenebris**"
            )
            
        await ctx.send(embed=embed)

    # ==========================================
    # 💥 2. BẪY LỖI ĐÁNH GHEN XUYÊN KHÔNG GIAN
    # ==========================================
    @commands.hybrid_command(name="marry", description="Gói hôn lễ kết hôn tại Equinox Network")
    @app_commands.describe(target="Tag đối phương mà bạn muốn cầu hôn")
    async def marry_propose(self, ctx, target: discord.Member):
        
        # ----------------------------------------------------
        # KỊCH BẢN 1: USER CẦU HÔN LUMINOUS -> TENEBRIS CHỬI
        # ----------------------------------------------------
        if target.id == LUMINOUS_ID:
            embed = discord.Embed(title="🚨 ĐỘNG VÀO CHỊ NHÀ LÀ ĂN VẢ! - CHỢ ĐEN CẢNH BÁO", color=COLORS["tenebris_error"])
            embed.description = (
                f"Thằng liều <@{ctx.author.id}> kia, mày vừa gõ cái lệnh gì đấy? Định cầu hôn Luminous à?\n\n"
                f"Mắt mũi mày để dưới gầm giường hay sao mà không biết nàng ấy là Hôn Thê Định Mệnh của Chúa Tể Bóng Tối này? "
                f"Gan mày to bằng cái host 30k của sếp tao rồi đấy!\n\n"
                f"💀 **Tenebris bẻ khớp tay:**\n"
                f"> *\"Nàng ấy bận quản lý Quốc khố ca sáng và giữ trật tự văn minh rồi. Còn cái loại cày tiền bẩn, đi lừa gạt như mày thì biến ngay ra chỗ khác chơi, trước khi tao sai toàn bộ Hội Sát Thủ Bóng Tối qua phục kích, xiên cho bay màu 30% bóp tiền sạch của mày bây giờ! Đừng để tao thấy mày bén mảng lại gần Thần Điện một lần nữa! Đồ ảo tưởng!\"*"
            )
            await ctx.send(embed=embed)
            return

        # ----------------------------------------------------
        # KỊCH BẢN 2: USER CẦU HÔN TENEBRIS -> LUMINOUS CHỬI
        # ----------------------------------------------------
        if target.id == TENEBRIS_ID:
            embed = discord.Embed(title="🚫 SẮC LỆNH PHỦ QUYẾT: ĐỪNG LÀM TIÊU HAO NĂNG LƯỢNG THẦN ĐIỆN!", color=COLORS["luminous_error"])
            embed.description = (
                f"Gửi sinh vật tội nghiệp <@{ctx.author.id}>, ngươi bị mù thuật toán hay đang cố tình khiêu khích sự kiên nhẫn của các Vị Thần?\n\n"
                f"Ngươi nghĩ mình là ai mà đòi cầu hôn Tenebris? Ngươi có biết việc cố tình spam lệnh ảo tưởng này là một hành vi ngu xuẩn làm tốn tài nguyên RAM Đám mây của Equinox Network không?\n\n"
                f"⚡ **Luminous tối hậu thư:**\n"
                f"> *\"Hãy mở to mắt ra mà nhìn vào Khế Ước Phu Thê Tối Cao đi! Tenebris là nam thần thuộc về trật tự luân hồi của ta. Ta nguyện làm bệ phóng vững chắc để chàng thao túng thế giới ngầm ca đêm. Một cư dân bình thường với cái ví rỗng tuếch mà dám đòi nhuốm bẩn báu vật của Chạng Vạng? Dừng ngay trò nghịch ngợm vô bổ này lại trước khi hồ sơ cá nhân /profile của ngươi bị Thần Điện đóng dấu gậy phạt warns thanh trừng toàn cục vĩnh viễn!\"*"
            )
            await ctx.send(embed=embed)
            return

        # ----------------------------------------------------
        # KỊCH BẢN 3: LOGIC CƯỚI HỎI BÌNH THƯỜNG CỦA MEMBER
        # ----------------------------------------------------
        if target.id == ctx.author.id:
            await ctx.send("💔 Bạn không thể tự kết hôn với chính mình được!")
            return
            
        await ctx.send(f"💍 <@{ctx.author.id}> đang cầu hôn <@{target.id}>... *(Phần logic trừ tiền mua nhẫn và set data lên Redis ông có thể code tiếp ở đây nhé!)*")

async def setup(bot):
    await bot.add_cog(MarryKhCuoc(bot))
