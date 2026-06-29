# 🪐 Equinox Network V2 - The Revolutionary Ecosystem

**Equinox Network V2** là bản tái cấu trúc toàn diện từ nền tảng V1, chuyển dịch sang kiến trúc **Event-Driven (Hướng sự kiện)** và **Decoupling (Tách biệt Logic/UI)**. Hệ thống vận hành song song hai thực thể bot đối lập trên cùng một mã nguồn, tạo nên một thế giới ngầm đầy kịch tính và một hoàng gia sang trọng.

**Chủ sở hữu hệ sinh thái:** **Silo**

---

## 🏛️ Kiến Trúc Hệ Thống (Modular Design)

Dự án được xây dựng theo cấu trúc Modular hóa cực cao, giúp dễ dàng mở rộng và bảo trì:

- **`config/`**: Quản lý bí mật hệ thống và cấu hình ca trực.
- **`core/`**: Trái tim của hệ thống, xử lý nạp Identity Bot và kết nối KeyDB Pub/Sub.
- **`backend/`**:
    - `database.py`: Tầng truy cập dữ liệu (Data Access Layer) trên KeyDB.
    - `economy_engine.py`: Động cơ xử lý logic tiền tệ, rửa tiền, ám sát.
    - `web_server.py`: Server xử lý OAuth2 và tín hiệu Deploy.
    - `presence_proxy.py`: WebSocket Gateway giữ trạng thái Profile 24/7.
- **`ai_labs/`**: Bộ não AI Gemini với cơ chế xoay tua API Key và Circuit Breaker.
- **`cogs_shared/`**: Tầng hiển thị (UI/UX) với các lệnh tương tác người dùng.

---

## 🌟 Tính Năng Nổi Bật

### 1. Cơ Chế Giao Ca Song Hành (Dual Persona)
Hệ thống tự động hoán đổi trạng thái giữa hai bot theo thời gian thực (GMT+7):
- **Luminous (06:00 - 17:59)**: Văn minh, hoàng gia, quản lý **Aequor** (Tiền sạch).
- **Tenebris (18:00 - 05:59)**: Giang hồ, chợ đen, thao túng **Aequis** (Tiền bẩn).

### 2. Rich Presence Tối Thượng (/status add)
Đặc quyền dành cho Admin+ và Voice Premium Key:
- **Double-Modal UI**: Tùy chỉnh tên app, nội dung, ảnh và nút bấm trên Profile thật.
- **Proxy Presence (/livestatus)**: Duy trì Profile luôn sáng đèn 24/7 kể cả khi tắt máy thông qua WebSocket Proxy.

### 3. AI Labs - Thao Túng & Chữa Lành
- **Luminous AI**: Tư vấn lịch sự, hoàng gia, giúp giải quyết mâu thuẫn.
- **Tenebris AI**: Cục súc, mỉa mai, có 20% tỉ lệ đưa tin giả để kích động drama.
- **Circuit Breaker**: Tự động xoay tua API Key Gemini khi bị giới hạn (429).

### 4. Kinh Tế & Drama (Economy V2)
- **Mở Túi Mù (Star Pouch)**: Nhận tiền ngẫu nhiên lên đến 100M, loại tiền phụ thuộc vào bot đang trực.
- **Trạm Rửa Tiền**: Chuyển đổi Aequis sang Aequor với mức phí 15-25% nộp vào Quỹ Gia Đình.
- **Hệ Thống Sát Thủ**: Ám sát cướp 30% tài sản sạch.
- **Di Chúc Ngầm**: Bảo vệ tài sản cho người phối ngẫu khi bị sát hại.
- **Truy Nã (Bounty)**: Tự động treo thưởng lên đầu kẻ thủ ác.

### 5. Phân Cấp Quyền Lực (Levels 0 - 4)
- **Level 4 (Owner - Silo)**: Quyền lực tối thượng, kiểm soát toàn bộ hệ thống.
- **Level 3 (Dev)**: Debug và điều phối lỗi.
- **Level 2 (Admin)**: Miễn phí dùng lệnh Status, thực thi công lý tại Tòa án.
- **Luật Bảo Vệ Cấp Trên**: Cấp dưới tuyệt đối không thể phạt gậy (Warn) cấp trên.

---

## 🛠️ Hướng Dẫn Cài Đặt

### 1. Yêu cầu hệ thống
- Python 3.10+
- KeyDB (hoặc Redis)
- Google Gemini API Keys

### 2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3. Biến môi trường (.env)
Cần cấu hình các biến sau trên Render hoặc file `.env`:
- `LUMINOUS_TOKEN` & `TENEBRIS_TOKEN`
- `LUMINOUS_CLIENT_ID` & `LUMINOUS_CLIENT_SECRET`
- `REDIS_URI`: Địa chỉ kết nối KeyDB.
- `OWNER_ID`: ID Discord của **Silo**.
- `OAUTH2_REDIRECT_URI`: Link callback của web server.

### 4. Khởi chạy
```bash
python main.py
```

---

## 📜 Giấy Phép & Bản Quyền
Bản quyền hệ sinh thái thuộc về **Equinox Network**.
Được phát triển và duy trì bởi **Silo** (Owner) & **Jules** (Core Developer).

---
*Equinox Network V2 - Nơi ánh sáng và bóng tối giao thoa.*
