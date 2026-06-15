import redis.asyncio as redis
from config.settings import REDIS_URI

# Khởi tạo Pool kết nối Redis toàn cục
redis_pool = redis.ConnectionPool.from_url(REDIS_URI, decode_responses=True)

async def get_redis_connection():
    """Gọi kết nối Redis dùng chung cho toàn bộ dự án"""
    return redis.Redis(connection_pool=redis_pool)

async def init_redis_system():
    """Khởi tạo các biến hạch tâm mặc định nếu DB mới tinh"""
    r = await get_redis_connection()
    
    # 1. Mạch luân hồi Ngày/Đêm (Mặc định bắt đầu là DAY)
    if not await r.hexists("equinox:system:config", "current_cycle"):
        await r.hset("equinox:system:config", "current_cycle", "DAY")
    
    # 2. Cờ hiệu Sự Kiện Lớn (Big Event Overdrive)
    if not await r.hexists("equinox:system:config", "event_overdrive"):
        await r.hset("equinox:system:config", "event_overdrive", "OFF")

    # 3. Trạng thái Shutdown khẩn cấp (Nút bấm hạt nhân)
    if not await r.hexists("equinox:system:shutdown_status", "luminous"):
        await r.hset("equinox:system:shutdown_status", "luminous", "ACTIVE")
    if not await r.hexists("equinox:system:shutdown_status", "tenebris"):
        await r.hset("equinox:system:shutdown_status", "tenebris", "ACTIVE")
        
    print("☁️ Đã đồng bộ các biến hạch tâm lên Redis thành công!")
