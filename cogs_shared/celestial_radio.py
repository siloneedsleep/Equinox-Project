import os
import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
from database.redis_client import get_redis_connection

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class CelestialRadio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    # ==============================================================================
    # 📻 LỆNH SLASH: PHÁT NHẠC TÂM TRẠNG AI (CHIA CA LORE)
    # ==============================================================================
    @app_commands.command(name="mood", description="Nhờ Luminous hoặc Tenebris đọc vị tâm trạng và bốc ngay 1 list nhạc phù hợp kèm link")
    @app_commands.describe(tam_trang="Nhập tâm trạng hiện tại của sếp (Ví dụ: đang sầu đời, sung sức cày code, cô đơn...)")
    async def ai_mood_radio(self, interaction: discord.Interaction, tam_trang: str):
        await interaction.response.defer()
        
        r = await get_redis_connection()
        
        # Đọc ca trực thực tế
        cycle_bytes = await r.hget("equinox:system:config", "current_cycle")
        cycle = cycle_bytes.decode('utf-8') if cycle_bytes else "DAY"

        # Định hình prompt ép AI bốc link nhạc thật (Spotify hoặc Youtube công khai)
        if cycle == "DAY":
            system_instruction = (
                "Bạn là Luminous, nữ thần Ánh Sáng hệ sinh thái Equinox. Văn phong: ngọt ngào, ấm áp, chữa lành. "
                "Nhiệm vụ: Người dùng sẽ gửi tâm trạng của họ. Hãy an ủi nhẹ nhàng rồi gợi ý 2-3 bài hát phù hợp. "
                "BẮT BUỘC: Mỗi bài hát phải đi kèm một đường link Youtube hoặc Spotify thật và đang hoạt động (Ví dụ: [Tên bài](link)). "
                "Xu hướng nhạc ban ngày: Acoustic, Pop Ballad nhẹ nhàng, nhạc không lời chữa lành. "
                "Xưng là 'Em', gọi họ là 'Sếp'. Trả lời ngắn gọn dưới 150 từ."
            )
            embed_title = "📻 TRẠM PHÁT THANH LUMINOUS: GIAI ĐIỆU TINH TÚ"
            embed_color = 0xFFD700
        else:
            system_instruction = (
                "Bạn là Tenebris, chúa tể Bóng Tối gác cổng Chợ Đen. Văn phong: lạnh lùng, phũ phàng, khịa bẩn, dark humor. "
                "Nhiệm vụ: Người dùng sẽ gửi tâm trạng của họ. Hãy khịa họ một câu rồi quăng cho họ 2-3 bài hát để nghe qua đêm. "
                "BẮT BUỘC: Mỗi bài hát phải đi kèm một đường link Youtube hoặc Spotify thật đang hoạt động (Ví dụ: [Tên bài](link)). "
                "Xu hướng nhạc ban đêm: Lo-fi hiphop chill buồn, Phonk đập đá, Rock/Metal dữ dội hoặc Synthwave cổ điển. "
                "Xưng là 'Ta', gọi họ là 'Ngươi' hoặc 'Sếp'. Trả lời ngắn gọn dưới 150 từ."
            )
            embed_title = "📻 RADIO CHỢ ĐEN TENEBRIS: GIAI ĐIỆU BÓNG ĐÊM"
            embed_color = 0x4B0082

        prompt = f"Chỉ thị hệ thống: {system_instruction}\n\nTâm trạng hiện tại của người dùng: {tam_trang}\n\nHãy xuất playlist ngay:"

        try:
            response = await self.bot.loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
            ai_reply = response.text
        except Exception as e:
            ai_reply = f"🚨 *Tần số radio bị nhiễu sóng:* (Lỗi: {e})"

        # Ghi log Karma ngầm cho hành động nghe nhạc
        try:
            from cogs_shared.celestial_karma import CelestialKarma
            await CelestialKarma.log_karma_action(interaction.user.id, f"Dùng lệnh /mood chia sẻ tâm trạng '{tam_trang}'")
        except Exception:
            pass

        embed = discord.Embed(description=ai_reply, color=embed_color)
        embed.set_author(name=embed_title, icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Tâm trạng ghi nhận: {tam_trang}")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CelestialRadio(bot))
