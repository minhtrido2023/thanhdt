# Charter — Order-book execution shadow (10-level bid-ask) (`order_book_execution_shadow`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-08-18 · **Kết thúc dự kiến:** 2026-09-14

## 🎯 Mục đích

Giảm implementation shortfall/slippage và adverse selection của child order bằng dữ liệu snapshot 10 mức bid-ask; đây là nghiên cứu execution-only, KHÔNG tạo alpha, KHÔNG đổi chọn mã/sizing/lệnh.

## 📅 Nghiệm thu / mốc kết thúc

20 phiên evidence từ 2026-08-18, không tính ngày không có snapshot hợp lệ hoặc không có child-order opportunity. Review cố định 2026-09-16 09:30 ICT; nếu <20 phiên, báo thiếu mẫu và gia hạn minh bạch, không kết luận sớm.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) Telemetry v1 ghi được snapshot 10 mức, quyết định baseline/HYBRID, child order, fill và hậu kiểm 1/5/15 phút với khóa nối traceable — Pha 0: chỉ instrumentation; không tác động cách đặt lệnh paper hoặc live.
- ⏳ (pending) Shadow policy chỉ đưa khuyến nghị KEEP/REDUCE/DEFER; không có đường gọi broker, không đổi child size, không đổi lịch HYBRID — Pha 1: policy đơn giản, khóa trước rule và version.
- ⏳ (pending) Có >=20 phiên evidence và so sánh ngoài mẫu với baseline HYBRID theo slippage, fill-rate, time-to-fill và adverse selection — Không dùng P&L/alpha làm tiêu chí.
- ⏳ (pending) Quant-skeptic review trước bất kỳ paper A/B có tác động execution; user sign-off trước mọi thay đổi live

## ℹ️ Ghi chú vận hành

Kế hoạch đã được user chốt 2026-08-14: ưu tiên cải thiện chất lượng fill và giảm chi phí giao dịch, không nghiên cứu alpha. Pha 0 (trước 2026-08-18): audit nguồn snapshot + schema immutable + retention + freshness; Pha 1 (20 phiên): bot giữ nguyên HYBRID, shadow policy chỉ log KEEP/REDUCE/DEFER. Rule đầu tiên nếu đủ dữ liệu: REDUCE khi spread rộng và top-of-book mỏng; KHÔNG dùng imbalance để dự đoán giá hoặc tăng aggressiveness. Thiết kế phải fail-open về baseline HYBRID khi snapshot thiếu/cũ/lỗi. Mọi số phải tách theo side, ticker-liquidity bucket và phiên; kiểm định bằng paired comparison cùng opportunity, không so P&L toàn portfolio.

## 🔍 Nguồn dữ liệu kiểm chứng

- `telemetry v1 (sẽ tạo): timestamp, 10 mức bid/ask, spread/microprice/imbalance, baseline decision, shadow recommendation, order/fill và hậu kiểm 1/5/15 phút`
- `data/execution_logs/exec_main_*_journal.csv (baseline HYBRID, chỉ đối chiếu)`
- `snapshot nguồn broker với timestamp/freshness được kiểm tra`
