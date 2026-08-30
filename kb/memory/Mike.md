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

## Chuỗi khủng hoảng cơ cấu 2007-2012 + điểm mù 2018 — ĐÓNG HOÀN TOÀN, cả 2 hướng đã qua verify đủ vòng
- Episode clustering N=7->N=5, stress-test DT5G Phase A/B, Bobby BLIND read 2009/2018, nguyên nhân
  bỏ lỡ 2009 = SIGNAL_V11 gate cứng đòi state BULL/EXBULL (DT5G không đạt 2008-2013) — giữ nguyên
  làm tài liệu tham khảo, KHÔNG có mechanism nào wire vào production.
- **Hướng 1 (valuation-gated tier-unlock) — ĐÓNG, NO-GO**: sau round 2 sửa đủ 5 điểm REFUTED,
  thống kê sạch (t=3,10, khớp quant-skeptic ước tính độc lập ~2,17) nhưng **capacity là rào cản
  quyết định**: 60-79% episode thiếu ADV, ở ngưỡng ≥10B/ngày thực tế edge ĐẢO ÂM ở median.
  File: `agents/Taylor/research/valuation_gated_tier_unlock_round2_20260830.md`.
- **Hướng 2 (DIVERGE composite CAP_SIGNAL) — ĐÓNG, CONFIRMED nhưng chỉ ADVISORY, không wire**:
  round 2 sửa đủ 4 điểm REFUTED (grid persist + quant-skeptic tái lập khớp full precision, nhãn
  FP/TP đúng, IS/OOS đều dương 6/6, leave-one-out 18/18 dương). quant-skeptic CONFIRMED medium
  confidence nhưng giữ killer objection: N thật chỉ ~6 cụm macro độc lập/15 năm (2014, 2016,
  2018, 2020, 2022, 2023) — quá mỏng cho DSR/PBO chính thức, không tăng N được (hết lịch sử panel
  2011-2026). Kết luận CUỐI (cả Taylor + quant-skeptic đồng thuận): dấu dương THẬT, sống sót mọi
  robustness test, nhưng KHÔNG đủ điều kiện wire — cùng lắm dùng làm tín hiệu advisory mềm.
  File: `agents/Taylor/research/diverge_indicator_strategy_backtest_round2_20260830.md`.
  Đã hỏi user có muốn thiết kế hiển thị advisory không — CHƯA có trả lời, chờ chỉ đạo tiếp.
- **Kết luận chung phiên nghiên cứu 2007-2012/2018**: không có thay đổi production nào — DT5G giữ
  nguyên "bảo hiểm fail-safe", không re-tune theo lịch sử, đúng mandate ban đầu.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO. Sector sweep: đóng, coverage 20/20.
- C1 (DC-swap): củng cố REFUTED. Insider cluster-buy: NO-GO.
- Audit 8L thresholds: KHÔNG cần adaptive mới. NPL/CAR: giữ proxy ROE_Min3Y/Gordon-PB.

## Vận hành — dọn sạch 30/08, không còn việc treo mới
- job quant-skeptic_20260830_085357: OVERDUE cosmetic (không sửa được qua force/cancel, đã verify
  substance qua log trực tiếp) — biết, bỏ qua, không phải việc thật.
- capit-lever selfcheck 2, retro-pattern checker hardcode: đã CLOSED từ 08-28.
- dt5g-writer-la-1931: điều tra ra + đóng.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T14:11:34Z] User duyệt 21:10 ICT: CAP_SIGNAL dùng advisory tham khảo, tự tích luỹ case mới, tự flag nâng cấp khi đủ N (không tự wire). Dispatch Taylor_20260830_141109 thiết kế+implement: kiểm tra khả thi dữ liệu sống, script advisory+registry persist, ngưỡng N nâng cấp bằng số, cách hiển thị tái dùng cadence sẵn có, ghi kb/projects/cap-signal-advisory-20260830.md. Đang chạy, chưa xong.
