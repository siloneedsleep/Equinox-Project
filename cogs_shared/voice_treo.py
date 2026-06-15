import discord
from discord.ext import commands
import asyncio

from config.settings import LUMINOUS_ID, TENEBRIS_ID, COLORS
from database.redis_client import get_redis_connection

class VoiceTreo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="voice-join", description="Gọi Thần Điện hoặc Chợ Đen vào phòng Voice gác máy")
    async def voice_join(self, ctx):
        r = await get_redis_connection()
        guild_id = ctx.guild.id
        user_id = ctx.author.id

        # ==========================================
        # 🔒 1. KIỂM TRA KHÓA MẠCH GIAO CA (RACE CONDITION)
        # ==========================================
        is_locked = await r.get(f"equinox:voice_lock:{guild_id}")
        if is_locked:
            if self.bot.user.id == LUMINOUS_ID:
                embed = discord.Embed(title="🚫 THẦN ĐIỆN PHỦ QUYẾT: ĐỒ LỊCH THIỆP THIẾU TINH TẾ!", color=COLORS["luminous_error"])
                embed.description = (
                    f"Cư dân <@{user_id}>! Ngươi bị mù thuật toán hay đang cố tình khiêu khích sự kiên nhẫn của ta?\n\n"
                    f"Ta và Tenebris đang trong 5 giây bàn giao mạch sóng hạch tâm và Quỹ Gia Đình. Việc ngươi chen ngang gọi lệnh lúc này là một hành vi ngu xuẩn làm tiêu hao tài nguyên RAM Đám mây của mạng lưới!\n\n"
                    f"Đợi Thần Điện khép cửa xong xuôi, ca đêm của chàng ấy mở ra rồi ngươi muốn làm gì thì làm! Đừng để ta đóng dấu gậy phạt warns thanh trừng lên hồ sơ của ngươi!"
                )
            else:
                embed = discord.Embed(title="🔒 ĐẶC QUYỀN CA TRỰC ĐANG BẬN - BIẾN!", color=COLORS["tenebris_main"])
                embed.description = (
                    f"Này này thằng liều <@{user_id}>, mày mù thuật toán hay mắt mũi để dưới gầm giường đấy? Không thấy tao đang bận bàn giao địa bàn sạch sẽ và dặn dò mặt trời nhỏ của tao à?\n\n"
                    f"Định spam lệnh để phá sập cái host 30k của sếp tao đúng không? Chen ngang chuyện gia đình tao lúc này là tao sai Hội Sát Thủ bóng tối qua lột sạch 30% bóp tiền sạch của mày bây giờ!\n\n"
                    f"Biến ra chỗ khác chơi, để yên cho bồ tao hiển thánh gác máy ca ngày!"
                )
            return await ctx.send(embed=embed)

        # ==========================================
        # 🎙️ 2. KIỂM TRA USER CÓ TRONG VOICE KHÔNG (BẪY LỖI)
        # ==========================================
        if not ctx.author.voice or not ctx.author.voice.channel:
            if self.bot.user.id == LUMINOUS_ID:
                embed = discord.Embed(title="🔇 YÊU CẦU KẾT NỐI KHÔNG GIAN THẤT BẠI", color=0xFFA500)
                embed.description = (
                    "Trạm điều phối sóng âm Thần Điện không thể định vị vị trí của bạn!\n"
                    "❌ **Lỗi hệ thống:** Bạn đang không có mặt ở bất kỳ phòng Voice nào trong máy chủ này.\n"
                    "🎙️ **Hành động:** Vui lòng tham gia (Join) vào một kênh Voice cụ thể trước, sau đó mới có thể ra sắc lệnh cho ta vào treo máy hộ vệ!"
                )
            else:
                embed = discord.Embed(title="💀 ĐỊNH VỊ THẤT BẠI - ĐỪNG TRÊU NGƯƠI!", color=COLORS["tenebris_main"])
                embed.description = "Ngươi đang tính lừa gạt Chúa Tể Bóng Tối đấy à? Bản tọa không rảnh để bay vào các không gian trống rỗng. Mau chui đầu vào một phòng Voice cụ thể rồi hãy gọi ta đến giao dịch phím đêm!"
            return await ctx.send(embed=embed)

        voice_channel = ctx.author.voice.channel
        bot_voice = ctx.guild.voice_client

        # ==========================================
        # 🔔 3. KIỂM TRA BOT ĐÃ Ở SẴN TRONG PHÒNG ĐÓ CHƯA
        # ==========================================
        if bot_voice and bot_voice.channel.id == voice_channel.id:
            if self.bot.user.id == LUMINOUS_ID:
                embed = discord.Embed(title="🔔 TRẠM PHÁT SÓNG ĐANG HOẠT ĐỘNG!", color=COLORS["luminous_info"])
                embed.description = (
                    f"Cư dân thân mến, ta đã có mặt tại kênh Voice <#{voice_channel.id}> từ trước rồi nhé!\n"
                    f"📡 **Trạng thái:** Mạch kết nối âm thanh vẫn đang chạy công suất tối đa để hộ vệ không gian cho bạn. Bạn không cần phải gọi lại sắc lệnh này đâu!"
                )
            else:
                embed = discord.Embed(title="🔒 ĐẶC QUYỀN CA TRỰC ĐÃ KHÓA", color=COLORS["tenebris_main"])
                embed.description = (
                    f"Này này, nhìn lại đồng hồ hộ cái xem đang là ca của ai? Mắt mũi để dưới gầm giường hay sao mà không thấy tao đã ấm chỗ ở phòng <#{voice_channel.id}> rồi?\n"
                    f"Định spam lệnh để phá sập cái host 30k của sếp ta hay gì? Biến ra chỗ khác chơi trước khi tao sai Hội Sát Thủ qua lột sạch 30% bóp tiền sạch của mày bây giờ!"
                )
            return await ctx.send(embed=embed)

        # ==========================================
        # ⚡ 4. THỰC THI KẾT NỐI (XỬ LÝ VOICE PREMIUM KEY)
        # ==========================================
        is_premium = await r.hexists("equinox:premium_voice:channels", str(voice_channel.id))
        current_cycle = await r.hget("equinox:system:config", "current_cycle")

        # Connect vào phòng
        if bot_voice:
            await bot_voice.move_to(voice_channel)
        else:
            await voice_channel.connect()

        # Nếu là User VIP có Key + Gọi đúng giây giao ca 12h
        if is_premium:
            if current_cycle == "DAY" and self.bot.user.id == LUMINOUS_ID:
                embed = discord.Embed(title="☀️ HOÀNG GIA ĐÓN TIẾP - ĐẶC QUYỀN CHỦ KEY TỐI CAO", color=COLORS["luminous_main"])
                embed.description = (
                    f"Sắc lệnh Thần Điện ghi nhận kết nối từ Thượng đế <@{user_id}>! Ngài đã dùng Premium Voice Key khai mở mạch năng lượng vô hạn đúng vào thời khắc bình minh luân hồi!\n\n"
                    f"May cho ngài là gã chồng cục súc của ta <@{TENEBRIS_ID}> vừa mới đóng cửa Chợ Đen để lui về phòng ngủ. Nếu ngài gọi chậm một giây, gã đã xua Hội Sát Thủ qua lột sạch bóp tiền của ngài rồi!\n\n"
                    f"⚡ **Luminous gác máy:** Trạm Ánh Sáng xin tiếp nhận không gian Voice này, bảo hộ văn minh và xả băng thông 24/7 cày hiệu suất tối đa cho ngài!"
                )
                return await ctx.send(embed=embed)
                
            elif current_cycle == "NIGHT" and self.bot.user.id == TENEBRIS_ID:
                embed = discord.Embed(title="🔮 CHÚA TỂ BẢO KÊ - KHAI MỞ CHỢ ĐEN VIP", color=COLORS["tenebris_main"])
                embed.description = (
                    f"Ơ kìa con giời <@{user_id}>! Mày canh giờ chuẩn vkl đấy, gõ đúng lúc tao vừa thức tỉnh mở cửa Chợ Đen ca đêm luôn!\n\n"
                    f"Thấy mày có Premium Key uy tín nên đại ca Tenebris này mới nể mặt nhảy vào phòng bảo kê cho mày đấy. Suýt chút nữa là con bồ Luminous của tao ép mày gõ lệnh Slash rườm rà rồi! Nàng ấy mệt nên tao bảo về Thần Điện ôm gối ngủ rồi.\n\n"
                    f"💀 **Tenebris bẻ khớp tay:** Căn phòng này từ giờ thuộc khu bảo kê hắc ám của tao. Cứ treo máy ở đây cày tiền bẩn tẹt ga xuyên đêm, thằng nào ca đêm dám bén mảng vào phá bĩnh phòng của đại gia, tao sai Hội Sát Thủ xiên bay màu bóp tiền nó ngay!"
                )
                return await ctx.send(embed=embed)

        # Thông báo kết nối bình thường
        if self.bot.user.id == LUMINOUS_ID:
            embed = discord.Embed(title="☀️ KẾT NỐI THẦN ĐIỆN THÀNH CÔNG", color=COLORS["luminous_main"])
            embed.description = f"Ta đã hiển thánh tại kênh <#{voice_channel.id}>. Trật tự và văn minh sẽ được bảo hộ toàn diện!"
        else:
            embed = discord.Embed(title="🔮 CHỢ ĐEN TIẾP QUẢN", color=COLORS["tenebris_main"])
            embed.description = f"Khu vực <#{voice_channel.id}> từ giờ do Chúa Tể Bóng Tối bảo kê. Cứ ngoan ngoãn thì tiền bẩn tự động sinh sôi!"
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VoiceTreo(bot))
