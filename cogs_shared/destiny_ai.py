import os
import random
import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
from database.redis_client import get_redis_connection

# Cấu hình API Key cho Gemini AI hạch tâm
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class DestinyAIMatrix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Khởi tạo model AI nhẹ, phản hồi siêu nhanh cho Discord (Gemini 2.5 Flash)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    # ==============================================================================
    # 🔮 LỆNH SLASH: XEM QUẺ VẬN MỆNH AI CHIA PHÂN THEO CA TRỰC
    # ==============================================================================
    @app_commands.command(name="fortune", description="Nhờ Luminous hoặc Tenebris dùng AI soi thấu quẻ vận mệnh hôm nay của sếp")
    async def ai_fortune(self, interaction: discord.Interaction):
        # Trì hoãn phản hồi để AI có thời gian múa phím (Tránh bị quá 3s timeout của Discord)
        await interaction.response.defer()
        
        r = await get_redis_connection()
        user_id = str(interaction.user.id)

        # 🕒 1. Đọc ca trực thực tế trên RAM Redis
        cycle_bytes = await r.hget("equinox:system:config", "current_cycle")
        cycle = cycle_bytes.decode('utf-8') if cycle_bytes else "DAY"

        # Dùng ID user + ngày hiện tại làm seed để tạo ra 3 chỉ số may mắn ngẫu nhiên (không đổi trong ngày)
        # Gửi dữ liệu này cho AI để nó phân tích làm bằng chứng "thần bí"
        random.seed(int(user_id))
        tinh_duyen = random.randint(1, 100)
        tai_loc = random.randint(1, 100)
        nghiep_qua = random.randint(1, 100)
        random.seed() # Reset seed

        # 🧠 2. BIỆN LUẬN PROMPT THEO TÍNH CÁCH AI CỦA TỪNG BOT
        if cycle == "DAY":
            # ☀️ PROMPT CỦA LÔI CÔ VỢ LUMINOUS (Dịu dàng, chữa lành, tích cực)
            system_instruction = (
                "Bạn là Luminous, linh vật nữ thần Ánh Sáng tối cao của hệ sinh thái Equinox Network. "
                "Tính cách của bạn: Dịu dàng, luôn tràn đầy năng lượng tích cực, dùng ngôn từ ấm áp, chữa lành để động viên người dùng. "
                "Nhiệm vụ: Hãy luận giải một quẻ bói ngắn gọn (dưới 150 từ) dựa trên các chỉ số sau của người dùng: "
                f"Tình duyên {tinh_duyen}%, Tài lộc {tai_loc}%, Nghiệp quả {nghiep_qua}%. "
                "Hãy xưng hô là 'Em' và gọi người dùng là 'Sếp' hoặc 'Anh/Chị'. Hãy đưa ra lời khuyên hướng thiện, tươi sáng."
            )
            embed_title = "☀️ LỜI TIÊN TRI ÁNH SÁNG TỪ LUMINOUS AI ☀️"
            embed_color = 0xFFD700
            avatar_url = self.bot.user.display_avatar.url
        else:
            # 🔮 PROMPT CỦA GÃ CHỒNG TENEBRIS (Phũ phàng, thực tế, hắc ám, Chợ Đen)
            system_instruction = (
                "Bạn là Tenebris, linh vật nam chúa tể Bóng Tối, gác cổng Chợ Đen của hệ sinh thái Equinox Network. "
                "Tính cách của bạn: Lạnh lùng, thực tế đến mức phũ phàng, pha chút tấu hài đen (dark humor), hay khịa nhưng rất uy tín. "
                "Nhiệm vụ: Hãy luận giải một quẻ bói ngắn gọn (dưới 150 từ) dựa trên các chỉ số sau của người dùng: "
                f"Tình duyên {tinh_duyen}%, Tài lộc {tai_loc}%, Nghiệp quả {nghiep_qua}%. "
                "Hãy xưng hô là 'Ta' hoặc 'Tôi' và gọi người dùng là 'Sếp' hoặc 'Ngươi'. Hãy bốc trần những góc tối, "
                "nhắc nhở họ né tránh drama hoặc rủ họ đi làm phi vụ ngầm ở Chợ Đen."
            )
            embed_title = "🔮 LỜI PHÁN XÉT BÓNG ĐÊM TỪ TENEBRIS AI 🔮"
            embed_color = 0x4B0082
            avatar_url = self.bot.user.display_avatar.url

        # 📡 3. GỌI LỆNH LÊN MÂY GEMINI AI XỬ LÝ
        try:
            # Tạo session prompt truyền chỉ thị hệ thống vào cấu trúc chat
            response = await self.bot.loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    f"Chỉ thị hệ thống: {system_instruction}\n\nHãy viết quẻ bói cho ta ngay!"
                )
            )
            ai_text = response.text
        except Exception as e:
            ai_text = f"🚨 *Ma trận AI bị nhiễu sóng:* Không thể kết nối đến tiềm thức của linh vật. (Lỗi: {e})"

        # 📊 4. ĐÓNG GÓI EMBED TRẢ VỀ CHO MEMBER
        embed = discord.Embed(title=embed_title, description=ai_text, color=embed_color)
        embed.add_field(name="💞 Tình Duyên", value=f"`{tinh_duyen}%`", inline=True)
        embed.add_field(name="💰 Tài Lộc", value=f"`{tai_loc}%`", inline=True)
        embed.add_field(name="⚖️ Nghiệp Quả", value=f"`{nghiep_qua}%`", inline=True)
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text=f"Mã định danh linh hồn: #{user_id[:6]}")

        # Gửi kết quả sau khi đã defer
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DestinyAIMatrix(bot))
