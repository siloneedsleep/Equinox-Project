import subprocess
import time
import sys
import os
from flask import Flask
from threading import Thread

# ==============================================================================
# 🎛️ BỘ KHỞI TẠO WEB SERVER GIẢ LẬP ĐỂ ĐÁNH LỪA RENDER
# ==============================================================================
app = Flask('keep_alive')

@app.route('/')
def home():
    return "🚀 Equinox Network Ecosystem is Live and Running!"

def run_server():
    # Render tự động cấp cổng qua biến PORT, mặc định chạy 10000 hoặc 8080 nếu chạy local
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# Kích hoạt web server mở cổng ngay lập tức trước khi chạy tiến trình Bot
keep_alive()

# ==============================================================================
# 🚀 LUỒNG ĐIỀU PHỐI VÀ KHỞI CHẠY HỆ SINH THÁI BOT COUPLE
# ==============================================================================
def start_bot(script_name, color_code):
    print(f"{color_code}Đang kích hoạt tiến trình: {script_name}... \033[0m")
    return subprocess.Popen([sys.executable, script_name])

if __name__ == "__main__":
    print("🚀 EQUINOX NETWORK - BOOT SEQUENCE INITIATED 🚀\n")
    
    # Kích hoạt song song 2 tiến trình trên cùng 1 host
    luminous_process = start_bot("luminous_main.py", "\033[93m")  # Yellow
    time.sleep(2) # Tránh nghẽn kết nối Redis cùng một tích tắc
    tenebris_process = start_bot("tenebris_main.py", "\033[95m")  # Purple
    
    try:
        luminous_process.wait()
        tenebris_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 SHUTTING DOWN EQUINOX NETWORK...")
        luminous_process.terminate()
        tenebris_process.terminate()
        print("✅ Đã tắt toàn bộ hệ thống.")
