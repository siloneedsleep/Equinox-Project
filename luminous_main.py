import os
import datetime
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
from config.settings import TOKENS, LUMINOUS_ID, TENEBRIS_ID
from database.redis_client import get_redis_connection, init_redis_system

intents = discord.Intents.all()

class LuminousBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="l!", intents=intents, help_command=None)

    async def setup_hook(self):
        await init_redis_system() 
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_dir = os.path.join(current_dir, 'cogs_shared')
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    try:
                        await self.load_extension(f'cogs_shared.{filename[:-3]}')
                        print(f"☀️ [Luminous] Đã nạp extension: {filename}")
                    except Exception as e:
                        print(f"❌ [Luminous] Lỗi nạp extension {filename}: {e}")
        
        try:
            await self.tree.sync()
            print("🚀 [Luminous] Đã đồng bộ hóa thành công ma trận lệnh Slash!")
        except Exception as e:
            print(f"❌ [Luminous] Lỗi sync tree: {e}")

bot = LuminousBot()
TENEBRIS_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={TENEBRIS_ID}&permissions=8&scope=bot%20applications.commands"

def get_realtime_cycle():
    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    return "DAY" if 0 <= now.hour < 12 else "NIGHT"

@bot.check
async def global_luminous_check(ctx):
    r = await get_redis_connection()
    
    # TRẢ VỀ NGUYÊN BẢN: So sánh chuỗi trực tiếp, dẹp bỏ decode gây chập mạch
    if await r.hget("equinox:system:shutdown_status", "luminous") == "SHUTDOWN":
        return False
        
    if await r.get("equinox:system:global_lock") or await r.get("equinox:system:reboot_lock"):
        return False
        
    if ctx.guild and not ctx.guild.get_member(TENEBRIS_ID):
        class InviteView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.add_item(discord.ui.Button(label="Triệu Hồi Tenebris (Admin) 🔮", url=TENEBRIS_INVITE_URL, style=discord.ButtonStyle.link))

        embed = discord.Embed(
            title="⚠️ HỆ SINH THÁI CHƯA HOÀN CHỈNH! ⚠️",
            description=f"Thần Điện Luminous không thể vận hành đơn độc nếu thiếu đi vòng tay bảo vệ của ông xã **<@{TENEBRIS_ID}>**.\n\nHãy bấm nút bên dưới để rước nốt chồng em về chung một nhà sếp ơi!",
            color=0xFF0055
        )
        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed, view=InviteView(), delete_after=30)
        return False

    if await r.hget("equinox:system:config", "event_overdrive") != "ON":
        cycle = get_realtime_cycle()
        if cycle == "NIGHT" and ctx.command.name not in ["staff", "profile", "marry", "check-marry"]:
            await ctx.send("🌙 Đang là ca đêm (12:00 - 00:00). Trạm Ánh Sáng đã khép cửa... Vui lòng sang thế giới ngầm của Tenebris (t!).")
            return False
    return True

@bot.event
async def on_ready():
    print(f"☀️ {bot.user.name} đã thức tỉnh trực tuyến!")
    r = await get_redis_connection()
    
    try:
        app_info = await bot.application_info()
        owner_id = app_info.owner.id
        
        env_owner = os.getenv("OWNER_DISCORD_ID")
        if env_owner:
            owner_id = int(env_owner)
            
        await r.sadd("equinox:staff:owners", owner_id)
        print(f"👑 [Hạch Tâm] Đã nhận diện Owner tối cao: {owner_id}")
    except Exception as e:
        print(f"❌ Lỗi gác cổng nhân sự ca ngày: {e}")
        
    if not luminous_presence_task.is_running():
        luminous_presence_task.start()

@tasks.loop(seconds=15)
async def luminous_presence_task():
    r = await get_redis_connection()
    cycle = get_realtime_cycle()
    await r.hset("equinox:system:config", "current_cycle", cycle)
    
    if await r.hget("equinox:system:config", "event_overdrive") == "ON":
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="⚡ BIG EVENT OVERDRIVE ⚡"))
        return
        
    if cycle == "DAY":
        await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name="☀️ Đang chiếu sáng Thần Điện | l!help"))
    else:
        await bot.change_presence(status=discord.Status.dnd, activity=discord.CustomActivity(name="💤 Trạm Ánh Sáng đang ngủ sâu."))

@luminous_presence_task.before_loop
async def before_presence(): 
    await bot.wait_until_ready()

# SỬA CHÍ MẠNG: Trả lại đúng nguồn Token bốc từ file config của sếp
bot.run(TOKENS["LUMINOUS"])
