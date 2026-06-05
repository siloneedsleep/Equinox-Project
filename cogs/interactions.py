import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import time
import random
import asyncio

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
        users[user_str] = {"cash": 0, "bank": 0, "partner": None}
    return users[user_str]

def generate_progress_bar(percent, length=15):
    filled = int((percent / 100) * length)
    empty = length - filled
    return "█" * filled + "░" * empty

# ==============================================================================
# 📊 GIAO DIỆN NÚT BẤM: TRƯNG CẦU DÂN Ý (VOTE)
# ==============================================================================
class VoteView(discord.ui.View):
    def __init__(self, option_a, option_b):
        super().__init__(timeout=None)
        self.option_a = option_a
        self.option_b = option_b
        self.voters = {} # {user_id: 'A' hoặc 'B'}

    def get_results(self):
        votes_a = list(self.voters.values()).count('A')
        votes_b = list(self.voters.values()).count('B')
        total = votes_a + votes_b
        
        if total == 0:
            return 0, 0, total
        
        pct_a = round((votes_a / total) * 100)
        pct_b = round((votes_b / total) * 100)
        return pct_a, pct_b, total

    async def update_embed(self, interaction):
        pct_a, pct_b, total = self.get_results()
        
        embed = interaction.message.embeds[0]
        embed.set_field_at(0, name=f"🔴 {self.option_a}", value=f"`{generate_progress_bar(pct_a)}` **{pct_a}%**", inline=False)
        embed.set_field_at(1, name=f"🔵 {self.option_b}", value=f"`{generate_progress_bar(pct_b)}` **{pct_b}%**", inline=False)
        embed.set_footer(text=f"Tổng số phiếu: {total} | Bạn có quyền đổi phiếu nếu muốn!")
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Chọn A", style=discord.ButtonStyle.danger, custom_id="vote_a")
    async def btn_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.voters[interaction.user.id] = 'A'
        await self.update_embed(interaction)

    @discord.ui.button(label="Chọn B", style=discord.ButtonStyle.primary, custom_id="vote_b")
    async def btn_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.voters[interaction.user.id] = 'B'
        await self.update_embed(interaction)

