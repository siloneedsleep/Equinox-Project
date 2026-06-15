import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# ⚙️ CẤU HÌNH HẠCH TÂM EQUINOX NETWORK
# ==========================================

TOKENS = {
    "LUMINOUS": os.getenv("LUMINOUS_TOKEN"),
    "TENEBRIS": os.getenv("TENEBRIS_TOKEN")
}

LUMINOUS_ID = 1489963153855877180  
TENEBRIS_ID = 1496524822023503882  

# KẾT NỐI REDIS ĐÁM MÂY
REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379/0")

# HẠN NGẠCH SLOT NHÂN SỰ ĐIỀU HÀNH
STAFF_LIMITS = {
    "owner": 1,
    "dev": 2,
    "admin": 3,
    "event_manager": 2,
    "staff": 10
}

# CẤU HÌNH MÀU SẮC ĐẶC TRƯNG (HEX COLORS)
COLORS = {
    "luminous_main": 0xFFD700,   # Vàng Kim Hoàng Gia
    "luminous_love": 0xFFB6C1,   # Vàng Hồng Lãng Mạn
    "luminous_info": 0x00FFFF,   # Xanh Dương Bình Yên
    "luminous_error": 0xFF0055,  # Đỏ Neon Cảnh Báo
    "tenebris_main": 0x1A1A1A,   # Đen Obsidian
    "tenebris_love": 0x2E0854,   # Tím Đen Huyền Bí
    "tenebris_action": 0x4B0082, # Tím Đậm Hắc Ám
    "tenebris_error": 0x8B0000,  # Đỏ Đậm Máu
}
