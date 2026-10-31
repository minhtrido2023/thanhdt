# oshares → live: được / chưa được (ghi 31/10/2026, cho user quyết)

Trạng thái: R2–R10 ĐÃ MERGE (WC `69bbbd692`, mike master). Knob `OSHARES_SOURCE_DEFAULT = "fin"` — CHƯA bật.
Selfcheck trên bản chính sau merge R10: 0 FAIL, mọi mutant bị bắt, `env -u TZ` + ICT.
Reviewer R10: arch-review APPROVED (high, 0 thay đổi bắt buộc) + quant-skeptic CONFIRMED (high), cho cả merge lẫn live.

## ĐƯỢC (khi bật live)
- Sửa lỗi nhìn trước của `fin`: số cổ phiếu quý (`ticker_financial.OShares`) bị vendor ghi đè về sau, nên DCF `fin` đang dùng số CP chưa phát hành tại thời điểm đó.
  Ca gốc PHR: giá sau ngày không hưởng quyền × số CP trước thưởng ⇒ "CHEAP giả" (MoS +0,31); live → RICH.
- Số CP đúng theo từng thời điểm (PIT): MST 83,6tr (đợt riêng lẻ chốt 24/11), HHV (quyền mua ex 25/12) — cả hai reviewer tự kiểm trên BQ.
- Khóa khung giá/số CP cùng ngày giao dịch không hưởng quyền (R5/R8/R9): sự kiện chưa executed, ex-date đúng asof, chuỗi giá lặp đều ép về `fin` + kêu stderr, không im lặng.
- Chốt chặn LAG: tập cờ `DCF_RICH` khi live ⊇ khi `fin` (4 asof × 3 chân: thêm 0, mất 0); không mã nào mất cờ RICH. Số live thấp hơn quý >0,5% → dùng số quý (bảo thủ).
- Rollback 1 từ (`"live"`→`"fin"`); ops_health mục 17 cảnh báo nếu ai gán biến môi trường ngoài cây code.
- Tác động đo được (asof 29/10): 9/145 mã đổi FV, 6 mã >5%; PHR, HTN, AIG chuyển CHEAP→RICH; REE, GAS đổi nhãn; BSR ép về `fin`. R10 vs R9: 16/38.925 ô khác (MST FV 3.792→2.791, vẫn RICH).

## CHƯA ĐƯỢC / RỦI RO CÒN LẠI
- Phạm vi hẹp: chỉ tới caller khai `price_date` (`lag_dd_pack`, `due_diligence` không skip, `dcf_check` tự đọc giá: sector_lens_monitor 19:20, converge/alphalens). Plan echo, EOD, paper vẫn `fin` ⇒ bật live KHÔNG sửa những chỗ đó.
- `fin` vẫn là mặc định ở backtest cũ và nhánh fallback ⇒ các số pin cũ vẫn mang số CP nhìn trước; sau khi bật, có hai khung đo khác nhau trong lịch sử DCF (`dcf_lens_history.csv` không có cột nguồn số CP — marker ngày cutover ghi ở `dcf_lens_history.md`).
- `LIVE_BELOW_FIN` là xấp xỉ bảo thủ chứ không phân loại đúng: không có nguồn số CP PIT để tách (A) giảm vốn/hủy cổ phiếu quỹ hợp lệ với (B) vendor ghi đè. Cả hai bị đẩy về số quý (FV thấp hơn, thêm cờ). Ngưỡng 0,5% chọn tay (đã ngoài 29 ca thực, mutant dung sai 50% bị bắt).
- Chi phí vận hành: mỗi mã chưa có cache tốn ~4–5 lời gọi `bq`, mỗi lời timeout 300s. Đường lập plan 21:00 không dính (price_date None → `fin`, 0 lời gọi) nhưng các job quét rộng dính.
- Bẫy dữ liệu chưa vá ở gốc: `ticker_financial.OShares` không PIT (MST, HHV) — nên ghi vào data_registry; ca phát hành riêng lẻ mà vendor ghi ex-date trễ vẫn cần theo dõi.
- `lag_dd_gate_selfcheck` không tự phủ `_rich_deep_fin` (phủ chéo qua `oshares_dcf_selfcheck`); chạy từ worktree cần `WC_ROOT`.
- Bật live thay đổi nhãn thật (PHR/HTN/AIG CHEAP→RICH) trên lens DD/LAG: cần người đọc lại các mã đang theo dõi.

## Điều kiện kỹ thuật khi bật (nếu quyết)
Một commit: `OSHARES_SOURCE_DEFAULT="live"` + ghi CUTOVER (giờ ICT) vào `kb/projects/oshares-live-dcf-20261030.md` và `kb/data_registry/trading-bot/dcf_lens_history.md`;
trước đó selfcheck PROD 0 FAIL (đã đạt); ngoài 19:00–23:10 ICT; đủ CONFIRMED + APPROVED (đã có) + xác nhận của user.
