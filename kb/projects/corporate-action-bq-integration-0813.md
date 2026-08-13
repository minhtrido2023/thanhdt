---
kind: project
status: DONG (voi 1 muc mo)
date: 2026-08-13
---

# corporate_action BQ integration + paper-report bug fix (2026-08-13)

User yêu cầu nghiên cứu bảng BQ mới `tav2_bq.corporate_action` (per-event corp-action, refresh
hàng ngày từ 08-13). Duyệt (a) dùng làm nguồn đo cổ tức/ex-rights + (b) build Oshares "live".

## Kết quả (6 vòng dispatch Taylor + quant-skeptic)

1. **Nghiên cứu + đăng ký**: `kb/data_registry/price-volume/corporate_action_bq.md` (status TRAP —
   AIS lag ~7 tuần so exright_date, cần tự verify freshness mỗi lần đọc).
2. **Việc A** (nguồn đo cổ tức) — `dividend_adjusted_return.py` dùng `corporate_action.DIV` phân
   loại DIV/ISS, tiền broker vẫn là nguồn số chính thức. **CONFIRMED**.
3. **Việc B** (`oshares_live.py`) — thiết kế đầu **REFUTED** (anchor look-ahead qua
   `ticker_financial.OShares` restated; roll-forward no-op trên 75% ISS không-accrue) → vá lại
   (anchor chỉ AIS, fail-closed khi ratio∈{0,NULL}) → **CONFIRMED**. **CHƯA WIRE vào consumer nào**
   — chưa xác định phạm vi (backtest point-in-time vs report/rating live hôm nay), cần user chọn
   trước khi dispatch tiếp.
4. **Việc C** (bug thật): `alphalens_report.py`/`converge_report.py` so `entry_price` thô đóng
   băng với `Close` đã điều chỉnh hồi tố (Bẫy 2, `ticker_close_vs_price_dividend_adj.md`) — mọi
   sự kiện quyền sau ngày vào lệnh bị tính thành lỗ giá oan. Case thật: MBB (pha loãng 25%,
   exright 2026-08-11) báo −18,8% thay vì đúng convention accrue-only −2,9%. Sửa bằng
   `paper_entry_adjust.py` (rebase entry theo `Close/Price` tại ngày chụp giá) + làm rõ convention
   accrue-only (không giả định đã subscribe rights). **CONFIRMED** qua 2 lớp hiệu chỉnh.
5. **Việc D** (cổng chặn tái phát bug) — `report_return_gate.py` nối vào ĐÚNG kênh
   `newdeals_daily_report.py`→`notify_thread.sh` (không phải chỉ qua email), qua 5 vòng thu hẹp
   residual risk (marker tautology, dual rc=3 producer, banner đếm sai, hardcode thread ID).
   **CONFIRMED** vòng 5.

## Việc còn mở

- **Việc B chưa wire** — cần user/Mike chọn consumer đầu tiên (backtest vs live report) trước khi
  dispatch thiết kế điểm wire.
- **Vòng 6 (rc=1 build_message failure + import-time KeyError registry) — CHỦ ĐỘNG BỎ QUA**
  (quyết định user 2026-08-13): xác suất thấp, đã có `cron_health_check_daily.sh` (08:25 ICT) bắt
  một phần `rc=1`; KeyError registry chỉ xảy ra do lỗi thao tác con người và sẽ crash ồn ào chứ
  không âm thầm sai. Chấp nhận làm residual risk đã biết, không dispatch thêm.
- **`corporate_action` freshness**: user xác nhận refresh hàng ngày từ 08-13 nhưng job vòng 1
  (Taylor_20260813_041648) đo `MAX(ingested_at)` vẫn là batch nạp 08-12 — cần verify lại 08-14.

## Commit chính
`WorkingClaude@2037e5c`, `mike@91434457` (vòng 1) · `WorkingClaude@abd7cd6`, `mike@60085443`
(vòng 3) · `WorkingClaude@7790fd6`, `mike@17d0c749` (vòng 4) · `WorkingClaude@e0ff1fb`,
`mike@066df954` (vòng 5).

↩ [Về index dự án](INDEX.md)
