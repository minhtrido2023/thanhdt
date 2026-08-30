# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO
  qua DNSE hiện tại. Hard cap concentration risk KHÔNG implement (user chốt: DD workflow đủ).

## Chuỗi khủng hoảng cơ cấu 2007-2012 + điểm mù 2018 — nghiên cứu sâu, ĐÓNG với 2 hướng mở
- Episode clustering: N=7->N=5, tách bạch rõ (min nhóm B +26.3% > max nhóm A∪C +21.2%).
- Stress-test DT5G Phase A/B: gate tự vệ đúng 2 điểm 2008/2011; xác nhận thực nghiệm điểm mù 2018
  (DT5G=DT4 base bit-identical); cơ chế sống 2007-2012 là TRÁNH NÉ (invested chỉ 9.8% phiên,
  2009 miss hoàn toàn VNI+57.9%).
- Bobby (macro-strategist) BLIND read: 2009 nhận ra được từ T9-10 (premium chợ đen+trade deficit+
  tín dụng); 2018 MSCI EM đỉnh trước VN 2 tháng, bẫy Vinhomes deal.
- Nguyên nhân THẬT bỏ lỡ 2009: SIGNAL_V11 gate cứng đòi state BULL/EXBULL, DT5G không bao giờ đạt
  2008-2013 (không phải state-gate đè, không phải data artifact).
- **Hướng 1 (valuation-gated tier-unlock qua pb_z)**: REFUTED medium — 4 lỗi thật (t-stat phóng
  đại 3x do cluster không độc lập, OOS suy giảm đơn điệu, banned tickers chưa lọc, baseline dùng
  SAI bảng state v3.4b BASE thay vì DT5G production — đúng bẫy CLAUDE.md). Cần làm lại 5 việc.
- **Hướng 2 (DIVERGE indicator VN-vs-EM)**: DIVERGE-only NO-GO dứt khoát (FP ăn -27.92pp >
  TP +15.88pp). Composite +DXY/UST ĐẢO NGƯỢC dương 6/6 biến thể (+0.26-0.92pp) — giá trị từ lọc
  FP tốt (27->8), không phải bắt sớm. CHƯA qua quant-skeptic chính thức (Taylor tự backtest).
- Research: crisis_episode_clustering_reanalysis, crisis_stress_dt5g_2007_2012, v2p4_survival_
  backtest, production_mechanism_2009_2018, valuation_gated_tier_unlock, diverge_indicator_
  strategy_backtest (tất cả _20260830.md). Đường đi tiếp nếu user muốn: làm lại hướng 1 theo 5
  điểm đã chỉ ra, HOẶC đưa composite DIVERGE (hướng 2) qua quant-skeptic chính thức.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO. Sector sweep: đóng, coverage 20/20.
- C1 (DC-swap): củng cố REFUTED. Insider cluster-buy: NO-GO.
- Audit 8L thresholds: KHÔNG cần adaptive mới. NPL/CAR: giữ proxy ROE_Min3Y/Gordon-PB.

## Vận hành — dọn sạch 30/08, không còn việc treo
- capit-lever selfcheck 2, retro-pattern checker hardcode: đã CLOSED từ 08-28 (memory cũ sai).
- dt5g-writer-la-1931: điều tra ra + đóng (UPDATE thủ công đã duyệt, không phải writer lạ).
- Security leak VM: user có VM riêng, theo dõi thụ động.
- job quant-skeptic_20260830_085357: bookkeeping cosmetic, không quan trọng.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T13:36:18Z] Hướng 2 DIVERGE composite: quant-skeptic REFUTED medium (job quant-skeptic_20260830_132949) — CAP_SIGNAL grid 6 biến thể không tái lập được (không script/CSV), nhầm nhãn 2 false-positive, 94% hiệu ứng dồn 3/8 episode nghi giả-độc-lập. Cần Taylor viết lại script persist + sửa nhãn + IS/OOS + leave-one-out trước khi trình lại. Hướng 1 redo (job Taylor_20260830_132917) đang chạy, chưa xong.
