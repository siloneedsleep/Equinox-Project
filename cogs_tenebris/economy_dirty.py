import discord
from discord.ext import commands
import random

from config.settings import COLORS
from database.redis_client import get_redis_connection

class EconomyDirty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # 🚨 1. BUÔN LẬU KIẾM TIỀN BẨN (SMUGGLE)
    # ==========================================
    @commands.command(name="smuggle", aliases=["buonlau"])
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def smuggle_money(self, ctx):
        r = await get_redis_connection()
        user_key = f"equinox:user:{ctx.author.id}"
        
        # Tỷ lệ thành công 70%, thất bại 30%
        success = random.random() < 0.7
        
        if success:
            amount = random.randint(10000, 50000)
            await r.hincrby(user_key, "balance_dirty", amount)
            await r.hincrby(user_key, "danger_level", 1)
            
            embed = discord.Embed(title="📦 BUÔN LẬU TRÓT LỌT", color=COLORS["tenebris_action"])
            embed.description = f"Khá lắm con giời <@{ctx.author.id}>! Chuyến hàng cấm đêm nay trót lọt, tao chia cho mày **+{amount:,} Star** bẩn. Giấu cho kỹ vào!"
        else:
            fine = random.randint(5000, 20000)
            current_dirty = int(await r.hget(user_key, "balance_dirty") or 0)
            actual_fine = min(fine, current_dirty)
            
            await r.hincrby(user_key, "balance_dirty", -actual_fine)
            embed = discord.Embed(title="🚨 BỊ LỰC LƯỢNG TRỊ AN SỜ GÁY", color=COLORS["tenebris_error"])
            embed.description = f"Ngu thì chết <@{ctx.author.id}>! Đang tuồn hàng thì bị tóm. Chạy tụt quần rớt mất **-{actual_fine:,} Star** bẩn!"
            
        await ctx.send(embed=embed)

    # ==========================================
    # 🥷 2. MÓC TÚI TRẤN LỘT (ROB)
    # ==========================================
    @commands.command(name="rob", aliases=["moctui"])
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def rob_money(self, ctx, target: discord.Member = None):
        if not target:
            return await ctx.send("Muốn cướp của ai thì tag nó vào! Gõ không thế cướp không khí à?")
            
        if target.id == ctx.author.id:
            return await ctx.send("Tự cướp chính mình? Mày bị ngáo à?")
            
        if target.bot:
            return await ctx.send("Động vào máy móc của tao làm gì? Tìm người mà cướp!")

        r = await get_redis_connection()
        robber_key = f"equinox:user:{ctx.author.id}"
        target_key = f"equinox:user:{target.id}"
        
        target_dirty = int(await r.hget(target_key, "balance_dirty") or 0)
        
        if target_dirty < 5000:
            return await ctx.send(f"Thằng <@{target.id}> này trên răng dưới dế, két sắt ngầm có chưa tới 5,000 Star bẩn. Tha cho nó đi!")

        # Tỷ lệ cướp 40% thành công
        success = random.random() < 0.4
        
        if success:
            stolen_amount = int(target_dirty * random.uniform(0.05, 0.15))
            async with r.pipeline(transaction=True) as pipe:
                pipe.hincrby(target_key, "balance_dirty", -stolen_amount)
                pipe.hincrby(robber_key, "balance_dirty", stolen_amount)
                pipe.hincrby(robber_key, "danger_level", 2)
                await pipe.execute()
                
            embed = discord.Embed(title="🥷 CƯỚP ĐÊM THÀNH CÔNG", color=COLORS["tenebris_action"])
            embed.description = f"Quá đẳng cấp! <@{ctx.author.id}> vừa đục két sắt ngầm của <@{target.id}> và cuỗm mất **{stolen_amount:,} Star** bẩn!"
        else:
            penalty = random.randint(10000, 30000)
            robber_dirty = int(await r.hget(robber_key, "balance_dirty") or 0)
            actual_penalty = min(penalty, robber_dirty)
            
            async with r.pipeline(transaction=True) as pipe:
                pipe.hincrby(robber_key, "balance_dirty", -actual_penalty)
                pipe.hincrby(target_key, "balance_dirty", actual_penalty)
                await pipe.execute()
                
            embed = discord.Embed(title="💀 BỊ ĐẬP NGƯỢC", color=COLORS["tenebris_error"])
            embed.description = f"Gà! <@{ctx.author.id}> định móc túi <@{target.id}> nhưng bị phát giác và đấm sưng mỏ, đền bù ngược lại **{actual_penalty:,} Star** bẩn cho nạn nhân!"
            
        await ctx.send(embed=embed)

    # ==========================================
    # 🧼 3. RỬA TIỀN BẨN (WASH)
    # ==========================================
    @commands.command(name="wash", aliases=["ruatien"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def wash_money(self, ctx, amount: str):
        r = await get_redis_connection()
        user_key = f"equinox:user:{ctx.author.id}"
        
        dirty_bal = int(await r.hget(user_key, "balance_dirty") or 0)
        
        if dirty_bal <= 0:
            return await ctx.send("Mày làm gì có đồng Star bẩn nào mà đòi rửa? Cút đi cày t!smuggle đi!")
            
        if amount.lower() == "all":
            wash_amount = dirty_bal
        else:
            try:
                wash_amount = int(amount)
            except ValueError:
                return await ctx.send("Nhập số lượng hẳn hoi vào! Mù chữ à?")
                
            if wash_amount <= 0:
                return await ctx.send("Số tiền rửa phải lớn hơn 0!")
                
            if wash_amount > dirty_bal:
                return await ctx.send(f"Mày chỉ có tối đa **{dirty_bal:,} Star** bẩn thôi thằng mõm!")

        tax_rate_min, tax_rate_max = 0.15, 0.25
        partner_tier = int(await r.hget(f"equinox:partner:{ctx.guild.id}", "tier") or 0)
        if partner_tier >= 2:
            tax_rate_min, tax_rate_max = 0.10, 0.20

        tax_rate = random.uniform(tax_rate_min, tax_rate_max)
        tax_amount = int(wash_amount * tax_rate)
        clean_amount = wash_amount - tax_amount

        async with r.pipeline(transaction=True) as pipe:
            pipe.hincrby(user_key, "balance_dirty", -wash_amount)
            pipe.hincrby(user_key, "balance_clean", clean_amount)
            pipe.incrby("equinox:system:family_fund", tax_amount)
            await pipe.execute()

        embed = discord.Embed(title="🧼 RỬA TIỀN THÀNH CÔNG", color=COLORS["tenebris_main"])
        embed.description = f"Phi vụ trót lọt! Tao đã tuồn tiền của <@{ctx.author.id}> qua mặt Thần Điện."
        embed.add_field(name="Tiền bẩn đem rửa", value=f"{wash_amount:,} Star", inline=True)
        embed.add_field(name=f"Cắt phế ({int(tax_rate*100)}%)", value=f"-{tax_amount:,} Star", inline=True)
        embed.add_field(name="Ví sạch nhận được", value=f"**{clean_amount:,} Star**", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyDirty(bot))
