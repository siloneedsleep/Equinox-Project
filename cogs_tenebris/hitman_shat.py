import discord
from discord.ext import commands
import random
import asyncio

from config.settings import COLORS, LUMINOUS_ID
from database.redis_client import get_redis_connection

class HitmanShat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # 🗡️ LỆNH THUÊ SÁT THỦ ÁM SÁT CẶP ĐÔI (HITMAN)
    # ==========================================
    @commands.command(name="hitman", aliases=["satthu"])
    @commands.cooldown(1, 3600, commands.BucketType.user) # Cooldown 1 tiếng 1 lần
    async def hire_hitman(self, ctx, target: discord.Member = None):
        if not target:
            return await ctx.send("Muốn thuê sát thủ đi xiên ai thì phải tag nó vào! Trái quy tắc giang hồ à?")
            
        if target.id == ctx.author.id:
            return await ctx.send("Tự bỏ tiền thuê sát thủ xiên mình? Mày bị ngáo đá à?")
            
        if target.bot:
            return await ctx.send("Sát thủ của tao không nhận hợp đồng chém máy móc, tìm người thật đi!")

        r = await get_redis_connection()
        robber_key = f"equinox:user:{ctx.author.id}"
        target_key = f"equinox:user:{target.id}"
        
        # 1. Kiểm tra tình trạng hôn nhân của mục tiêu (Chỉ nhắm vào người có Nhẫn Kim Cương)
        target_partner = await r.hget(target_key, "partner_id")
        target_ring = await r.hget(target_key, "ring_type")
        
        if not target_partner or target_ring != "diamond":
            return await ctx.send(f"Thằng <@{target.id}> này nghèo rớt mồng tơi, tay không đeo nhẫn Kim Cương thì Hội Sát Thủ không rảnh đi săn đâu! Mục tiêu quá phèn!")

        # 2. Kiểm tra tài chính của người thuê
        cost = 100000 # Giá thuê cố định 100k Star bẩn
        dirty_bal = int(await r.hget(robber_key, "balance_dirty") or 0)
        
        if dirty_bal < cost:
            return await ctx.send(f"Bóp mày làm gì có nổi **{cost:,} Star** bẩn mà đòi thuê Hội Sát Thủ? Đi cày `t!smuggle` đi thằng cái bang!")

        # Thu tiền phí trước
        await r.hincrby(robber_key, "balance_dirty", -cost)
        
        # 3. Tính toán Tỷ lệ thành công
        # Mặc định: 40% thành công. Nếu nạn nhân có Nhẫn Chạng Vạng: Giảm còn 10%
        success_chance = 0.40
        has_twilight_ring = await r.hget(target_key, "has_twilight_ring") == "TRUE"
        
        if has_twilight_ring:
            success_chance = 0.10
            
        is_success = random.random() < success_chance

        embed_process = discord.Embed(title="🗡️ HỘI SÁT THỦ XUẤT QUÂN", color=COLORS["tenebris_main"])
        embed_process.description = f"<@{ctx.author.id}> đã xì ra **{cost:,} Star** bẩn. Sát thủ đang trong bóng đêm tiếp cận bóp tiền của <@{target.id}>..."
        msg = await ctx.send(embed=embed_process)
        
        await asyncio.sleep(3) # Tạo độ delay hồi hộp

        if is_success:
            # Thành công: Trừ 30% tiền sạch của nạn nhân, cộng vào tiền bẩn của người thuê
            target_clean = int(await r.hget(target_key, "balance_clean") or 0)
            
            if target_clean < 50000:
                # Nếu nạn nhân nghèo quá thì sát thủ chê
                embed_fail = discord.Embed(title="🗡️ MỤC TIÊU QUÁ NGHÈO", color=COLORS["tenebris_error"])
                embed_fail.description = f"Sát thủ đã tiếp cận được <@{target.id}> nhưng phát hiện ví nó có chưa tới 50,000 Star sạch. Hội Sát Thủ khinh không thèm chém. Mày mất toi {cost:,} tiền thuê!"
                return await msg.edit(embed=embed_fail)
                
            stolen_amount = int(target_clean * 0.30)
            
            async with r.pipeline(transaction=True) as pipe:
                pipe.hincrby(target_key, "balance_clean", -stolen_amount)
                pipe.hincrby(robber_key, "balance_dirty", stolen_amount)
                pipe.hincrby(robber_key, "danger_level", 5) # Tăng mức độ nguy hiểm
                await pipe.execute()
                
            embed_success = discord.Embed(title="💀 ÁM SÁT THÀNH CÔNG!", color=COLORS["tenebris_action"])
            embed_success.description = f"Khét lẹt! Sát thủ đã rạch ví của <@{target.id}>, cướp thành công **{stolen_amount:,} Star** sạch biến thành tiền bẩn ném vào két cho <@{ctx.author.id}>!"
            await msg.edit(embed=embed_success)
            
            # Gửi Embed chia buồn dằn mặt mang phong cách Luminous (Tương tác chéo)
            channel = ctx.channel
            embed_luminous = discord.Embed(title="💒 THÔNG BÁO BIẾN CỐ PHU THÊ", color=COLORS["luminous_error"])
            embed_luminous.description = f"Sắc lệnh khẩn cấp từ Thần Điện! Cư dân <@{target.id}> vừa bị thế lực ngầm đánh úp và tổn thất **-{stolen_amount:,} Star**.\n\nHào quang chiếc nhẫn Kim Cương của bạn quá sáng đã thu hút kẻ ác. Lần sau hãy cẩn thận hơn!"
            embed_luminous.set_footer(text="Luminous đã ghi nhận tổn thất này.")
            await channel.send(embed=embed_luminous)

        else:
            # Thất bại
            embed_fail = discord.Embed(title="🛡️ ÁM SÁT THẤT BẠI!", color=COLORS["tenebris_error"])
            if has_twilight_ring:
                embed_fail.description = f"Vãi cả chưởng! <@{target.id}> có trang bị Nhẫn Chạng Vạng. Sát thủ vừa tới gần đã bị phản phệ nôn máu rút lui! <@{ctx.author.id}> mất trắng tiền thuê!"
            else:
                embed_fail.description = f"Sát thủ đi đứng lóng ngóng đạp phải đuôi chó bị phát hiện! Kế hoạch đi săn của <@{ctx.author.id}> đổ bể, mất trắng {cost:,} Star tiền thuê!"
            
            await msg.edit(embed=embed_fail)

async def setup(bot):
    await bot.add_cog(HitmanShat(bot))
