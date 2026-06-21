---
name: MCP simulation chỉ chạy tuần tự
description: Simulation MCP chỉ xử lý 1 lần chạy mỗi lần, phải chờ kết quả xong mới gọi tiếp
type: feedback
originSessionId: 3ea46ac2-6f2d-4507-bf14-dfbcbbff35b9
---
MCP simulation_v1_6_webui chỉ chạy được 1 lần tại một thời điểm — không được gọi song song.

**Why:** Server simulation không hỗ trợ concurrent requests; gọi song song sẽ gây lỗi hoặc kết quả sai.

**How to apply:** Khi cần chạy nhiều simulation (ví dụ: nhiều filter, nhiều giai đoạn), phải chạy tuần tự — chờ có kết quả từ lần trước mới gọi lần tiếp theo. Không dùng parallel tool calls cho MCP simulation.
