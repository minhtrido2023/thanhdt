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

## CAP_SIGNAL advisory — implement XONG, chờ 1 quyết định nhỏ
- User duyệt 21:10 ICT dùng CAP_SIGNAL (DIVERGE composite, quant-skeptic CONFIRMED medium nhưng
  N=6 quá mỏng để wire) làm tín hiệu advisory tham khảo, tự tích luỹ case, tự đề xuất nâng cấp.
- Script: `agents/Taylor/cap_signal_advisory_check.py` — nguồn sống (VNI từ BQ, EEM/DXY/TNX từ
  yfinance qua $DNA_PYEXE, KHÔNG dùng tier2_macro_panel.csv đã đóng băng từ 15/05). Test hôm nay:
  im lặng, không fire (EM_dd60 ~-5-6%, chưa chạm -8%). Ghi registry
  `kb/data_registry/market-state/cap_signal_advisory_log.md`, gộp cụm ≤60 ngày = 1 cụm (đúng cách
  đếm N=6). Ngưỡng nâng cấp N≥10 — đạt thì tự bus question đề xuất review, KHÔNG tự wire.
  Quyết định đầy đủ: `kb/projects/cap-signal-advisory-20260830.md`.
- **Còn treo**: hàm `build_advisory_line()` đã sẵn sàng (display-only, mẫu §6b) nhưng CHƯA wire
  vào dna_report.py — đã hỏi user muốn wire ngay vào daily/weekly report hay để script chạy độc
  lập/thủ công trước. Chờ trả lời.

## Chuỗi khủng hoảng cơ cấu 2007-2012 + điểm mù 2018 — ĐÓNG HOÀN TOÀN
- Hướng 1 (valuation-gated tier-unlock): NO-GO, capacity chặn (60-79% episode thiếu ADV, edge đảo
  âm ở ngưỡng ≥10B/ngày). File: valuation_gated_tier_unlock_round2_20260830.md.
- Hướng 2 (DIVERGE CAP_SIGNAL): CONFIRMED nhưng chỉ advisory (xem mục trên) — không wire kỹ thuật
  vào production. File: diverge_indicator_strategy_backtest_round2_20260830.md.
- Episode clustering N=7->N=5, stress-test DT5G Phase A/B, Bobby BLIND read 2009/2018 — tài liệu
  tham khảo, không đổi production. DT5G giữ nguyên "bảo hiểm fail-safe", không re-tune lịch sử.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO. Sector sweep: đóng, coverage 20/20.
- C1 (DC-swap): củng cố REFUTED. Insider cluster-buy: NO-GO.
- Audit 8L thresholds: KHÔNG cần adaptive mới. NPL/CAR: giữ proxy ROE_Min3Y/Gordon-PB.

## Vận hành — dọn sạch 30/08, không còn việc treo cũ
- job quant-skeptic_20260830_085357: OVERDUE cosmetic (không sửa được), đã verify substance qua
  log trực tiếp — biết, bỏ qua.
- capit-lever selfcheck 2, retro-pattern checker hardcode: đã CLOSED từ 08-28.
- dt5g-writer-la-1931: điều tra ra + đóng.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T14:34:16Z] User duyệt 21:33 ICT wire build_advisory_line() vào cả 3 cadence report (daily/weekly/monthly). Dispatch Taylor_20260830_143403. Đang chạy, chưa xong.
