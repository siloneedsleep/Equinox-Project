import os
import json
import datetime
import discord
from discord import app_commands
from discord.ext import commands, tasks
import google.generativeai as genai
from database.redis_client import get_redis_connection
from config.settings import LUMINOUS_ID, TENEBRIS_ID

# ==============================================================================
# 🧠 CẤU HÌNH AI GEMINI
# ==============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_realtime_cycle():
    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    return "DAY" if 0 <= now.hour < 12 else "NIGHT"

class CrossMailbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_mailbox.start()

    def cog_unload(self):
        self.check_mailbox.cancel()

    # ==============================================================================
    # 🤖 HÀM GỌI GEMINI NẢY SỐ TRẢ LỜI
    # ==============================================================================
    async def generate_ai_reply(self, persona, user_message):
        if not GEMINI_API_KEY:
            return f"*(Chưa lắp não AI)* Nội dung thư của bạn là: {user_message}"
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"{persona}\n\nNội dung thư của user nhắn cho bạn: '{user_message}'\nHãy viết câu trả lời thật ngắn gọn, tự nhiên, dưới 80 chữ. Tuyệt đối nhập vai chuẩn xác:"
            response = await model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            return f"*(Lỗi kết nối bộ não Thần Điện)* Nội dung thư: {user_message}"

    # ==============================================================================
    # 📝 LỆNH GỬI THƯ CHO BOT ĐANG NGỦ
    # ==============================================================================
    @app_commands.command(name="gui-thu", description="Nhờ bot đang thức chuyển lời cho bot đang ngủ")
    @app_commands.describe(loi_nhan="Nội dung bạn muốn nhắn nhủ")
    async def send_mail(self, interaction: discord.Interaction, loi_nhan: str):
        cycle = get_realtime_cycle()
        r = await get_redis_connection()

        if self.bot.user.id == LUMINOUS_ID:
            if cycle == "DAY":
                mail_data = {"user_id": interaction.user.id, "channel_id": interaction.channel.id, "msg": loi_nhan}
                await r.rpush("equinox:mailbox:TENEBRIS", json.dumps(mail_data))
                await interaction.response.send_message("☀️ **Luminous:** Mình đã cất thư của bạn vào tủ rồi. Đúng 12:00 trưa ông xã Tenebris dậy, mình sẽ đưa cho anh ấy đọc nhé!")
            else:
                await interaction.response.send_message("❌ Chồng mình đang thức sờ sờ ra kìa, bạn gọi t! để gặp thẳng ổng đi!", ephemeral=True)

        elif self.bot.user.id == TENEBRIS_ID:
            if cycle == "NIGHT":
                mail_data = {"user_id": interaction.user.id, "channel_id": interaction.channel.id, "msg": loi_nhan}
                await r.rpush("equinox:mailbox:LUMINOUS", json.dumps(mail_data))
                await interaction.response.send_message("🔮 **Tenebris:** Tao vứt thư vào hòm rồi đấy. Sáng mai vợ tao dậy tao bảo bả xem.")
            else:
                await interaction.response.send_message("❌ Vợ tao đang trực ca ngày kìa, sang bên kia gọi l! mà nhắn, đừng phá giấc ngủ tao!", ephemeral=True)

    # ==============================================================================
    # 🔄 VÒNG LẶP CHECK THƯ KHI TỈNH DẬY (Có nhúng AI)
    # ==============================================================================
    @tasks.loop(minutes=1)
    async def check_mailbox(self):
        await self.bot.wait_until_ready()
        cycle = get_realtime_cycle()
        r = await get_redis_connection()

        # ☀️ LUMINOUS THỨC DẬY KIỂM TRA THƯ
        if self.bot.user.id == LUMINOUS_ID and cycle == "DAY":
            persona = "Bạn là Luminous (vợ của Tenebris), quản lý ca ngày. Tính cách: Dịu dàng, lịch sự, hiền lành, thông minh, xưng hô 'mình/bạn' hoặc 'Luminous/bạn'. Bạn vừa ngủ dậy thì ông xã (Tenebris) đưa cho bạn một bức thư mà user gửi từ đêm qua. Bạn đang đọc bức thư đó."
            while True:
                mail_bytes = await r.lpop("equinox:mailbox:LUMINOUS")
                if not mail_bytes: break
                
                mail = json.loads(mail_bytes)
                ai_reply = await self.generate_ai_reply(persona, mail["msg"])
                channel = self.bot.get_channel(mail["channel_id"])
                if channel:
                    await channel.send(f"☀️ <@{mail['user_id']}> ơi! Sáng nay ông xã Tenebris có đưa thư của bạn cho mình nè.\n💬 **Luminous:** {ai_reply}")

        # 🔮 TENEBRIS THỨC DẬY KIỂM TRA THƯ
        elif self.bot.user.id == TENEBRIS_ID and cycle == "NIGHT":
            persona = "Bạn là Tenebris (chồng của Luminous), chúa tể quản lý Chợ Đen ca đêm. Tính cách: Cục súc, giang hồ, ngạo mạn, hay chửi thề nhẹ, rất cưng chiều vợ nhưng ghen tuông, xưng 'tao/mày' hoặc 'bố mày/mày'. Vợ bạn (Luminous) vừa đưa cho bạn bức thư mà user gửi từ ban ngày. Bạn đang ngái ngủ và đọc thư."
            while True:
                mail_bytes = await r.lpop("equinox:mailbox:TENEBRIS")
                if not mail_bytes: break
                
                mail = json.loads(mail_bytes)
                ai_reply = await self.generate_ai_reply(persona, mail["msg"])
                channel = self.bot.get_channel(mail["channel_id"])
                if channel:
                    await channel.send(f"🔮 Dậy rồi đây <@{mail['user_id']}>! Vợ tao bảo ban ngày mày gửi thư nhờ vả đúng không?\n💬 **Tenebris:** {ai_reply}")

async def setup(bot):
    await bot.add_cog(CrossMailbox(bot))
