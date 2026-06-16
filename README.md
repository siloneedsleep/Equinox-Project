# 🚀 EQUINOX NETWORK - DISCORD BOT ECOSYSTEM

**Equinox Network** là một hệ sinh thái Discord BOT Couple độc đáo, vận hành theo cơ chế âm dương hòa hợp giữa hai thực thể đối lập nhưng bổ trợ lẫn nhau: **Luminous** (Nữ thần Ánh sáng) và **Tenebris** (Chúa tể Bóng tối). Dự án mang đến trải nghiệm nhập vai, quản lý kinh tế, giải trí và trị an cực kỳ có chiều sâu với sự đồng bộ thời gian thực (real-time) thông qua cơ sở dữ liệu đám mây.

---

## 🏗️ KIẾN TRÚC HỆ THỐNG (CORE ARCHITECTURE)

* **Shared Host & Independent Processes:** Hai BOT chạy trên cùng một máy chủ (Host) nhưng thông qua 2 tiến trình (Processes) hoàn toàn độc lập.
* **Real-time Database:** Sử dụng chung một cơ sở dữ liệu **Redis Cloud** (In-Memory) để đồng bộ hóa dữ liệu ví tiền, khế ước kết hôn, trạng thái ca trực và truyền tín hiệu chéo giữa hai bot mà không có độ trễ.
* **Global Cooldown Lock:** Cơ chế khóa mạch lệnh vĩ mô 5 giây lúc 12:00 (Trưa/Đêm) để tự động hoán đổi ca trực, thay đổi trạng thái (Presence) và chống xung đột luồng (Race Condition).

---

## 🎭 BỘ NHẬN DIỆN THỰC THỂ (THE BOT COUPLE)

| Tiêu chí | ☀️ LUMINOUS (Ca Ngày) | 🌙 TENEBRIS (Ca Đêm) |
| :--- | :--- | :--- |
| **Định vị** | Ánh sáng, văn minh, chính thống và lịch sự. | Bản ngã hắc ám, thế giới ngầm và thực tế. |
| **Văn phong** | Thông thái, nghiêm túc, hoàng gia Thần Điện. | Cục súc, giang hồ chợ đen, mỉa mai, bén nhọn. |
| **Giao diện Lệnh** | Hiện đại (Hybrid: Slash `/` & Prefix `l!`). | Cổ điển, giấu giếm (Prefix `t!`). |
| **Màu sắc (Hex)** | Vàng Kim (#FFD700), Vàng Hồng (#FFB6C1), Xanh Dương (#00FFFF). | Đen Obsidian (#1A1A1A), Tím Đen (#2E0854), Tím Đậm (#4B0082). |
| **Kinh tế** | Quản lý tiền sạch: **Aequor (Star)**. | Thao túng tiền bẩn: **Aequis (Star)**. |

---

## 🌟 TÍNH NĂNG NỔI BẬT (KEY FEATURES)

### 1. Nền Kinh Tế Song Song & Trạm Rửa Tiền
* **Kinh tế Hợp pháp (Luminous):** Cung cấp các tính năng gửi tiết kiệm ngân hàng lấy lãi, chuyển tiền, mua sắm vật phẩm và Gacha túi mù tỷ lệ 0.5% nổ hũ.
* **Kinh tế Ngầm (Tenebris):** Cày tiền bẩn thông qua buôn lậu, móc túi và sòng bạc Casino (Tài Xỉu, Blackjack) không đóng phế.
* **Rửa Tiền (Laundering):** Rửa tiền bẩn thành tiền sạch qua Tenebris với mức phí ngẫu nhiên 15-25% nạp vào Quỹ Gia Đình.

### 2. Khế Ước Phu Thê & Sự Trả Thù
* **Đám cưới Thế kỷ:** Mua Nhẫn Kim Cương qua Luminous để hưởng đặc quyền 0% thuế giao dịch trọn đời. 
* **Hội Sát Thủ (Hitman):** Người độc thân có thể thuê sát thủ bên Tenebris ám sát các cặp đôi mang Nhẫn Kim Cương để cướp 30% tài sản sạch. Luminous sẽ tự động nổ Embed chia buồn dằn mặt.
* **Đánh Ghen Xuyên Không Gian:** Cố tình gõ lệnh cầu hôn Luminous thì Tenebris sẽ xuất hiện chửi bới dằn mặt, và ngược lại.

### 3. Voice Premium & Bàn Giao Ca Trực
* **Bàn Giao 5 Giây:** Khi chuyển ca, hai bot sẽ có màn tương tác, thả thính trực tiếp trong 5 giây tại phòng Voice trước khi đổi vị trí.
* **Voice Premium Key:** Hệ thống kích hoạt mã Key để mở khóa băng thông treo máy 24/7 không bị ngắt kết nối cho các "đại gia".

### 4. Quản Trị Vĩ Mô & Kỷ Luật
* **Hạn Ngạch Nhân Sự Động:** Phân quyền nghiêm ngặt lưu trên Redis gồm 1 Owner, 2 Dev, 3 Admin, 2 Event Manager, và 10 Staff.
* **Big Event Overdrive:** Sự kiện lớn đóng băng luân hồi, ép cả hai bot thức tỉnh 100% công suất gánh tải.
* **Cưỡng Chế Trị An:** Hệ thống phạt gậy (Warn) tự động đóng băng tài khoản khi chạm mốc 3 gậy, kèm lệnh trình đơn xin ân xá gửi thẳng vào DM của Owner.
* **Nút Bấm Hạt Nhân:** Lệnh tắt khẩn cấp `/system-kill` dập nguồn bot (đưa vào trạng thái vô hình, chặn lệnh) mà không làm sập luồng Voice.

---

## 🛠️ HƯỚNG DẪN CÀI ĐẶT (INSTALLATION)

1. Clone repository về máy chủ.
2. Cài đặt các thư viện cần thiết:
   `pip install -r requirements.txt`
3. Tạo file `.env` tại thư mục gốc và cấu hình các biến môi trường:
   `LUMINOUS_TOKEN=your_luminous_bot_token`
   `TENEBRIS_TOKEN=your_tenebris_bot_token`
   `REDIS_URI=redis://localhost:6379/0`
4. Kích hoạt toàn bộ hệ sinh thái (Chạy song song 2 tiến trình):
   `python run_ecosystem.py`

---
*Equinox Network - Nơi ánh sáng và bóng tối cùng tồn tại để tạo nên trật tự vĩnh hằng.*

