# Charter — AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX) (`alphalens`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** DollarBill
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** 2026-09-30

## 🎯 Mục đích

4 tên Tier-1 chọn bằng lens định giá (PE vs PE_MA1Y; PB vs Gordon justified-PB) có beat VNINDEX qua 3 tháng không? Buy-and-hold, equal-weight 25%/tên.

## 📅 Nghiệm thu / mốc kết thúc

2026-09-30 (audit: Taylor)

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) Excess return dương vs VNINDEX qua full window 3 tháng
- ⏳ (pending) Exit conditions per-name không bị vi phạm sớm (PE > PE_MA1Y / PB > justPB)
- ⏳ (pending) Audit độc lập bởi Taylor tại 2026-09-30

## ℹ️ Ghi chú vận hành

Giá MTM từ BQ cache (close phiên gần nhất đã sync) — trong phiên sẽ trễ 1 ngày, đúng thiết kế EOD.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/alphalens_paper.json`
- `data/bq_cache/ticker_1m.parquet (Close + VNINDEX, sync 23:45 ICT)`
