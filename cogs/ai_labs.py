import discord
from discord.ext import commands
from discord import app_commands
import json
import uuid

# ==============================================================================
# 🧰 TỪ ĐIỂN CATALOG AI VÀ HÀM TIỆN ÍCH
# ==============================================================================
# Bảng giá niêm yết các đời máy (Phí nâng cấp cộng thêm vào 1,000,000 ⭐ gốc)
AI_CATALOG = {
    "openai": [
        {"label": "GPT-3.5 Turbo", "desc": "Miễn phí nâng cấp", "value": "gpt-3.5-turbo", "fee": 0},
        {"label": "GPT-4o (Cao Cấp)", "desc": "+200,000 ⭐ Phí nâng cấp", "value": "gpt-4o", "fee": 200000},
        {"label": "GPT-4-32k (Siêu Cấp)", "desc": "+500,000 ⭐ Phí nâng cấp", "value": "gpt-4-32k", "fee": 500000}
    ],
    "claude": [
        {"label": "Claude 3 Haiku", "desc": "Miễn phí nâng cấp", "value": "claude-3-haiku", "fee": 0},
        {"label": "Claude 3.5 Sonnet", "desc": "+300,000 ⭐ Phí nâng cấp", "value": "claude-3-5-sonnet", "fee": 300000},
        {"label": "Claude 3 Opus", "desc": "+700,000 ⭐ Tối Thượng", "value": "claude-3-opus", "fee": 700000}
    ],
    "gemini": [
        {"label": "Gemini 1.5 Flash", "desc": "Miễn phí nâng cấp", "value": "gemini-1.5-flash", "fee": 0},
        {"label": "Gemini 1.5 Pro", "desc": "+250,000 ⭐ Phí nâng cấp", "value": "gemini-1.5-pro", "fee": 250000},
        {"label": "Gemini Ultra", "desc": "+600,000 ⭐ Đỉnh Cao", "value": "gemini-ultra", "fee": 600000}
    ],
    "groq": [
        {"label": "Llama 3 8b (Groq)", "desc": "Miễn phí nâng cấp", "value": "llama3-8b", "fee": 0},
        {"label": "Llama 3 70b (Groq)", "desc": "+100,000 ⭐ Tốc độ ánh sáng", "value": "llama3-70b", "fee": 100000},
        {"label": "Mixtral 8x7b", "desc": "+150,000 ⭐ Phí nâng cấp", "value": "mixtral-8x7b", "fee": 150000}
    ],
    "cohere": [
        {"label": "Command Light", "desc": "Miễn phí nâng cấp", "value": "command-light", "fee": 0},
        {"label": "Command R", "desc": "+150,000 ⭐ Phí nâng cấp", "value": "command-r", "fee": 150000},
        {"label": "Command R+", "desc": "+350,000 ⭐ Dành cho Doanh nghiệp", "value": "command-r-plus", "fee": 350000}
    ],
    "mistral": [
        {"label": "Mistral 7B", "desc": "Miễn phí nâng cấp", "value": "mistral-7b", "fee": 0},
        {"label": "Mixtral 8x22B", "desc": "+200,000 ⭐ Phí nâng cấp", "value": "mixtral-8x22b", "fee": 200000},
        {"label": "Mistral Large", "desc": "+450,000 ⭐ Phí nâng cấp", "value": "mistral-large", "fee": 450000}
    ],
    "openrouter": [
        {"label": "Auto-Routing (Free)", "desc": "Miễn phí", "value": "openrouter-free", "fee": 0},
        {"label": "Premium Routing", "desc": "+300,000 ⭐ Phí nâng cấp", "value": "openrouter-premium", "fee": 300000}
    ],
    "together": [
        {"label": "Llama Free", "desc": "Miễn phí", "value": "together-free", "fee": 0},
        {"label": "Premium Models", "desc": "+200,000 ⭐ Phí nâng cấp", "value": "together-premium", "fee": 200000}
    ]
}

