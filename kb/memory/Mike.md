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

## Chuỗi khủng hoảng cơ cấu 2007-2012 + điểm mù 2018 — ĐÓNG HOÀN TOÀN, cả 2 hướng NO-GO/REFUTED
- Episode clustering N=7->N=5, stress-test DT5G Phase A/B, Bobby BLIND read 2009/2018, nguyên nhân
  bỏ lỡ 2009 = SIGNAL_V11 gate cứng đòi state BULL/EXBULL (DT5G không đạt 2008-2013) — tất cả giữ
  nguyên làm tài liệu tham khảo, KHÔNG có mechanism nào wire vào production.
- **Hướng 1 (valuation-gated tier-unlock) — ĐÓNG, NO-GO**: round 2 sửa đủ 5 điểm quant-skeptic
  REFUTED round 1 (baseline DT5G đã đúng sẵn; tự sửa bug cluster-SE t=4.19->3.10 khớp quant-skeptic
  ước tính độc lập ~2.17; loại banned tickers 1399->1348; OOS hết âm đơn điệu tuyệt đối). NHƯNG
  **capacity là rào cản quyết định**: 60-79% episode thiếu ADV cho lệnh sạch 2-5% NAV, ở ngưỡng
  ≥10B/ngày thực tế edge ĐẢO ÂM ở median. T=3.10 thống kê sạch nhưng chưa qua quant-skeptic verify
  lần 2 (round 3) — không quan trọng vì NO-GO đến từ capacity, độc lập với t-stat.
  File: `agents/Taylor/research/valuation_gated_tier_unlock_round2_20260830.md`.
- **Hướng 2 (DIVERGE composite CAP_SIGNAL) — ĐÓNG, REFUTED**: DIVERGE-only NO-GO dứt khoát (đã xác
  nhận sạch, tái lập đúng). CAP_SIGNAL dương 6/6 biến thể REFUTED vì: (1) grid không có script/CSV
  tái lập được, (2) report tự nhận nhầm 2 episode false-positive, (3) 94% hiệu ứng dồn 3/8 episode,
  2 trong đó cách nhau ~5 tuần lịch (nghi giả-độc-lập). Cần Taylor viết lại script persist + sửa
  nhãn + IS/OOS + leave-one-out nếu muốn trình lại — CHƯA có kế hoạch làm tiếp, chờ user chỉ đạo.
  File: `agents/Taylor/research/diverge_indicator_strategy_backtest_20260830.md`.
  Job: quant-skeptic_20260830_132949.
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

- [2026-08-30T13:54:22Z] Hướng 2 làm lại (round 2): dispatch Taylor_20260830_135407, sửa 4 điểm quant-skeptic REFUTED (script grid persist, nhãn FP đúng, IS/OOS split, leave-one-out). File đích: diverge_indicator_strategy_backtest_round2_20260830.md, topic diverge-indicator-strategy-backtest-round2-20260830. Đang chạy, chưa xong.
