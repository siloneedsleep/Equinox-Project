import os
import discord
from discord.ext import commands
import random
import asyncio

from config.settings import COLORS
from database.redis_client import get_redis_connection
# Hook ngầm hệ thống Sổ Sinh Tử AI
from cogs_shared.celestial_karma import CelestialKarma 

class HitmanShat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Hàm lõi check ca trực ban đêm khẩn cấp
    async def _check_night_shift(self, ctx, r) -> bool:
        cycle_bytes = await r.hget("equinox:system:config", "current_cycle")
        cycle = cycle_bytes.decode('utf-8') if cycle_bytes else "DAY"
        is_overdrive = await r.hget("equinox:system:config", "event_overdrive") in (b"ON", "ON")
        
        if cycle == "DAY" and not is_overdrive:
            await ctx.send("☀️ Ban ngày Đội trị an Luminous đi tuần tra gắt vcl sếp ơi! "
                           "Tầm này mà mò đi thuê sát thủ giang hồ là bị xích cổ cả lũ lên Thần Điện đấy. "
                           "Đợi ca đêm ma trận (t!) mở cửa nhé!")
            return False
        return True

    # ==========================================
    # 🗡️ LỆNH THUÊ SÁT THỦ ÁM SÁT CẶP ĐÔI (HITMAN)
    # ==========================================
    @commands.command(name="hitman", aliases=["satthu"])
    @commands.cooldown(1, 3600, commands.BucketType.user) # Cooldown 1 tiếng 1 lần
    async def hire_hitman(self, ctx, target: discord.Member = None):
        if not target:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Muốn thuê sát thủ đi xiên ai thì phải tag nó vào! Trái quy tắc giang hồ à?")
            
        if target.id == ctx.author.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Tự bỏ tiền thuê sát thủ xiên mình? Mày bị ngáo đá à?")
            
        if target.bot:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Sát thủ của tao không nhận hợp đồng chém máy móc, tìm người thật đi!")

        r = await get_redis_connection()
        
        # ⏳ Check lệch ca trực ban ngày
        if not await self._check_night_shift(ctx, r):
            ctx.command.reset_cooldown(ctx)
            return

        robber_key = f"equinox:economy:wallets:{ctx.author.id}"
        target_key = f"equinox:economy:wallets:{target.id}"
        
        # 1. Kiểm tra tình trạng hôn nhân của mục tiêu (Chỉ nhắm vào người đeo Nhẫn Kim Cương)
        target_partner = await r.hget(target_key, "partner_id")
        target_ring_bytes = await r.hget(target_key, "ring_type")
        target_ring = target_ring_bytes.decode('utf-8') if target_ring_bytes else None
        
        if not target_partner or target_ring != "diamond":
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Thằng <@{target.id}> này nghèo rớt mồng tơi, tay không đeo nhẫn Kim Cương thì Hội Sát Thủ không rảnh đi săn đâu! Mục tiêu quá phèn!")

        # 2. Kiểm tra tài chính của người thuê
        cost = 100000 # Giá thuê cố định 100k Aequis bẩn
        dirty_bal = int(await r.hget(robber_key, "aequis") or 0) # balance_dirty -> aequis
        
        if dirty_bal < cost:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Bóp mày làm gì có nổi **{cost:,} Aequis** bẩn mà đòi thuê Hội Sát Thủ? Đi cày `t!smuggle` đi thằng cái bang!")

        # 🔒 KHÓA TRỪ TIỀN PHÍ TRƯỚC LẬP TỨC ĐỂ CHỐNG SPAM BUG TIỀN TRÙNG LẶP
        await r.hincrby(robber_key, "aequis", -cost)
        
        # Ghi log Karma ngầm khi ký kết hợp đồng trong bóng tối
        await CelestialKarma.log_karma_action(ctx.author.id, f"Bỏ ra 100k Aequis cọc thuê sát thủ ám sát ngầm @{target.display_name}")

        # 3. Tính toán Tỷ lệ thành công
        # Mặc định: 40% thành công. Nếu nạn nhân có Nhẫn Chạng Vạng: Giảm còn 10%
        success_chance = 0.40
        has_twilight_ring = await r.hget(target_key, "has_twilight_ring") in (b"TRUE", "TRUE")
        
        if has_twilight_ring:
            success_chance = 0.10
            
        is_success = random.random() < success_chance

        embed_process = discord.Embed(title="🗡️ HỘI SÁT THỦ XUẤT QUÂN", color=COLORS["tenebris_main"])
        embed_process.description = f"<@{ctx.author.id}> đã xì ra **{cost:,} Aequis** bẩn.\nSát thủ đang ẩn mình trong bóng đêm, tiếp cận bóp tiền của <@{target.id}>..."
        msg = await ctx.send(embed=embed_process)
        
        await asyncio.sleep(3) # Tạo độ delay hồi hộp kịch tính

        if is_success:
            # Thành công: Trừ 30% tiền sạch (aequor) của nạn nhân, cộng vào tiền bẩn (aequis) của người thuê
            target_clean = int(await r.hget(target_key, "aequor") or 0) # balance_clean -> aequor
            
            if target_clean < 50000:
                # Nếu nạn nhân nghèo quá thì sát thủ chê bỏ về, người thuê mất tiền cọc
                await CelestialKarma.log_karma_action(ctx.author.id, f"Hợp đồng xử @{target.display_name} bể kèo vì mục tiêu ví có dưới 50k tiền sạch")
                
                embed_fail = discord.Embed(title="🗡️ MỤC TIÊU QUÁ NGHÈO", color=COLORS["tenebris_error"])
                embed_fail.description = f"Sát thủ đã tiếp cận được <@{target.id}> nhưng phát hiện ví nó có chưa tới 50,000 Aequor sạch. Hội Sát Thủ khinh không thèm chém bẩn kiếm. Mày mất toi {cost:,} tiền cọc thuê!"
                return await msg.edit(embed=embed_fail)
                
            stolen_amount = int(target_clean * 0.30)
            
            async with r.pipeline(transaction=True) as pipe:
                pipe.hincrby(target_key, "aequor", -stolen_amount) # balance_clean -> aequor
                pipe.hincrby(robber_key, "aequis", stolen_amount)  # balance_dirty -> aequis
                pipe.hincrby(robber_key, "danger_level", 5)       # Tăng mức độ nguy hiểm lên 5 tinh cầu
                await pipe.execute()
                
            # Đóng dấu log Karma cho cả hai linh hồn
            await CelestialKarma.log_karma_action(ctx.author.id, f"Sát thủ ám sát thành công @{target.display_name}, cuỗm sạch {stolen_amount:,} Aequor")
            await CelestialKarma.log_karma_action(target.id, f"Bị sát thủ đột kích ca đêm rạch ví, tổn thất {stolen_amount:,} Aequor sạch")

            embed_success = discord.Embed(title="💀 ÁM SÁT THÀNH CÔNG!", color=COLORS["tenebris_action"])
            embed_success.description = f"Khét lẹt! Sát thủ đã rạch ví ngầm của <@{target.id}>, cướp thành công **{stolen_amount:,} Aequor** sạch biến thành tiền bẩn ném thẳng vào két sắt cho <@{ctx.author.id}>!"
            await msg.edit(embed=embed_success)
            
            # Gửi Embed chia buồn dằn mặt mang phong cách Luminous (Tương tác chéo)
            channel = ctx.channel
            embed_luminous = discord.Embed(title="💒 THÔNG BÁO BIẾN CỐ PHU THÊ", color=COLORS["luminous_error"])
            embed_luminous.description = f"🚨 **Sắc lệnh khẩn cấp từ Thần Điện!**\nCư dân phu thê <@{target.id}> vừa bị thế lực bóng đêm đánh úp bất ngờ và tổn thất nặng nề: **-{stolen_amount:,} Aequor**.\n\nHào quang chiếc nhẫn Kim Cương của bạn quá rực rỡ đã thu hút tà niệm Chợ Đen. Lần sau hãy bảo an cẩn thận hơn!"
            embed_luminous.set_footer(text="Luminous đã ghi nhận chương mục tổn thất tài sản này.")
            await channel.send(embed=embed_luminous)

        else:
            # Thất bại
            embed_fail = discord.Embed(title="🛡️ ÁM SÁT THẤT BẠI!", color=COLORS["tenebris_error"])
            if has_twilight_ring:
                await CelestialKarma.log_karma_action(ctx.author.id, f"Thuê sát thủ ám sát @{target.display_name} nhưng bị Nhẫn Chạng Vạng phản phệ nôn máu")
                embed_fail.description = f"Vãi cả chưởng! <@{target.id}> có trang bị Nhẫn Chạng Vạng hộ thân. Sát thủ vừa tới gần đã bị hào quang hỗn mang phản phệ nôn máu rút lui! <@{ctx.author.id}> mất trắng tiền thuê!"
            else:
                await CelestialKarma.log_karma_action(ctx.author.id, f"Thuê sát thủ ám sát @{target.display_name} thất bại vì sát thủ đi đứng ngáo ngơ")
                embed_fail.description = f"Sát thủ đi đứng lóng ngóng đạp phải đuôi chó trong ngõ bị phát hiện! Kế hoạch đi săn của <@{ctx.author.id}> đổ bể, mất trắng {cost:,} Aequis tiền thuê!"
            
            await msg.edit(embed=embed_fail)

async def setup(bot):
    await bot.add_cog(HitmanShat(bot))