def load_db():
    try:
        with open("storage.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(data):
    with open("storage.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 🧩 GIAO DIỆN MODAL: BIỂU MẪU CHIA SẺ AI XUYÊN MÁY CHỦ
# ==============================================================================
class AIShareModal(discord.ui.Modal, title='📝 Hồ Sơ Cấp Phép AI Lên Sàn Nhà Chính'):
    ai_name_input = discord.ui.TextInput(label='Tên Hiển Thị Trên Chợ', placeholder='Ví dụ: Ma Tôn Giải Toán...', max_length=50)
    ai_bio = discord.ui.TextInput(label='Tiểu Sử & Công Dụng', style=discord.TextStyle.paragraph, placeholder='Giới thiệu độ bá đạo của con AI này...', max_length=300)
    ai_type = discord.ui.TextInput(label='Phân Loại (Tag)', placeholder='Học Tập / Tâm Sự / Code / Bói Toán', max_length=30)

    def __init__(self, bot, ai_id, hq_forum_id):
        super().__init__()
        self.bot = bot
        self.ai_id = ai_id
        self.hq_forum_id = hq_forum_id

    async def on_submit(self, interaction: discord.Interaction):
        data = load_db()
        ai_data = data["system"]["custom_ais"][self.ai_id]
        
        forum_channel = self.bot.get_channel(self.hq_forum_id)
        if not forum_channel or not isinstance(forum_channel, discord.ForumChannel):
            return await interaction.response.send_message("❌ Kênh Diễn Đàn Nhà Chính chưa được sếp Setup hoặc bị lỗi!", ephemeral=True)
        
        embed = discord.Embed(title=f"🤖 {self.ai_name_input.value}", description=self.ai_bio.value, color=discord.Color.gold())
        embed.add_field(name="🧠 Bộ Não (Đời máy)", value=f"`{ai_data['provider'].upper()} - {ai_data['model_version']}`", inline=False)
        embed.add_field(name="🏷️ Phân Loại", value=f"*{self.ai_type.value}*", inline=True)
        embed.add_field(name="👑 Chủ Sở Hữu", value=f"<@{ai_data['creator_id']}>", inline=True)
        embed.set_footer(text="Bấm nút bên dưới để trải nghiệm ngay hoàn toàn miễn phí!")

        view = discord.ui.View()
        btn = discord.ui.Button(label="Chat Thử Với AI Này", style=discord.ButtonStyle.primary, custom_id=f"chat_test_{self.ai_id}")
        view.add_item(btn)

        thread_post = await forum_channel.create_thread(
            name=f"⭐ [{self.ai_type.value}] - {self.ai_name_input.value}",
            embed=embed,
            view=view
        )
        
        ai_data["is_shared"] = True
        ai_data["forum_post_id"] = thread_post.thread.id
        save_db(data)

        if interaction.guild_id == forum_channel.guild.id:
            await interaction.response.send_message(f"✅ Lên sàn thành công! Xem bài viết của bạn tại: {thread_post.thread.mention}")
        else:
            await interaction.response.send_message(
                f"✨ **Thực thể AI của bạn đã được trưng bày tại Sàn Diễn Đàn Hoàng Gia!**\n"
                f"🏰 Tham gia ngay Server Nhà Chính để hóng review: `[GẮN_LINK_SERVER_CỦA_SẾP_VÀO_ĐÂY]`\n"
                f"📌 Xem trực tiếp bài đăng tại đây: {thread_post.thread.jump_url}", 
                ephemeral=True
            )

# ==============================================================================
# 🧩 MENU CHỌN ĐỜI MÁY (TỰ ĐỘNG LẤY TỪ DICTIONARY THEO HÃNG)
# ==============================================================================
class AIModelSelect(discord.ui.Select):
    def __init__(self, provider):
        self.provider = provider
        # Quét lấy danh sách đời máy từ Catalog
        models = AI_CATALOG.get(provider, [{"label": "Mô hình mặc định", "desc": "Miễn phí", "value": "default", "fee": 0}])
        
        options = []
        for m in models:
            options.append(discord.SelectOption(label=m["label"], description=m["desc"], value=m["value"]))
            
        super().__init__(placeholder=f"Bước 2: Chọn Đời Máy {provider.upper()}...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        
        # Tìm mức giá của đời máy vừa chọn
        models = AI_CATALOG.get(self.provider, [])
        upgrade_fee = 0
        for m in models:
            if m["value"] == selected_value:
                upgrade_fee = m["fee"]
                break
                
        total_fee = 1000000 + upgrade_fee  # Cố định phí nền móng là 1 Triệu Star

        # Xóa dropdown, hiện nút xác nhận thanh toán
        btn = discord.ui.Button(label=f"🧪 KÍCH HOẠT PHÒNG THÍ NGHIỆM (-{total_fee:,} ⭐)", style=discord.ButtonStyle.danger)
        
        async def confirm_callback(inter: discord.Interaction):
            if inter.user.id != self.view.user.id: return
            
            data = load_db()
            user_data = data.setdefault("users", {}).setdefault(str(inter.user.id), {"cash": 0})
            
            if user_data.get("cash", 0) < total_fee:
                return await inter.response.send_message(f"❌ Bạn chỉ có {user_data.get('cash', 0):,} ⭐, không đủ tiền đúc thực thể này!", ephemeral=True)
            
            user_data["cash"] -= total_fee
            ai_id = f"AI_{str(uuid.uuid4())[:8].upper()}"
            ai_vault = data.setdefault("system", {}).setdefault("custom_ais", {})
            ai_vault[ai_id] = {
                "ai_name": self.view.ai_name,
                "creator_id": inter.user.id,
                "provider": self.provider,
                "model_version": selected_value,
                "system_prompt": self.view.ai_prompt,
                "is_shared": False,
                "forum_post_id": None
            }
            save_db(data)
            
            embed = discord.Embed(title="🎉 KÍCH HOẠT THỰC THỂ AI ĐỘC BẢN THÀNH CÔNG!", color=discord.Color.green())
            embed.description = f"Chủ nhân <@{inter.user.id}>, thực thể **{self.view.ai_name}** đã được đúc thành công."
            embed.add_field(name="🔮 Thông số", value=f"• Lõi: `{self.provider.upper()} - {selected_value}`\n• Đặc quyền: **Xài vô hạn, Miễn phí 100% phí chat!**", inline=False)
            embed.add_field(name="📜 Sổ tay điều hành", value="`1.` `/ai-chat` : Trò chuyện\n`2.` `/ai-setting` : Đổi Prompt\n`3.` `/ai-share` : Trưng bày lên Chợ Diễn Đàn Nhà Chính", inline=False)
            
            await inter.response.edit_message(content=None, embed=embed, view=None)

        btn.callback = confirm_callback
        self.view.clear_items()
        self.view.add_item(btn)
        await interaction.response.edit_message(content="**💳 XÁC NHẬN THANH TOÁN GIAO DỊCH VĨ MÔ:**", view=self.view)

# ==============================================================================
# 🧩 MENU CHỌN HÃNG AI (CHỈ HIỂN THỊ HÃNG NÀO SẾP ĐÃ NẠP KEY)
# ==============================================================================
class AIProviderSelect(discord.ui.Select):
    def __init__(self, available_providers):
        # Tự động map tên hãng cho đẹp dựa trên danh sách Key quét được từ Database
        provider_names = {
            "openai": "OpenAI (ChatGPT)", "claude": "Anthropic (Claude)", "gemini": "Google (Gemini)",
            "groq": "Groq (Siêu Tốc)", "cohere": "Cohere", "mistral": "Mistral AI", 
            "openrouter": "OpenRouter", "together": "Together AI"
        }
        
        options = []
        for p in available_providers:
            label = provider_names.get(p, p.upper())
            options.append(discord.SelectOption(label=label, value=p, description=f"Nền tảng {label}"))
            
        super().__init__(placeholder="Bước 1: Chọn Nền Tảng (Chỉ hiện hãng đã có Key)...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.clear_items()
        self.view.add_item(AIModelSelect(self.values[0])) 
        await interaction.response.edit_message(view=self.view)

class AICreateView(discord.ui.View):
    def __init__(self, user, ai_name, ai_prompt, available_providers):
        super().__init__(timeout=120)
        self.user = user
        self.ai_name = ai_name
        self.ai_prompt = ai_prompt
        self.add_item(AIProviderSelect(available_providers))

# ==============================================================================
# 🧠 COG: LÕI PHÒNG THÍ NGHIỆM AI (AI LABS)
# ==============================================================================
class AILabs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="system-aisetshelf", description="[OWNER/DEV] Setup kênh Forum tại Nhà Chính để trưng bày AI")
    async def sys_aisetshelf(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        data = load_db()
        sys_data = data.get("system", {})
        if interaction.user.id not in [sys_data.get("owner_id"), sys_data.get("developer")]:
            return await interaction.response.send_message("❌ Từ chối truy cập!", ephemeral=True)
            
        sys_data["ai_forum_channel_id"] = channel.id
        save_db(data)
        await interaction.response.send_message(f"✅ Đã thiết lập Trạm Diễn Đàn AI tại: {channel.mention}", ephemeral=True)

    @app_commands.command(name="ai-create", description="[1,000,000 ⭐] Đúc thực thể AI riêng biệt xài vô hạn")
    async def ai_create(self, interaction: discord.Interaction, ai_name: str, ai_prompt: str):
        data = load_db()
        vault = data.get("system", {}).get("ai_vault", {})
        
        # Lõi Quét Database thông minh: Lấy ra danh sách các Key đang có
        available_providers = list(vault.keys())
        
        # Nếu sếp chưa nạp 1 cái key nào qua lệnh /system-addkey
        if not available_providers:
            return await interaction.response.send_message("⚠️ Sếp Tổng chưa nạp bất kỳ nguyên liệu API Key nào vào kho! Tính năng tạm khóa.", ephemeral=True)

        view = AICreateView(interaction.user, ai_name, ai_prompt, available_providers)
        await interaction.response.send_message(f"🧪 **PHÒNG THÍ NGHIỆM LUMINOUS AI**\n*Đang chuẩn bị đúc thực thể: `{ai_name}`*", view=view, ephemeral=True)

    @app_commands.command(name="ai-share", description="Bật/Tắt chế độ chia sẻ Thực thể AI lên Chợ Diễn Đàn Nhà Chính")
    @app_commands.choices(action=[
        app_commands.Choice(name="BẬT Chia sẻ (ON)", value="on"),
        app_commands.Choice(name="TẮT Chia sẻ (OFF)", value="off")
    ])
    async def ai_share(self, interaction: discord.Interaction, action: str):
        data = load_db()
        ai_dict = data.get("system", {}).get("custom_ais", {})
        hq_forum_id = data.get("system", {}).get("ai_forum_channel_id")
        
        user_ai_id = next((aid for aid, info in ai_dict.items() if info["creator_id"] == interaction.user.id), None)
        if not user_ai_id:
            return await interaction.response.send_message("❌ Bạn chưa sở hữu thực thể AI nào!", ephemeral=True)
            
        ai_info = ai_dict[user_ai_id]

        if action == "on":
            if ai_info.get("is_shared"):
                return await interaction.response.send_message("⚠️ Thực thể của bạn đã ở trên sàn rồi!", ephemeral=True)
            if not hq_forum_id:
                return await interaction.response.send_message("⚠️ Nhà Chính chưa thiết lập Sàn giao dịch AI!", ephemeral=True)
                
            await interaction.response.send_modal(AIShareModal(self.bot, user_ai_id, hq_forum_id))
            
        else:
            if not ai_info.get("is_shared"):
                return await interaction.response.send_message("⚠️ Bạn đã rút AI khỏi sàn rồi mà!", ephemeral=True)
                
            post_id = ai_info.get("forum_post_id")
            if post_id:
                try:
                    forum = self.bot.get_channel(hq_forum_id)
                    thread = forum.get_thread(post_id)
                    if thread: await thread.delete()
                except Exception:
                    pass
            
            ai_info["is_shared"] = False
            ai_info["forum_post_id"] = None
            save_db(data)
            await interaction.response.send_message("🚮 Đã rút thực thể AI của bạn khỏi Sàn Diễn Đàn!", ephemeral=True)

    @app_commands.command(name="ai-chat", description="Trò chuyện miễn phí vô hạn với AI của bạn")
    async def ai_chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        await interaction.followup.send(f"*(API Đang gọi ngầm đến não bộ AI của sếp...)*\n**User:** {message}\n**AI:** Xin chào chủ nhân! Tui là bản thể AI độc quyền của ngài!")

async def setup(bot):
    await bot.add_cog(AILabs(bot))
