import os
import datetime
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv 
load_dotenv()
from config.settings import TOKENS, LUMINOUS_ID, TENEBRIS_ID
from database.redis_client import get_redis_connection, init_redis_system

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="t!", intents=intents, help_command=None)
LUMINOUS_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={LUMINOUS_ID}&permissions=8&scope=bot%20applications.commands"

def get_realtime_cycle():
    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    return "DAY" if 0 <= now.hour < 12 else "NIGHT"

async def tenebris_setup_hook():
    await init_redis_system() 
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cogs_dir = os.path.join(current_dir, 'cogs_shared')
    if os.path.exists(cogs_dir):
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await bot.load_extension(f'cogs_shared.{filename[:-3]}')
                    print(f"📦 [Tenebris] Đã nạp extension: {filename}")
                # FIX LỖI 9: Cấm nuốt bug nạp cogs
                except commands.ExtensionNotFound:
                    print(f"❌ [Tenebris] Không tìm thấy extension: {filename}")
                except commands.ExtensionFailed as e:
                    print(f"❌ [Tenebris] Extension bị lỗi {filename}: {e}")
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"❌ [Tenebris] Lỗi sync tree: {e}")

bot.setup_hook = tenebris_setup_hook

@bot.check
async def global_tenebris_check(ctx):
    r = await get_redis_connection()
    if await r.hget("equinox:system:shutdown_status", "tenebris") == "SHUTDOWN": return False 
    if await r.get("equinox:system:global_lock") or await r.get("equinox:system:reboot_lock"): return False
    
    if ctx.command:
        if await r.hget("equinox:system:config", "event_overdrive") != "ON":
            cycle = get_realtime_cycle()
            if cycle == "DAY" and ctx.command.name not in ["staff", "profile", "marry", "check-marry"]:
                await ctx.send("☀️ Đang là ca ngày. Vợ tao đang trực, biến ra chỗ khác!")
                return False
    return True

@bot.event
async def on_ready():
    print(f"🔮 {bot.user.name} đã thức tỉnh trực tuyến!")
    if not tenebris_presence_task.is_running():
        tenebris_presence_task.start()

@tasks.loop(seconds=15)
async def tenebris_presence_task():
    r = await get_redis_connection()
    old_cycle = await r.hget("equinox:system:config", "current_cycle") or "NIGHT"
    cycle = get_realtime_cycle()
    
    # FIX LỖI 4: Gài khóa Global Lock 5 giây khi chuyển ca
    if cycle != old_cycle:
        await r.setex("equinox:system:global_lock", 5, "1")
        
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

# FIX LỖI 1: XÓA LỆNH bot.run() Ở CUỐI FILE. Nhường quyền cho run_ecosystem.py
