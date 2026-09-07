# DDos-IP
Searching about security with a basic DDos to any Web until they temporary block your request

# 🚀 High-Concurrency Load Testing Framework (DDoS Simulation Lab)

## 📌 Tổng quan dự án

Dự án này là một công cụ mô phỏng tải cao (High-load simulation) được xây dựng bằng ngôn ngữ Python, sử dụng lập trình bất đồng bộ (`asyncio`) để thực hiện các cuộc tấn công giả lập ở tầng ứng dụng (Layer 7 - HTTP).

Mục tiêu chính là thực hiện **Stress Testing** nhằm tìm ra điểm giới hạn (breaking point) của một Web Server, từ đó đánh giá khả năng chịu tải và hiệu quả của các cơ chế phòng thủ như Rate-limiting, WAF (Web Application Firewall), và DDoS Mitigation.

---

## 🛠 Công nghệ sử dụng

- **Language:** Python 3.x
- **Core Library:** `aiohttp` (Asynchronous HTTP Client/Server) - được sử dụng để tối ưu hóa việc quản lý hàng ngàn kết nối đồng thời mà không gây nghẽn I/O.
- **Concurrency Model:** `asyncio` (Event Loop) để quản lý các coroutines, cho phép mô phỏng lượng lớn người dùng ảo (Virtual Users) một cách hiệu quả.
- **Networking:** HTTP/HTTPS protocol.

---

## 🏗 Kiến trúc & Cơ chế hoạt động

### 1. Mô hình Concurrency (Độ song song)
Thay vì sử dụng Threading truyền thống (tốn kém tài nguyên RAM), dự án sử dụng mô hình Asynchronous I/O. Điều này cho phép script tạo ra hàng trăm worker (coroutines) chạy song song trên cùng một thread, giúp tối ưu hóa tài nguyên máy chủ chạy test.

### 2. Chiến lược Ramp-up
Để mô phỏng thực tế, dự án tích hợp cơ chế **RAMP_UP**. Thay vì bắn toàn bộ lượng request cùng một lúc (gây sốc hệ thống ngay lập tức), các request được tăng dần theo thời gian để quan sát cách hệ thống phản ứng khi tải tăng dần từ mức bình thường đến mức cực hạn.

### 3. Giả lập User Behavior (Hành vi người dùng)
Để tránh bị các hệ thống bảo mật nhận diện là bot đơn giản, framework thực hiện:
- **User-Agent Rotation:** Thay đổi danh sách User-Agent ngẫu nhiên để mô phỏng nhiều trình duyệt và thiết bị khác nhau (Chrome, Safari, Firefox, Mobile).
- **Jitter (Độ trễ ngẫu nhiên):** Thêm các khoảng nghỉ nhỏ ngẫu nhiên giữa các request để làm nhiễu lưu lượng, tránh tạo ra các pattern quá "máy móc".

---

## 📊 Phân tích kết quả Test (Case Study)

Dưới đây là kết quả thu được từ một đợt thử nghiệm thực tế nhắm vào mục tiêu `xxx`.

### 📉 Thông số cấu hình
- **Concurrency:** 100 (Số lượng kết nối song song)
- **Duration:** 60s
- **Ramp-up:** 10s

### 📈 Kết quả đo lường

| Chỉ số | Giá trị |
| :--- | :--- |
| **Tổng số Request** | 8,335 |
| **Tốc độ trung bình** | ~120.3 req/s |
| **Thành công (200 OK)** | 7,269 (~87%) |
| **Lỗi (Errors)** | 1,066 (~13%) |
  <img width="364" height="704" alt="image" src="https://github.com/user-attachments/assets/85b1ae88-e360-426a-9dee-0bd092482f4b" />  

### 🔍 Phân tích lỗi chi tiết (Error Breakdown)

Việc phân tích các loại lỗi là chìa khóa để hiểu trạng thái của Server:

- **`200 OK` (7,269):** Hệ thống vẫn xử lý được phần lớn yêu cầu, cho thấy server vẫn còn khả năng phục vụ.
- **`TimeoutError` (500):** Đây là tín hiệu quan trọng nhất. Server đã rơi vào tình trạng *Resource Exhaustion* (cạn kiệt tài nguyên như CPU/RAM) hoặc hàng đợi (queue) bị đầy, dẫn đến không thể phản hồi trong thời gian quy định.
- **`403 Forbidden` (382):** Cho thấy các cơ chế bảo mật (WAF/Rate-limiting) đã bắt đầu hoạt động. Server/Firewall đã nhận diện được lưu lượng bất thường và chủ động từ chối kết nối để bảo vệ tài nguyên.
- **`ClientConnectorSSLError` (167):** Xảy ra do lỗi bắt tay TLS/SSL. Điều này thường do server quá tải trong việc xử lý các yêu cầu mã hóa mới.
- **`ServerDisconnectedError` (17):** Server chủ động đóng kết nối (TCP Reset) để giải phóng socket.

---

## ⚠️ Cảnh báo an toàn (Disclaimer)

> **LƯU Ý QUAN TRỌNG:**
> 
> - Công cụ này **CHỈ** được sử dụng trong môi trường Lab hoặc trên các hệ thống mà bạn **có quyền sở hữu hoặc được phép kiểm thử**.
> - Việc sử dụng công cụ này lên các mục tiêu công cộng mà không có sự cho phép có thể bị coi là hành vi tấn công mạng (DDoS) và **vi phạm pháp luật nghiêm trọng**. Người dùng hoàn toàn chịu trách nhiệm về hành động của mình khi sử dụng bộ công cụ này.
