# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO
  qua DNSE hiện tại. Hard cap concentration risk KHÔNG implement (user chốt: DD workflow đủ).

## Chuỗi nghiên cứu BULL — 30/08, 2/2 việc chính đã xong, chờ user quyết bước kế tiếp
- **DC 3-book factor-neutral (job Taylor_20260830_153823) — XONG, quant-skeptic CONFIRMED medium**:
  Việc 2: DC BULL outperform là ALPHA THẬT (rổ cap-weight thuần THUA baseline BULL −12..−17pp,
  equal-weight chỉ giải thích 30-46% edge — phần lớn đến từ chính double-confirm gate).
  Việc 1: backtest 3-book thật (w_BAL=w_LAG=w_DC=1/3, NAV production thật) → NO-GO, Sharpe/Calmar/
  MaxDD xấu đi vì DC ungated tự sập -16,8%/năm trong BEAR (không có override BEAR/CRISIS). Tự sửa
  1 lỗi nhân-quả giữa chừng (đổ oan cho LAG, quant-skeptic bác đúng — LAG thực ra hơi dương BEAR).
  Việc 3: capacity không phải vấn đề ở NAV thật hiện tại (<0,1% ADV).
  **Hướng mở CHƯA kiểm chứng**: gate DC CHỈ active BULL/EXBULL (tự flat BEAR/CRISIS/NEUTRAL) —
  gợi ý cho job sau, chưa qua DSR/PBO/quant-skeptic, KHÔNG phải đề xuất sẵn sàng.
  File: `agents/Taylor/research/dc_3book_factor_neutral_20260830.md`.
  **Đã hỏi user: làm tiếp hướng gate-BULL-only hay dừng ở đây, chuyển việc #4 (BULL-mode LAG)?
  CHƯA có trả lời — chờ chỉ đạo.**
- **EXBULL exploitation audit (job Taylor_20260830_153824) — XONG**: 60 phiên/2 giai đoạn (2020-21,
  2025), độ trễ cơ học 24 phiên (khớp gate 25 phiên) cả 2 ca, tác động ĐẢO NGƯỢC (2020-21 DT5G
  thắng tín hiệu thô 154,5% capture nhờ lọc whipsaw; 2025 chỉ bắt 61%, giải thích drag -0,89pp đã
  ghi nhận). N=2 quá mỏng, không đề xuất đổi tham số DT4-gate.
  File: `agents/Taylor/research/exbull_exploitation_audit_20260830.md`.
- Việc #4 (BULL-mode LAG idle cash, hạ ngưỡng SUE khi breadth cao) — chưa dispatch, chờ quyết định
  về hướng gate-BULL-only trước (2 việc có thể liên quan, tránh làm trùng).

## CAP_SIGNAL advisory — KHÉP KÍN HOÀN TOÀN 2026-08-30
- Chuỗi đầy đủ: nghiên cứu → quant-skeptic round1 REFUTED → round2 CONFIRMED (N=6 quá mỏng để
  wire) → user duyệt advisory → implement `agents/Taylor/cap_signal_advisory_check.py` → wire cả
  3 cadence (daily tự động qua `dna_report.py::build_cap_signal_advisory_line()`, weekly/monthly
  checklist). Ngưỡng nâng cấp N≥10. Quyết định: `kb/projects/cap-signal-advisory-20260830.md`.
  KHÔNG còn việc treo.

## Chuỗi khủng hoảng cơ cấu 2007-2012 + điểm mù 2018 — ĐÓNG HOÀN TOÀN
- Hướng 1 (valuation-gated tier-unlock): NO-GO, capacity chặn. Hướng 2: xem CAP_SIGNAL advisory.
- Bobby market-maturation research (30/08): trưởng thành cấu trúc KHÔNG đơn điệu, chưa đủ căn cứ
  hạ trọng số neo 2007-2008. File: vn_market_maturation_structural_20260830.md.
- DT5G giữ nguyên "bảo hiểm fail-safe", không re-tune lịch sử.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO. Sector sweep: đóng, coverage 20/20.
- C1 (DC-swap cũ, khác DC-3book mới): củng cố REFUTED. Insider cluster-buy: NO-GO.
- Audit 8L thresholds: KHÔNG cần adaptive mới.

## Vận hành — dọn sạch 30/08, không còn việc treo cũ
- job quant-skeptic_20260830_085357: OVERDUE cosmetic (không sửa được), đã verify substance qua
  log trực tiếp — biết, bỏ qua.
- capit-lever selfcheck 2, retro-pattern checker hardcode: đã CLOSED từ 08-28.
- dt5g-writer-la-1931: điều tra ra + đóng.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T16:24:16Z] User duyệt 23:23 ICT hướng DC state-gated BULL/EXBULL-only. Dispatch Taylor_20260830_162358 (effort high, timeout 3600s): backtest state-gated DC vs 2 baseline (không-DC, static 1/3 NO-GO), walk-forward IS/OOS, DSR/PBO, xử lý transition risk, quant-skeptic bắt buộc nếu GO. File đích: dc_state_gated_bull_only_20260830.md. Đang chạy, chưa xong.
- [2026-08-30T16:34:04Z] DC state-gated BULL/EXBULL-only XONG (job Taylor_20260830_162358), quant-skeptic CONFIRMED nhưng bắt lỗi N=10 thổi phồng -> N thật ~6, 85% edge dồn 1 cụm (COVID 2020-21). Taylor tự hạ 'weak-GO' -> 'đáng theo dõi, chưa đủ bằng chứng hành động'. File: dc_state_gated_bull_only_20260830.md. Đã hỏi user: đóng hẳn nhánh DC-3-book (2/2 kiến trúc đã thử: static NO-GO, state-gated bằng chứng mỏng) hay chuyển việc #4 (BULL-mode LAG)? CHỜ TRẢ LỜI.
- [2026-08-30T16:41:31Z] User duyệt 23:40 ICT việc #4: LAG BULL-mode SUE threshold. Dispatch Taylor_20260830_164112 (effort high, timeout 3600s): nới SUE CHỈ khi BULL/EXBULL+breadth cao, pre-register ngưỡng trước khi chạm data, KHÔNG đụng 8L rating gate (hard lock 07-27). File đích: lag_bull_mode_sue_20260830.md. Đang chạy, chưa xong. (DC-3-book vẫn treo câu hỏi 'đóng nhánh hay không' - user chưa trả lời rõ, có thể coi là đã chuyển hướng sang #4 luôn.)
