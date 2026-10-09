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

USER CHỐT 2026-10-09 00:25 ICT (decided_by: user, phương án A): BỎ mốc review theo ngày (trần cũ 2026-10-06 đã qua mà gate 1 không thể đạt — v2 chỉ reverse-unwind khi state RỜI gate, 57 phiên đầu toàn NEUTRAL). Review EVENT-ANCHORED khi xảy ra SỚM NHẤT 1 trong 2: (a) state DT5G lần đầu rời NEUTRAL (BULL/EXBULL ⇒ bằng chứng gate mở rộng; BEAR/CRISIS ⇒ chu kỳ reverse-unwind đầu tiên), hoặc (b) trigger park quay lại kích hoạt (lãi huy động Big-4 có xu hướng hạ — cảnh báo cron refresh_deposit_cctg_weekly.sh). Không backtest thêm. Cron ghi sổ giữ nguyên. Lý do: park=0 từ 2026-10-01 ⇒ tiền nhàn rỗi ở Trứng vàng, DC-book không có vốn live; đọc sổ 2026-10-09: cum −0,16% (07-17→10-08) vs VNINDEX −2,71%, idle proxy dep1m ~+0,9%.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) Trọn 1 chu kỳ deploy → reverse-unwind → settle trên paper, đúng thứ tự ưu tiên thiết kế
- ⏳ (pending) P&L sleeve NET-of-TC không mâu thuẫn backtest (+5.0pp/năm sleeve parking kỳ vọng)
- ⏳ (pending) User sign-off sau review event-anchored (Mike + Taylor đề xuất ngày khi đủ điều kiện)

## ℹ️ Ghi chú vận hành

Sleeve clock chạy từ 2026-06-26 (backfill NAV cơ sở 1B); user duyệt paper 2026-07-06 (job Taylor_20260706_132553).

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/dc_book_waterfall_paper_state.json`
- `data/dc_book_waterfall_paper_nav.csv`
