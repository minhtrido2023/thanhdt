# Charter — Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45) (`fill_timing`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** 2026-07-31

## 🎯 Mục đích

Edge backtest (BUY 11:15 rẻ hơn open +17.6bps t=12.0; SELL tại open +11.8bps vs ATC) có capture được NET-of-noise trên fill thật không? (noise 110-220bps >> edge 17bps → cần nhiều tuần)

## 📅 Nghiệm thu / mốc kết thúc

Checkpoint 2026-07-31 ĐÃ CHẠY 2026-08-04. Mốc mới: sau khi gỡ blocker netting + 1 phiên BUY-window nữa (ước ~1 tuần) → quant-skeptic → user quyết flip gate theo MECHANICS.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) BUY window adherence cao (lệnh dồn 10:45-11:15)
- ✅ (pass) SELL window adherence cao (lệnh tại open 09:15-09:45)
- ✅ (pass) 0 rejects/fails (hoặc từng cái được giải thích)
- ⏳ (pending) BUY fill không tệ hơn open đáng kể; SELL không thấp hơn open đáng kể
- ⏳ (pending) quant-skeptic → user sign-off mới flip fill_timing_live_gate

## ℹ️ Ghi chú vận hành

Mechanics (window adherence) đo được sớm; EDGE bps cần nhiều tuần — không gate sớm trên bps.

## 🔍 Nguồn dữ liệu kiểm chứng

- `execution_quality_review.py`
- `data/execution_logs/exec_*_journal.csv (ft-notes)`
