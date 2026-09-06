# Charter — Order-book execution shadow (10-level bid-ask) (`order_book_execution_shadow`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-08-18 · **Kết thúc dự kiến:** 2026-09-23

## 🎯 Mục đích

Giảm implementation shortfall/slippage và adverse selection của child order bằng dữ liệu snapshot 10 mức bid-ask; đây là nghiên cứu execution-only, KHÔNG tạo alpha, KHÔNG đổi chọn mã/sizing/lệnh.

## 📅 Nghiệm thu / mốc kết thúc

20 phiên evidence từ 2026-08-18, không tính ngày không có snapshot hợp lệ hoặc không có child-order opportunity. GIA HẠN 2026-09-06 (user duyệt, đề xuất Taylor job Taylor_20260906_144656): mốc gốc 09-16 dựa trên ước tính nhịp phiên cũ, đo lại tại 09-06 cho tỉ lệ phiên-có-evidence thật 10/11 = 90,9% (đếm qua vn_market.is_holiday) — ngoại suy điểm 09-21, cận bảo thủ (Wilson lower-bound, N=11 còn mỏng) 10-05. Review mới cố định 2026-09-23 09:30 ICT, nằm giữa 2 cận có đệm; nếu <20 phiên tại đó, báo thiếu mẫu + gia hạn tiếp theo cùng công thức, không kết luận sớm.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) Telemetry v1 ghi được snapshot 10 mức, quyết định baseline/HYBRID, child order, fill và hậu kiểm 1/5/15 phút với khóa nối traceable — Pha 0: chỉ instrumentation; không tác động cách đặt lệnh paper hoặc live.
- ⏳ (pending) Shadow policy chỉ đưa khuyến nghị KEEP/REDUCE/DEFER; không có đường gọi broker, không đổi child size, không đổi lịch HYBRID — Pha 1: policy đơn giản, khóa trước rule và version.
- ⏳ (pending) Có >=20 phiên evidence và so sánh ngoài mẫu với baseline HYBRID theo slippage, fill-rate, time-to-fill và adverse selection — Không dùng P&L/alpha làm tiêu chí.
- ⏳ (pending) Quant-skeptic review trước bất kỳ paper A/B có tác động execution; user sign-off trước mọi thay đổi live

## ℹ️ Ghi chú vận hành

Kế hoạch đã được user chốt 2026-08-14 và duyệt triển khai telemetry v1 ngày 2026-08-15: ưu tiên cải thiện chất lượng fill và giảm chi phí giao dịch, không nghiên cứu alpha. Schema khóa version: orderbook_l2_v1 + orderbook_execution_v1; giá VND, quantity G1 là shares, timestamp nguồn tách timestamp capture, snapshot quá 5 giây hoặc thiếu timestamp nguồn = INVALID và policy bắt buộc KEEP (fail-open baseline). Shadow policy spread_depth_v1: KEEP mặc định; REDUCE khi spread >=2 tick và touch depth <1x child; DEFER khi spread >=4 tick và touch depth <0,5x child. Kết quả shadow KHÔNG có đường gọi broker/không được đọc vào giá, KL hoặc lịch HYBRID. Raw + telemetry giữ ít nhất xuyên review 16/09 và 30 ngày sau review. Hậu kiểm 1/5/15 phút dựng offline, không thêm API call. RESILIENCE LOẠI KHỎI v1 theo user duyệt 2026-08-15: cadence 60s không đủ đo tái tạo sổ trong vài giây; muốn nghiên cứu phải mở chương trình/log riêng. Mọi số tách theo side, ticker-liquidity bucket và phiên; paired comparison cùng opportunity, không so P&L toàn portfolio.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/orderbook_shadow_<account>_<date>.jsonl — schema orderbook_execution_v1: trace_id parent/child, baseline, KEEP/REDUCE/DEFER, latency và snapshot immutable`
- `data/execution_logs/dnse_raw_<date>.jsonl kind=quote_l2 — schema orderbook_l2_v1, G1 10 mức, VND + shares, source_ts/source_age_ms`
- `data/execution_logs/exec_<account>_<date>_journal.csv — PLACE/FILL/DONE nối bằng child_oid; hậu kiểm 1/5/15 phút dựng offline từ snapshot kế tiếp`
