import discord
from discord.ext import commands
from discord import app_commands
import json
import time
import random

# ==============================================================================
# 🧰 HÀM TIỆN ÍCH DATABASE
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
        users[user_str] = {"cash": 0, "bank": 0, "bank_unlock_time": None, "inventory": {}}
    return users[user_str]

# ==============================================================================
# 🛒 GIAO DIỆN SELECT MENU: SIÊU CỬA HÀNG (/SHOP)
# ==============================================================================
class ShopSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Vé Nhuộm Màu Role", description="50,000 ⭐ | Tự do đổi màu Hex cho Role cá nhân.", emoji="🎨", value="role_color_ticket"),
            discord.SelectOption(label="Vé Danh Hiệu Profile", description="75,000 ⭐ | Gắn Tag danh hiệu lấp lánh trên thẻ.", emoji="🏷️", value="profile_tag_ticket"),
            discord.SelectOption(label="Hộ Chiếu Nhà Chính (7 Ngày)", description="30,000 ⭐ | Thông hành sang HQ, Miễn 100% Thuế.", emoji="🛂", value="hq_visa_7d"),
            discord.SelectOption(label="Bảo Hiểm Tài Sản Cấp 1", description="20,000 ⭐ | Đền bù 80% nếu bị cướp/ám sát.", emoji="🛡️", value="insurance_anti_rob"),
            discord.SelectOption(label="Hợp Đồng Gián Điệp", description="100,000 ⭐ | Phá hoại kinh tế server đối thủ.", emoji="🕵️", value="spy_contract")
        ]
        super().__init__(placeholder="👇 Bấm vào đây để chọn mua vật phẩm...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # 🛡️ LÁ CHẮN ANTI-CRASH COMPONENT TRY-EXCEPT
        try:
            item_value = self.values[0]
            prices = {
                "role_color_ticket": 50000, "profile_tag_ticket": 75000, 
                "hq_visa_7d": 30000, "insurance_anti_rob": 20000, "spy_contract": 100000
            }
            item_names = {
                "role_color_ticket": "Vé Nhuộm Màu Role 🎨", "profile_tag_ticket": "Vé Danh Hiệu Profile 🏷️", 
                "hq_visa_7d": "Hộ Chiếu Nhà Chính (7 Ngày) 🛂", "insurance_anti_rob": "Bảo Hiểm Tài Sản Cấp 1 🛡️", "spy_contract": "Hợp Đồng Gián Điệp 🕵️"
            }
            
            price = prices[item_value]
            
            data = load_db()
            user_data = get_user_data(data, interaction.user.id)
            
            if user_data["cash"] < price:
                return await interaction.response.send_message(f"❌ Nghèo mà đòi xài sang! Bạn chỉ có **{user_data['cash']:,} ⭐**, còn thiếu **{price - user_data['cash']:,} ⭐** nữa!", ephemeral=True)
                
            # Trừ tiền, thêm vào túi đồ
            user_data["cash"] -= price
            inv = user_data.setdefault("inventory", {})
            inv[item_value] = inv.get(item_value, 0) + 1
            
            # Cộng tiền vào Ngân khố quốc gia
            sys_data = data.setdefault("system", {})
            sys_data["global_treasury"] = sys_data.get("global_treasury", 0) + price
            
            save_db(data)
            
            await interaction.response.send_message(f"✅ **GIAO DỊCH THÀNH CÔNG!**\nBạn đã mua `{item_names[item_value]}` với giá **{price:,} ⭐**.\n*Vật phẩm đã được cất an toàn vào túi đồ của bạn.*", ephemeral=True)
            
        except Exception as e:
            print(f"🚨 [Anti-Crash Shop] Lỗi giao dịch của {interaction.user.name}: {e}")
            await interaction.response.send_message("⚠️ Lõi cơ sở dữ liệu đang nghẽn mạch. Giao dịch đã tự động hủy để bảo toàn Star của bạn!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Shop không bao giờ hết hạn nút bấm
        self.add_item(ShopSelect())

# ==============================================================================
# 🪙 COG: TRÁI TIM KINH TẾ (ECONOMY)
# ==============================================================================
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================================================
    # 💰 LỆNH KIỂM TRA SỐ DƯ (Hỗ trợ phím tắt siêu nhanh)
    # ==========================================================================
    @commands.command(name="balance", aliases=["bal", "b"])
    async def balance(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        data = load_db()
        user_data = get_user_data(data, target.id)
        
        cash = user_data["cash"]
        bank = user_data["bank"]
        total = cash + bank
        
        embed = discord.Embed(title=f"💳 Tài Khoản Của {target.display_name}", color=discord.Color.blue())
        embed.add_field(name="Tiền Mặt (Cash)", value=f"**{cash:,}** ⭐", inline=True)
        embed.add_field(name="Ngân Hàng (Bank)", value=f"**{bank:,}** ⭐", inline=True)
        embed.add_field(name="Tổng Tài Sản", value=f"**{total:,}** ⭐", inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)

    # ==========================================================================
    # 💸 LỆNH CHUYỂN TIỀN CÓ THUẾ (Biến số Nhà Chính HQ)
    # ==========================================================================
    @commands.command(name="pay", aliases=["p"])
    async def pay(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Số tiền chuyển phải lớn hơn 0!")
        if member.id == ctx.author.id:
            return await ctx.send("❌ Bị ảo à? Sao lại tự chuyển tiền cho chính mình?")
        if member.bot:
            return await ctx.send("❌ Không thể hối lộ bot!")

        data = load_db()
        sender_data = get_user_data(data, ctx.author.id)
        receiver_data = get_user_data(data, member.id)
        
        if sender_data["cash"] < amount:
            return await ctx.send(f"❌ Ví bạn chỉ có **{sender_data['cash']:,} ⭐**, không đủ để chuyển!")

        # ⚖️ LOGIC THUẾ GIAO DỊCH (TAX ENGINE)
        sys_data = data.setdefault("system", {})
        hq_guild_id = sys_data.get("hq_guild_id")
        
        tax_rate = 0.05 # Mặc định thu 5%
        
        # Đặc quyền 1: Giao dịch tại Nhà Chính (HQ) miễn thuế 100%
        if ctx.guild.id == hq_guild_id:
            tax_rate = 0.0
        # (Sau này ghép File Partner.py vào sẽ check thêm nếu là VIP thì giảm còn 2%)
            
        tax_amount = int(amount * tax_rate)
        final_amount = amount - tax_amount
        
        # Xử lý dòng tiền
        sender_data["cash"] -= amount
        receiver_data["cash"] += final_amount
        sys_data["global_treasury"] = sys_data.get("global_treasury", 0) + tax_amount
        
        save_db(data)
        
        msg = f"💸 **GIAO DỊCH THÀNH CÔNG!**\nBạn đã chuyển cho {member.mention} **{final_amount:,} ⭐**."
        if tax_amount > 0:
            msg += f"\n*(Hệ thống đã thu **{tax_amount:,} ⭐** (5%) thuế nạp vào Ngân khố quốc gia. Cần miễn thuế? Hãy xin Visa sang Nhà Chính!)*"
        else:
            msg += f"\n*(🏰 Bạn đang giao dịch tại Nhà Chính HQ: **Miễn 100% Thuế!**)*"
            
        await ctx.send(msg)

    # ==========================================================================
    # 🏦 LỆNH GỬI TIẾT KIỆM (Đóng băng tinh thể)
    # ==========================================================================
    @commands.command(name="bank-deposit", aliases=["dep", "d"])
    async def bank_deposit(self, ctx, amount: str, days: int = 1):
        if days not in [1, 3, 7]:
            return await ctx.send("❌ Chỉ hỗ trợ các kỳ hạn đóng băng: `1`, `3`, `7` ngày!")
            
        data = load_db()
        user_data = get_user_data(data, ctx.author.id)
        
        if amount.lower() == "all":
            amt = user_data["cash"]
        else:
            try: amt = int(amount)
            except: return await ctx.send("❌ Số tiền không hợp lệ!")
            
        if amt <= 0 or user_data["cash"] < amt:
            return await ctx.send("❌ Bạn không đủ tiền mặt để gửi vào ngân hàng!")
            
        # Tính toán thời gian khóa và lãi suất ngầm
        unlock_time = int(time.time()) + (days * 86400)
        
        user_data["cash"] -= amt
        user_data["bank"] += amt
        user_data["bank_unlock_time"] = unlock_time
        save_db(data)
        
        await ctx.send(f"🏦 **GỬI NGÂN HÀNG THÀNH CÔNG!**\nBạn đã đóng băng **{amt:,} ⭐** vào kho tinh thể.\n⏳ Thời gian mở khóa: <t:{unlock_time}:R>.")

    # ==========================================================================
    # 🏪 LỆNH SLASH SHOP (TÍCH HỢP DROPDOWN MƯỢT MÀ)
    # ==========================================================================
    @app_commands.command(name="shop", description="Mở cửa hàng độc quyền mua sắm vật phẩm VIP")
    async def shop(self, interaction: discord.Interaction):
        data = load_db()
        user_cash = get_user_data(data, interaction.user.id)["cash"]
        
        embed = discord.Embed(title="🏪 TRẠM THƯƠNG MẠI LIÊN MINH LUMINOUS", description="*Chào mừng Phú Hào đến với trung tâm mua sắm đặc quyền.*", color=discord.Color.purple())
        
        # Hiển thị list hàng hóa
        embed.add_field(name="🏷️ DANH MỤC VẬT PHẨM:", value=(
            "**1. 🎨 Vé Nhuộm Màu Role** - `50,000 ⭐`\n"
            "**2. 🏷️ Vé Danh Hiệu Profile** - `75,000 ⭐`\n"
            "**3. 🛂 Hộ Chiếu Nhà Chính (7d)** - `30,000 ⭐` *(Miễn thuế /pay 100%)*\n"
            "**4. 🛡️ Bảo Hiểm Tài Sản Cấp 1** - `20,000 ⭐` *(Chống bị cướp)*\n"
            "**5. 🕵️ Hợp Đồng Gián Điệp** - `100,000 ⭐`"
        ), inline=False)
        
        embed.add_field(name="💰 Số dư của bạn:", value=f"**{user_cash:,} ⭐** sạch.", inline=False)
        embed.set_footer(text="👇 Chọn vật phẩm bạn muốn mua ở Menu bên dưới!")
        
        await interaction.response.send_message(embed=embed, view=ShopView())

async def setup(bot):
    await bot.add_cog(Economy(bot))
