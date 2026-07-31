# Charter — DC-book NEUTRAL idle-cash Waterfall (`dc_waterfall`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-06 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Khi NEUTRAL và BAL/LAG rỗng, giải ngân tiền rảnh theo thứ tự BAL/LAG → DC book (double-confirm, ex-DHG) → custom30V có thắng để-nguyên-custom30V không? (backtest +5.0pp sleeve, DSR 0.775 = insurance-grade, chưa phải alpha tin cậy cao)

## 📅 Nghiệm thu / mốc kết thúc

Event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN hoàn tất (LAG dự kiến refill cuối 07) + settle 4-6 tuần. Sàn ~2 tháng, trần 2026-10-06 (né mùa BCTC Q3). LAG refill trượt lịch → mốc trượt theo.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) Trọn 1 chu kỳ deploy → reverse-unwind → settle trên paper, đúng thứ tự ưu tiên thiết kế
- ⏳ (pending) P&L sleeve NET-of-TC không mâu thuẫn backtest (+5.0pp/năm sleeve parking kỳ vọng)
- ⏳ (pending) User sign-off sau review event-anchored (Mike + Taylor đề xuất ngày khi đủ điều kiện)

## ℹ️ Ghi chú vận hành

Sleeve clock chạy từ 2026-06-26 (backfill NAV cơ sở 1B); user duyệt paper 2026-07-06 (job Taylor_20260706_132553).

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/dc_book_waterfall_paper_state.json`
- `data/dc_book_waterfall_paper_nav.csv`
