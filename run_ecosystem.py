import subprocess
import time
import sys

def start_bot(script_name, color_code):
    print(f"{color_code}Đang kích hoạt tiến trình: {script_name}... \033[0m")
    return subprocess.Popen([sys.executable, script_name])

if __name__ == "__main__":
    print("🚀 EQUINOX NETWORK - BOOT SEQUENCE INITIATED 🚀\n")
    
    # Kích hoạt song song 2 tiến trình trên cùng 1 host
    luminous_process = start_bot("luminous_main.py", "\033[93m")  # Yellow
    time.sleep(2) # Tránh nghẽn connect Redis cùng 1 tích tắc
    tenebris_process = start_bot("tenebris_main.py", "\033[95m")  # Purple
    
    try:
        luminous_process.wait()
        tenebris_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 SHUTTING DOWN EQUINOX NETWORK...")
        luminous_process.terminate()
        tenebris_process.terminate()
        print("✅ Đã tắt toàn bộ hệ thống.")