# ==============================================================================
# 🎁 GIAO DIỆN NÚT BẤM: THAM GIA GIVEAWAY
# ==============================================================================
class GiveawayView(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(label="🎉 Tham Gia", style=discord.ButtonStyle.success, custom_id="join_giveaway")
    async def btn_join(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_db()
        gw_data = data.setdefault("system", {}).setdefault("giveaways", {}).get(str(self.message_id))
        
        if not gw_data:
            return await interaction.response.send_message("❌ Sự kiện này đã kết thúc hoặc bị lỗi!", ephemeral=True)
            
        participants = gw_data.setdefault("participants", [])
        if interaction.user.id in participants:
            participants.remove(interaction.user.id)
            save_db(data)
            return await interaction.response.send_message("Đã **HỦY** tham gia sự kiện rút thăm!", ephemeral=True)
            
        participants.append(interaction.user.id)
        save_db(data)
        await interaction.response.send_message("🎉 Đã **THAM GIA** rút thăm thành công! Chúc nhân phẩm độ bạn.", ephemeral=True)

# ==============================================================================
# ⚖️ TÒA ÁN LY HÔN (NÚT BẤM DÀNH CHO BỒI THẨM ĐOÀN)
# ==============================================================================
class DivorceCourtView(discord.ui.View):
    def __init__(self, user1, user2, total_assets, jury_ids):
        super().__init__(timeout=86400) # Tòa xử trong 24h
        self.user1 = user1
        self.user2 = user2
        self.total_assets = total_assets
        self.jury_ids = jury_ids
        self.votes = {}

    async def check_verdict(self, interaction):
        if len(self.votes) == len(self.jury_ids):
            # Tất cả đã bỏ phiếu -> Phán quyết
            v1 = list(self.votes.values()).count('5050')
            v2 = list(self.votes.values()).count('u1')
            v3 = list(self.votes.values()).count('u2')
            
            winner = max({'5050': v1, 'u1': v2, 'u2': v3}.items(), key=lambda x: x[1])[0]
            
            data = load_db()
            u1_data = get_user_data(data, self.user1.id)
            u2_data = get_user_data(data, self.user2.id)
            
            u1_data["cash"] = 0; u1_data["bank"] = 0
            u2_data["cash"] = 0; u2_data["bank"] = 0
            
            msg = "⚖️ **PHÁN QUYẾT TỪ BỒI THẨM ĐOÀN:**\n"
            if winner == '5050':
                half = self.total_assets // 2
                u1_data["cash"] += half
                u2_data["cash"] += half
                msg += f"Tài sản được chia đều! Mỗi người nhận **{half:,} ⭐**."
            elif winner == 'u1':
                u1_data["cash"] += self.total_assets
                msg += f"{self.user1.mention} thắng kiện và cuỗm trọn **{self.total_assets:,} ⭐**!"
            else:
                u2_data["cash"] += self.total_assets
                msg += f"{self.user2.mention} thắng kiện và cuỗm trọn **{self.total_assets:,} ⭐**!"
                
            u1_data["partner"] = None
            u2_data["partner"] = None
            save_db(data)
            
            for child in self.children: child.disabled = True
            await interaction.message.edit(content=msg, view=self)
            
            # Đóng thread
            if isinstance(interaction.channel, discord.Thread):
                await interaction.channel.edit(archived=True, locked=True)

    @discord.ui.button(label="⚖️ Chia 50/50", style=discord.ButtonStyle.secondary)
    async def btn_5050(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.jury_ids: return await interaction.response.send_message("❌ Bạn không phải bồi thẩm đoàn!", ephemeral=True)
        self.votes[interaction.user.id] = '5050'
        await interaction.response.send_message("✅ Đã ghi nhận phiếu bầu!", ephemeral=True)
        await self.check_verdict(interaction)

    @discord.ui.button(label="Đưa hết cho Người Gửi", style=discord.ButtonStyle.primary)
    async def btn_u1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.jury_ids: return
        self.votes[interaction.user.id] = 'u1'
        await interaction.response.send_message("✅ Đã ghi nhận phiếu bầu!", ephemeral=True)
        await self.check_verdict(interaction)

    @discord.ui.button(label="Đưa hết cho Bị Cáo", style=discord.ButtonStyle.danger)
    async def btn_u2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.jury_ids: return
        self.votes[interaction.user.id] = 'u2'
        await interaction.response.send_message("✅ Đã ghi nhận phiếu bầu!", ephemeral=True)
        await self.check_verdict(interaction)

# ==============================================================================
# 🎭 COG: GIAO TIẾP XÃ HỘI & SỰ KIỆN
# ==============================================================================
class SocialInteractions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_task.start()

    def cog_unload(self):
        self.giveaway_task.cancel()

    # ==========================================================================
    # ⏳ TASK CHẠY NGẦM: CHỐNG SẬP GIVEAWAY
    # ==========================================================================
    @tasks.loop(seconds=15)
    async def giveaway_task(self):
        data = load_db()
        giveaways = data.get("system", {}).get("giveaways", {})
        
        expired = []
        now = int(time.time())
        
        for msg_id, gw_info in giveaways.items():
            if now >= gw_info["end_time"]:
                expired.append((msg_id, gw_info))
                
        for msg_id, gw_info in expired:
            try:
                channel = self.bot.get_channel(gw_info["channel_id"])
                msg = await channel.fetch_message(int(msg_id))
                
                participants = gw_info.get("participants", [])
                winners_count = gw_info.get("winners_count", 1)
                
                if len(participants) == 0:
                    await msg.reply("❌ Sự kiện kết thúc nhưng méo có ai tham gia! Hủy quà.")
                else:
                    winners = random.sample(participants, min(len(participants), winners_count))
                    winners_mentions = ", ".join([f"<@{w}>" for w in winners])
                    
                    # Phát quà (Nếu quà là Star)
                    for w in winners:
                        u_data = get_user_data(data, w)
                        if str(gw_info["prize"]).isdigit(): # Nếu là tiền Star
                            u_data["cash"] += int(gw_info["prize"])
                            
                    await msg.reply(f"🎉 **KẾT QUẢ GIVEAWAY!**\nChúc mừng {winners_mentions} đã trúng phần thưởng: **{gw_info['prize']}**!")
                
                # Cập nhật nút bấm hết hạn
                view = discord.ui.View()
                btn = discord.ui.Button(label="Sự kiện đã kết thúc", style=discord.ButtonStyle.secondary, disabled=True)
                view.add_item(btn)
                await msg.edit(view=view)
                
            except Exception as e:
                print(f"Lỗi kết thúc GW: {e}")
                
            # Xóa khỏi DB sau khi xong
            del data["system"]["giveaways"][msg_id]
            
        if expired: save_db(data)

    @giveaway_task.before_loop
    async def before_gw_task(self):
        await self.bot.wait_until_ready()

    # ==========================================================================
    # 🎁 LỆNH KHỞI TẠO GIVEAWAY CHỐNG SẬP
    # ==========================================================================
    @app_commands.command(name="giveaway-start", description="[ADMIN] Tạo sự kiện rút thăm may mắn")
    async def gw_start(self, interaction: discord.Interaction, prize: str, duration_minutes: int, winners: int = 1):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Yêu cầu quyền Admin!", ephemeral=True)
            
        end_time = int(time.time() + (duration_minutes * 60))
        
        embed = discord.Embed(title="🎉 SỰ KIỆN RÚT THĂM MAY MẮN!", description=f"Phần thưởng: **{prize}**\nSố lượng giải: **{winners}**", color=discord.Color.purple())
        embed.add_field(name="⏳ Kết thúc sau:", value=f"<t:{end_time}:R> (<t:{end_time}:f>)", inline=False)
        embed.set_footer(text="Bấm nút bên dưới để ghi danh!")
        
        await interaction.response.send_message("Đang tạo sự kiện...", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        
        # Gắn ID Message vào DB để task ngầm tự canh me
        data = load_db()
        gw_db = data.setdefault("system", {}).setdefault("giveaways", {})
        gw_db[str(msg.id)] = {
            "channel_id": interaction.channel.id,
            "end_time": end_time,
            "prize": prize,
            "winners_count": winners,
            "participants": []
        }
        save_db(data)
        
        await msg.edit(view=GiveawayView(msg.id))

    # ==========================================================================
    # 📊 LỆNH TRƯNG CẦU DÂN Ý (THANH PROGRESS BAR)
    # ==========================================================================
    @app_commands.command(name="vote-create", description="Tạo một cuộc bỏ phiếu cộng đồng")
    async def vote_create(self, interaction: discord.Interaction, question: str, option_a: str, option_b: str):
        embed = discord.Embed(title="📊 TRƯNG CẦU DÂN Ý", description=f"**{question}**", color=discord.Color.dark_theme())
        embed.add_field(name=f"🔴 {option_a}", value=f"`{generate_progress_bar(0)}` **0%**", inline=False)
        embed.add_field(name=f"🔵 {option_b}", value=f"`{generate_progress_bar(0)}` **0%**", inline=False)
        embed.set_footer(text="Tổng số phiếu: 0 | Bạn có quyền đổi phiếu nếu muốn!")
        
        view = VoteView(option_a, option_b)
        await interaction.response.send_message(embed=embed, view=view)

    # ==========================================================================
    # 💍 LỆNH KẾT HÔN & LY HÔN (TÒA ÁN THREAD ẨN)
    # ==========================================================================
    @commands.command(name="marry")
    async def marry(self, ctx, target: discord.Member):
        if target.id == ctx.author.id or target.bot:
            return await ctx.send("❌ Bị tự kỷ hay gì mà đòi cưới Bot hoặc cưới chính mình?")
            
        data = load_db()
        u1 = get_user_data(data, ctx.author.id)
        u2 = get_user_data(data, target.id)
        
        if u1["partner"] or u2["partner"]:
            return await ctx.send("❌ Một trong hai người đã có gia đình! Bot không ủng hộ ngoại tình.")
            
        await ctx.send(f"💍 {target.mention}, bạn có đồng ý kết nghĩa phu thê với {ctx.author.mention} không? Gõ `dong y` hoặc `tu choi` trong 30s.")
        
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=lambda m: m.author == target and m.channel == ctx.channel)
            if msg.content.lower() in ["dong y", "đồng ý"]:
                u1["partner"] = target.id
                u2["partner"] = ctx.author.id
                save_db(data)
                await ctx.send(f"🎉 Chúc mừng 2 người <@{ctx.author.id}> và <@{target.id}> đã thành phu thê! Giờ đây giao thương giữa 2 người sẽ được giảm thuế ngầm.")
            else:
                await ctx.send("💔 Lời cầu hôn đã bị từ chối khéo léo...")
        except asyncio.TimeoutError:
            await ctx.send("⏳ Hết thời gian suy nghĩ, lời cầu hôn bị hủy!")

    @commands.command(name="divorce")
    async def divorce(self, ctx):
        data = load_db()
        u1 = get_user_data(data, ctx.author.id)
        
        partner_id = u1.get("partner")
        if not partner_id:
            return await ctx.send("❌ Bạn ế lòi mồm ra thì đòi ly hôn với ai?")
            
        try:
            partner = await ctx.guild.fetch_member(partner_id)
        except:
            # Partner rời server -> Đơn phương ly hôn
            u1["partner"] = None
            save_db(data)
            return await ctx.send("🗑️ Vợ/Chồng bạn đã bỏ trốn khỏi Server. Hệ thống tự động phê duyệt đơn ly hôn đơn phương!")
            
        # TÍNH TỔNG TÀI SẢN ĐỂ TRANH CHẤP
        u2 = get_user_data(data, partner_id)
        total_assets = u1["cash"] + u1["bank"] + u2["cash"] + u2["bank"]
        
        # Bốc ngẫu nhiên 3 người trong server (trừ 2 đứa ly hôn và bot) làm bồi thẩm đoàn
        members = [m for m in ctx.guild.members if not m.bot and m.id not in [ctx.author.id, partner_id]]
        jury = random.sample(members, min(3, len(members)))
        jury_ids = [j.id for j in jury]
        jury_mentions = " ".join([j.mention for j in jury])
        
        # Mở Thread Tòa Án
        thread = await ctx.channel.create_thread(name=f"⚖️ Tòa Án Ly Hôn: {ctx.author.name} vs {partner.name}", type=discord.ChannelType.public_thread)
        
        embed = discord.Embed(title="🏛️ KHAI ĐÌNH: PHÂN CHIA TÀI SẢN", color=discord.Color.red())
        embed.description = f"**Nguyên cáo:** {ctx.author.mention}\n**Bị cáo:** {partner.mention}\n**Tổng tài sản tranh chấp:** `{total_assets:,} ⭐`"
        embed.add_field(name="👨‍⚖️ Ban Bồi Thẩm Đoàn (Quyền Phán Quyết)", value=f"Mời {jury_mentions} vào ném đá bỏ phiếu chia tài sản!")
        
        view = DivorceCourtView(ctx.author, partner, total_assets, jury_ids)
        await thread.send(f"{ctx.author.mention} {partner.mention} {jury_mentions}", embed=embed, view=view)
        await ctx.send(f"🚨 **Phiên tòa tranh chấp đã được mở tại đây:** {thread.mention}")

async def setup(bot):
    await bot.add_cog(SocialInteractions(bot))
