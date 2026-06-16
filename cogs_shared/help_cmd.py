import discord
from discord.ext import commands

from config.settings import LUMINOUS_ID, COLORS

class HelpCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Mở tài liệu vận hành / Sổ tay tội phạm")
    async def custom_help(self, ctx):
        if self.bot.user.id == LUMINOUS_ID:
            embed = discord.Embed(title="📚 TÀI LIỆU VẬN HÀNH LUMINOUS", color=COLORS["luminous_info"])
            embed.description = "Chào mừng đến với hệ thống vĩ mô. Hãy chọn phân khu quyền hạn của bạn ở Menu thả xuống bên dưới để tra cứu mật mã!"
            embed.set_footer(text="Giao diện bọc tính năng Mắt Mù ẩn lệnh theo Rank.")
            # Giao diện Select Menu ẩn hiện theo Rank sẽ được bọc ở Discord UI View
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="💀 SỔ TAY TỘI PHẠM CHỢ ĐEN", color=COLORS["tenebris_main"])
            embed.description = (
                "**🔫 Lệnh Cày Tiền Bẩn:**\n"
                "`t!smuggle` - Buôn lậu chất cấm kiếm tiền bẩn\n"
                "`t!rob @user` - Móc túi, trấn lột trực tiếp\n"
                "`t!wash [số tiền]` - Rửa tiền bẩn thành tiền sạch\n\n"
                "**🎰 Sòng Bạc (Casino):**\n"
                "`t!tx [t/x] [số tiền]` - Đánh Tài Xỉu (Tỷ lệ nổ hũ ca đêm cao)\n"
                "`t!bj [số tiền]` - Đánh Xì dách Blackjack UI\n\n"
                "**🗡️ Giang Hồ Lệnh:**\n"
                "`t!hitman @user` - Thuê sát thủ xiên cặp đôi cưới Nhẫn Kim Cương\n"
                "`t!marry check` - Kiểm tra sổ phu thê\n"
                "`t!voice-join` - Mời đại ca vào phòng Voice bảo kê\n"
            )
            embed.set_footer(text="Trạm hắc ám Tenebris")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCmd(bot))
