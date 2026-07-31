# Charter — ORB intraday VN30F (ring-fenced) (`orb_intraday`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-06-09 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Chiến lược opening-range-breakout VN30F (sign OR 09:00-09:30 → giữ tới 14:30, no stop) có sống sót qua regime BẤT LỢI không? Verdict quant-skeptic 2026-07-01: NO-integrate — n≈17-21 phiên toàn NEUTRAL uptrend benign, Sharpe cao là artifact mẫu nhỏ; walk-forward 2024 lỗ cả năm chưa được giải quyết. Paper tích lũy tiếp để có bằng chứng đủ mạnh.

## 📅 Nghiệm thu / mốc kết thúc

≥60 phiên GỒM ít nhất một giai đoạn chop/bear → re-eval quant-skeptic. Không có deadline lịch — điều kiện là REGIME, không phải số ngày.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) ≥60 phiên paper GỒM giai đoạn chop/bear (hiện toàn benign uptrend — chưa đủ điều kiện đánh giá)
- ⏳ (pending) Walk-forward 2024 full-year loss được giải thích/không lặp lại trong forward window
- ⏳ (pending) Hạ tầng phái sinh: tài khoản VSD margin + đường thực thi VN30F (bot hiện CASH-EQUITY ONLY — chưa thể live dù edge có thật)
- ⏳ (pending) Nếu tích hợp: sleeve RIÊNG vốn riêng ≤5% NAV + quant-skeptic + user sign-off

## ℹ️ Ghi chú vận hành

Section ORB trong Telegram 18:00 (telegram_recommend.py) đã GỠ 2026-07-07 để hết trùng — report này là kênh duy nhất. Verdict đầy đủ: bus event Taylor 2026-07-01 (job Taylor_20260701_113638).

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/orb_pt_status.json`
- `data/orb_pt_log.csv (orb_pt.py, papertrade_daily.sh 15:30 ICT)`
