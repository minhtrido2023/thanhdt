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

## Chuỗi nghiên cứu BULL — 30/08, ĐÓNG HOÀN TOÀN, không có mechanism nào wire
1. **DC 3-book static 1/3** → NO-GO (DC ungated sập -16,8%/năm BEAR, không override).
2. **DC state-gated BULL/EXBULL-only** → quant-skeptic CONFIRMED nhưng bằng chứng quá mỏng:
   N=10 thổi phồng thành N thật ~6, 85% edge dồn 1 cụm (COVID 2020-21). Taylor tự hạ "weak-GO" ->
   "đáng theo dõi, chưa đủ bằng chứng hành động".
3. **EXBULL exploitation audit** → độ trễ cơ học 24 phiên (khớp gate 25 phiên) luôn xảy ra, nhưng
   tác động 2 chiều tuỳ hình dạng sóng (2020-21 DT5G thắng 154,5% capture nhờ lọc whipsaw; 2025
   chỉ bắt 61%, giải thích drag -0,89pp đã biết). N=2 quá mỏng, không đổi tham số DT4-gate.
4. **LAG BULL-mode SUE (nới NP_R>=15 xuống 12/10.5 khi BULL+breadth cao)** → NO-GO. Deal mới
   KHÔNG rác (win-rate 75-80%, gần bằng baseline) nhưng thua vì CROWDING-OUT: chênh lệch âm dồn
   hết vào 2021 (năm tốt nhất), batch mới pha loãng funding LAG đang cash-constrained. N độc lập
   chỉ 2/8 episode khả dụng.

**Kết luận chung**: DC alpha có thật (xác nhận 2 lần độc lập) nhưng chưa tìm được kiến trúc khả
thi để khai thác; LAG's funding-constraint là nút thắt thật (không phải tiêu chí SUE sai). Không
mechanism nào đủ điều kiện wire — DT5G/V2.4 giữ nguyên. Files: dc_3book_factor_neutral_20260830.md,
dc_state_gated_bull_only_20260830.md, exbull_exploitation_audit_20260830.md,
lag_bull_mode_sue_20260830.md (tất cả agents/Taylor/research/).
**Đã báo user đề xuất đóng chuỗi nghiên cứu hôm nay — chờ xác nhận hoặc việc mới.**

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

