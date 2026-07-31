# Charter — Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX) (`engine_room_oos`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-06-11 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

V2.3-book (NGUỒN TÍN HIỆU của live V2.4 — trading_bot/strategies.py đọc pt_v22_dt5g_open_positions.csv để build plan thật) có tiếp tục thắng các kiến trúc BỊ LOẠI (V11 Song Sinh, V12 Âm Dương, V4 switched-allocator) trên OOS forward không? = validation liên tục của lựa chọn V2.4. Nếu một hệ bị loại dominate BỀN risk-adjusted → mở lại câu hỏi rotation (qua quant-skeptic + DSR/PBO, không tự wire).

## 📅 Nghiệm thu / mốc kết thúc

Review 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11) — Taylor trình bảng + khuyến nghị giữ panel / thu gọn / mở câu hỏi rotation.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) V2.3-book không bị hệ đã loại dominate risk-adjusted qua 6 tháng OOS chung (so trên CỬA SỔ CHUNG — NAV thô khác inception là apples-oranges)
- ⏳ (pending) pt_v22 artifacts fresh mỗi phiên (PRODUCTION DEPENDENCY — plan live scale từ sổ này; stale = sự cố ops, đã có tiền lệ 2026-07-07)

## ℹ️ Ghi chú vận hành

pt_v22_dt5g KHÔNG PHẢI paper thí nghiệm — là sổ tín hiệu production, KHÔNG BAO GIỜ retire khi V2.4 còn live. V11/V12/V4 giữ chạy làm control arms (chi phí ~0, không gửi kênh nào). Inception khác nhau (V11/V12 cũ hơn, V4 06-01, V23 06-11) — probe tự rebase về cửa sổ chung. VINTAGE: các sim sinh papertrade_compare5.csv chạy trên giá đến T-1 lúc 15:30 → dòng cuối cửa sổ LUÔN = T-1 (sàn cấu trúc như capitulation_shadow, không phải stale).

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/papertrade_compare5.csv (papertrade_compare.py)`
- `data/pt_v22_dt5g_*.csv (V2.3-book = production signal), data/pt_v4_dt5g_logs.csv, data/pt_v11_tq34b_logs.csv, data/pt_v12_macro_logs.csv`
