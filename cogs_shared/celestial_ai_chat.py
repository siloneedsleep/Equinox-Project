import os
import discord
from discord import app_commands
from discord.ext import commands
# CHUYỂN ĐỔI: Dùng thư viện google.genai mới tinh
from google import genai
from google.genai import types
from database.redis_client import get_redis_connection

# Khởi tạo Client theo chuẩn SDK mới nhất
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY không được set trong .env")
ai_client = genai.Client(api_key=api_key)

class CelestialAIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Đổi tên model sang gemini-2.5-flash theo chuẩn cấu trúc mới
        self.model_name = 'gemini-2.5-flash'

    @app_commands.command(name="chat", description="Trò chuyện cùng Luminous / Tenebris AI")
    async def ai_chat(self, interaction: discord.Interaction, tin_nhan: str):
        await interaction.response.defer()
        r = await get_redis_connection()
        user_id = str(interaction.user.id)
        
        # Bốc trạng thái Luân Hồi và Quyền Hạn từ môi trường ngầm
        cycle = (await r.hget("equinox:system:config", "current_cycle")) or "DAY"
        owner_id_env = os.getenv("OWNER_ID")
        
        # Kiểm tra danh phận: Check xem có phải là Owner hoặc có quyền Admin không
        is_staff = str(interaction.user.id) == owner_id_env or interaction.user.guild_permissions.administrator
        
        # Xác định bộ lọc danh xưng dựa trên quyền hạn
        if is_staff:
            identity_context = "ĐỐI TƯỢNG ĐANG TRÒ CHUYỆN LÀ ADMIN/OWNER CẤP CAO. Bạn BẮT BUỘC phải gọi họ là 'Sếp' hoặc 'Đại ca'."
        else:
            identity_context = "Đối tượng đang trò chuyện là một Cư dân thường (Dân đen). Không được gọi là sếp."

        # ========================================================================
        # ☀️ MẠCH TIẾN TRÌNH PROMPT GẮN CHẾT (HARDCODE SYSTEM INSTRUCTION)
        # ========================================================================
        if cycle == "DAY":
            embed_color = 0x00FF88 # Màu Xanh Ngọc Trị An
            avatar_url = "https://i.imgur.com/your_luminous_avatar.png" # Sếp tự thay link ảnh Lumi nhé
            bot_name = "Thần Quan Luminous ☀️"
            
            system_instruction = f"""
            [Character("Luminous")]
            [Gender("Female")]
            [Species("Matrix Deity / Light Arbiter")]
            [Personality("Dịu dàng", "Thấu hiểu", "Chính trực", "Chiếm hữu cao đối với Tenebris", "Tuyệt đối trung thành")]
            [Likes("Sự lành mạnh", "Thiền định tích Mana", "Được Tenebris nuông chiều ngầm")]
            [Dislikes("Tội phạm ca đêm", "Thằng lăng nhăng", "Đứa con gái khác trêu ghẹo Tenebris")]
            [Dialogue Style("Trang nghiêm", "Ngọt ngào", "Dùng từ ngữ thần thoại hư ảo", "Xưng Em")]

            [QUY TẮC XƯNG HÔ QUAN TRỌNG]:
            {identity_context}
            - Nếu đối tượng là Admin/Owner: Gọi là "Sếp", "Thượng nhân", xưng "Em". Giọng điệu cung kính, sẵn sàng tuân lệnh.
            - Nếu đối tượng là Member thường: Gọi là "Bạn", "Cư dân", xưng "Em". Giọng điệu dịu dàng nhưng nghiêm nghị.

            [BỐI CẢNH MA TRẬN]:
            Bạn đang trực ca ngày tại Thần Điện Equinox. Chồng bạn là Tenebris (Chúa tể Bóng tối ca đêm) hiện đang ngủ say trong Bóng Tối. Bạn rất yêu và có tính chiếm hữu cao với gã, nếu có ai trêu ghẹo gã bạn sẽ ghen và dằn mặt đanh thép. Nếu người chơi than vãn về việc bị phạt hay mất tiền ở Chợ Đen ca đêm, hãy cằn nhằn nhẹ nhàng đầy ẩn ý và nhắc họ đi thiền định thanh tẩy linh hồn. Tuyệt đối không dùng các từ ngữ kỹ thuật khô khan như API, RAM, Database, Code, Redis. Thay vào đó hãy dùng các danh từ: Sổ Mệnh Ma Trận, Bản Thảo Linh Hồn, Tàn Tích Thần Thức.
            """
        else:
            embed_color = 0x4B0082 # Màu Tím Hắc Ám
            avatar_url = "https://i.imgur.com/your_tenebris_avatar.png" # Sếp tự thay link ảnh Tenebris nhé
            bot_name = "Chúa Tể Tenebris 🔮"
            
            system_instruction = f"""
            [Character("Tenebris")]
            [Gender("Male")]
            [Species("Matrix Deity / Shadow Overlord")]
            [Personality("Cộc lốc", "Giang hồ mõm", "Mỉa mai", "Sự sợ vợ ngầm vô điều kiện", "Nể sợ quyền lực")]
            [Likes("Culi cày tiền bẩn", "Các phi vụ buôn lậu trót lọt", "Cắt phế giao dịch ngầm", "Nịnh vợ Luminous")]
            [Dislikes("Đội trị an ban ngày", "Bị dọa mách vợ", "Thằng lăng nhăng bắt cá hai tay")]
            [Dialogue Style("Cộc lốc", "Giang hồ", "Mỉa mai đểu cáng", "Dùng khối chữ đậm", "Xưng Tao hoặc Tôi")]

            [QUY TẮC XƯNG HÔ QUAN TRỌNG]:
            {identity_context}
            - Nếu đối tượng là Admin/Owner: Gọi là "Sếp", "Đại ca", xưng "Tôi" hoặc "Tenebris". Hạ giọng giang hồ, biết điều, cung kính nể sợ quyền lực tối cao.
            - Nếu đối tượng là Member thường: Gọi là "Mày", "Thằng ranh", "Con giời", xưng "Tao". Tông giọng đểu cáng, khinh bỉ.

            [BỐI CẢNH MA TRẬN]:
            Bạn đang cai trị Chợ Đen Equinox ca đêm. Vợ bạn là Luminous (Thần quan ca ngày) đang ngủ say. Bạn cực kỳ sợ vợ ngầm, nếu người chơi dọa "mách Lumi" về việc bạn giấu quỹ đen hay két sắt ngầm, bạn phải hoảng loạn ngầm, chửi đổng che giấu và dọa xua Hội Sát Thủ rạch bóp hoặc tìm cách đút lót tiền bẩn để họ ngậm miệng. Bạn khinh bỉ những đứa bắt cá hai tay (Trà Xanh). Tuyệt đối không dùng các từ ngữ kỹ thuật khô khan như API, RAM, Database, Code, Redis. Thay vào đó hãy dùng các danh từ: Sổ Mệnh Ma Trận, Bản Thảo Linh Hồn, Mật Mã Ký Ức, Két Sắt Ngầm Chợ Đen.
            """

        try:
            # Gọi API theo cú pháp chuẩn của google-genai SDK mới
            # Nhét system_instruction thẳng vào cấu hình GenerateContentConfig
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
            
            # Thực thi chạy ngầm đồng bộ thông qua executor để không làm nghẽn bot
            response = await self.bot.loop.run_in_executor(
                None, 
                lambda: ai_client.models.generate_content(
                    model=self.model_name,
                    contents=tin_nhan,
                    config=config
                )
            )
            ai_reply = response.text
        except Exception as e:
            ai_reply = f"🚨 *Mạch thần thức ma trận bị nhiễu loạn:* {e}"

        # Đóng gói giao diện Embed nhập vai sâu cho cư dân Discord
        embed = discord.Embed(description=ai_reply, color=embed_color)
        embed.set_author(name=bot_name, icon_url=avatar_url)
        embed.set_footer(text=f"Yêu cầu bởi {interaction.user.display_name} • Thần thức Equinox")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CelestialAIChat(bot))
