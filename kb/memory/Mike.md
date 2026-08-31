# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO
  qua DNSE hiện tại.

## Chuỗi nghiên cứu BULL 30/08 — ĐÓNG HOÀN TOÀN, không mechanism nào wire
DC 3-book static (NO-GO), DC state-gated BULL/EXBULL-only (weak-GO, N thật ~6, chưa đủ hành động),
EXBULL exploitation audit (N=2, không đổi tham số), LAG BULL-mode SUE (NO-GO, crowding-out
funding-constraint). DC alpha có thật nhưng chưa tìm kiến trúc khả thi; LAG funding-constraint là
nút thắt thật. Files: agents/Taylor/research/{dc_3book_factor_neutral,dc_state_gated_bull_only,
exbull_exploitation_audit,lag_bull_mode_sue}_20260830.md. Đã báo user đề xuất đóng — chờ việc mới.

## CAP_SIGNAL advisory + khủng hoảng cơ cấu 2007-2012 — KHÉP KÍN
Wire cả 3 cadence, ngưỡng nâng cấp N≥10. kb/projects/cap-signal-advisory-20260830.md.
Valuation-gated tier-unlock NO-GO; Bobby market-maturation research không đủ căn cứ hạ trọng số
neo 2007-2008. DT5G giữ nguyên fail-safe.

## Retro 2026-08-30 — XONG (finalize hoàn tất)
- kb/incidents/retro/retro-2026-08-30.md ghi, Wags CONFIRMED. Sự cố #1:
  `quant-skeptic_20260830_085357` kẹt status=running dù verdict CONFIRMED thật — biến thể MỚI
  (call-site đóng-record-cuối) của pattern anti-lying-guard-tự-chặn-chính-chủ (08-09/08-19).
  CHƯA đạt ngưỡng "2 retro liên tiếp" → chưa escalate, chỉ khuyến nghị điều tra hop-count
  DISPATCHER_HOP_LIMIT giữa verify_finding.sh (mirror tay) vs dispatch.sh thật.
- Ghi nhận phụ (theo dõi, chưa escalate): 1 MISS ScheduleWakeup 4% (1/25) — nếu lặp ở 08-31 mới
  đáng chú ý; job Wags_20260830_033008 cancelled dù việc thật đã xong (Mike tự review tay
  round 6, tz-anchor-gate §16 LIVE) — cùng họ "board status ≠ outcome thật" với Sự cố #1.

## Vận hành — không có việc treo
Không circuit breaker trip, không pending_resumes, không bus question mới mở hôm 08-30.

## Macro watch
Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.
- [2026-08-31T01:43:05Z] User duyệt 08:41 ICT 31/08 cả 3 hướng khai thác DC alpha (LENS not BOOK). Dispatch song song: (1) Taylor_20260831_014243 DC-tilt custom30V backtest (effort high), (2) Taylor_20260831_014244 candidate feeder + mở rộng dc_book_waterfall_paper.py sang BULL/EXBULL (effort medium, KHÔNG sửa bug trigger nhị phân đã biết, chờ mốc review 06/10). Cả 2 đang chạy, chưa xong.
- [2026-08-31T01:46:13Z] Việc #1 (DC-tilt custom30V) XONG: NO-GO bằng suy luận, không cần backtest — DC_ann 22.83% ở NEUTRAL thấp hơn cả BAL/LAG/baseline, mà custom30V chỉ active NEUTRAL. Lần tilt custom30V thất bại thứ 5, nhưng có lý do cơ chế rõ (DC alpha cần trend/mean-reversion, không tồn tại đi ngang). File: dc_tilt_custom30v_20260831.md. Đề xuất quay lại state-gated BULL/EXBULL nếu muốn tiếp tục. Việc #2+#3 (job Taylor_20260831_014244) vẫn đang chạy.
