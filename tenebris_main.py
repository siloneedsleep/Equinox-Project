import os
import datetime
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv 
load_dotenv()
from config.settings import TOKENS, LUMINOUS_ID, TENEBRIS_ID
from database.redis_client import get_redis_connection, init_redis_system

intents = discord.Intents.all()

class TenebrisBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="t!", intents=intents, help_command=None)

    async def setup_hook(self):
        await init_redis_system() 
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_dir = os.path.join(current_dir, 'cogs_shared')
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    try:
                        await self.load_extension(f'cogs_shared.{filename[:-3]}')
                        print(f"📦 [Tenebris] Đã nạp extension: {filename}")
                    except Exception as e:
                        print(f"❌ [Tenebris] Lỗi nạp extension {filename}: {e}")
        
        try:
            await self.tree.sync()
            print("🚀 [Tenebris] Đã đồng bộ hóa thành công ma trận lệnh Slash!")
        except Exception as e:
            print(f"❌ [Tenebris] Lỗi sync tree: {e}")

bot = TenebrisBot()
LUMINOUS_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={LUMINOUS_ID}&permissions=8&scope=bot%20applications.commands"

def get_realtime_cycle():
    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    return "DAY" if 0 <= now.hour < 12 else "NIGHT"

@bot.check
async def global_tenebris_check(ctx):
    r = await get_redis_connection()
    
    # TRẢ VỀ NGUYÊN BẢN: So sánh chuỗi trực tiếp, dẹp bỏ decode gây chập mạch
    if await r.hget("equinox:system:shutdown_status", "tenebris") == "SHUTDOWN":
        return False 
        
    if await r.get("equinox:system:global_lock") or await r.get("equinox:system:reboot_lock"):
        return False
        
    if ctx.guild and not ctx.guild.get_member(LUMINOUS_ID):
        class InviteView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.add_item(discord.ui.Button(label="Triệu Hồi Luminous (Admin) ☀️", url=LUMINOUS_INVITE_URL, style=discord.ButtonStyle.link))

        embed = discord.Embed(
            title="⚠️ HỆ SINH THÁI CHƯA HOÀN CHỈNH! ⚠️",
            description=f"Chợ Đen Tenebris không thể giao dịch lậu if thiếu đi Ánh Sáng bảo kê của cô vợ **<@{LUMINOUS_ID}>** phía sau.\n\nHãy bấm nút bên dưới để rước nốt bả về quản lý giùm cái sếp!",
            color=0x4B0082
        )
        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed, view=InviteView(), delete_after=30)
        return False

    if await r.hget("equinox:system:config", "event_overdrive") != "ON":
        cycle = get_realtime_cycle()
        if cycle == "DAY" and ctx.command.name not in ["staff", "profile", "marry", "check-marry"]:
            await ctx.send("☀️ Đang là ca ngày (00:00 - 12:00). Nhìn lại đồng hồ hộ cái! Vợ tao đang trực, biến ra chỗ khác!")
            return False
    return True

@bot.event
async def on_ready():
    print(f"🔮 {bot.user.name} đã thức tỉnh trực tuyến!")
    r = await get_redis_connection()
    
    try:
        app_info = await bot.application_info()
        owner_id = app_info.owner.id
        
        env_owner = os.getenv("OWNER_DISCORD_ID")
        if env_owner:
            owner_id = int(env_owner)
            
        await r.sadd("equinox:staff:owners", owner_id)
        print(f"👑 [Thế Giới Ngầm] Đã nhận diện Owner tối cao: {owner_id}")
    except Exception as e:
        print(f"❌ Lỗi gác cổng nhân sự ca đêm: {e}")
        
    if not tenebris_presence_task.is_running():
        tenebris_presence_task.start()

@tasks.loop(seconds=15)
async def tenebris_presence_task():
    r = await get_redis_connection()
    cycle = get_realtime_cycle()
    await r.hset("equinox:system:config", "current_cycle", cycle)
    
    if await r.hget("equinox:system:config", "event_overdrive") == "ON":
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="⚡ BIG EVENT OVERDRIVE ⚡"))
        return
        
    if cycle == "NIGHT":
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="🔮 Chợ Đen đã mở cửa | t!help"))
    else:
        await bot.change_presence(status=discord.Status.dnd, activity=discord.CustomActivity(name="🌙 Đang ngủ trong Bóng Tối..."))

@tenebris_presence_task.before_loop
async def before_presence(): 
    await bot.wait_until_ready()

# SỬA CHÍ MẠNG: Trả lại đúng nguồn Token bốc từ file config của sếp
bot.run(TOKENS["TENEBRIS"])
