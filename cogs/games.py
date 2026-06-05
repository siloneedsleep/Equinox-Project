import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import asyncio

# ==============================================================================
# 🧰 HÀM TIỆN ÍCH DATABASE & KINH TẾ
# ==============================================================================
def load_db():
    try:
        with open("storage.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(data):
    with open("storage.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_data(data, user_id):
    users = data.setdefault("users", {})
    user_str = str(user_id)
    if user_str not in users:
        users[user_str] = {"cash": 0, "bank": 0, "inventory": {}}
    return users[user_str]

# ==============================================================================
# 🃏 GIAO DIỆN NÚT BẤM: XÌ DÁCH (BLACKJACK)
# ==============================================================================
class BlackjackView(discord.ui.View):
    def __init__(self, player, bet_amount):
        super().__init__(timeout=60) # Tự xử thua nếu ngâm bài quá 60s
        self.player = player
        self.bet_amount = bet_amount
        self.player_hand = [random.randint(1, 10), random.randint(1, 10)]
        self.dealer_hand = [random.randint(1, 10), random.randint(1, 10)]
        
    def get_hand_value(self, hand):
        return sum(hand)

    def generate_embed(self, status="Đang chơi..."):
        p_val = self.get_hand_value(self.player_hand)
        d_val = self.get_hand_value(self.dealer_hand)
        
        # Nếu đang chơi thì giấu lá thứ 2 của nhà cái
        d_display = f"{self.dealer_hand[0]} + ❓" if status == "Đang chơi..." else f"{' + '.join(map(str, self.dealer_hand))} (Tổng: {d_val})"
        
        color = discord.Color.gold()
        if "Thắng" in status: color = discord.Color.green()
        elif "Thua" in status or "Quắc" in status: color = discord.Color.red()
            
        embed = discord.Embed(title="🃏 ĐẤU TRƯỜNG XÌ DÁCH (BLACKJACK)", description=f"**Mức cược:** `{self.bet_amount:,} ⭐`\n**Trạng thái:** {status}", color=color)
        embed.add_field(name="🤵 Nhà cái (Bot)", value=f"`{d_display}`", inline=False)
        embed.add_field(name=f"👤 {self.player.display_name}", value=f"`{' + '.join(map(str, self.player_hand))} (Tổng: {p_val})`", inline=False)
        return embed

    async def end_game(self, interaction, result, multiplier=0):
        for child in self.children:
            child.disabled = True # Khóa nút
            
        data = load_db()
        user_data = get_user_data(data, self.player.id)
        
        if multiplier > 0:
            win_amount = int(self.bet_amount * multiplier)
            user_data["cash"] += win_amount # Trả lại vốn + Lãi
        else:
            pass # Tiền cược đã bị trừ lúc gõ lệnh
            
        save_db(data)
        await interaction.response.edit_message(embed=self.generate_embed(result), view=self)
        self.stop()

    @discord.ui.button(label="Rút Bài (Hit)", style=discord.ButtonStyle.primary, emoji="🃏")
    async def btn_hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player.id: return
        
        self.player_hand.append(random.randint(1, 10))
        if self.get_hand_value(self.player_hand) > 21:
            await self.end_game(interaction, "❌ Bạn đã bị Quắc (Bù)! Nhà cái ăn tiền.", 0)
        else:
            await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="Dằn Bài (Stand)", style=discord.ButtonStyle.danger, emoji="🛑")
    async def btn_stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player.id: return
        
        p_val = self.get_hand_value(self.player_hand)
        
        # Lõi nhà cái tự rút bài nếu điểm dưới 17
        while self.get_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(random.randint(1, 10))
            
        d_val = self.get_hand_value(self.dealer_hand)
        
        if d_val > 21 or p_val > d_val:
            await self.end_game(interaction, "🎉 Chúc mừng! Bạn đã thắng nhà cái.", 2) # X2 tiền
        elif p_val == d_val:
            await self.end_game(interaction, "🤝 Hòa bài! Tiền cược được hoàn trả.", 1) # X1 tiền (Hòa vốn)
        else:
            await self.end_game(interaction, "❌ Thua trắng! Nhà cái lớn điểm hơn.", 0)

# ==============================================================================
# 🎲 COG: ĐẤU TRƯỜNG CASINO
# ==============================================================================
class CasinoGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================================================
    # 🎲 LỆNH: TÀI XỈU SIÊU TỐC (l!taixiu / l!tx)
    # ==========================================================================
    @commands.command(name="taixiu", aliases=["tx"])
    async def taixiu(self, ctx, choice: str = None, amount: str = None):
        if choice not in ["tai", "t", "xiu", "x"] or not amount:
            return await ctx.send("❌ Cú pháp sai! Vui lòng gõ: `l!tx <tai/xiu> <số_tiền_cược>`")
            
        data = load_db()
        user_data = get_user_data(data, ctx.author.id)
        
        if amount.lower() == "all": bet = user_data["cash"]
        else:
            try: bet = int(amount)
            except: return await ctx.send("❌ Số tiền cược không hợp lệ!")
            
        if bet <= 0 or user_data["cash"] < bet:
            return await ctx.send(f"❌ Bạn không đủ tiền! Ví chỉ có **{user_data['cash']:,} ⭐**.")
            
        # Trừ tiền cược trước chống bug spam
        user_data["cash"] -= bet
        save_db(data)
        
        # Tung xúc xắc
        dice = [random.randint(1, 6) for _ in range(3)]
        total = sum(dice)
        
        # Bão (3 hạt giống nhau) -> Nhà cái lụm hết
        is_bao = (dice[0] == dice[1] == dice[2])
        is_tai = 11 <= total <= 17
        is_xiu = 4 <= total <= 10
        
        choice_is_tai = choice in ["tai", "t"]
        
        msg = await ctx.send(f"🎲 **Nhà cái đang lắc xúc xắc...**")
        await asyncio.sleep(1.5) # Giả lập delay cho hồi hộp
        
        dice_str = " | ".join([f"**{d}**" for d in dice])
        result_msg = f"🎲 Xúc xắc: [ {dice_str} ] ➔ **Tổng {total}**\n"
        
        data = load_db() # Load lại DB cho chắc ăn
        user_data = get_user_data(data, ctx.author.id)
        
        if is_bao:
            result_msg += f"🔥 **NỔ BÃO ({dice[0]}{dice[1]}{dice[2]})!** Tất cả người chơi thua sạch cược."
        elif (choice_is_tai and is_tai) or (not choice_is_tai and is_xiu):
            win_amt = bet * 2
            user_data["cash"] += win_amt
            result_msg += f"✅ Chúc mừng! Bạn đoán đúng và bú **{win_amt:,} ⭐**!"
        else:
            result_msg += f"❌ Bạn đã đoán sai. Mất sạch **{bet:,} ⭐** tiền cược."
            
        save_db(data)
        await msg.edit(content=result_msg)

    # ==========================================================================
    # 🃏 LỆNH: XÌ DÁCH HOÀNG GIA (l!blackjack / l!bj)
    # ==========================================================================
    @commands.command(name="blackjack", aliases=["bj"])
    async def blackjack(self, ctx, amount: str):
        data = load_db()
        user_data = get_user_data(data, ctx.author.id)
        
        if amount.lower() == "all": bet = user_data["cash"]
        else:
            try: bet = int(amount)
            except: return await ctx.send("❌ Số tiền cược không hợp lệ!")
            
        if bet <= 0 or user_data["cash"] < bet:
            return await ctx.send("❌ Ví cạn mà đòi ngồi mâm VIP? Mời nạp thêm Star!")
            
        # Trừ tiền lên sòng
        user_data["cash"] -= bet
        save_db(data)
        
        view = BlackjackView(ctx.author, bet)
        await ctx.send(embed=view.generate_embed(), view=view)

    # ==========================================================================
    # 🎰 LỆNH SLASH: MUA GIẤY PHÉP SÒNG BẠC (CHỈ DÀNH CHO ADMIN SERVER)
    # ==========================================================================
    @app_commands.command(name="casino-license", description="[5,000,000 ⭐] Mua nhượng quyền Sòng Bạc Tư Nhân tại Server")
    async def casino_license(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Phải là Admin của Server mới được phép đấu thầu Sòng Bạc!", ephemeral=True)
            
        data = load_db()
        user_data = get_user_data(data, interaction.user.id)
        
        # Check tier VIP của Server để giảm giá
        sys_data = data.setdefault("system", {})
        partner_tier = sys_data.setdefault("partners", {}).get(str(interaction.guild.id), {}).get("tier", "standard")
        
        license_price = 5000000 # Giá gốc 5 củ Star
        if partner_tier == "vip_premium": license_price = int(license_price * 0.8) # Giảm 20%
        elif partner_tier == "vip_standard": license_price = int(license_price * 0.9) # Giảm 10%
        
        if user_data["cash"] < license_price:
            return await interaction.response.send_message(f"❌ Bạn cần **{license_price:,} ⭐** mặt để thầu Sòng Bạc Tư Nhân tại đây!", ephemeral=True)
            
        # Thu tiền giấy phép nạp Ngân khố
        user_data["cash"] -= license_price
        sys_data["global_treasury"] = sys_data.get("global_treasury", 0) + license_price
        
        # Cấp giấy phép vào Server
        server_data = sys_data["partners"].setdefault(str(interaction.guild.id), {})
        server_data["has_casino_license"] = True
        server_data["casino_owner"] = interaction.user.id
        
        save_db(data)
        await interaction.response.send_message(f"🎉 **ĐẤU THẦU THÀNH CÔNG!**\nChúc mừng ngài <@{interaction.user.id}> đã trở thành **Ông Trùm Sòng Bạc** tại Server này!\n*(Đã thanh toán {license_price:,} ⭐ phí nhượng quyền)*")

async def setup(bot):
    await bot.add_cog(CasinoGames(bot))
